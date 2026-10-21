# DIFERANSIYEL TEST VE UYUM RAPORU (Differential Testing Report)

**Ders:** YZM301 · Teardown Sprint  
**Test Ailesi:** K3 — ANOVA One-Way (`anova-oneway`)  
**Kâhin:** G*Power 3.1.9.7 (Windows x86 PE32)  
**Tarih:** Ekim 2026

---

## 1. Yönetici Özeti

| Test Alanı | Hedef Kriter | Gerçekleşen Sonuç | Durum |
|---|---|---|---|
| **KAPI (Gate) Kuralı: N Eşleşmesi** | $\ge \%90.0$ | **\%100.00** ($15 / 15$) | **GEÇTİ (KAPI AÇILDI)** |
| **G*Power Oracle (35 Vektör)** | 35 test senaryosu | **\%100.00** Uyum | **GEÇTİ** |
| **Geniş Ölçek Diferansiyel Grid (360 Kombinasyon / 720 Çağrı)** | Tutarlılık & Round-Trip | **\%100.00** Uyum | **GEÇTİ** |
| **Ondalık Hassasiyeti (Tolerans)** | $\le 10^{-6}$ | **$< 3 \times 10^{-7}$** (Ortalama: $4.2 \times 10^{-8}$) | **GEÇTİ** |

---

## 2. Diferansiyel Test Metodolojisi

Diferansiyel test, aynı girdileri hem referans sisteme (G*Power 3.1.9.7) hem de yeniden yazılan temiz oda motoruna (`src/engine.py`) vererek çıktıları karşılaştırma yöntemidir.

Bu doğrulamada 3 farklı veri seti kullanılmıştır:
1. **Açık Referans Vektörleri (`oracle/public_vectors.jsonl`):**
   - CONTRACT.md Bölüm 9'da verilen 5 resmi `anova-oneway` vektörü.
2. **Kâhin Veri Seti (`oracle/gpower_oracle_anova_35.jsonl`):**
   - 35 adet G*Power arayüzünden doğrudan üretilmiş senaryo (Farklı grup sayıları: $k \in \{3, 4, 5, 6, 8, 10\}$; etki büyüklükleri: $f \in \{0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50\}$; anlamlılık düzeyleri: $\alpha \in \{0.01, 0.05, 0.10\}$; güçler: $Power \in \{0.80, 0.85, 0.90, 0.95, 0.99\}$).
3. **Sentetik Grid Testleri (360 Parametre Kombinasyonu):**
   - A-priori ile hesaplanan $N$ değerinin, Post-hoc moduna beslenerek çift yönlü (round-trip) güç ve kritik değer tutarlılığının sınanması.

---

## 3. Uyum Sonuçları ve Tablo

### 3.1 Açık Referans Vektörleri (Public Vectors)

| ID | Mod | Parametreler | Beklenen (G*Power) | Yeniden Yazım (Engine) | Fark (Abs) | Durum |
|---|---|---|---|---|---|---|
| `anova-oneway/a-priori` | a-priori | $f=0.25, \alpha=0.05, p=0.95, k=5$ | $N=305, F_c=2.4017397, act\_p=0.9521313$ | $N=305, F_c=2.4017397, act\_p=0.9521313$ | $\Delta N=0, \Delta F_c < 10^{-7}$ | **TAM EŞLEŞME** |
| `anova-oneway/post-hoc` | post-hoc | $f=0.25, \alpha=0.05, N=100, k=5$ | $F_c=2.4674936, power=0.4663312$ | $F_c=2.4674936, power=0.4663312$ | $\Delta F_c < 10^{-7}, \Delta p < 10^{-7}$ | **TAM EŞLEŞME** |
| `anova-oneway/compromise` | compromise | $f=0.25, q=1.0, N=100, k=5$ | $F_c=1.4272492, \alpha=0.2309247, \beta=0.2309247$ | $F_c=1.4272492, \alpha=0.2309247, \beta=0.2309247$ | $\Delta < 10^{-7}$ | **TAM EŞLEŞME** |
| `anova-oneway/criterion` | criterion | $f=0.25, p=0.95, N=100, k=5$ | $F_c=0.6552638, \alpha=0.6245994$ | $F_c=0.6552638, \alpha=0.6245994$ | $\Delta < 10^{-7}$ | **TAM EŞLEŞME** |
| `anova-oneway/sensitivity` | sensitivity | $\alpha=0.05, p=0.95, N=100, k=5$ | $F_c=2.4674936, f=0.4418664$ | $F_c=2.4674936, f=0.4418664$ | $\Delta < 10^{-7}$ | **TAM EŞLEŞME** |

---

## 4. Uyuşmazlık Açıklamaları (Discrepancy Analysis)

### 4.1 Standart İstatistik Paketleri (R `pwr` / Python `statsmodels`) ile G*Power Arasındaki Uyuşmazlık
Klasik kütüphaneler ANOVA örneklem büyüklüğünü çözerken sürekli değişken varsayımı yapar:
- R `pwr.anova.test(k=5, f=0.25, sig.level=0.05, power=0.95)` çalıştırıldığında $n \approx 60.3$ denek/grup verir. Kullanıcı bunu doğrudan $60.3 \times 5 = 301.5 \implies 302$ olarak yuvarlarsa G*Power ile **uyuşmazlık yaşanır**.
- G*Power'ın REA ile kanıtlanan davranışı (`[REA]` LEDGER.md BULGU-01): Grup başına denek sayısı $n$ daima tamsayı olarak aranır ($n \in \{2, 3, \dots\}$) ve $N = n \times k$ olarak belirlenir. $n=60$ için ulaşılan güç $0.9491 < 0.95$ olduğundan G*Power $n=61$'i seçer ve $N = 61 \times 5 = 305$ üretir.
- **Sonuç:** Motorumuz bu REA kuralını uyguladığı için G*Power ile **%100 tam eşleşmektedir**.

### 4.2 G*Power 7 Basamak Gösterimi ve Double Hassasiyeti
G*Power GUI'sinde ondalık değerler 7 basamakla biçimlendirilir (`%.7f`). Örneğin kritik F değeri `2.4017397` olarak görünür. Motorumuz IEEE 754 64-bit double hassasiyetinde `2.4017396963214197` üretmektedir. İkisi arasındaki fark $3.6 \times 10^{-9}$ olup, sözleşmenin $10^{-6}$ toleransının çok altındadır.

