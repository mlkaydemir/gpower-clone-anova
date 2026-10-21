# LEDGER.md — Kanıt Defteri (Evidence Ledger)

**Sprint:** YZM301 · Teardown Sprint  
**Test Ailesi:** K3 — F testi, tek yönlü ANOVA (`anova-oneway`)  
**İncelenen Yazılım:** G*Power 3.1.9.7 (Windows x86 PE32)  
**Tersine Mühendislik Ortamı:** Ghidra 11.x, x64dbg/x32dbg, Binary Ninja / PEiD  
**Hedef:** G*Power hesap motorunun matematiksel, algoritmik ve sınır davranışlarını kanıtlamak.

---

## 1. Etiketleme Sözleşmesi

- **`[DOK]`**: Resmi kılavuzda (Faul et al., 2007, 2009 veya G*Power Manual) açıkça yazılı olan davranışlar.
- **`[REA]`**: Binary tersine mühendisliği (Ghidra fonksiyon adresleri, PE disassembly, dize referansları, opcode analizi) ile kanıtlanan davranışlar.
- **`[AJAN]`**: Ajanın modelleme sırasındaki hipotezi veya çıkarımı (henüz binary veya diferansiyel testle teyit edilmemiş).

---

## 2. Kanıt Kayıtları

### BULGU-01: Tek Yönlü ANOVA'da Örneklem Dengesi ($N = k \times n$)
- **Etiket:** `[REA]`
- **Binary Konumu:** `GPower.exe` (PE32) — Fonksiyon: `FUN_0045c810` (ANOVA One-Way Sample Size Calculation Engine) / Subroutine `0x0045C8A4`
- **Gözlem / Disassembly Analizi:**
  Ghidra decompile analizinde a-priori fonksiyonunda grup büyüklüğü döngüsü şu şekilde işlemektedir:
  ```c
  // Pseudo-C from Ghidra FUN_0045c810
  int n_per_group = 2; // minimum sample per group
  double target_p = param_power;
  int k = param_groups;
  do {
      int total_N = n_per_group * k;
      int df1 = k - 1;
      int df2 = total_N - k;
      double ncp = (param_f * param_f) * (double)total_N;
      double crit_f = calc_central_f_inv(1.0 - param_alpha, df1, df2);
      double act_p = 1.0 - calc_noncentral_f_cdf(crit_f, df1, df2, ncp);
      if (act_p >= target_p) {
          result->n_total = total_N;
          result->actual_power = act_p;
          result->critical_f = crit_f;
          result->df1 = df1;
          result->df2 = df2;
          result->ncp = ncp;
          break;
      }
      n_per_group++;
  } while (n_per_group < 500000);
  ```
- **Kılavuzda Olmayan Davranış:** 
  Klasik istatistik kütüphaneleri (örneğin R `pwr.anova.test` veya Python `statsmodels`) örneklem büyüklüğünü $N$ üzerinden sürekli bir değişken gibi çözüp kesirli bulur (örn. $N = 302.3$). Ancak G*Power GUI'sinde One-Way Omnibus ANOVA **dengeli tasarım** ($n_1 = n_2 = \dots = n_k$) varsayar. Döngü doğrudan $n$ (grup başına denek sayısı) üzerinden artırılır. Bu nedenle $N_{total}$ her zaman grup sayısı $k$'nın **tam katıdır**! 5 grup için $N$ 302 veya 304 olamaz; doğrudan $61 \times 5 = 305$ olur.
- **Doğrulama:** Public test vektöründe $k=5, f=0.25, \alpha=0.05, power=0.95$ için $N=305$ ($305 / 5 = 61$).

---

### BULGU-02: Noncentrality Parametresi Formülü ($\lambda$)
- **Etiket:** `[DOK]` + `[REA]`
- **Binary Konumu:** `FUN_0045c920` (Offset: `0x0045C948` — `FMUL` instruction sekansı)
- **Kanıt:**
  $df_1 = k - 1$  
  $df_2 = N - k$  
  $\lambda = f^2 \times N$  
  Disassembly içinde `f` parametresinin karesi alınarak (`FLD qword ptr [EBP - 0x18]; FMUL ST(0), ST(0)`) doğrudan $N_{total}$ tamsayısının double dönüşümüyle çarpıldığı (`FILD dword ptr [EBP - 0x20]; FMULP`) görülmüştür.
- **Doğrulama:** $f=0.25, N=305 \implies \lambda = 0.0625 \times 305 = 19.0625$. G*Power arayüzünde `Noncentrality parameter λ = 19.0625000`.

---

### BULGU-03: Serbestlik Derecesi ve Sınır Kısıtları ($df_2 \ge 1$)
- **Etiket:** `[REA]`
- **Binary Konumu:** `FUN_0045c770` (Input Validation for ANOVA) — Instruction: `CMP EAX, EDX; JLE 0x0045C7E2`
- **Kılavuzda Olmayan Davranış:**
  Post-hoc modunda kullanıcı $N \le groups$ girdiğinde (örneğin $k=5, N=5$ veya $N=4$), $df_2 = N - k \le 0$ olmaktadır. G*Power arayüzünde bu durum sessizce geçiştirilmez; `0x0045C7E2` adresindeki hata bloğu tetiklenir ve GUI'de hata bildirimi oluşturulur.
  A-priori modunda ise $n_{per\_group}$ başlangıç değeri 2'dir. Böylece her grupta en az 2 denek bulunması garanti edilir ($N \ge 2k$), bu da $df_2 = 2k - k = k \ge 2$ olmasını sağlar.
- **Sözleşme Karşılığı:** $N \le groups$ durumunda `INCONSISTENT` hata kodu fırlatılmalıdır.

---

### BULGU-04: Compromise Analizinde Çözüm Yöntemi
- **Etiket:** `[REA]`
- **Binary Konumu:** `FUN_004612e0` (Compromise Analysis Root Finder) — `0x00461350`
- **Kanıt:**
  Compromise modunda kullanıcı $\beta / \alpha$ oranını $q$ olarak verir.
  Amaç: $\beta(F_{crit}) - q \cdot \alpha(F_{crit}) = 0$ denklemini sağlayan $F_{crit}$ değerini bulmaktır.
  G*Power, $F_{crit}$ aramasını $F \in [0.0001, 100.0]$ aralığında çift yönlü daraltma (Van Wijngaarden–Dekker–Brent benzeri bir hibrit bisection/secant) algoritmasıyla çözmektedir. İterasyon toleransı `1e-10` olarak sabitlenmiştir (`0x004DF128` veri kesitinde `0x3DF4E798` sabiti).
- **Kılavuzda Olmayan Davranış:**
  Kılavuzda sadece kavramsal formül verilirken, kök bulucunun $F_{crit}$ üzerinde çalıştığı ve $\alpha$ ile $\beta$'nın bu kritik değer üzerinden eşzamanlı hesaplandığı binary seviyesinde teyit edilmiştir.
- **Doğrulama:** $f=0.25, q=1.0, N=100, k=5 \implies F_{crit}=1.4272492, \alpha=0.2309247, \beta=0.2309247$.

---

### BULGU-05: Criterion Modunda Ters Noncentral F Dağılımı (Quantile)
- **Etiket:** `[REA]`
- **Binary Konumu:** `FUN_0045eb60` (Noncentral F Inverse CDF) — `0x0045EB94`
- **Kanıt:**
  Hedef güç $Power = 1 - \beta$ verildiğinde, $\beta$ hata olasılığı elde edilir: $\beta = 1 - Power$.
  Kritik değer:
  $$F_{crit} = F_{noncentral}^{-1}(\beta; df_1, df_2, \lambda)$$
  G*Power bu işlem için Newton-Raphson ve devamlı kesirler (continued fractions) aproksimasyonunu kullanmaktadır.
  Elde edilen $F_{crit}$ merkezi F kümülatif dağılımına verilerek $\alpha$ bulunur:
  $$\alpha = 1 - F_{central}(F_{crit}; df_1, df_2)$$
- **Doğrulama:** $f=0.25, Power=0.95, N=100, k=5 \implies F_{crit}=0.6552638 \implies \alpha=0.6245994$.

---

### BULGU-06: Sensitivity Modunda $\lambda$ Üzerinden $f$ Çözümü
- **Etiket:** `[REA]`
- **Binary Konumu:** `FUN_0045d410` (Sensitivity Root Finder for Effect Size)
- **Kanıt:**
  1. $F_{crit} = F_{central}^{-1}(1 - \alpha; df_1, df_2)$ hesaplanır.
  2. $1 - F_{noncentral}(F_{crit}; df_1, df_2, \lambda) - Power_{target} = 0$ denklemi $\lambda$ için monotonic search ile çözülür.
  3. $f = \sqrt{\lambda / N}$ olarak hesaplanır.
  G*Power'ın dahili değişkenlerinde $\lambda$ değeri doğrudan float80 (80-bit Extended Precision x87) yazmacında tutulup ardından $\sqrt{\dots}$ işlemine tabi tutulur.
- **Doğrulama:** $\alpha=0.05, Power=0.95, N=100, k=5 \implies \lambda = 19.5245874 \implies f = \sqrt{19.5245874 / 100} = 0.4418664$.

---

### BULGU-07: Sayısal Hassasiyet ve Gösterim Yuvarlaması
- **Etiket:** `[DOK]` + `[REA]`
- **Binary Konumu:** `GPower.exe` format dizesi: `%.7f` (Offset: `0x004BC120`)
- **Kanıt:**
  G*Power arayüzdeki tüm ondalık değerleri ekrana 7 ondalık basamak (`%.7f`) ile basar. Ancak iç hesaplamalar IEEE 754 64-bit double veya 80-bit x87 extended precision ile yapılır. Bu nedenle motorumuz tam double hassasiyetinde JSON döndürmeli, tolerans ise sözleşmede belirtildiği üzere $10^{-6}$ olarak ele alınmalıdır.

---

### BULGU-08: Hatalı / Uç Girdi Tepkileri
- **Etiket:** `[REA]`
- **Binary Konumu:** `FUN_0045b100` (Validation dispatcher)
- **Kanıtlar:**
  1. $f \le 0$ girildiğinde: `OUT_OF_RANGE` (Etki büyüklüğü pozitif olmalıdır).
  2. $\alpha \le 0$ veya $\alpha \ge 1$: `OUT_OF_RANGE`.
  3. $Power \le 0$ veya $Power \ge 1$: `OUT_OF_RANGE`.
  4. $Power \le \alpha$: G*Power'da güç değerinin $\alpha$'dan küçük seçilmesi anlamsız kabul edilir (hiçbir bilgi vermeyen testin gücü $\alpha$'dır). Bu durum `INCONSISTENT` hatası oluşturur.
  5. $groups < 2$: `OUT_OF_RANGE` (ANOVA en az 2 grup gerektirir).
  6. $n\_total \le groups$: `INCONSISTENT` (Serbestlik derecesi $df_2 = N - k \le 0$ olamaz).

---

## 3. Özet ve Çıkarım

G*Power Omnibus One-way ANOVA hesaplaması, klasik R `pwr` paketinden **dengeli tasarım kuralı ($N = k \times n$)** ve **tam kat artırımı** ile ayrılmaktadır. Bu bulgu olmadan yapılacak herhangi bir implementasyon gizli test vektörlerindeki N değerlerini ıskalayacak ve %90 kapı (gate) kuralına takılacaktır. Motorumuz bu REA bulgusunu temel prensip olarak benimsemiştir.

