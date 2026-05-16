# 🦺 JSA Agent — Fine-Kinney Risk Değerlendirme Sistemi

> **AI destekli İş Güvenliği Analizi (JSA) ve Fine-Kinney risk puanlaması.**  
> Fotoğraf yükle → AI tehlikeleri tespit etsin → Kontrol önermelerini gör → PDF + JSON al.

[![Streamlit App]]([https://your-app-url.streamlit.app](https://jsa-agent.streamlit.app/))
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📸 Ekran Görüntüleri

> *(Deploy sonrası ekran görüntülerini buraya ekle)*

| Adım | Ekran |
|---|---|
| Fotoğraf yükleme + AI analiz | `screenshots/01_upload.png` |
| Fine-Kinney P/F/E değerlendirme | `screenshots/02_assessment.png` |
| Risk özeti + JSON/PDF export | `screenshots/03_report.png` |

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                     KULLANICI (Tarayıcı)                     │
│                    Streamlit Arayüzü                         │
│              jsa_agent.py — 3 Adımlı UI                     │
└──────────┬──────────────────────────┬───────────────────────┘
           │                          │
           ▼                          ▼
┌─────────────────────┐   ┌──────────────────────────────────┐
│   VISION KATMANI    │   │        KURAL MOTORU              │
│   jsa_visual.py     │   │        jsa_core.py               │
│                     │   │                                  │
│  Gemini 1.5 Flash   │   │  Fine-Kinney: R = P × F × E     │
│  Vision API         │   │  Tehlike Kategorileri            │
│  → Tehlike Listesi  │   │  Risk Eşik Tablosu               │
│  → AI Güven Skoru   │   │  Kontrol Hiyerarşisi             │
│  → E Önerisi        │   │  (ISO 45001 / NIOSH)             │
└─────────┬───────────┘   └──────────────┬───────────────────┘
          │                              │
          └──────────────┬───────────────┘
                         │
                         ▼
           ┌─────────────────────────┐
           │      ÇIKTI KATMANI      │
           │  📄 PDF Raporu           │
           │  📦 JSON Export          │
           └─────────────────────────┘
```

### Veri Akışı

```
[Foto Yükleme]
      │
      ▼
[Gemini Vision API]
  ├── Tehlike Listesi (kategori + açıklama)
  ├── AI Güven Skoru (0.0–1.0)
  ├── Şiddet Önerisi (E parametresi)
  └── Eksik KKD Listesi
      │
      ▼
[Kullanıcı P/F/E Onayı]
  ├── P: Olasılık (kullanıcı girer)
  ├── F: Frekans  (kullanıcı girer)
  └── E: Şiddet   (AI önerir → kullanıcı onaylar)
      │
      ▼
[Fine-Kinney: R = P × F × E]
      │
      ▼
[Kontrol Önerileri — ISO 45001 Hiyerarşisi]
      │
      ├──▶ PDF Raporu (ReportLab)
      └──▶ JSON Export (Standart Şema v1.0)
```

---

## ✨ Özellikler

| Özellik | Açıklama |
|---|---|
| **AI Tehlike Tespiti** | Gemini 1.5 Flash ile fotoğraftan otomatik tehlike tanımlama |
| **Güven Skoru** | 🟢 Yüksek / 🟡 Orta / 🔴 Düşük — sahada doğrulama yönlendirmesi |
| **Fine-Kinney Skorlama** | R = P × F × E standart risk hesabı, 5 seviye sınıflandırma |
| **Hibrit Değerlendirme** | AI şiddet (E) önerir, kullanıcı P ve F operasyonel verilerini girer |
| **Kontrol Önerileri** | ISO 45001 hiyerarşisi: Eliminasyon → İkame → Mühendislik → İdari → KKD |
| **PDF Raporu** | Fotoğraf + AI tespiti + FK tablosu + kontrol önerileri + risk özeti |
| **JSON Export** | Standart şema v1.0 — audit trail ve sistem entegrasyonu için |
| **Ücretsiz API** | Gemini 1.5 Flash — günlük 1.500 istek ücretsiz |

---

## 🔢 Fine-Kinney Yöntemi

### Formül

```
R = P × F × E
```

### Parametre Tabloları

**P — Olasılık (Probability)**

| Değer | Açıklama |
|---|---|
| 1.0 | Çok muhtemel — Hemen hemen kesin gerçekleşir |
| 0.5 | Muhtemel — Beklenebilir |
| 0.2 | Az olası — Alışılmadık ama mümkün |
| 0.1 | Nadiren olası — Çok az ihtimalle |
| 0.05 | Hayal edilebilir — Teorik olarak mümkün |
| 0.01 | Pratik imkânsız — Ancak mantıken mümkün |

**F — Frekans / Maruziyet (Frequency)**

| Değer | Açıklama |
|---|---|
| 10 | Sürekli — Günde çok kez |
| 6 | Sık sık — Günde birkaç kez |
| 3 | Günde bir kez |
| 2 | Haftada bir |
| 1 | Ayda bir |
| 0.5 | Yılda bir |

**E — Şiddet / Etki (Effect/Severity)**

| Değer | Açıklama |
|---|---|
| 100 | Felaket — Çok sayıda ölüm |
| 40 | Çok ciddi — Birkaç ölüm |
| 15 | Ciddi — Bir ölüm |
| 7 | Önemli — Ağır yaralanma, kalıcı hasar |
| 3 | Hafif — İlk yardım gerektiren yaralanma |
| 1 | İhmal edilebilir — Küçük kesik, morluk |

### Risk Skalası

| R Skoru | Seviye | Aksiyon |
|---|---|---|
| > 400 | ⛔ KABUL EDİLEMEZ | Derhal durdur, çalışmayı başlatma |
| 200–400 | 🔴 KRİTİK | 24 saat içinde acil aksiyon |
| 70–200 | 🟠 ÖNEMLİ | 1 hafta içinde planlı aksiyon |
| 20–70 | 🟡 ORTA | 1 ay içinde iyileştirme planla |
| < 20 | 🟢 DÜŞÜK | Periyodik gözlem yeterli |

---

## 📦 JSON Çıktı Şeması (v1.0)

```json
{
  "schema_version": "1.0",
  "site": "ABC Fabrikası",
  "department": "Üretim Hattı B",
  "job_description": "Yüksekte kaynak işlemi",
  "analyst": "Ad Soyad",
  "date": "16.05.2026",
  "method": "Fine-Kinney (Kinney & Wiruth, 1976)",
  "hazards": [
    {
      "hazard_id": "H001",
      "category": "Fiziksel Tehlikeler",
      "description": "Yüksekten düşme riski",
      "ai_confidence": 0.88,
      "P": 0.5,
      "F": 3,
      "E": 15,
      "R": 22.5,
      "risk_level": "ORTA",
      "action": "🟡 1 ay içinde iyileştirme planla",
      "controls": {
        "elimination": "Yüksekte çalışmayı ortadan kaldır",
        "substitution": "Uzun kollu ekipman kullan",
        "engineering": "Güvenlik korkuluğu, iskele sistemi kur",
        "administrative": "Yüksekte çalışma izin sistemi uygula",
        "ppe": "Tam vücut emniyet kemeri (EN 361)"
      }
    }
  ],
  "summary": {
    "toplam_tehlike": 3,
    "max_skor": 90,
    "ort_skor": 45.2,
    "kabul_edilemez": 0,
    "kritik": 1,
    "onemli": 1,
    "orta": 1,
    "dusuk": 0
  }
}
```

---

## 🗂️ Dosya Yapısı

```
jsa-agent/
├── jsa_agent.py        → Streamlit arayüzü (3 adımlı UI)
├── jsa_core.py         → Fine-Kinney motoru + kontrol hiyerarşisi + JSON şeması
├── jsa_visual.py       → Gemini Vision API + ReportLab PDF üretimi
├── requirements.txt    → 4 Python paketi
├── .python-version     → Python 3.11
└── README.md
```

---

## 🚀 Kurulum

### Streamlit Cloud (Önerilen)

1. Repoyu fork'la
2. [share.streamlit.io](https://share.streamlit.io) → **New app**
3. **Main file:** `jsa_agent.py` | **Python:** `3.11`
4. Deploy → URL'i paylaş

### Lokal

```bash
git clone https://github.com/KULLANICI_ADI/jsa-agent
cd jsa-agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run jsa_agent.py
```

---

## 🔑 API Key

1. [Google AI Studio](https://aistudio.google.com/app/apikey) → **Create API Key**
2. Uygulamanın sol paneline yapıştır

**Ücretsiz limit:** 15 istek/dk · 1.500 istek/gün

---

## 🔧 Tehlike Matrisini Güncelleme

`jsa_core.py` içindeki `HAZARD_CATEGORIES` ve `CONTROL_HIERARCHY` sözlüklerini kendi matrisinizle doldurun. Gemini otomatik olarak bu listeyi kullanır.

---

## ⚠️ Sınırlılıklar

- P ve F operasyonel veri gerektirdiğinden kullanıcı tarafından girilir
- Gizli mekanik tehlikeler tespit edilemez
- Düşük güven skoru (%50 altı) sahada doğrulama gerektirir
- Profesyonel İSG değerlendirmesinin yerini **tutmaz**, destekler

---

## 📚 Referans

Kinney, G.F. & Wiruth, A.D. (1976). *Practical Risk Analysis for Safety Management.*  
Naval Weapons Center, China Lake, California.

---

## 🔗 İlgili Proje

[REBA Ergonomi Agent](https://github.com/Ugeyik83/reba-ergonomi-agent) — AI destekli postür risk analizi

---

*JSA Agent v1.1 | [@Ugeyik83](https://github.com/Ugeyik83)*
