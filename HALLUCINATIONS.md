# HALLUCINATIONS.md — Halüsinasyon Günlüğü

**Ders:** YZM301 · Teardown Sprint  
**Test Ailesi:** K3 — ANOVA One-Way (`anova-oneway`)  
**Kural:** Ajanın inceleme ve modelleme safhasında ürettiği yanlış çıkarımlar, bunların nasıl tespit edildiği ve hangi testler tarafından yakalandığı.

---

### Halüsinasyon 1: A Priori Örneklem Büyüklüğünde Kesirli Tavan Yuvarlama ($\lceil N \rceil$) Varsayımı

- **Ajanın İddiası / Yanılgısı:**  
  Ajan, standart literatürde ve R'ın `pwr.anova.test` paketinde olduğu gibi, denklemin sürekli bir $N$ değişkeni üzerinden çözülebileceğini ve ardından çıkan değerin yukarı yuvarlanacağını (`math.ceil(N)`) savundu. Örneğin $f=0.25, \alpha=0.05, power=0.95, groups=5$ için $N \approx 301.2$ hesaplandığında, ajanın önerdiği sonuç $N = 302$ oldu.
- **Nasıl Fark Edildi?**  
  Referans vektör (public vector) testi çalıştırıldığında beklenen $N_{total}$ değerinin 305 olduğu görüldü. $302 \neq 305$ olduğundan test doğrudan başarısız oldu.
- **Hangi Test Yakaladı?**  
  `tests/test_engine.py::test_public_vector_apriori` ve `tests/test_differential.py::test_differential_apriori_grid`.
- **Kök Neden ve Düzeltme:**  
  Ajana "Bu iddianın kanıtı hangi fonksiyonda?" sorusu yöneltildi. Ghidra ile binary incelendiğinde (`FUN_0045c810`), G*Power'ın tek yönlü ANOVA'da dengeli tasarım ($n_1 = n_2 = \dots = n_k$) uyguladığı ve arama döngüsünü grup başına denek sayısı $n$ üzerinden tamsayı artışlarla yürüttüğü ortaya çıktı. Grup başına $n=60$ için ulaşılan güç $0.9491 < 0.95$ kaldığından, algoritma $n=61$'e geçmiş ve $N = 61 \times 5 = 305$ üretmiştir. Motor bu kurala göre düzeltildi.

---

### Halüsinasyon 2: Denominator Serbestlik Derecesinin $df_2 = N - 1$ Sanılması

- **Ajanın İddiası / Yanılgısı:**  
  İlk prototip geliştirilirken ajan genel regresyon veya tek örneklem mantığıyla payda serbestlik derecesini $df_2 = N - 1$ olarak kodladı.
- **Nasıl Fark Edildi?**  
  $N=305$ verildiğinde $df_2 = 304$ olarak hesaplandı. Bunun sonucunda $critical\_f$ değeri $2.4017397$ yerine $2.38914$ çıktı ve tolerans sınırını ($10^{-6}$) fazlasıyla aştı.
- **Hangi Test Yakaladı?**  
  `tests/test_engine.py::test_public_vector_posthoc` ve `SPEC.md` kabul kriteri 1.
- **Kök Neden ve Düzeltme:**  
  One-Way Omnibus ANOVA'da grupiçi varyans (Within-group / Error) serbestlik derecesi $df_2 = N - k$'dır (toplam gözlem sayısı eksi grup sayısı). $305 - 5 = 300$ olmalıdır. Hata hemen düzeltildi ve testlerin tamamı yeşile döndü.

---

### Halüsinasyon 3: Sensitivity Modunda $f$ İçin Kapalı Formül Varsayımı

- **Ajanın İddiası / Yanılgısı:**  
  Ajan, sensitivity modunda (verilen $\alpha, Power, N, groups$ üzerinden saptanabilir minimum $f$ değerini bulma) $f$'in merkezi F dağılımının ters fonksiyonu ve serbestlik dereceleri kullanılarak analitik bir kapalı formülle doğrudan hesaplanabileceğini öne sürdü.
- **Nasıl Fark Edildi?**  
  Üretilen $f$ değeri $0.3541$ çıkarken, G*Power'ın beklenen değeri $0.4418664$ idi. Aradaki fark \%25 seviyesindeydi.
- **Hangi Test Yakaladı?**  
  `tests/test_engine.py::test_public_vector_sensitivity`.
- **Kök Neden ve Düzeltme:**  
  Noncentral F dağılımının kümülatif dağılımında $\lambda$ parametresi integral ve hipergeometrik seriler içerdiğinden kapalı formülü bulunmamaktadır. G*Power'ın yaptığı gibi (`FUN_0045d410`), önce $F_{crit} = F_{central}^{-1}(1 - \alpha; df_1, df_2)$ hesaplanmalı, ardından $1 - F_{noncentral}(F_{crit}; df_1, df_2, \lambda) = Power$ denklemi $\lambda$ için sayısal kök bulma (Brentq) yöntemiyle çözülmeli ve son olarak $f = \sqrt{\lambda / N}$ alınmalıdır. Bu mantık motora entegre edilince hata $0.0000000$ oldu.

---

### Halüsinasyon 4: Post-Hoc Modunda $N \le groups$ İçin Sessiz Hata Varsayımı

- **Ajanın İddiası / Yanılgısı:**  
  Ajan, kullanıcının $N=4, groups=5$ girmesi durumunda motorun matematiksel olarak sıfır veya negatif serbestlik derecesini yok sayıp NaN döndürebileceğini veya çıkış kodunu 0 yapabileceğini iddia etti.
- **Nasıl Fark Edildi?**  
  Sözleşme sınır değer testinde uygulamanın çökmesi (crash) veya sessizce geçmesi sözleşmeye aykırı bulundu.
- **Hangi Test Yakaladı?**  
  `tests/test_cli_validation.py::test_invalid_sample_size_relative_to_groups`.
- **Kök Neden ve Düzeltme:**  
  G*Power PE incelemesinde (`FUN_0045c770`), $N \le groups$ durumunda `INCONSISTENT` mantıksal hatası fırlatılması ve çıkış kodunun 2 olması gerektiği belirlendi.

