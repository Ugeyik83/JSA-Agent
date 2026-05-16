# jsa_core.py — Fine-Kinney Kural Motoru
# v1.3 — Orijinal tehlike kategorileri ve kontrol hiyerarşisi restore edildi

# ── Fine-Kinney Parametreleri ─────────────────────────────────────────────────

PROBABILITY = {
    "Çok muhtemel (10.0)":              10.0,
    "Muhtemel (6.0)":                    6.0,
    "Olası (3.0)":                       3.0,
    "Mümkün fakat düşük (1.0)":          1.0,
    "Beklenmez fakat mümkün (0.5)":      0.5,
    "Beklenmez (0.2)":                   0.2,
}

FREQUENCY = {
    "Hemen hemen sürekli (Bir saate birkaç defa)(10)":      10,
    "Sık (Günde bir veya birkaç defa) (6)":                  6,
    "Ara sıra (haftada bir veya birkaç defa) (3)":            3,
    "Sık değil (Ayda bir veya birkaç defa) (2)":              2,
    "Seyrek (Yılda birkaç defa) (1)":                         1,
    "Çok seyrek (Yılda bir defa veya daha az) (0.5)":        0.5,
}

SEVERITY = {
    "Birden fazla ölümlü kaza/Çevresel felaket (100)":                                                    100,
    "Öldürücü kaza/Tam Maluliyet/Ciddi çevresel zarar (40)":                                               40,
    "Sakatlık/Uzuv Kaybı/Çevresel engel oluşturma/Meslek Hastalığı (15)":                                  15,
    "Önemli hasar, yaralanma, dış ilkyardım ihtiyacı/arazi sınırları dışında çevresel zarar (7)":           7,
    "Küçük hasar/yaralanma, dahili ilk yardım/arazi sınırları içinde çevresel zarar (3)":                   3,
    "Ucuz atlatma, ramak kaldı/Çevresel zarar yok (1)":                                                     1,
}

RISK_LEVELS = [
    (400, "KABUL EDİLEMEZ", "#8B0000", "⛔ Derhal durdur, çalışmayı başlatma"),
    (200, "KRİTİK",         "#FF0000", "🔴 1 hafta içinde acil aksiyon"),
    (70,  "ÖNEMLİ",         "#FF8C00", "🟠 1 ay içinde planlı aksiyon"),
    (20,  "ORTA",           "#FFD700", "🟡 Gözlemle, eğer aksiyon gerekiyorsa 3 ay içinde iyileştirme planla"),
    (0,   "DÜŞÜK",          "#228B22", "🟢 Periyodik gözlem yeterli"),
]

# ── Tehlike Kategorileri ──────────────────────────────────────────────────────

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
        "Çarpma / takılma": {
            "elimination":    "Engel ve çarpışma noktalarını kaldır",
            "substitution":   "Düzenli yerleşim planı ile mesafeyi artır",
            "engineering":    "Köşe koruyucu, sarı-siyah bant, yeterli aydınlatma",
            "administrative": "Yaya trafik planı, hız limiti talimatı",
            "ppe":            "Baret (EN 397), yüksek görünürlüklü yelek (EN ISO 20471)",
        },
        "Sıkışma / ezilme": {
            "elimination":    "Sıkışma riskli alanı yeniden tasarla",
            "substitution":   "Daha geniş geçiş aralığı sağla",
            "engineering":    "Fotosell bariyer, acil durdurma butonu",
            "administrative": "LOTO prosedürü, güvenli çalışma talimatı",
            "ppe":            "Çelik burunlu bot, baret, eldiven",
        },
        "Gürültü maruziyeti": {
            "elimination":    "Gürültü kaynağını kaldır",
            "substitution":   "Sessiz ekipmanla değiştir",
            "engineering":    "Akustik kabin, titreşim izolasyonu, bariyer",
            "administrative": "Maruziyet süresi rotasyonu, sessiz alan tanımla",
            "ppe":            "Kulak tıkacı / kulaklık (EN 352), SNR ≥ 30 dB",
        },
        "Titreşim maruziyeti": {
            "elimination":    "Titreşim kaynağını kaldır",
            "substitution":   "Düşük titreşimli ekipman kullan",
            "engineering":    "Titreşim sönümleyici koltuk / tutamak",
            "administrative": "Maruziyet süresi sınırı (EU DIR 2002/44/EC), rotasyon",
            "ppe":            "Titreşim sönümleyici eldiven (EN ISO 10819)",
        },
        "Aşırı sıcaklık (sıcak/soğuk)": {
            "elimination":    "Aşırı sıcaklık ortamında çalışmayı kaldır",
            "substitution":   "İklimlendirilmiş alan kullan",
            "engineering":    "Isıtma/soğutma sistemi, havalandırma",
            "administrative": "Maruziyet süresi sınırı, su ve mola takvimi",
            "ppe":            "Isı / soğuk koruyucu giysi, iklim ölçer",
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
        "Radyasyon maruziyeti": {
            "elimination":    "Radyasyon kaynağını kaldır",
            "substitution":   "Daha düşük aktiviteli kaynak kullan",
            "engineering":    "Kurşun zırh, mesafe bariyeri, uyarı levhası",
            "administrative": "Radyasyon çalışma izni, dozimetre takibi",
            "ppe":            "Kurşun önlük, tiroid koruyucu, dozimetre",
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
        "Aşındırıcı madde": {
            "elimination":    "Aşındırıcı maddeyi formülasyondan çıkar",
            "substitution":   "Daha az aşındırıcı alternatif kullan",
            "engineering":    "Kapalı sistem, göz duşu, acil duş",
            "administrative": "SDS eğitimi, kimyasal taşıma prosedürü",
            "ppe":            "Yüz siperi, kimyasal dirençli eldiven ve apron",
        },
        "Toksik madde maruziyeti": {
            "elimination":    "Toksik maddeyi kaldır",
            "substitution":   "Daha az toksik alternatif kullan",
            "engineering":    "Kapalı sistem, LEV, gaz dedektörü",
            "administrative": "TWA/STEL izleme, sağlık gözetimi",
            "ppe":            "SCBA veya uygun filtreli maske, koruyucu tulum",
        },
    },
    "Ergonomik Tehlikeler": {
        "Ağır yük taşıma": {
            "elimination":    "Manuel taşıma ihtiyacını ortadan kaldır",
            "substitution":   "Elektrikli transpalet, forklift kullan",
            "engineering":    "Konveyör, kaldırma yardımcısı, ayarlanabilir tezgah",
            "administrative": "25 kg üzeri ekip kaldırma kuralı, rotasyon",
            "ppe":            "Bel destek kemeri (destekleyici), kaymaz eldiven",
        },
        "Tekrarlayan hareket": {
            "elimination":    "Tekrarlayan görevi otomasyonla kaldır",
            "substitution":   "Ergonomik alet tasarımı kullan",
            "engineering":    "Exoskeleton desteği, güç aletleri",
            "administrative": "Mikro mola takvimi, görev rotasyonu",
            "ppe":            "Kompresyon eldiveni, bilek desteği",
        },
        "Zorlamalı / uygunsuz postür": {
            "elimination":    "Zorlamalı postürü gerektiren görevi yeniden tasarla",
            "substitution":   "Ayarlanabilir çalışma istasyonu kullan",
            "engineering":    "Yükseklik ayarlı tezgah, kol desteği, eğimli yüzey",
            "administrative": "REBA/RULA değerlendirmesi, periyodik duruş değişikliği",
            "ppe":            "Bel ve diz desteği, ergonomik giysi",
        },
        "Uzun süreli statik duruş": {
            "elimination":    "Sabit duruş gerektiren görevi kaldır",
            "substitution":   "Oturarak çalışma imkanı sağla",
            "engineering":    "Anti-yorgunluk mat, ayak desteği, yükseklik ayarlı tezgah",
            "administrative": "Periyodik hareket molası, germe egzersizi programı",
            "ppe":            "Ergonomik bot, kompresyon çorabı",
        },
        "El-kol titreşimi": {
            "elimination":    "El aletini otomasyonla kaldır",
            "substitution":   "Düşük titreşimli alet kullan",
            "engineering":    "Titreşim izolasyonlu tutamak",
            "administrative": "Maruziyet süresi sınırı, rotasyon",
            "ppe":            "Titreşim sönümleyici eldiven (EN ISO 10819)",
        },
    },
    "Biyolojik Tehlikeler": {
        "Biyolojik ajan maruziyeti": {
            "elimination":    "Biyolojik ajan kaynağını kaldır / sterilize et",
            "substitution":   "Daha güvenli biyolojik ajan kullan",
            "engineering":    "Biyogüvenlik kabini, negatif basınçlı oda",
            "administrative": "Biyogüvenlik prosedürü, aşılama programı",
            "ppe":            "Tulum, eldiven, N95/FFP3 maske, gözlük",
        },
        "Keskin cisim yaralanması": {
            "elimination":    "Keskin cisim kullanımını azalt",
            "substitution":   "Güvenli iğne / bistüri sistemi kullan",
            "engineering":    "Keskin atık kutusu, otomatik kapanır kap",
            "administrative": "Keskin alet güvenlik prosedürü, eğitim",
            "ppe":            "Kesme dirençli eldiven (EN 388), gözlük",
        },
        "Haşere / hayvan teması": {
            "elimination":    "Haşere / hayvan temasını ortadan kaldır",
            "substitution":   "Uzaktan izleme sistemi kullan",
            "engineering":    "Bariyer, tuzak, kapalı çalışma alanı",
            "administrative": "Haşere kontrol programı, acil prosedür",
            "ppe":            "Koruyucu eldiven, bot, gözlük",
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
        "Kesici / delici alet": {
            "elimination":    "Kesici alet kullanımını kaldır",
            "substitution":   "Daha güvenli kesim yöntemi kullan",
            "engineering":    "Alet koruyucusu, bıçak muhafazası",
            "administrative": "Kesici alet güvenlik talimatı, eğitim",
            "ppe":            "Kesme dirençli eldiven (EN 388), yüz siperi",
        },
        "Basınçlı sistem patlaması": {
            "elimination":    "Basınçlı sistemi kaldır",
            "substitution":   "Daha düşük basınçlı alternatif kullan",
            "engineering":    "Emniyet valfi, basınç göstergesi, periyodik test",
            "administrative": "Periyodik muayene takvimi, operatör eğitimi",
            "ppe":            "Yüz siperi, basınca dayanıklı eldiven",
        },
        "Vinç / kaldırma ekipmanı arızası": {
            "elimination":    "Kaldırma ihtiyacını ortadan kaldır",
            "substitution":   "Daha güvenli kaldırma sistemi kullan",
            "engineering":    "Yük kapasitesi kilidi, periyodik muayene sistemi",
            "administrative": "Operatör yetkilendirme, kaldırma planı, barikat",
            "ppe":            "Baret (EN 397), çelik burunlu bot, yüksek görünürlüklü yelek",
        },
    },
    "Yangın / Patlama": {
        "Yangın çıkma riski": {
            "elimination":    "Ateşleme kaynağı ve yanıcı maddeyi birbirinden ayır",
            "substitution":   "Yanmaz malzeme kullan",
            "engineering":    "Sprinkler sistemi, yangın kapısı, duman dedektörü",
            "administrative": "Acil tahliye planı, yangın tatbikatı, ateşleme izni",
            "ppe":            "Alev geciktirici iş elbisesi (EN ISO 11612)",
        },
        "Patlama riski": {
            "elimination":    "Patlayıcı atmosfer oluşumunu engelle",
            "substitution":   "İnert gaz kullan",
            "engineering":    "Ex-proof ekipman (ATEX), topraklama, havalandırma",
            "administrative": "ATEX zonlama, ateşleme kaynağı kontrolü, izin sistemi",
            "ppe":            "Antistatik iş elbisesi, ATEX onaylı KKD",
        },
        "Duman / oksijen azalması": {
            "elimination":    "Duman / gaz kaynağını kaldır",
            "substitution":   "Kapalı yakma sistemi kullan",
            "engineering":    "CO/O2 dedektörü, mekanik havalandırma, acil egzoz",
            "administrative": "Kapalı alan izin sistemi, gözetçi, tahliye planı",
            "ppe":            "SCBA veya hava ikmal hattı, can kurtarma halatı",
        },
    },
    "Psikososyal Tehlikeler": {
        "Aşırı iş yükü / stres": {
            "elimination":    "Stres yaratan görev yapısını kaldır",
            "substitution":   "Görev çeşitliliği artır, iş yükü dengele",
            "engineering":    "Dijital iş takip sistemi ile yük görünürlüğü",
            "administrative": "Görev analizi, EAP programı, yönetici eğitimi",
            "ppe":            "—",
        },
        "Şiddet / taciz riski": {
            "elimination":    "Taciz ve zorbalık kaynaklarını kaldır",
            "substitution":   "Destekleyici çalışma ortamı oluştur",
            "engineering":    "Anonim şikayet sistemi, güvenlik kamerası",
            "administrative": "Davranış kuralları, sıfır tolerans politikası",
            "ppe":            "—",
        },
        "Yalnız çalışma tehlikesi": {
            "elimination":    "Yalnız çalışma ihtiyacını kaldır",
            "substitution":   "Uzaktan gözetim sistemi kullan",
            "engineering":    "Panic button, otomatik check-in sistemi",
            "administrative": "Yalnız çalışma prosedürü, periyodik check-in",
            "ppe":            "Kişisel alarm cihazı",
        },
    },
}

# Kategori bazında genel önlem (fallback)
GENERAL_CONTROLS = {
    "Fiziksel Tehlikeler":    {"engineering": "Fiziksel bariyer ve koruyucu kur", "ppe": "Uygun KKD kullan (baret, bot, yelek)"},
    "Kimyasal Tehlikeler":    {"engineering": "Havalandırma sağla, kapalı sistem kullan", "ppe": "Maske, eldiven, gözlük"},
    "Ergonomik Tehlikeler":   {"engineering": "Ergonomik çalışma istasyonu kur", "ppe": "Destek ekipmanı kullan"},
    "Biyolojik Tehlikeler":   {"engineering": "Hijyen istasyonu kur", "ppe": "Eldiven, maske, tulum"},
    "Mekanik Tehlikeler":     {"engineering": "Makine muhafazası ve bariyer kur", "ppe": "Sıkışma/darbe KKD kullan"},
    "Yangın / Patlama":       {"engineering": "Yangın söndürücü ve alarm kur", "ppe": "Alev geciktirici KKD"},
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
    Kategori eşleştirmesi partial match ile yapılır.
    """
    cat_lower = category.lower().strip()

    # Tam eşleşme
    matched_cat_key = None
    if category in CONTROL_HIERARCHY:
        matched_cat_key = category
    else:
        # Partial match
        for key in CONTROL_HIERARCHY:
            key_core = key.split("—")[-1].strip().lower()
            if key_core in cat_lower or cat_lower in key_core:
                matched_cat_key = key
                break

    if not matched_cat_key:
        for key in GENERAL_CONTROLS:
            key_core = key.split("—")[-1].strip().lower()
            if key_core in cat_lower or cat_lower in key_core:
                return GENERAL_CONTROLS[key]
        return {"administrative": "Sahaya özel risk değerlendirmesi yapın", "ppe": "Uygun KKD belirleyin"}

    cat_controls = CONTROL_HIERARCHY[matched_cat_key]
    desc_lower = description.lower()

    best_match = None
    best_score = 0
    for hazard_key, controls in cat_controls.items():
        keywords = hazard_key.lower().split()
        score = sum(1 for kw in keywords if len(kw) > 3 and kw in desc_lower)
        if score > best_score:
            best_score = score
            best_match = controls

    if best_match and best_score >= 1:
        return best_match

    return GENERAL_CONTROLS.get(matched_cat_key, {
        "administrative": "Sahaya özel risk değerlendirmesi yapın",
        "ppe":            "Uygun KKD belirleyin"
    })


# ── JSON Output Standardı ─────────────────────────────────────────────────────

def build_json_output(meta: dict, hazard_rows: list) -> dict:
    hazards_out = []
    for i, row in enumerate(hazard_rows, 1):
        risk = row["risk"]
        controls = get_controls(row.get("kategori", ""), row.get("tehlike", ""))
        hazards_out.append({
            "hazard_id":     f"H{i:03d}",
            "category":      row.get("kategori", ""),
            "description":   row.get("tehlike", ""),
            "ai_confidence": row.get("confidence", None),
            "P":             risk["P"],
            "F":             risk["F"],
            "E":             risk["E"],
            "R":             risk["R"],
            "risk_level":    risk["level"],
            "action":        risk["action"],
            "controls":      controls,
        })

    risks = [r["risk"] for r in hazard_rows]
    summary = get_risk_summary(risks) if risks else {}

    return {
        "schema_version":  "1.0",
        "site":            meta.get("firma", ""),
        "department":      meta.get("bolum", ""),
        "job_description": meta.get("is_tanimi", ""),
        "analyst":         meta.get("analist", ""),
        "date":            meta.get("tarih", ""),
        "method":          "Fine-Kinney (Kinney & Wiruth, 1976)",
        "hazards":         hazards_out,
        "summary":         summary,
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
        if r >= threshold and threshold > 0:
            level, color, action = lvl, clr, act
            break

    return {"P": p, "F": f, "E": e, "R": r, "level": level, "color": color, "action": action}


def get_all_hazards_flat() -> list:
    """Tüm tehlikeleri düz liste olarak döndür (AI prompt için)."""
    all_hazards = []
    for cat, hazards in HAZARD_CATEGORIES.items():
        for h in hazards:
            all_hazards.append(f"[{cat}] {h}")
    return all_hazards


def get_risk_summary(results: list) -> dict:
    if not results:
        return {}
    scores = [r["R"] for r in results]
    levels = [r["level"] for r in results]
    return {
        "toplam_tehlike":  len(results),
        "max_skor":        max(scores),
        "ort_skor":        round(sum(scores) / len(scores), 2),
        "kabul_edilemez":  levels.count("KABUL EDİLEMEZ"),
        "kritik":          levels.count("KRİTİK"),
        "onemli":          levels.count("ÖNEMLİ"),
        "orta":            levels.count("ORTA"),
        "dusuk":           levels.count("DÜŞÜK"),
    }