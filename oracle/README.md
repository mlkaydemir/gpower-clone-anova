# ORACLE — G*Power 3.1.9.7 Referans Vektörleri ve Kâhin Kayıtları

**Ders:** YZM301 · Teardown Sprint  
**Test Ailesi:** K3 — ANOVA One-Way (`anova-oneway`)  
**Kâhin Kaynağı:** G*Power 3.1.9.7 (Windows x86, Heinrich Heine Universität Düsseldorf)

---

## 1. Kâhin (Oracle) Nedir ve Nasıl Toplandı?

Yazılım testinde "kâhin" (test oracle), verilen bir girdi için sistemin üretmesi gereken doğru cevabı bildiğimiz mekanizmadır. Bu sprintte kâhinimiz G*Power 3.1.9.7 yazılımıdır.

Bu dizinde yer alan referans veri setleri:
1. **`public_vectors.jsonl`**: `CONTRACT.md` Bölüm 9'da ders eğitmeni tarafından sağlanan 25 açık referans vektörü (5 aile × 5 analiz modu).
2. **`gpower_oracle_anova_35.jsonl` / `gpower_oracle_anova_35.csv`**: K3 ailesi (`anova-oneway`) için farklı klinik tasarım parametreleriyle (3, 4, 5, 6, 8, 10 tedavi kolu; küçük/orta/büyük etki büyüklükleri; farklı anlamlılık düzeyleri ve güç hedefleri) oluşturulmuş 35 adet doğrulanmış kâhin vektörü.

---

## 2. G*Power 3.1.9.7 Arayüz Adımları ve Protokol Kaydı

G*Power GUI'sinde referans değerleri toplama adımları:
1. Üst menüden **Test family** $\rightarrow$ `F tests` seçilir.
2. **Statistical test** $\rightarrow$ `ANOVA: Fixed effects, omnibus, one-way` seçilir.
3. **Type of power analysis** açılır kutusundan ilgili mod seçilir:
   - `A priori: Compute required sample size - given α, power, and effect size`
   - `Post hoc: Compute achieved power - given α, sample size, and effect size`
   - `Compromise: Compute implied α and power - given β/α ratio, sample size, and effect size`
   - `Criterion: Compute required α - given power, sample size, and effect size`
   - `Sensitivity: Compute required effect size - given α, power, and sample size`
4. İlgili girdi parametreleri (`Effect size f`, `α err prob`, `Power (1-β err prob)`, `Number of groups`, `Total sample size`, vb.) doldurulur.
5. **Calculate** butonuna basılır.
6. Alt paneldeki **Output Parameters** (`Noncentrality parameter λ`, `Critical F`, `Numerator df`, `Denominator df`, `Total sample size`, `Actual power`) protokol alanına kopyalanır.

---

## 3. Ekran Görüntüsü Referansları (Screenshots Guide)

Kâhin doğrulaması için alınan ekran görüntüleri ve protokol kayıtları:
- `screenshots/anova_apriori_k5_f025.png`: Public vector 11 doğrulaması ($N=305$, $df_1=4, df_2=300, \lambda=19.0625$).
- `screenshots/anova_posthoc_k5_N100.png`: Public vector 12 doğrulaması ($Power=0.4663312$).
- `screenshots/anova_compromise_q1.png`: Public vector 13 doğrulaması ($\alpha=\beta=0.2309247$).
- `screenshots/anova_criterion_p95.png`: Public vector 14 doğrulaması ($\alpha=0.6245994$).
- `screenshots/anova_sensitivity_p95.png`: Public vector 15 doğrulaması ($f=0.4418664$).

