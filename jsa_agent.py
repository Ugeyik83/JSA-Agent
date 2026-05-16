# jsa_agent.py — JSA Streamlit Arayüzü
# Fine-Kinney Risk Değerlendirme Ajanı

import streamlit as st
from PIL import Image
import io
from datetime import datetime

from jsa_core import (
    PROBABILITY, FREQUENCY, SEVERITY,
    HAZARD_CATEGORIES, calculate_risk, get_risk_summary,
    get_controls, CONTROL_LABELS, build_json_output
)
from jsa_visual import init_gemini, detect_hazards_gemini, generate_pdf

# ── Sayfa Konfigürasyonu ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="JSA Agent — Fine-Kinney",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .stApp header { background-color: #1B2A4A; }
    h1 { color: #1B2A4A !important; }
    h2, h3 { color: #2E5FAC !important; }
    .risk-box {
        padding: 12px 18px; border-radius: 8px;
        font-weight: bold; font-size: 18px;
        text-align: center; margin: 8px 0;
    }
    .stButton > button {
        background-color: #2E5FAC; color: white;
        border: none; border-radius: 6px;
        font-weight: bold;
    }
    .stButton > button:hover { background-color: #1B2A4A; }
    div[data-testid="stMetricValue"] { font-size: 28px !important; color: #1B2A4A; }
</style>
""", unsafe_allow_html=True)

# ── Session State Başlat ───────────────────────────────────────────────────────
if "gemini_result" not in st.session_state:
    st.session_state.gemini_result = None
if "hazard_rows" not in st.session_state:
    st.session_state.hazard_rows = []
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/safety-helmet.png", width=64)
    st.title("JSA Agent")
    st.caption("Fine-Kinney Risk Değerlendirme")
    st.divider()

    # API Key
    st.subheader("🔑 API Ayarları")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="https://platform.openai.com/api-keys adresinden alın"
    )
    st.divider()

    # Meta Bilgiler
    st.subheader("📋 Rapor Bilgileri")
    firma    = st.text_input("Firma / Tesis", placeholder="ABC Fabrikası")
    bolum    = st.text_input("Bölüm / Alan",  placeholder="Üretim Hattı B")
    is_tani  = st.text_input("İş Tanımı",     placeholder="Yüksekte kaynak işlemi")
    analist  = st.text_input("Analist Adı",   placeholder="Ad Soyad")
    tarih    = st.date_input("Analiz Tarihi", value=datetime.today())
    st.divider()

    st.caption("📐 Fine-Kinney: R = P × F × E")
    st.caption("Kinney & Wiruth, 1976")

# ── ANA BAŞLIK ────────────────────────────────────────────────────────────────
st.title("🦺 İş Güvenliği Analizi Ajanı")
st.markdown("**Fine-Kinney yöntemi** ile AI destekli tehlike tespiti ve risk puanlaması.")
st.divider()

# ── ADIM 1: FOTOĞRAF YÜKLEME ─────────────────────────────────────────────────
st.header("1️⃣ Fotoğraf Yükle")
uploaded_file = st.file_uploader(
    "İş sahası fotoğrafı yükleyin",
    type=["jpg", "jpeg", "png"],
    help="Net, iyi aydınlatılmış bir iş sahası fotoğrafı daha iyi sonuç verir."
)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.session_state.uploaded_image = image
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(image, caption="Yüklenen Fotoğraf", use_column_width=True)
    with col2:
        st.info(f"""
        📁 **Dosya:** {uploaded_file.name}
        📐 **Boyut:** {image.size[0]} × {image.size[1]} px
        """)

        if not api_key:
            st.warning("⚠️ Sol panelden OpenAI API Key girin.")
        else:
            if st.button("🔍 AI ile Tehlike Tespit Et", use_container_width=True):
                with st.spinner("🤖 AI fotoğrafı analiz ediyor, tehlikeler tespit ediliyor..."):
                    try:
                        model = init_gemini(api_key)
                        result = detect_hazards_gemini(model, image)
                        st.session_state.gemini_result = result
                        st.session_state.hazard_rows = []
                        st.success(f"✅ {len(result.get('hazards', []))} tehlike tespit edildi.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"API Hatası: {e}")

# ── ADIM 2: TEHLİKE LİSTESİ + P/F/E GİRİŞİ ──────────────────────────────────
if st.session_state.gemini_result:
    st.divider()
    st.header("2️⃣ Tehlikeleri Değerlendir")

    result = st.session_state.gemini_result
    hazards = result.get("hazards", [])

    # Genel gözlem ve eksik KKD
    if result.get("general_observations"):
        st.info(f"🔎 **Genel Gözlem:** {result['general_observations']}")
    if result.get("missing_ppe"):
        st.warning(f"🧢 **Eksik KKD:** {', '.join(result['missing_ppe'])}")

    if not hazards:
        st.warning("Tehlike tespit edilemedi. Farklı bir fotoğraf deneyin.")
    else:
        st.markdown(f"**{len(hazards)} tehlike tespit edildi.** Aşağıda her tehlike için P/F/E değerlerini onaylayın veya düzeltin.")

        hazard_rows = []
        p_keys = list(PROBABILITY.keys())
        f_keys = list(FREQUENCY.keys())
        e_keys = list(SEVERITY.keys())

        for h in hazards:
            with st.expander(
                f"⚠️ Tehlike #{h['id']}: {h['description']}",
                expanded=True
            ):
                col_info, col_pfk = st.columns([1, 2])

                with col_info:
                    st.markdown(f"**Kategori:** {h.get('category', '—')}")
                    st.markdown(f"**Konum:** {h.get('location', '—')}")
                    st.markdown(f"**Etkilenen Bölge:** {h.get('affected_body_part', '—')}")
                    conf = h.get("confidence", 0)
                    if conf >= 0.75:
                        conf_color = "🟢"
                        conf_note  = "Yüksek — sahada doğrulama önerilir"
                    elif conf >= 0.50:
                        conf_color = "🟡"
                        conf_note  = "Orta — sahada doğrulayın"
                    else:
                        conf_color = "🔴"
                        conf_note  = "Düşük — manuel inceleme gerekli"
                    st.progress(conf, text=f"{conf_color} Model Tahmin Beyanı: %{int(conf*100)} — {conf_note}")

                with col_pfk:
                    st.markdown("**Fine-Kinney Parametreleri**")

                    # Gemini önerdiği şiddeti varsayılan yap
                    suggested_e = h.get("suggested_severity", e_keys[2])
                    default_e_idx = e_keys.index(suggested_e) if suggested_e in e_keys else 2

                    p_sel = st.selectbox(
                        f"P — Olasılık #{h['id']}",
                        p_keys,
                        index=2,
                        key=f"p_{h['id']}"
                    )
                    f_sel = st.selectbox(
                        f"F — Frekans #{h['id']}",
                        f_keys,
                        index=2,
                        key=f"f_{h['id']}"
                    )
                    e_sel = st.selectbox(
                        f"E — Şiddet #{h['id']} (AI önerisi işaretli)",
                        e_keys,
                        index=default_e_idx,
                        key=f"e_{h['id']}"
                    )

                    risk = calculate_risk(p_sel, f_sel, e_sel)

                    # Risk kutusu
                    color = risk["color"]
                    st.markdown(
                        f'<div class="risk-box" style="background-color:{color}20; '
                        f'border-left: 5px solid {color}; color:{color}">'
                        f'R = {risk["R"]} — {risk["level"]}</div>',
                        unsafe_allow_html=True
                    )
                    st.caption(risk["action"])

                hazard_rows.append({
                    "tehlike":    h["description"],
                    "kategori":   h.get("category", ""),
                    "p_label":    p_sel,
                    "f_label":    f_sel,
                    "e_label":    e_sel,
                    "risk":       risk,
                    "confidence": h.get("confidence", 0),
                })

                # Kontrol önerileri — expander içinde ayrı bölüm
                controls = get_controls(h.get("category", ""), h["description"])
                if controls:
                    with st.expander("🛡️ Kontrol Önerileri (ISO 45001 Hiyerarşisi)", expanded=False):
                        for key, label in CONTROL_LABELS.items():
                            val = controls.get(key, "—")
                            st.markdown(f"**{label}:** {val}")

        st.session_state.hazard_rows = hazard_rows

# ── ADIM 3: ÖZET + PDF ────────────────────────────────────────────────────────
if st.session_state.hazard_rows:
    st.divider()
    st.header("3️⃣ Risk Özeti ve Rapor")

    risks = [r["risk"] for r in st.session_state.hazard_rows]
    summary = get_risk_summary(risks)

    # Metrik kartlar
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Toplam Tehlike",    summary["toplam_tehlike"])
    col2.metric("Max Risk Skoru",    summary["max_skor"])
    col3.metric("⛔ Kabul Edilemez", summary["kabul_edilemez"])
    col4.metric("🔴 Kritik",         summary["kritik"])
    col5.metric("🟠 Önemli",         summary["onemli"])

    st.divider()

    # PDF Üret
    if st.button("📄 PDF Raporu Oluştur ve İndir", use_container_width=True):
        if not st.session_state.uploaded_image:
            st.error("Fotoğraf bulunamadı.")
        else:
            with st.spinner("PDF oluşturuluyor..."):
                meta = {
                    "firma":     firma,
                    "bolum":     bolum,
                    "is_tanimi": is_tani,
                    "analist":   analist,
                    "tarih":     tarih.strftime("%d.%m.%Y"),
                }
                try:
                    pdf_bytes = generate_pdf(
                        image=st.session_state.uploaded_image,
                        gemini_result=st.session_state.gemini_result,
                        hazard_rows=st.session_state.hazard_rows,
                        meta=meta,
                    )
                    dosya_adi = f"JSA_Raporu_{tarih.strftime('%Y%m%d')}.pdf"
                    st.download_button(
                        label="⬇️ PDF İndir",
                        data=pdf_bytes,
                        file_name=dosya_adi,
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.success("✅ PDF hazır!")
                except Exception as e:
                    st.error(f"PDF oluşturma hatası: {e}")

    # JSON Export
    import json as _json
    meta_for_json = {
        "firma": firma, "bolum": bolum,
        "is_tanimi": is_tani, "analist": analist,
        "tarih": tarih.strftime("%d.%m.%Y"),
    }
    json_output = build_json_output(meta_for_json, st.session_state.hazard_rows)
    json_str = _json.dumps(json_output, ensure_ascii=False, indent=2)

    col_json, col_prev = st.columns([1, 1])
    with col_json:
        st.download_button(
            label="⬇️ JSON Export (Standart Şema)",
            data=json_str,
            file_name=f"JSA_{tarih.strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
        )
    with col_prev:
        with st.expander("🔍 JSON Önizleme"):
            st.code(json_str[:1500] + ("\n..." if len(json_str) > 1500 else ""), language="json")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "JSA Agent v1.0 | Fine-Kinney Yöntemi (Kinney & Wiruth, 1976) | "
    "AI destekli analiz profesyonel değerlendirmenin yerini tutmaz."
)