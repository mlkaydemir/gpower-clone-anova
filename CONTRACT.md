# CONTRACT.md — `gpower-clone` Arayüz Sözleşmesi

**Sözleşme sürümü:** 1.0.0  
**Ders:** YZM301 · Teardown Sprint  
**Referans (kâhin):** G*Power 3.1.9.7 (Windows)  

Bu belge, yeniden yazdığınız hesap motorunun dış dünyayla **nasıl konuştuğunu** tanımlar: komut, parametre adları, çıktı alanları, hata biçimi ve karşılaştırma kuralları. Gizli test vektörleri, bütün takımların uygulamalarında **aynı düzenekle, otomatik olarak** çalıştırılacak. Sözleşmeye uymayan bir uygulama, hesabı doğru olsa bile değerlendirilemez.

## Etik niyet

Bu çalışma, G*Power'ın yazarlarının (Faul, Erdfelder, Lang ve Buchner) bilim dünyasına ücretsiz sunduğu emeğe saygıyla, yalnızca eğitim amacıyla yürütülen bir derstir; G*Power'ı değiştirmiyor, dağıtmıyor, satmıyor ve hiçbir çıktımızı G*Power olarak sunmuyoruz. G*Power'ı yalnızca davranışını gözlemlediğimiz bir referans olarak kullanıyoruz: kaynak kodu ya da kaynak koda dönüştürülmüş çıktısı yayımlanmıyor, hesap yayımlanmış yöntemlerden ve gözlenen davranıştan bağımsız olarak yeniden yazılıyor. Amacımız G*Power'la yarışmak değil, ona ajan çağı için bir katkı önermektir; en iyi çalışmaları yazarların değerlendirmesine sunacak, yazarların talebi hâlinde ilgili materyali derhal yayından kaldıracağız.

---

## 1. Kapsam

| Kapsamda | Kapsam dışı |
|---|---|
| 5 test ailesi (Bölüm 4) | G*Power'daki diğer tüm testler |
| 5 analiz modu (Bölüm 3) | Grafik (X-Y plot) ve protokol çıktısı |
| Etki büyüklüğünün doğrudan girilmesi | Etki büyüklüğünü ortalama ve standart sapmadan hesaplama ("Determine" penceresi) |

**Zorunlu modlar:** `a-priori` ve `post-hoc`.  
**Bonus modlar:** `compromise`, `criterion`, `sensitivity`.  

---

## 2. Genel kurallar

### 2.1 Komut

```
gpower-clone --test <TEST_ID> --mode <MODE_ID> [--<alan> <değer> ...]
```

- Çalıştırılabilir dosyanın adı `gpower-clone`. Dil serbest. README'de kurulumu ve çalıştırmayı tek komutla gösterin.
- Her parametre `--<alan> <değer>` biçimindedir. Alan adları Bölüm 4'teki tablolarla **birebir** aynıdır.
- **Varsayılan değer yoktur.** Bir mod için gerekli olan her alan açıkça verilmelidir. Eksik alan hatadır.
- Tanınmayan bir alan hatadır. Modla ilgisiz bir alan (örneğin `post-hoc` modunda `--power`) da hatadır.
- Ondalık ayırıcı her zaman noktadır (`0.05`). İşletim sisteminin dil ayarından etkilenmemelisiniz.
- Ağ erişimi yoktur. Her çağrı 2 saniye içinde tamamlanmalıdır.
- Aynı girdi her zaman aynı çıktıyı verir (deterministik).

### 2.2 Sürüm sorgusu

```
gpower-clone --version
```
```json
{"contract_version": "1.0.0", "name": "<takım-adı>", "engine": "<dil ve sürüm>"}
```

### 2.3 Başarılı çıktı

- `stdout`'a **tek satır JSON** yazılır. Başka hiçbir şey yazılmaz (log, uyarı ve ilerleme bilgisi `stderr`'e).
- Çıkış kodu `0`.
- Sayılar JSON `number` olarak yazılır, **tam double hassasiyetle**. Yuvarlamayın; karşılaştırmayı düzenek yapar (Bölüm 6).
- Tam sayı alanları (`n1`, `n2`, `n_total`, `df`, `df1`, `df2`) JSON tam sayısıdır (`88`, `88.0` değil).
- Bölüm 4'te listelenen alanlar **zorunludur**. Fazladan alan yazabilirsiniz; düzenek onları yok sayar.

### 2.4 Hata çıktısı

```json
{"error": "Power, alpha değerinden büyük olmalı", "code": "INCONSISTENT", "field": "power"}
```

- `stdout`'a tek satır JSON. `error` alanı insan için açıklamadır (Türkçe ya da İngilizce).
- Çıkış kodları: `2` geçersiz girdi, `1` iç hata (hesap yapılamadı, beklenmeyen durum).

| `code` | Anlamı |
|---|---|
| `MISSING_PARAM` | Mod için gerekli bir alan verilmedi |
| `UNKNOWN_PARAM` | Tanınmayan ya da bu modla ilgisiz alan |
| `INVALID_VALUE` | Sayı değil, tam sayı olması gereken yerde ondalık vb. |
| `OUT_OF_RANGE` | Bölüm 5'teki aralığın dışında |
| `INCONSISTENT` | Değerler tek tek geçerli ama birlikte anlamsız |
| `UNSUPPORTED` | Bilinmeyen `--test` ya da `--mode` |
| `NO_SOLUTION` | Girdiler geçerli ama G*Power da bir sonuç üretemiyor |

---

## 3. Analiz modları

| `MODE_ID` | G*Power'daki adı | Ne hesaplar | Durum |
|---|---|---|---|
| `a-priori` | A priori: Compute required sample size | Gerekli örneklem büyüklüğü | **Zorunlu** |
| `post-hoc` | Post hoc: Compute achieved power | Ulaşılan güç | **Zorunlu** |
| `compromise` | Compromise: Compute implied α & power | β/α oranına göre α ve güç | Bonus |
| `criterion` | Criterion: Compute required α | Gerekli α | Bonus |
| `sensitivity` | Sensitivity: Compute required effect size | Saptanabilir en küçük etki büyüklüğü | Bonus |

---

## 4. Test aileleri (K3: `anova-oneway`)

### 4.3 `anova-oneway` · K3

**G*Power:** F tests – ANOVA: Fixed effects, omnibus, one-way  
**Klinik örnek:** Üç tedavi kolu  

| Mod | Girdi alanları | Çıktı alanları |
|---|---|---|
| `a-priori` | `f`, `alpha`, `power`, `groups` | `ncp`, `critical_f`, `df1`, `df2`, `n_total`, `actual_power` |
| `post-hoc` | `f`, `alpha`, `n_total`, `groups` | `ncp`, `critical_f`, `df1`, `df2`, `power` |
| `compromise` | `f`, `beta_alpha_ratio`, `n_total`, `groups` | `ncp`, `critical_f`, `df1`, `df2`, `alpha`, `beta`, `power` |
| `criterion` | `f`, `power`, `n_total`, `groups` | `ncp`, `critical_f`, `df1`, `df2`, `alpha` |
| `sensitivity` | `alpha`, `power`, `n_total`, `groups` | `ncp`, `critical_f`, `df1`, `df2`, `f` |

| Alan | G*Power etiketi |
|---|---|
| `f` | Effect size f |
| `groups` | Number of groups |
| `critical_f` | Critical F |
| `df1`, `df2` | Numerator df, Denominator df |

Örnek:
```bash
gpower-clone --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.95 --groups 5
```
```json
{"ncp": 19.0625, "critical_f": 2.4017397, "df1": 4, "df2": 300, "n_total": 305, "actual_power": 0.9521313}
```

---

## 5. Girdi aralıkları

| Alan | Tür | Aralık |
|---|---|---|
| `alpha` | ondalık | 0 < alpha < 1 |
| `power` | ondalık | 0 < power < 1 |
| `beta_alpha_ratio` | ondalık | > 0 |
| `f` | ondalık | > 0 |
| `n_total` | tam sayı | ≥ 2 (ve ANOVA'da n_total > groups) |
| `groups` | tam sayı | ≥ 2 |

---

## 6. Karşılaştırma kuralları

| Alan türü | Kural |
|---|---|
| Tam sayılar: `n_total`, `df1`, `df2` | **Tam eşleşme** |
| Ondalıklar: `ncp`, `critical_f`, `actual_power`, `power`, `alpha`, `beta`, `f` | \|sizin − G*Power\| ≤ 1e-6 **ya da** göreli fark ≤ 1e-6 |
| Hata beklenen vektör | `error` alanı var ve çıkış kodu `0` değil. |

### Kapı
Gizli `a-priori` vektörlerinde **N alanlarının** (`n_total`) en az **%90** oranında tam eşleşmesi gerekir.

