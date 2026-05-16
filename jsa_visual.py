# jsa_visual.py — OpenAI GPT-4o Vision Tehlike Tespiti + ReportLab PDF Raporu

import os
import json
import base64
import io
from datetime import datetime
from pathlib import Path

from openai import OpenAI
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage, KeepTogether
)

from jsa_core import HAZARD_CATEGORIES, get_all_hazards_flat, get_controls, CONTROL_LABELS

# ── OpenAI Konfigürasyonu ──────────────────────────────────────────────────────

def init_gemini(api_key: str):
    """OpenAI client döndür — fonksiyon adı geriye dönük uyumluluk için korundu."""
    return OpenAI(api_key=api_key)


def image_to_base64_str(image: Image.Image) -> str:
    """PIL Image → base64 string (OpenAI vision formatı)."""
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def detect_hazards_gemini(client, image: Image.Image) -> dict:
    """
    OpenAI GPT-4o Vision ile tehlike tespiti.
    Fonksiyon adı geriye dönük uyumluluk için korundu.
    Çıktı: {"hazards": [...], "general_observations": str, "missing_ppe": [...]}
    """
    hazard_list_str = "\n".join(f"- {h}" for h in get_all_hazards_flat())
    b64_image = image_to_base64_str(image)

    prompt = f"""
Sen deneyimli bir İş Sağlığı ve Güvenliği uzmanısın.
Bu iş sahası fotoğrafını analiz et ve tehlikeleri tespit et.

Aşağıdaki tehlike listesinden uygun olanları seç. Listede olmayan tehlike görürsen ekleyebilirsin:

{hazard_list_str}

SADECE aşağıdaki JSON formatında yanıt ver. Başka hiçbir metin, açıklama veya markdown bloğu ekleme:

{{
  "hazards": [
    {{
      "id": 1,
      "description": "Tehlike açıklaması (Türkçe, net ve özgün)",
      "category": "Kategori adı",
      "location": "Görselde nerede görüldüğü (sol/sağ/ön plan vb.)",
      "affected_body_part": "Etkilenebilecek vücut bölgesi",
      "suggested_severity": "Felaket — Çok sayıda ölüm (100) veya diğer severity seçeneklerinden biri",
      "confidence": 0.80
    }}
  ],
  "general_observations": "Genel saha gözlemi (1-2 cümle)",
  "missing_ppe": ["eksik KKD 1", "eksik KKD 2"]
}}

Güven skoru (confidence) 0.0–1.0 arası olmalı.
Eğer görüntü net değilse veya tehlike tespit edemiyorsan boş liste döndür.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}",
                            "detail": "high"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "hazards": [],
            "general_observations": "Görüntü analiz edilemedi.",
            "missing_ppe": []
        }


# ── PDF Rapor Üretimi ─────────────────────────────────────────────────────────

# Türkçe karakter desteği için Unicode font kaydet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import urllib.request, tempfile, os as _os

def _register_fonts():
    """DejaVuSans fontunu indir ve kaydet — Türkçe/UTF-8 tam destek."""
    try:
        pdfmetrics.getFont("DejaVu")
        return "DejaVu", "DejaVu-Bold"
    except Exception:
        pass

    # Önce sistemde ara (Ubuntu/Debian'da genellikle kurulu gelir)
    system_paths = {
        "DejaVu":      ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                        "/usr/share/fonts/dejavu/DejaVuSans.ttf"],
        "DejaVu-Bold": ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"],
    }
    found = {}
    for name, paths in system_paths.items():
        for p in paths:
            if _os.path.exists(p):
                found[name] = p
                break

    if len(found) == 2:
        try:
            for name, path in found.items():
                pdfmetrics.registerFont(TTFont(name, path))
            return "DejaVu", "DejaVu-Bold"
        except Exception:
            pass

    # Sistemde yoksa indir — 3 retry, iki farklı URL kaynağı
    url_sets = [
        {
            "DejaVu":      "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf",
            "DejaVu-Bold": "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf",
        },
        {
            "DejaVu":      "https://sourceforge.net/projects/dejavu/files/dejavu/2.37/dejavu-fonts-ttf-2.37.tar.bz2",
        },
    ]
    tmp = tempfile.gettempdir()
    for url_map in url_sets[:1]:  # ilk set yeterli
        try:
            for name, url in url_map.items():
                path = _os.path.join(tmp, f"{name}.ttf")
                if not _os.path.exists(path):
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=10) as resp, open(path, "wb") as f:
                        f.write(resp.read())
                pdfmetrics.registerFont(TTFont(name, path))
            return "DejaVu", "DejaVu-Bold"
        except Exception:
            pass

    return "Helvetica", "Helvetica-Bold"

FONT_NORMAL, FONT_BOLD = _register_fonts()

# Renk paleti
DARK_BLUE  = colors.HexColor("#1B2A4A")
MID_BLUE   = colors.HexColor("#2E5FAC")
LIGHT_BLUE = colors.HexColor("#EAF0FB")
RED        = colors.HexColor("#C0392B")
ORANGE     = colors.HexColor("#E67E22")
YELLOW     = colors.HexColor("#F1C40F")
GREEN      = colors.HexColor("#1E8449")
GRAY       = colors.HexColor("#F4F6F9")
TEXT_DARK  = colors.HexColor("#1A1A2E")

RISK_COLOR_MAP = {
    "KABUL EDİLEMEZ": colors.HexColor("#8B0000"),
    "KRİTİK":         colors.HexColor("#C0392B"),
    "ÖNEMLİ":         colors.HexColor("#E67E22"),
    "ORTA":           colors.HexColor("#F1C40F"),
    "DÜŞÜK":          colors.HexColor("#1E8449"),
}


def _styles():
    custom = {
        "title": ParagraphStyle(
            "title", fontName=FONT_BOLD, fontSize=22,
            textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=12
        ),
        "subtitle": ParagraphStyle(
            "subtitle", fontName=FONT_NORMAL, fontSize=11,
            textColor=MID_BLUE, alignment=TA_CENTER, spaceAfter=2
        ),
        "section": ParagraphStyle(
            "section", fontName=FONT_BOLD, fontSize=12,
            textColor=DARK_BLUE, spaceBefore=12, spaceAfter=6
        ),
        "body": ParagraphStyle(
            "body", fontName=FONT_NORMAL, fontSize=9,
            textColor=TEXT_DARK, leading=13
        ),
        "cell": ParagraphStyle(
            "cell", fontName=FONT_NORMAL, fontSize=8,
            textColor=TEXT_DARK, leading=11
        ),
        # Koyu zemin için beyaz — tablo header'larında kullanılır
        "cell_bold": ParagraphStyle(
            "cell_bold", fontName=FONT_BOLD, fontSize=8,
            textColor=colors.white, leading=11
        ),
        # Koyu zemin değil, açık zemin için koyu bold
        "cell_bold_dark": ParagraphStyle(
            "cell_bold_dark", fontName=FONT_BOLD, fontSize=8,
            textColor=TEXT_DARK, leading=11
        ),
        "small": ParagraphStyle(
            "small", fontName=FONT_NORMAL, fontSize=7,
            textColor=colors.HexColor("#666666")
        ),
    }
    return custom


def generate_pdf(
    image: Image.Image,
    gemini_result: dict,
    hazard_rows: list,        # [{"tehlike", "kategori", "p_label", "f_label", "e_label", "risk"}]
    meta: dict,               # {"firma", "bolum", "is_tanimi", "analist", "tarih"}
    output_path: str = None,
) -> bytes:
    """
    Tam JSA / Fine-Kinney PDF raporu üret.
    Döndürür: PDF bytes (Streamlit download için)
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
    )
    W = A4[0] - 3.6*cm  # kullanılabilir genişlik
    S = _styles()
    story = []

    # ── BAŞLIK BLOĞU ──────────────────────────────────────────────────────────
    story.append(Paragraph("İŞ GÜVENLİĞİ ANALİZİ RAPORU", S["title"]))
    story.append(Paragraph("Fine-Kinney Risk Değerlendirme Yöntemi", S["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE, spaceAfter=10))
    # ── META BİLGİLER TABLOSU ─────────────────────────────────────────────────
    meta_data = [
        ["Firma / Tesis", meta.get("firma", "—"),
         "Analiz Tarihi", meta.get("tarih", datetime.today().strftime("%d.%m.%Y"))],
        ["Bölüm / Alan",  meta.get("bolum", "—"),
         "Analist",       meta.get("analist", "—")],
        ["İş Tanımı",     meta.get("is_tanimi", "—"), "", ""],
    ]
    meta_table = Table(
        [[Paragraph(str(c), S["cell_bold_dark"] if i % 2 == 0 else S["cell"])
          for i, c in enumerate(row)] for row in meta_data],
        colWidths=[3.2*cm, 6.5*cm, 3.2*cm, 5.0*cm],
    )
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), GRAY),
        ("BACKGROUND", (0,0), (0,-1), LIGHT_BLUE),
        ("BACKGROUND", (2,0), (2,-1), LIGHT_BLUE),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("PADDING", (0,0), (-1,-1), 5),
        ("SPAN", (1,2), (3,2)),  # İş tanımı satırı birleştir
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # ── FOTOĞRAF ──────────────────────────────────────────────────────────────
    story.append(Paragraph("📷 Analiz Edilen Görsel", S["section"]))

    img_buf = io.BytesIO()
    # Oranı koruyarak genişliği sınırla
    max_w = W * 0.75
    orig_w, orig_h = image.size
    scale = min(max_w / orig_w, (8*cm) / orig_h)
    img_w = orig_w * scale
    img_h = orig_h * scale
    image.save(img_buf, format="JPEG", quality=85)
    img_buf.seek(0)
    rl_img = RLImage(img_buf, width=img_w, height=img_h)
    story.append(rl_img)

    # Genel gözlem
    obs = gemini_result.get("general_observations", "")
    if obs:
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Genel Gözlem:</b> {obs}", S["body"]))

    missing_ppe = gemini_result.get("missing_ppe", [])
    if missing_ppe:
        story.append(Paragraph(
            f"<b>Eksik KKD:</b> {', '.join(missing_ppe)}", S["body"]
        ))
    story.append(Spacer(1, 8))

    # ── TEHLİKE TESPİT TABLOSU (Gemini ham çıktı) ────────────────────────────
    hazards_raw = gemini_result.get("hazards", [])
    if hazards_raw:
        story.append(Paragraph("🔍 AI Tehlike Tespiti (Gemini)", S["section"]))
        det_header = [
            Paragraph("<b>#</b>", S["cell_bold"]),
            Paragraph("<b>Tehlike</b>", S["cell_bold"]),
            Paragraph("<b>Kategori</b>", S["cell_bold"]),
            Paragraph("<b>Konum</b>", S["cell_bold"]),
            Paragraph("<b>Etkilenen Bölge</b>", S["cell_bold"]),
            Paragraph("<b>Güven</b>", S["cell_bold"]),
        ]
        det_rows = [det_header]
        for h in hazards_raw:
            conf = h.get("confidence", 0)
            det_rows.append([
                Paragraph(str(h.get("id", "")), S["cell"]),
                Paragraph(h.get("description", ""), S["cell"]),
                Paragraph(h.get("category", ""), S["cell"]),
                Paragraph(h.get("location", ""), S["cell"]),
                Paragraph(h.get("affected_body_part", ""), S["cell"]),
                Paragraph(f"%{int(conf*100)}", S["cell"]),
            ])
        det_table = Table(
            det_rows,
            colWidths=[0.7*cm, 5.5*cm, 3.2*cm, 2.8*cm, 2.8*cm, 1.5*cm],
        )
        det_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, GRAY]),
            ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#CCCCCC")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("PADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(det_table)
        story.append(Spacer(1, 10))

    # ── FINE-KINNEY SKORLAMA TABLOSU ─────────────────────────────────────────
    if hazard_rows:
        story.append(Paragraph("📊 Fine-Kinney Risk Değerlendirmesi", S["section"]))

        fk_header = [
            Paragraph("<b>#</b>", S["cell_bold"]),
            Paragraph("<b>Tehlike</b>", S["cell_bold"]),
            Paragraph("<b>P</b>", S["cell_bold"]),
            Paragraph("<b>F</b>", S["cell_bold"]),
            Paragraph("<b>E</b>", S["cell_bold"]),
            Paragraph("<b>R = P×F×E</b>", S["cell_bold"]),
            Paragraph("<b>Risk Seviyesi</b>", S["cell_bold"]),
            Paragraph("<b>Aksiyon</b>", S["cell_bold"]),
        ]
        fk_rows = [fk_header]
        for i, row in enumerate(hazard_rows, 1):
            risk = row["risk"]
            level = risk["level"]
            lvl_color = RISK_COLOR_MAP.get(level, colors.black)
            fk_rows.append([
                Paragraph(str(i), S["cell"]),
                Paragraph(row.get("tehlike", ""), S["cell"]),
                Paragraph(str(risk["P"]), S["cell"]),
                Paragraph(str(risk["F"]), S["cell"]),
                Paragraph(str(risk["E"]), S["cell"]),
                Paragraph(f"<b>{risk['R']}</b>", S["cell_bold"]),
                Paragraph(f"<b>{level}</b>", ParagraphStyle(
                    "lvl", fontName=FONT_BOLD, fontSize=8,
                    textColor=lvl_color
                )),
                Paragraph(risk["action"], S["small"]),
            ])

        fk_table = Table(
            fk_rows,
            colWidths=[0.6*cm, 4.8*cm, 1.0*cm, 1.0*cm, 1.0*cm, 1.5*cm, 2.5*cm, 4.5*cm],
        )
        fk_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, GRAY]),
            ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#CCCCCC")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("PADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(fk_table)
        story.append(Spacer(1, 10))

    # ── ÖZET İSTATİSTİK ───────────────────────────────────────────────────────
    if hazard_rows:
        story.append(Paragraph("📈 Risk Özeti", S["section"]))
        from jsa_core import get_risk_summary
        risks = [r["risk"] for r in hazard_rows]
        summary = get_risk_summary(risks)

        sum_data = [
            ["Toplam Tehlike", str(summary.get("toplam_tehlike", 0)),
             "Max Risk Skoru", str(summary.get("max_skor", 0))],
            ["Kabul Edilemez", str(summary.get("kabul_edilemez", 0)),
             "Kritik",         str(summary.get("kritik", 0))],
            ["Önemli",         str(summary.get("onemli", 0)),
             "Orta",           str(summary.get("orta", 0))],
            ["Düşük",          str(summary.get("dusuk", 0)),
             "Ort. Risk Skoru",str(summary.get("ort_skor", 0))],
        ]
        sum_table = Table(
            [[Paragraph(str(c), S["cell_bold_dark"] if i % 2 == 0 else S["cell"])
              for i, c in enumerate(row)] for row in sum_data],
            colWidths=[4.5*cm, 3.0*cm, 4.5*cm, 3.0*cm],
        )
        sum_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), GRAY),
            ("BACKGROUND", (0,0), (0,-1), LIGHT_BLUE),
            ("BACKGROUND", (2,0), (2,-1), LIGHT_BLUE),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
            ("PADDING", (0,0), (-1,-1), 5),
        ]))
        story.append(sum_table)
        story.append(Spacer(1, 10))

    # ── RİSK KONTROL ÖNERİLERİ TABLOSU ──────────────────────────────────────
    if hazard_rows:
        story.append(Paragraph("🛡️ Risk Kontrol Önerileri (ISO 45001 Hiyerarşisi)", S["section"]))
        story.append(Paragraph(
            "Önlemler, etkinlik sırasına göre listelenmiştir: "
            "Eliminasyon (en etkili) → KKD (son çare)",
            S["body"]
        ))
        story.append(Spacer(1, 6))

        ctrl_header = [
            Paragraph("<b>#</b>", S["cell_bold"]),
            Paragraph("<b>Tehlike</b>", S["cell_bold"]),
            Paragraph("<b>🔴 Eliminasyon</b>", S["cell_bold"]),
            Paragraph("<b>🟡 Mühendislik</b>", S["cell_bold"]),
            Paragraph("<b>🔵 İdari</b>", S["cell_bold"]),
            Paragraph("<b>🟢 KKD</b>", S["cell_bold"]),
        ]
        ctrl_rows = [ctrl_header]
        for i, row in enumerate(hazard_rows, 1):
            controls = get_controls(row.get("kategori", ""), row.get("tehlike", ""))
            ctrl_rows.append([
                Paragraph(str(i), S["cell"]),
                Paragraph(row.get("tehlike", ""), S["cell"]),
                Paragraph(controls.get("elimination", "—"), S["cell"]),
                Paragraph(controls.get("engineering", "—"), S["cell"]),
                Paragraph(controls.get("administrative", "—"), S["cell"]),
                Paragraph(controls.get("ppe", "—"), S["cell"]),
            ])

        ctrl_table = Table(
            ctrl_rows,
            colWidths=[0.6*cm, 3.8*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3.0*cm],
        )
        ctrl_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, GRAY]),
            ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#CCCCCC")),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("PADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(ctrl_table)
        story.append(Spacer(1, 10))

    # ── FINE-KINNEY REFERANS TABLOSU ──────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CCCCCC"), spaceBefore=8))
    story.append(Paragraph("Fine-Kinney Risk Skala Referansı", S["subtitle"]))

    ref_levels = [
        ("> 400",   "KABUL EDİLEMEZ", "Derhal durdur",               colors.HexColor("#8B0000")),
        ("200–400", "KRİTİK",         "24 saat içinde aksiyon",       colors.HexColor("#C0392B")),
        ("70–200",  "ÖNEMLİ",         "1 hafta içinde aksiyon",       colors.HexColor("#E67E22")),
        ("20–70",   "ORTA",           "1 ay içinde planlı aksiyon",   colors.HexColor("#F1C40F")),
        ("< 20",    "DÜŞÜK",          "Periyodik gözlem",             colors.HexColor("#1E8449")),
    ]

    ref_header = [
        Paragraph("R Skoru", S["cell_bold"]),
        Paragraph("Seviye",  S["cell_bold"]),
        Paragraph("Aksiyon", S["cell_bold"]),
    ]
    ref_rows = [ref_header]
    ref_style = [
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#CCCCCC")),
        ("PADDING", (0,0), (-1,-1), 5),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]
    for i, (skor, seviye, aksiyon, bg) in enumerate(ref_levels, 1):
        # Sarı için koyu metin, diğerleri beyaz
        txt_color = TEXT_DARK if bg == colors.HexColor("#F1C40F") else colors.white
        seviye_style = ParagraphStyle(
            f"ref_{i}", fontName=FONT_BOLD, fontSize=8,
            textColor=txt_color, leading=11
        )
        ref_rows.append([
            Paragraph(skor,    S["cell"]),
            Paragraph(seviye,  seviye_style),
            Paragraph(aksiyon, S["cell"]),
        ])
        ref_style.append(("BACKGROUND", (1,i), (1,i), bg))
        ref_style.append(("ROWBACKGROUNDS", (0,i), (0,i), [GRAY]))
        ref_style.append(("ROWBACKGROUNDS", (2,i), (2,i), [GRAY if i%2==0 else colors.white]))

    ref_table = Table(ref_rows, colWidths=[3.0*cm, 4.0*cm, 10.0*cm])
    ref_table.setStyle(TableStyle(ref_style))
    story.append(ref_table)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Bu rapor JSA Agent tarafından otomatik oluşturulmuştur. "
        f"Üretim tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')} | "
        f"Fine-Kinney yöntemi (Kinney & Wiruth, 1976)",
        S["small"]
    ))

    doc.build(story)
    pdf_bytes = buf.getvalue()

    if output_path:
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes