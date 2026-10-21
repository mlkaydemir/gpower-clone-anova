# SPEC.md — G*Power Clone (K3: ANOVA One-Way) Kabul Kriterleri

**Sözleşme:** CONTRACT.md v1.0.0  
**Biçim:** Gherkin (Cucumber formatı)  
**Kapsam:** F tests – ANOVA: Fixed effects, omnibus, one-way (`anova-oneway`)

---

Feature: Tek Yönlü ANOVA (One-Way ANOVA) Güç Analizi ve Örneklem Boyutu Hesaplama Motoru
  G*Power 3.1.9.7 davranışıyla tam uyumlu çalışan,
  Klinik araştırmacıların ve AI ajanlarının doğrudan tüketebileceği,
  Tek satır deterministik JSON üreten hesaplama arayüzü.

  # --------------------------------------------------------------------------
  # 1. A PRIORI ANALİZİ (Gereken Örneklem Büyüklüğü N)
  # --------------------------------------------------------------------------
  Scenario: A Priori Analizi - Standart Orta Etki ve Yüksek Güç
    Given analiz türü "anova-oneway" ve mod "a-priori" olarak seçildiğinde
    And grup sayısı "groups" 5 olarak verildiğinde
    And etki büyüklüğü "f" 0.25 olarak verildiğinde
    And anlamlılık düzeyi "alpha" 0.05 olarak verildiğinde
    And hedef güç "power" 0.95 olarak verildiğinde
    When hesaplama motoru çalıştırıldığında
    Then çıkış kodu 0 olmalıdır
    And "df1" değeri tam olarak 4 olmalıdır
    And "df2" değeri tam olarak 300 olmalıdır
    And "n_total" değeri tam olarak 305 olmalıdır
    And "n_total", "groups" değerine tam bölünmelidir (her grupta eşit 61 denek)
    And "ncp" değeri 19.0625000 ± 1e-6 olmalıdır
    And "critical_f" değeri 2.4017397 ± 1e-6 olmalıdır
    And "actual_power" değeri 0.9521313 ± 1e-6 olmalıdır
    And "actual_power" değeri hedef güçten (0.95) büyük veya eşit olmalıdır

  Scenario: A Priori Analizi - 3 Tedavi Kolu (Klinik Örnek)
    Given analiz türü "anova-oneway" ve mod "a-priori" olarak seçildiğinde
    And grup sayısı "groups" 3 olarak verildiğinde
    And etki büyüklüğü "f" 0.30 olarak verildiğinde
    And anlamlılık düzeyi "alpha" 0.05 olarak verildiğinde
    And hedef güç "power" 0.80 olarak verildiğinde
    When hesaplama motoru çalıştırıldığında
    Then çıkış kodu 0 olmalıdır
    And "df1" değeri tam olarak 2 olmalıdır
    And "n_total" değeri 3'e tam bölünebilen bir tamsayı olmalıdır
    And "actual_power" >= 0.80 olmalıdır

  # --------------------------------------------------------------------------
  # 2. POST HOC ANALİZİ (Ulaşılan Güç)
  # --------------------------------------------------------------------------
  Scenario: Post Hoc Analizi - Mevcut Veri Kümesinde Güç Tespiti
    Given analiz türü "anova-oneway" ve mod "post-hoc" olarak seçildiğinde
    And grup sayısı "groups" 5 olarak verildiğinde
    And etki büyüklüğü "f" 0.25 olarak verildiğinde
    And anlamlılık düzeyi "alpha" 0.05 olarak verildiğinde
    And toplam örneklem "n_total" 100 olarak verildiğinde
    When hesaplama motoru çalıştırıldığında
    Then çıkış kodu 0 olmalıdır
    And "df1" değeri tam olarak 4 olmalıdır
    And "df2" değeri tam olarak 95 olmalıdır
    And "ncp" değeri 6.2500000 ± 1e-6 olmalıdır
    And "critical_f" değeri 2.4674936 ± 1e-6 olmalıdır
    And "power" değeri 0.4663312 ± 1e-6 olmalıdır

  # --------------------------------------------------------------------------
  # 3. COMPROMISE ANALİZİ (Uzlaşma: Alfa ve Beta Orantısı)
  # --------------------------------------------------------------------------
  Scenario: Compromise Analizi - Eşit Hata Ağırlığı (Beta/Alfa Oranı = 1)
    Given analiz türü "anova-oneway" ve mod "compromise" olarak seçildiğinde
    And grup sayısı "groups" 5 olarak verildiğinde
    And etki büyüklüğü "f" 0.25 olarak verildiğinde
    And hata oranı "beta_alpha_ratio" 1.0 olarak verildiğinde
    And toplam örneklem "n_total" 100 olarak verildiğinde
    When hesaplama motoru çalıştırıldığında
    Then çıkış kodu 0 olmalıdır
    And "df1" değeri tam olarak 4 olmalıdır
    And "df2" değeri tam olarak 95 olmalıdır
    And "ncp" değeri 6.2500000 ± 1e-6 olmalıdır
    And "critical_f" değeri 1.4272492 ± 1e-6 olmalıdır
    And "alpha" değeri 0.2309247 ± 1e-6 olmalıdır
    And "beta" değeri 0.2309247 ± 1e-6 olmalıdır
    And "power" değeri 0.7690753 ± 1e-6 olmalıdır
    And "beta" / "alpha" oranı 1.0 olmalıdır

  # --------------------------------------------------------------------------
  # 4. CRITERION ANALİZİ (Gereken Anlamlılık Düzeyi Alfa)
  # --------------------------------------------------------------------------
  Scenario: Criterion Analizi - Hedef Güç İçin Kritik Alfa Tespiti
    Given analiz türü "anova-oneway" ve mod "criterion" olarak seçildiğinde
    And grup sayısı "groups" 5 olarak verildiğinde
    And etki büyüklüğü "f" 0.25 olarak verildiğinde
    And hedef güç "power" 0.95 olarak verildiğinde
    And toplam örneklem "n_total" 100 olarak verildiğinde
    When hesaplama motoru çalıştırıldığında
    Then çıkış kodu 0 olmalıdır
    And "df1" değeri tam olarak 4 olmalıdır
    And "df2" değeri tam olarak 95 olmalıdır
    And "ncp" değeri 6.2500000 ± 1e-6 olmalıdır
    And "critical_f" değeri 0.6552638 ± 1e-6 olmalıdır
    And "alpha" değeri 0.6245994 ± 1e-6 olmalıdır

  # --------------------------------------------------------------------------
  # 5. SENSITIVITY ANALİZİ (Saptanabilir Minimum Etki Büyüklüğü f)
  # --------------------------------------------------------------------------
  Scenario: Sensitivity Analizi - Belirli N ve Güçte Saptanabilir f
    Given analiz türü "anova-oneway" ve mod "sensitivity" olarak seçildiğinde
    And grup sayısı "groups" 5 olarak verildiğinde
    And anlamlılık düzeyi "alpha" 0.05 olarak verildiğinde
    And hedef güç "power" 0.95 olarak verildiğinde
    And toplam örneklem "n_total" 100 olarak verildiğinde
    When hesaplama motoru çalıştırıldığında
    Then çıkış kodu 0 olmalıdır
    And "df1" değeri tam olarak 4 olmalıdır
    And "df2" değeri tam olarak 95 olmalıdır
    And "critical_f" değeri 2.4674936 ± 1e-6 olmalıdır
    And "ncp" değeri 19.5245874 ± 1e-6 olmalıdır
    And "f" değeri 0.4418664 ± 1e-6 olmalıdır

  # --------------------------------------------------------------------------
  # 6. SINIR DEĞERLER VE HATA DURUMLARI (VALIDATION & ERROR CODES)
  # --------------------------------------------------------------------------
  Scenario: Hatalı Girdi - Eksik Parametre Durumu
    When CLI arayüzü "gpower-clone --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05" şeklinde eksik parametreyle çağrıldığında
    Then çıkış kodu 2 olmalıdır
    And stdout çıktısı tek satır JSON olmalıdır
    And JSON içinde "code" alanı "MISSING_PARAM" olmalıdır
    And JSON içinde "error" açıklaması bulunmalıdır

  Scenario: Hatalı Girdi - Tanınmayan Parametre Durumu
    When CLI arayüzüne modla ilgisiz bir parametre örn. "--ratio 1" veya "--unknown foo" verildiğinde
    Then çıkış kodu 2 olmalıdır
    And JSON içinde "code" alanı "UNKNOWN_PARAM" olmalıdır

  Scenario: Hatalı Girdi - Aralık Dışı Değer (Alpha <= 0 veya Alpha >= 1)
    When CLI arayüzüne "--alpha 0.0" veya "--alpha 1.05" verildiğinde
    Then çıkış kodu 2 olmalıdır
    And JSON içinde "code" alanı "OUT_OF_RANGE" olmalıdır
    And "field" alanı "alpha" olmalıdır

  Scenario: Hatalı Girdi - Aralık Dışı Grup Sayısı (Groups < 2)
    When CLI arayüzüne "--groups 1" verildiğinde
    Then çıkış kodu 2 olmalıdır
    And JSON içinde "code" alanı "OUT_OF_RANGE" olmalıdır
    And "field" alanı "groups" olmalıdır

  Scenario: Hatalı Girdi - Uyumsuz Değerler (Power <= Alpha)
    When CLI arayüzüne "--alpha 0.05 --power 0.03" gibi güç alfanın altında verildiğinde
    Then çıkış kodu 2 olmalıdır
    And JSON içinde "code" alanı "INCONSISTENT" olmalıdır
    And "field" alanı "power" olmalıdır

  Scenario: Hatalı Girdi - Uyumsuz Örneklem (n_total <= groups)
    When post-hoc analizinde "--groups 5 --n_total 4" verildiğinde
    Then çıkış kodu 2 olmalıdır
    And JSON içinde "code" alanı "INCONSISTENT" olmalıdır
    And JSON içinde "error" serbestlik derecesi hatasını belirtmelidir

  # --------------------------------------------------------------------------
  # 7. SÜRÜM SORGUSU VE ARAYÜZ STANDARDI
  # --------------------------------------------------------------------------
  Scenario: Sürüm Sorgusu
    When CLI arayüzü "gpower-clone --version" komutu ile çağrıldığında
    Then çıkış kodu 0 olmalıdır
    And stdout tek satır JSON olmalıdır
    And JSON içinde "contract_version" değeri "1.0.0" olmalıdır
    And JSON içinde "name" ve "engine" alanları bulunmalıdır
