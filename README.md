# 🦺 JSA Agent — Fine-Kinney Risk Değerlendirme Sistemi

> **AI destekli İş Güvenliği Analizi (JSA) ve Fine-Kinney risk puanlaması.**  
> Fotoğraf yükle → AI tehlikeleri tespit etsin → Kontrol önermelerini gör → PDF + JSON al.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://jsa-agent.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)

🔗 **Demo:** [jsa-agent.streamlit.app](https://jsa-agent.streamlit.app)

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                     KULLANICI (Tarayıcı)                    │
│                    Streamlit Arayüzü                        │
│              jsa_agent.py — 3 Adımlı UI                     │
└──────────┬──────────────────────────┬───────────────────────┘
           │                          │
           ▼                          ▼
┌─────────────────────┐   ┌──────────────────────────────────┐
│   VISION KATMANI    │   │        KURAL MOTORU              │
│   jsa_visual.py     │   │        jsa_core.py               │
│                     │   │                                  │
│  GPT-4o Vision API  │   │  Fine-Kinney: R = P × F × E      │
│  → Tehlike Listesi  │   │  Tehlike Kategorileri            │
│  → AI Güven Skoru   │   │  Risk Eşik Tablosu               │
│  → E Önerisi        │   │  Kontrol Hiyerarşisi             │
│  → Eksik KKD        │   │  (ISO 45001 / NIOSH)             │
└─────────┬───────────┘   └──────────────┬───────────────────┘
          │                              │
          └──────────────┬───────────────┘
                         │
                         ▼
           ┌─────────────────────────┐
           │      ÇIKTI KATMANI      │
           │  📄 PDF Raporu          │
           │  📦 JSON Export         │
           └─────────────────────────┘
```

### Veri Akışı

```
[Foto Yükleme]
      │
      ▼
[GPT-4o Vision API]
  ├── Tehlike Listesi (kategori + açıklama)
  ├── AI Güven Skoru 🟢🟡🔴
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
| **AI Tehlike Tespiti** | GPT-4o Vision ile fotoğraftan otomatik tehlike tanımlama |
| **Güven Skoru** | 🟢 Yüksek / 🟡 Orta / 🔴 Düşük — sahada doğrulama yönlendirmesi |
| **Fine-Kinney Skorlama** | R = P × F × E standart risk hesabı, 5 seviye sınıflandırma |
| **Hibrit Değerlendirme** | AI şiddet (E) önerir, kullanıcı P ve F operasyonel verilerini girer |
| **Kontrol Önerileri** | ISO 45001 hiyerarşisi: Eliminasyon → İkame → Mühendislik → İdari → KKD |
| **PDF Raporu** | Fotoğraf + AI tespiti + FK tablosu + kontrol önerileri + risk özeti |
| **JSON Export** | Standart şema v1.0 — audit trail ve sistem entegrasyonu için |

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
| 10.0 | Çok muhtemel — Hemen hemen kesin gerçekleşir |
| 6.0 | Muhtemel — Beklenebilir |
| 3.0 | Olası — Alışılmadık ama mümkün |
| 1.0 | Mümkün fakat düşük |
| 0.5 | Beklenmez fakat mümkün |
| 0.2 | Beklenmez |

**F — Frekans / Maruziyet (Frequency)**

| Değer | Açıklama |
|---|---|
| 10 | Hemen hemen sürekli — Bir saate birkaç defa |
| 6 | Sık — Günde bir veya birkaç defa |
| 3 | Ara sıra — Haftada bir veya birkaç defa |
| 2 | Sık değil — Ayda bir veya birkaç defa |
| 1 | Seyrek — Yılda birkaç defa |
| 0.5 | Çok seyrek — Yılda bir defa veya daha az |

**E — Şiddet / Etki (Effect/Severity)**

| Değer | Açıklama |
|---|---|
| 100 | Birden fazla ölümlü kaza / Çevresel felaket |
| 40 | Öldürücü kaza / Tam Maluliyet / Ciddi çevresel zarar |
| 15 | Sakatlık / Uzuv Kaybı / Meslek Hastalığı |
| 7 | Önemli hasar, dış ilkyardım ihtiyacı |
| 3 | Küçük hasar, dahili ilk yardım |
| 1 | Ucuz atlatma, ramak kaldı |

### Risk Skalası

| R Skoru | Seviye | Aksiyon |
|---|---|---|
| > 400 | ⛔ KABUL EDİLEMEZ | Derhal durdur, çalışmayı başlatma |
| 200–400 | 🔴 KRİTİK | 1 hafta içinde acil aksiyon |
| 70–200 | 🟠 ÖNEMLİ | 1 ay içinde planlı aksiyon |
| 20–70 | 🟡 ORTA | Gözlemle, eğer aksiyon gerekiyorsa 3 ay içinde iyileştirme planla |
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
      "P": 0.5, "F": 3, "E": 15, "R": 22.5,
      "risk_level": "ORTA",
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
    "kritik": 1,
    "onemli": 1,
    "orta": 1
  }
}
```

---

## 🗂️ Dosya Yapısı

```
jsa-agent/
├── jsa_agent.py        → Streamlit arayüzü (3 adımlı UI)
├── jsa_core.py         → Fine-Kinney motoru + kontrol hiyerarşisi + JSON şeması
├── jsa_visual.py       → GPT-4o Vision API + ReportLab PDF üretimi
├── requirements.txt    → Python bağımlılıkları
├── packages.txt        → Sistem bağımlılıkları (DejaVu font)
├── .python-version     → Python 3.11
└── README.md
```

---

## 🚀 Kurulum

### Streamlit Cloud (Önerilen)

1. Repoyu fork'la
2. [share.streamlit.io](https://share.streamlit.io) → **New app**
3. **Main file:** `jsa_agent.py` | **Python:** `3.11`
4. Deploy → [jsa-agent.streamlit.app](https://jsa-agent.streamlit.app)

### Lokal

```bash
git clone https://github.com/Ugeyik83/jsa-agent
cd jsa-agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run jsa_agent.py
```

---

## 🔑 API Key

**OpenAI:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys) → Create new secret key

Uygulamanın sol paneline `sk-...` formatında yapıştır. GPT-4o kullanıldığından görsel analiz kalitesi yüksektir.

---

## 🔧 Tehlike Matrisini Güncelleme

`jsa_core.py` içindeki `HAZARD_CATEGORIES` ve `CONTROL_HIERARCHY` sözlüklerini kendi kurumsal matrisinizle doldurun. GPT-4o otomatik olarak bu listeyi kullanarak sınıflandırma yapar.

---

## ⚠️ Sınırlılıklar

- P ve F operasyonel veri gerektirdiğinden kullanıcı tarafından girilir
- Gizli mekanik tehlikeler (pano içi, boru içi) tespit edilemez
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
