# jsa_core.py — Fine-Kinney Kural Motoru
# v1.2 — Kurumsal tehlike matrisi entegre edildi (ISO 13849 uyumlu)

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

# Risk Skoru → Seviye eşikleri
RISK_LEVELS = [
    (400, "KABUL EDİLEMEZ", "#8B0000", "⛔ Derhal durdur, çalışmayı başlatma"),
    (200, "KRİTİK",         "#FF0000", "🔴 24 saat içinde acil aksiyon"),
    (70,  "ÖNEMLİ",         "#FF8C00", "🟠 1 hafta içinde planlı aksiyon"),
    (20,  "ORTA",           "#FFD700", "🟡 1 ay içinde iyileştirme planla"),
    (0,   "DÜŞÜK",          "#228B22", "🟢 Periyodik gözlem yeterli"),
]

# ── Tehlike Kategorileri — Kurumsal Matris (ISO 13849 uyumlu) ─────────────────

HAZARD_CATEGORIES = {
    "1 — Mekanik Tehlikeler": [
        "1.1 Korumasız hareket eden makine parçaları",
        "1.2 Tehlikeli yüzeylere sahip parçalar",
        "1.3 Hareketli taşıma parçaları / hareketli iş araçları",
        "1.4 Kontrolsüz hareket eden parçalar",
        "1.5 Yıkılma, kayma, takılma, bükülme",
        "1.6 Düşme",
    ],
    "2 — Elektrikle İlgili Tehlikeler": [
        "2.1 Elektrik çarpması",
        "2.2 Elektrik arkı",
        "2.3 Elektrostatik yüklenme",
    ],
    "3 — Tehlikeli Maddeler": [
        "3.1 Gazlar",
        "3.2 Buharlar",
        "3.3 Aerosoller (tozlar, duman, sis)",
        "3.4 Sıvılar",
        "3.5 Katı malzeme",
    ],
    "4 — Biyolojik Tehlikeler": [
        "4.1 Patojen mikro organizmalar vasıtasıyla enfeksiyon tehlikesi (bakteri, virüs, mantar)",
        "4.2 Mikro organizmaların duyarlılığı arttırıcı ve toksik etkileri",
    ],
    "5 — Yangın ve Patlama Tehlikeleri": [
        "5.1 Yanıcı katı maddeler, sıvılar, gazlar",
        "5.2 Patlayıcı ortamlar",
        "5.3 Patlayıcı maddeler",
    ],
    "6 — Termik Tehlikeler": [
        "6.1 Sıcak parçalar / yüzeyler",
        "6.2 Soğuk parçalar / yüzeyler",
    ],
    "7 — Özel Fiziksel Etkilerin Yol Açtığı Tehlikeler": [
        "7.1 Gürültü",
        "7.2 Ultrason, kızılötesi ses",
        "7.3 Bütün vücut titreşimi",
        "7.4 El-kol titreşimi",
        "7.5 İyonize olmayan ışınlar (kızıl ve mor ötesi, lazer ışınları)",
        "7.6 İyonize ışınlar (röntgen, gama, parçacık ışınları)",
        "7.7 Elektromanyetik alanlar",
        "7.8 Düşük basınç veya yüksek basınç",
    ],
    "8 — Çalışma Koşullarının Yol Açtığı Tehlikeler": [
        "8.1 Çevrenin havası (sıcaklık, soğuk)",
        "8.2 Aydınlatma, ışık",
        "8.3 Boğulma",
    ],
    "9 — Fiziksel Baskılar": [
        "9.1 Ağır dinamik çalışma",
        "9.2 Tek yönlü dinamik çalışma",
        "9.3 Statik çalışma",
        "9.4 Statik ve dinamik çalışmanın kombinasyonu",
    ],
    "10 — Psikolojik Faktörler": [
        "10.1 Yetersiz görev tasarımı",
        "10.2 Organizasyon yetersizliği",
        "10.3 Yetersiz sosyal koşullar",
        "10.4 Yetersiz çalışma yeri ve çalışma çevresi tasarımı",
    ],
    "11 — Diğer Tehlikeler": [
        "11.1 İnsanların yol açtığı tehlikeler",
        "11.2 Hayvanların yol açtığı tehlikeler",
        "11.3 Bitkilerin ve bitkisel ürünlerin yol açtığı tehlikeler",
    ],
}

# ── Risk Kontrol Hiyerarşisi (ISO 45001 / NIOSH) ─────────────────────────────

CONTROL_HIERARCHY = {
    "1 — Mekanik Tehlikeler": {
        "1.1 Korumasız hareket eden makine parçaları": {
            "elimination":    "Tehlikeli hareketi ortadan kaldır, süreci yeniden tasarla",
            "substitution":   "Güvenli tasarımlı makineyle değiştir",
            "engineering":    "Koruyucu kapak, muhafaza, fotosell / ışık perdesi bariyer",
            "administrative": "LOTO prosedürü, makine güvenlik talimatı, operatör eğitimi",
            "ppe":            "Sıkışmaya karşı eldiven, saç/kıyafet düzeni",
        },
        "1.2 Tehlikeli yüzeylere sahip parçalar": {
            "elimination":    "Keskin kenar ve yüzeyleri tasarımda ortadan kaldır",
            "substitution":   "Yuvarlatılmış kenar / güvenli profil kullan",
            "engineering":    "Kenar koruyucu, köşebent, bariyer",
            "administrative": "Güvenli çalışma talimatı, eğitim",
            "ppe":            "Kesme dirençli eldiven (EN 388), yüz siperi",
        },
        "1.3 Hareketli taşıma parçaları / hareketli iş araçları": {
            "elimination":    "Manuel taşıma ihtiyacını ortadan kaldır",
            "substitution":   "Otomatik taşıma sistemi kullan",
            "engineering":    "Yaya koridoru, bariyer, uyarı ışığı / ses sistemi",
            "administrative": "Trafik yönetim planı, hız limiti, sürücü eğitimi",
            "ppe":            "Yüksek görünürlüklü yelek (EN ISO 20471), baret",
        },
        "1.4 Kontrolsüz hareket eden parçalar": {
            "elimination":    "Kontrolsüz harekete neden olan kaynağı kaldır",
            "substitution":   "Mekanik kilitleme sistemi kullan",
            "engineering":    "Tutma freni, emniyet mandalı, bariyer",
            "administrative": "Bakım talimatı, periyodik kontrol çizelgesi",
            "ppe":            "Baret (EN 397), yüz siperi, çelik burunlu bot",
        },
        "1.5 Yıkılma, kayma, takılma, bükülme": {
            "elimination":    "Zemin düzensizliklerini ve engelleri kaldır",
            "substitution":   "Kaymaz zemin kaplaması kullan",
            "engineering":    "Drenaj sistemi, sarı uyarı bantı, yeterli aydınlatma",
            "administrative": "Düzenli zemin kontrol çizelgesi, temizlik prosedürü",
            "ppe":            "Kaymaz tabanlı güvenlik botu (EN ISO 20345)",
        },
        "1.6 Düşme": {
            "elimination":    "Yüksekte çalışmayı ortadan kaldır, zemin seviyesinde yapılandır",
            "substitution":   "Uzun kollu ekipman / teleskopik alet kullan",
            "engineering":    "Güvenlik korkuluğu, güvenlik ağı, iskele sistemi",
            "administrative": "Yüksekte çalışma izin sistemi, buddy system",
            "ppe":            "Tam vücut emniyet kemeri, bağlantı halatı (EN 361)",
        },
    },
    "2 — Elektrikle İlgili Tehlikeler": {
        "2.1 Elektrik çarpması": {
            "elimination":    "Gereksiz elektrikli ekipmanı devre dışı bırak",
            "substitution":   "Düşük gerilimli sistem kullan",
            "engineering":    "İzolasyon, topraklama, kaçak akım rölesi (RCD)",
            "administrative": "Kilitleme/etiketleme (LOTO) prosedürü, izinli çalışma",
            "ppe":            "Yalıtımlı eldiven (EN 60903), yalıtımlı bot",
        },
        "2.2 Elektrik arkı": {
            "elimination":    "Enerji altında çalışmaktan kaçın",
            "substitution":   "Uzaktan kumanda sistemi kullan",
            "engineering":    "Ark flash bariyeri, güvenli mesafe işareti",
            "administrative": "Elektrik izin sistemi, ark flash risk analizi",
            "ppe":            "Ark flash koruyucu elbise (ATPV değerine göre), yüz siperi",
        },
        "2.3 Elektrostatik yüklenme": {
            "elimination":    "Statik yük üreten süreci kaldır",
            "substitution":   "İletken malzeme kullan",
            "engineering":    "Topraklama, iyonizatör, nem kontrolü",
            "administrative": "Antistatik çalışma prosedürü",
            "ppe":            "Antistatik iş elbisesi ve ayakkabı",
        },
    },
    "3 — Tehlikeli Maddeler": {
        "3.1 Gazlar": {
            "elimination":    "Tehlikeli gazı formülasyondan çıkar",
            "substitution":   "Daha az tehlikeli alternatif kullan",
            "engineering":    "Kapalı sistem, gaz dedektörü, acil havalandırma",
            "administrative": "GBF/SDS eğitimi, gaz ölçüm prosedürü",
            "ppe":            "Bağımsız hava ikmal cihazı (SCBA) veya uygun maske",
        },
        "3.2 Buharlar": {
            "elimination":    "Buhar üreten işlemi kaldır",
            "substitution":   "Daha düşük uçuculuklu ürün kullan",
            "engineering":    "Lokal egzoz havalandırma (LEV), genel havalandırma",
            "administrative": "TWA/STEL izleme, maruziyet süresi sınırı",
            "ppe":            "Yarım/tam yüz maskesi, uygun filtre kartuşu (EN 140)",
        },
        "3.3 Aerosoller (tozlar, duman, sis)": {
            "elimination":    "Toz üreten işlemi ıslak yöntemle değiştir",
            "substitution":   "Daha az toz üreten malzeme kullan",
            "engineering":    "Lokal egzoz, toz toplama sistemi, kapalı sistem",
            "administrative": "Maruziyet izleme, rotasyon",
            "ppe":            "FFP2/FFP3 toz maskesi (EN 149)",
        },
        "3.4 Sıvılar": {
            "elimination":    "Tehlikeli sıvıyı formülasyondan çıkar",
            "substitution":   "Daha az tehlikeli alternatif kullan",
            "engineering":    "Kapalı sistem, göz duşu, acil duş, dökülme havuzu",
            "administrative": "GBF/SDS eğitimi, kimyasal envanter kontrolü",
            "ppe":            "Kimyasal dirençli eldiven, tam yüz maskesi, apron",
        },
        "3.5 Katı malzeme": {
            "elimination":    "Tehlikeli katı maddeyi kaldır",
            "substitution":   "Daha güvenli form/granül kullan",
            "engineering":    "Kapalı taşıma sistemi, toz toplama",
            "administrative": "Güvenli taşıma ve depolama talimatı",
            "ppe":            "Toz maskesi, koruyucu eldiven, gözlük",
        },
    },
    "4 — Biyolojik Tehlikeler": {
        "4.1 Patojen mikro organizmalar vasıtasıyla enfeksiyon tehlikesi (bakteri, virüs, mantar)": {
            "elimination":    "Patojen kaynağını kaldır / sterilize et",
            "substitution":   "Daha güvenli biyolojik ajan kullan",
            "engineering":    "Biyogüvenlik kabini, negatif basınçlı oda",
            "administrative": "Biyogüvenlik prosedürü, aşılama programı",
            "ppe":            "Tulum, eldiven, N95/FFP3 maske, gözlük",
        },
        "4.2 Mikro organizmaların duyarlılığı arttırıcı ve toksik etkileri": {
            "elimination":    "Duyarlılaştırıcı ajanı kaldır",
            "substitution":   "Alternatif ajan kullan",
            "engineering":    "Havalandırma, kapalı sistem",
            "administrative": "Sağlık gözetimi, maruziyet kaydı",
            "ppe":            "Uygun filtreli maske, koruyucu eldiven",
        },
    },
    "5 — Yangın ve Patlama Tehlikeleri": {
        "5.1 Yanıcı katı maddeler, sıvılar, gazlar": {
            "elimination":    "Yanıcı madde miktarını minimize et",
            "substitution":   "Yanmaz / alev geciktirici alternatif kullan",
            "engineering":    "Sprinkler sistemi, yangın kapısı, duman dedektörü",
            "administrative": "Acil tahliye planı, yangın tatbikatı, ateşleme izni",
            "ppe":            "Alev geciktirici iş elbisesi (EN ISO 11612)",
        },
        "5.2 Patlayıcı ortamlar": {
            "elimination":    "Patlayıcı atmosfer oluşumunu engelle",
            "substitution":   "İnert gaz kullan",
            "engineering":    "Ex-proof ekipman (ATEX), topraklama, havalandırma",
            "administrative": "ATEX zonlama, ateşleme kaynağı kontrolü, izin sistemi",
            "ppe":            "Antistatik iş elbisesi, ATEX onaylı KKD",
        },
        "5.3 Patlayıcı maddeler": {
            "elimination":    "Patlayıcı madde kullanımından kaçın",
            "substitution":   "Daha az hassas alternatif kullan",
            "engineering":    "Güvenli depolama (patlayıcı deposu), mesafe bariyeri",
            "administrative": "Patlayıcı madde lisansı, yetkili personel, izin sistemi",
            "ppe":            "Balistik koruyucu, yüz siperi",
        },
    },
    "6 — Termik Tehlikeler": {
        "6.1 Sıcak parçalar / yüzeyler": {
            "elimination":    "Sıcak yüzeyle temas ihtiyacını kaldır",
            "substitution":   "Uzaktan kumandalı sistem kullan",
            "engineering":    "Isı yalıtımı, koruyucu kapak, uyarı etiketi",
            "administrative": "Sıcak çalışma izni, soğuma süresi talimatı",
            "ppe":            "Isıya dirençli eldiven (EN 407), yüz siperi",
        },
        "6.2 Soğuk parçalar / yüzeyler": {
            "elimination":    "Soğuk yüzeyle temas ihtiyacını kaldır",
            "substitution":   "Yalıtımlı ekipman kullan",
            "engineering":    "Isı yalıtımı, uyarı etiketi",
            "administrative": "Soğuğa maruziyet süresi sınırı, ısınma molası",
            "ppe":            "Soğuğa dirençli eldiven ve giysi (EN 511)",
        },
    },
    "7 — Özel Fiziksel Etkilerin Yol Açtığı Tehlikeler": {
        "7.1 Gürültü": {
            "elimination":    "Gürültü kaynağını kaldır",
            "substitution":   "Sessiz ekipmanla değiştir",
            "engineering":    "Akustik kabin, titreşim izolasyonu, bariyer",
            "administrative": "Maruziyet süresi rotasyonu, sessiz alan tanımla",
            "ppe":            "Kulak tıkacı / kulaklık (EN 352), SNR ≥ 30 dB",
        },
        "7.3 Bütün vücut titreşimi": {
            "elimination":    "Titreşim kaynağını kaldır",
            "substitution":   "Titreşim azaltılmış araç/ekipman kullan",
            "engineering":    "Titreşim sönümleyici koltuk, yol düzeltme",
            "administrative": "Maruziyet süresi sınırı, rotasyon",
            "ppe":            "Titreşim sönümleyici ayakkabı tabanı",
        },
        "7.4 El-kol titreşimi": {
            "elimination":    "El aletini otomasyonla kaldır",
            "substitution":   "Düşük titreşimli alet kullan",
            "engineering":    "Titreşim izolasyonlu tutamak",
            "administrative": "Maruziyet süresi sınırı (EU DIR 2002/44/EC), rotasyon",
            "ppe":            "Titreşim sönümleyici eldiven (EN ISO 10819)",
        },
        "7.5 İyonize olmayan ışınlar (kızıl ve mor ötesi, lazer ışınları)": {
            "elimination":    "Işın kaynağını kaldır",
            "substitution":   "Daha düşük güçlü sistem kullan",
            "engineering":    "Işın bariyeri, lazer güvenlik muhafazası",
            "administrative": "Lazer güvenlik eğitimi, uyarı levhası",
            "ppe":            "Lazer güvenlik gözlüğü (EN 207)",
        },
        "7.6 İyonize ışınlar (röntgen, gama, parçacık ışınları)": {
            "elimination":    "Radyasyon kaynağını kaldır",
            "substitution":   "Daha düşük aktiviteli kaynak kullan",
            "engineering":    "Kurşun zırh, mesafe, süre kısıtlaması",
            "administrative": "Radyasyon çalışma izni, dozimetre takibi",
            "ppe":            "Kurşun önlük, tiroid koruyucu, dozimetre",
        },
        "7.7 Elektromanyetik alanlar": {
            "elimination":    "EMF kaynağını kaldır",
            "substitution":   "Düşük EMF yayan ekipman kullan",
            "engineering":    "Faraday kafesi, mesafe bariyeri",
            "administrative": "Maruziyet sınır değeri takibi, uyarı levhası",
            "ppe":            "EMF koruyucu giysi (gerekiyorsa)",
        },
        "7.8 Düşük basınç veya yüksek basınç": {
            "elimination":    "Basınçlı sistem ihtiyacını kaldır",
            "substitution":   "Daha düşük/güvenli basınç seviyesi kullan",
            "engineering":    "Emniyet valfi, basınç göstergesi, periyodik test",
            "administrative": "Periyodik muayene, operatör eğitimi, basınçlı kap izni",
            "ppe":            "Yüz siperi, basınca dayanıklı eldiven",
        },
    },
    "8 — Çalışma Koşullarının Yol Açtığı Tehlikeler": {
        "8.1 Çevrenin havası (sıcaklık, soğuk)": {
            "elimination":    "Aşırı sıcaklık ortamında çalışmayı kaldır",
            "substitution":   "İklimlendirilmiş alan kullan",
            "engineering":    "Isıtma/soğutma sistemi, havalandırma",
            "administrative": "Maruziyet süresi sınırı, su ve mola takvimi",
            "ppe":            "Isı / soğuk koruyucu giysi, iklim ölçer",
        },
        "8.2 Aydınlatma, ışık": {
            "elimination":    "Yetersiz aydınlatma gerektiren çalışmayı kaldır",
            "substitution":   "Yeterli lümen değerinde aydınlatma kullan",
            "engineering":    "Ek aydınlatma armatürü, acil aydınlatma",
            "administrative": "Aydınlatma seviyesi periyodik ölçümü (EN 12464)",
            "ppe":            "Baş lambası, kişisel aydınlatma ekipmanı",
        },
        "8.3 Boğulma": {
            "elimination":    "Kapalı alan çalışmasını kaldır",
            "substitution":   "Uzaktan kumanda ile çalış",
            "engineering":    "Sürekli gaz izleme, mekanik havalandırma",
            "administrative": "Kapalı alan izin sistemi, gözetçi, kurtarma planı",
            "ppe":            "SCBA veya hava ikmal hattı, can kurtarma halatı",
        },
    },
    "9 — Fiziksel Baskılar": {
        "9.1 Ağır dinamik çalışma": {
            "elimination":    "Manuel kaldırma ihtiyacını ortadan kaldır",
            "substitution":   "Elektrikli transpalet, forklift kullan",
            "engineering":    "Konveyör, kaldırma yardımcısı, ayarlanabilir tezgah",
            "administrative": "25 kg üzeri ekip kaldırma kuralı, rotasyon",
            "ppe":            "Bel destek kemeri (destekleyici), kaymaz eldiven",
        },
        "9.2 Tek yönlü dinamik çalışma": {
            "elimination":    "Tekrarlayan görevi otomasyonla kaldır",
            "substitution":   "Ergonomik alet tasarımı kullan",
            "engineering":    "Güç aletleri, exoskeleton desteği",
            "administrative": "Mikro mola takvimi, görev rotasyonu",
            "ppe":            "Kompresyon eldiveni, bilek / dirsek desteği",
        },
        "9.3 Statik çalışma": {
            "elimination":    "Sabit duruşu gerektiren görevi kaldır",
            "substitution":   "Oturarak çalışma imkanı sağla",
            "engineering":    "Yükseklik ayarlı çalışma tezgahı, ayak desteği",
            "administrative": "Periyodik duruş değişikliği, germe egzersizi",
            "ppe":            "Anti-yorgunluk mat, ergonomik bot",
        },
        "9.4 Statik ve dinamik çalışmanın kombinasyonu": {
            "elimination":    "Kombinasyon yükü oluşturan görevi yeniden tasarla",
            "substitution":   "Yardımcı ekipmanla yükü azalt",
            "engineering":    "Ayarlanabilir çalışma istasyonu, kaldırma yardımcısı",
            "administrative": "Rotasyon, REBA/RULA değerlendirmesi",
            "ppe":            "Bel ve bilek desteği, ergonomik giysi",
        },
    },
    "10 — Psikolojik Faktörler": {
        "10.1 Yetersiz görev tasarımı": {
            "elimination":    "Stres yaratan görev yapısını kaldır",
            "substitution":   "Görev çeşitliliği artır",
            "engineering":    "İş akışı yazılımı ile yük dengeleme",
            "administrative": "Görev analizi, çalışan katılımlı tasarım",
            "ppe":            "—",
        },
        "10.2 Organizasyon yetersizliği": {
            "elimination":    "Yetersiz organizasyon yapısını kaldır",
            "substitution":   "Yalın yönetim modeli uygula",
            "engineering":    "Dijital iş takip sistemi",
            "administrative": "Yönetici eğitimi, açık iletişim kanalı",
            "ppe":            "—",
        },
        "10.3 Yetersiz sosyal koşullar": {
            "elimination":    "Taciz ve zorbalık kaynaklarını kaldır",
            "substitution":   "Destekleyici çalışma ortamı oluştur",
            "engineering":    "Anonim şikayet sistemi",
            "administrative": "Davranış kuralları, EAP programı",
            "ppe":            "—",
        },
        "10.4 Yetersiz çalışma yeri ve çalışma çevresi tasarımı": {
            "elimination":    "Ergonomik olmayan çalışma alanını yeniden tasarla",
            "substitution":   "Ergonomik mobilya ve ekipman kullan",
            "engineering":    "Aydınlatma, ses, sıcaklık kontrolü",
            "administrative": "Ergonomi değerlendirmesi, çalışan geri bildirimi",
            "ppe":            "—",
        },
    },
    "11 — Diğer Tehlikeler": {
        "11.1 İnsanların yol açtığı tehlikeler": {
            "elimination":    "İnsan hatasına yol açan durumu ortadan kaldır",
            "substitution":   "Otomasyonla insan müdahalesini azalt",
            "engineering":    "Hata önleyici (poka-yoke) sistem",
            "administrative": "Eğitim, prosedür, denetim",
            "ppe":            "Duruma göre belirlenir",
        },
        "11.2 Hayvanların yol açtığı tehlikeler": {
            "elimination":    "Hayvan temasını ortadan kaldır",
            "substitution":   "Uzaktan izleme sistemi kullan",
            "engineering":    "Bariyer, kafes, kapalı çalışma alanı",
            "administrative": "Hayvan davranış eğitimi, acil prosedür",
            "ppe":            "Koruyucu eldiven, bot, gözlük",
        },
        "11.3 Bitkilerin ve bitkisel ürünlerin yol açtığı tehlikeler": {
            "elimination":    "Tehlikeli bitki / bitkisel ürünle teması kaldır",
            "substitution":   "Daha güvenli alternatif kullan",
            "engineering":    "Kapalı sistem, havalandırma",
            "administrative": "Alerji tarama, SDS eğitimi",
            "ppe":            "Eldiven, maske, gözlük",
        },
    },
}

# Kategori bazında genel önlem (spesifik tehlike yoksa fallback)
GENERAL_CONTROLS = {
    "1 — Mekanik Tehlikeler":                          {"engineering": "Fiziksel bariyer ve koruyucu kur", "ppe": "Baret, bot, eldiven"},
    "2 — Elektrikle İlgili Tehlikeler":                {"engineering": "İzolasyon ve topraklama sağla", "ppe": "Yalıtımlı eldiven ve bot"},
    "3 — Tehlikeli Maddeler":                          {"engineering": "Havalandırma sağla, kapalı sistem kullan", "ppe": "Maske, eldiven, gözlük"},
    "4 — Biyolojik Tehlikeler":                        {"engineering": "Hijyen istasyonu kur", "ppe": "Eldiven, maske, tulum"},
    "5 — Yangın ve Patlama Tehlikeleri":               {"engineering": "Yangın söndürücü ve alarm kur", "ppe": "Alev geciktirici KKD"},
    "6 — Termik Tehlikeler":                           {"engineering": "Isı yalıtımı uygula", "ppe": "Isıya/soğuğa dirençli eldiven ve giysi"},
    "7 — Özel Fiziksel Etkilerin Yol Açtığı Tehlikeler": {"engineering": "Fiziksel etken kaynağını koru veya izole et", "ppe": "Duruma uygun KKD seç"},
    "8 — Çalışma Koşullarının Yol Açtığı Tehlikeler": {"engineering": "Ortam koşullarını iyileştir", "ppe": "Duruma uygun KKD seç"},
    "9 — Fiziksel Baskılar":                           {"engineering": "Ergonomik çalışma istasyonu kur", "ppe": "Destek ekipmanı kullan"},
    "10 — Psikolojik Faktörler":                       {"administrative": "Yük dengeleme ve destek programı uygula", "ppe": "—"},
    "11 — Diğer Tehlikeler":                           {"administrative": "Sahaya özel risk değerlendirmesi yap", "ppe": "Duruma göre belirle"},
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
    Önce kategoriye gir, sonra açıklamada anahtar kelime eşleştir.
    """
    cat_controls = CONTROL_HIERARCHY.get(category, {})
    desc_lower = description.lower()

    best_match = None
    best_score = 0
    for hazard_key, controls in cat_controls.items():
        keywords = hazard_key.lower().split()[:5]
        score = sum(1 for kw in keywords if len(kw) > 3 and kw in desc_lower)
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