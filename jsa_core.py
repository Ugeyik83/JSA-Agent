# jsa_core.py — Fine-Kinney Kural Motoru
# Tehlike kategorileri ileride kullanıcının matrisinden güncellenecek
# v1.1 — Risk kontrol önerileri + JSON output standardı eklendi

# ── Fine-Kinney Parametreleri ─────────────────────────────────────────────────

PROBABILITY = {
    "Çok muhtemel (10.0)":          10.0,
    "Muhtemel (6.0)":              6.0,
    "Olası (3.0)":              3.0,
    "Mümkün fakat düşük (1.0)":         1.0,
    "Beklenmez fakat mümkün (0.5)":     0.5,
    "Beklenmez (0.2)":      0.2,
}

FREQUENCY = {
    "Hemen hemen sürekli (Bir saate birkaç defa)(10)":   10,
    "Sık (Günde bir veya birkaç defa) (6)": 6,
    "Ara sıra (haftada bir veya birkaç defa) (3)":           3,
    "Sık değil (Ayda bir veya birkaç defa) (2)":             2,
    "Seyrek (Yılda biraç defa) (1)":                1,
    "Çok seyrek (Yılda bir defa veya daha az) (0.5)":       0.5,
}

SEVERITY = {
    "Birden fazla ölümlü kaza/Çevresel felaket (100)":     100,
    "Öldürücü kaza/Tam Maluliyet/Ciddi çevresel zarar (40)":         40,
    "Sakatlık /Uzuv Kaybı/Çevresel engel oluşturma/Meslek Hastalığı (15)":                15,
    "Önemli hasar, yaralanma, dış ilkyardım ihtiyacı/arazi sınırları dışında çevresel zarar (7)":           7,
    "Küçük hasar/yaralanma, dahili ilk yardım/arazi sınırları içinde çevresel zarar(3)":               3,
    "Ucuz atlatma, ramak kaldı/Çevresel zarar yok(1)":    1,
}

# Risk Skoru → Seviye eşikleri (Fine-Kinney standart)
RISK_LEVELS = [
    (400, "KABUL EDİLEMEZ",  "#8B0000", "⛔ Derhal durdur, çalışmayı başlatma"),
    (200, "KRİTİK",          "#FF0000", "🔴 24 saat içinde acil aksiyon"),
    (70,  "ÖNEMLİ",          "#FF8C00", "🟠 1 hafta içinde planlı aksiyon"),
    (20,  "ORTA",            "#FFD700", "🟡 1 ay içinde iyileştirme planla"),
    (0,   "DÜŞÜK",           "#228B22", "🟢 Periyodik gözlem yeterli"),
]

# ── Tehlike Kategorileri (Placeholder — matris verilince güncellenecek) ────────
HAZARD_CATEGORIES = {
    "Fiziksel Tehlikeler": [
        "Yüksekten düşme riski",
        "Döküntü / kaygan zemin",
        "Çarpma / takılma",
        "Sıkışma / ezilme",
        "Gürültü maruziyeti",
        "Titreşim maruziyeti",
        "Aşırı sıcaklık (sıcak/soğuk)",
        "Elektrik çarpması",
        "Yüklerin devrilmesi / düşmesi",
        "Radyasyon maruziyeti",
    ],
    "Kimyasal Tehlikeler": [
        "Kimyasal madde teması (cilt/göz)",
        "Kimyasal buhar inhalasyonu",
        "Yanıcı / patlayıcı madde",
        "Aşındırıcı madde",
        "Toksik madde maruziyeti",
    ],
    "Ergonomik Tehlikeler": [
        "Ağır yük taşıma",
        "Tekrarlayan hareket",
        "Zorlamalı / uygunsuz postür",
        "Uzun süreli statik duruş",
        "El-kol titreşimi",
    ],
    "Biyolojik Tehlikeler": [
        "Biyolojik ajan maruziyeti",
        "Keskin cisim yaralanması",
        "Haşere / hayvan teması",
    ],
    "Mekanik Tehlikeler": [
        "Hareketli makine parçaları",
        "Kesici / delici alet",
        "Basınçlı sistem patlaması",
        "Vinç / kaldırma ekipmanı arızası",
    ],
    "Yangın / Patlama": [
        "Yangın çıkma riski",
        "Patlama riski",
        "Duman / oksijen azalması",
    ],
    "Psikososyal Tehlikeler": [
        "Aşırı iş yükü / stres",
        "Şiddet / taciz riski",
        "Yalnız çalışma tehlikesi",
    ],
}

# ── Risk Kontrol Hiyerarşisi (ISO 45001 / NIOSH) ─────────────────────────────
CONTROL_HIERARCHY = {
    "Fiziksel Tehlikeler": {
        "Yüksekten düşme riski": {
            "elimination":    "Yüksekte çalışmayı ortadan kaldır, zemin seviyesinde yapılandır",
            "substitution":   "Uzun kollu ekipman / teleskopik alet kullan",
            "engineering":    "Güvenlik korkuluğu, güvenlik ağı, iskele sistemi kur",
            "administrative": "Yüksekte çalışma izin sistemi uygula, buddy system",
            "ppe":            "Tam vücut emniyet kemeri, bağlantı halatı (EN 361)",
        },
        "Döküntü / kaygan zemin": {
            "elimination":    "Sızıntı kaynağını tespit et ve kapat",
            "substitution":   "Kaymaz kaplama malzemesi kullan",
            "engineering":    "Drenaj sistemi, ızgara platform, sarı bant sınır çizgisi",
            "administrative": "Düzenli zemin kontrol çizelgesi, ıslak zemin işareti",
            "ppe":            "Kaymaz tabanlı güvenlik botu (EN ISO 20345)",
        },
        "Elektrik çarpması": {
            "elimination":    "Gereksiz elektrikli ekipmanı devre dışı bırak",
            "substitution":   "Düşük gerilimli sistem kullan",
            "engineering":    "İzolasyon, topraklama, kaçak akım rölesi (RCD)",
            "administrative": "Kilitleme/etiketleme (LOTO) prosedürü, izinli çalışma",
            "ppe":            "Yalıtımlı eldiven (EN 60903), yalıtımlı bot",
        },
        "Yüklerin devrilmesi / düşmesi": {
            "elimination":    "Yük taşıma ihtiyacını ortadan kaldır",
            "substitution":   "Mekanik taşıma sistemi kullan",
            "engineering":    "Yük sabitleme sistemi, bariyer, bariyerli depolama",
            "administrative": "İstif yükseklik limiti, yük güvenlik talimatı",
            "ppe":            "Baret (EN 397), çelik burunlu bot",
        },
        "Gürültü maruziyeti": {
            "elimination":    "Gürültü kaynağını kaldır",
            "substitution":   "Sessiz ekipmanla değiştir",
            "engineering":    "Akustik kabin, titreşim izolasyonu",
            "administrative": "Maruziyet süresi rotasyonu, sessiz alan tanımla",
            "ppe":            "Kulak tıkacı / kulaklık (EN 352), SNR ≥ 30 dB",
        },
    },
    "Kimyasal Tehlikeler": {
        "Kimyasal madde teması (cilt/göz)": {
            "elimination":    "Kimyasalı formülasyondan çıkar",
            "substitution":   "Daha az tehlikeli alternatif kullan",
            "engineering":    "Kapalı sistem, göz duşu, acil duş",
            "administrative": "GBF/SDS eğitimi, kimyasal envanter kontrolü",
            "ppe":            "Kimyasal dirençli eldiven, tam yüz maskesi, apron",
        },
        "Kimyasal buhar inhalasyonu": {
            "elimination":    "Buhar üreten işlemi kaldır",
            "substitution":   "Daha düşük uçuculuklu ürün kullan",
            "engineering":    "Lokal egzoz havalandırma (LEV), genel havalandırma",
            "administrative": "TWA/STEL izleme, maruziyet süresi sınırı",
            "ppe":            "Yarım/tam yüz maskesi, uygun filtre kartuşu (EN 140)",
        },
        "Yanıcı / patlayıcı madde": {
            "elimination":    "Yanıcı madde kullanımını azalt / kaldır",
            "substitution":   "Alev almaz alternatif kullan",
            "engineering":    "Ex-proof ekipman, topraklama, patlama kapağı",
            "administrative": "ATEX zonlama, ateşleme kaynağı kontrolü, izin sistemi",
            "ppe":            "Antistatik iş elbisesi, alev geciktirici KKD",
        },
    },
    "Ergonomik Tehlikeler": {
        "Ağır yük taşıma": {
            "elimination":    "Manuel taşıma ihtiyacını ortadan kaldır",
            "substitution":   "Elektrikli transpalet, forklift kullan",
            "engineering":    "Konveyör, kaldırma yardımcısı, çalışma yüksekliği ayarlı tezgah",
            "administrative": "25 kg üzeri ekip kaldırma kuralı, rotasyon",
            "ppe":            "Bel destek kemeri (önleyici değil, destekleyici), kaymaz eldiven",
        },
        "Tekrarlayan hareket": {
            "elimination":    "Tekrarlayan görevi otomasyonla kaldır",
            "substitution":   "Ergonomik alet tasarımı kullan",
            "engineering":    "Exoskeleton desteği, güç aletleri",
            "administrative": "Mikro mola takvimi, görev rotasyonu",
            "ppe":            "Kompresyon eldiveni, bilek desteği",
        },
    },
    "Mekanik Tehlikeler": {
        "Hareketli makine parçaları": {
            "elimination":    "Tehlikeli hareketi ortadan kaldır",
            "substitution":   "Güvenli tasarımlı makineyle değiştir",
            "engineering":    "Koruyucu kapak, muhafaza, fotosell bariyer",
            "administrative": "LOTO prosedürü, makine güvenlik talimatı",
            "ppe":            "Sıkışmaya karşı eldiven, saç/kıyafet düzeni",
        },
        "Basınçlı sistem patlaması": {
            "elimination":    "Basınçlı sistemi kaldır",
            "substitution":   "Daha düşük basınçlı alternatif kullan",
            "engineering":    "Emniyet valfi, basınç göstergesi, periyodik test",
            "administrative": "Periyodik muayene takvimi, operatör eğitimi",
            "ppe":            "Yüz siperi, basınca dayanıklı eldiven",
        },
    },
    "Yangın / Patlama": {
        "Yangın çıkma riski": {
            "elimination":    "Ateşleme kaynağı ve yanıcı maddeyi birbirinden ayır",
            "substitution":   "Yanmaz malzeme kullan",
            "engineering":    "Sprinkler sistemi, yangın kapısı, duman dedektörü",
            "administrative": "Acil tahliye planı, yangın tatbikatı, yangın izni",
            "ppe":            "Alev geciktirici iş elbisesi (EN ISO 11612)",
        },
    },
    "Biyolojik Tehlikeler": {
        "Keskin cisim yaralanması": {
            "elimination":    "Keskin cisim kullanımını azalt",
            "substitution":   "Güvenli iğne / bistüri sistemi kullan",
            "engineering":    "Keskin atık kutusu, otomatik kapanır kap",
            "administrative": "Keskin alet güvenlik prosedürü, eğitim",
            "ppe":            "Kesme dirençli eldiven (EN 388), gözlük",
        },
    },
}

# Kategori bazında genel önlem (spesifik tehlike yoksa fallback)
GENERAL_CONTROLS = {
    "Fiziksel Tehlikeler":    {"engineering": "Fiziksel bariyer ve koruyucu kur", "ppe": "Uygun KKD kullan (baret, bot, yelek)"},
    "Kimyasal Tehlikeler":    {"engineering": "Havalandırma sağla", "ppe": "Kimyasal KKD kullan (eldiven, maske)"},
    "Ergonomik Tehlikeler":   {"engineering": "Çalışma yüksekliğini ayarla", "ppe": "Destek ekipmanı kullan"},
    "Mekanik Tehlikeler":     {"engineering": "Makine muhafazası kur", "ppe": "Sıkışma/darbe KKD kullan"},
    "Yangın / Patlama":       {"engineering": "Yangın söndürücü ve alarm kur", "ppe": "Alev geciktirici KKD"},
    "Biyolojik Tehlikeler":   {"engineering": "Hijyen istasyonu kur", "ppe": "Eldiven ve maske kullan"},
    "Psikososyal Tehlikeler": {"administrative": "Yük dengeleme ve destek programı uygula", "ppe": "—"},
}

CONTROL_LABELS = {
    "elimination":    "🔴 1. Eliminasyon",
    "substitution":   "🟠 2. İkame",
    "engineering":    "🟡 3. Mühendislik",
    "administrative": "🔵 4. İdari",
    "ppe":            "🟢 5. KKD",
}


def get_controls(category: str, description: str) -> dict:
    """
    Tehlike kategorisi ve açıklamasına göre kontrol önerileri döndür.
    Önce kategoriye gir, sonra açıklamada anahtar kelime ara.
    Eşleşme yoksa genel kategori önermesini döndür.
    """
    cat_controls = CONTROL_HIERARCHY.get(category, {})
    desc_lower = description.lower()

    best_match = None
    best_score = 0
    for hazard_key, controls in cat_controls.items():
        keywords = hazard_key.lower().split()[:4]
        score = sum(1 for kw in keywords if kw in desc_lower)
        if score > best_score:
            best_score = score
            best_match = controls

    if best_match and best_score >= 1:
        return best_match

    return GENERAL_CONTROLS.get(category, {
        "administrative": "Sahaya özel risk değerlendirmesi yapın",
        "ppe":            "Uygun KKD belirleyin"
    })


# ── JSON Output Standardı ─────────────────────────────────────────────────────

def build_json_output(meta: dict, hazard_rows: list) -> dict:
    """
    Standart JSA JSON çıktısı üret.
    Harici sistemlere aktarım ve audit trail için kullanılır.
    """
    hazards_out = []
    for i, row in enumerate(hazard_rows, 1):
        risk = row["risk"]
        controls = get_controls(row.get("kategori", ""), row.get("tehlike", ""))
        hazards_out.append({
            "hazard_id":      f"H{i:03d}",
            "category":       row.get("kategori", ""),
            "description":    row.get("tehlike", ""),
            "ai_confidence":  row.get("confidence", None),
            "P":              risk["P"],
            "F":              risk["F"],
            "E":              risk["E"],
            "R":              risk["R"],
            "risk_level":     risk["level"],
            "action":         risk["action"],
            "controls":       controls,
        })

    risks = [r["risk"] for r in hazard_rows]
    summary = get_risk_summary(risks) if risks else {}

    return {
        "schema_version": "1.0",
        "site":           meta.get("firma", ""),
        "department":     meta.get("bolum", ""),
        "job_description":meta.get("is_tanimi", ""),
        "analyst":        meta.get("analist", ""),
        "date":           meta.get("tarih", ""),
        "method":         "Fine-Kinney (Kinney & Wiruth, 1976)",
        "hazards":        hazards_out,
        "summary":        summary,
    }


# ── Hesaplama Fonksiyonları ────────────────────────────────────────────────────

def calculate_risk(p_label: str, f_label: str, e_label: str) -> dict:
    """Fine-Kinney risk skoru hesapla. R = P × F × E"""
    p = PROBABILITY[p_label]
    f = FREQUENCY[f_label]
    e = SEVERITY[e_label]
    r = round(p * f * e, 2)

    level, color, action = "DÜŞÜK", "#228B22", "🟢 Periyodik gözlem yeterli"
    for threshold, lvl, clr, act in RISK_LEVELS:
        if r > threshold:
            level, color, action = lvl, clr, act
            break

    return {
        "P": p, "F": f, "E": e,
        "R": r,
        "level": level,
        "color": color,
        "action": action,
    }


def get_all_hazards_flat() -> list:
    """Tüm tehlikeleri düz liste olarak döndür (prompt için)."""
    all_hazards = []
    for cat, hazards in HAZARD_CATEGORIES.items():
        for h in hazards:
            all_hazards.append(f"[{cat}] {h}")
    return all_hazards


def get_risk_summary(results: list) -> dict:
    """Çoklu tehlike listesinden özet istatistik üret."""
    if not results:
        return {}

    scores = [r["R"] for r in results]
    levels = [r["level"] for r in results]

    return {
        "toplam_tehlike": len(results),
        "max_skor": max(scores),
        "ort_skor": round(sum(scores) / len(scores), 2),
        "kabul_edilemez": levels.count("KABUL EDİLEMEZ"),
        "kritik": levels.count("KRİTİK"),
        "onemli": levels.count("ÖNEMLİ"),
        "orta": levels.count("ORTA"),
        "dusuk": levels.count("DÜŞÜK"),
    }