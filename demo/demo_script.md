# 60 SANİYELİK CLI DEMO VİDEO REHBERİ (DEMO SCRIPT)

**Sprint:** YZM301 · Teardown Sprint  
**Test Ailesi:** K3 — ANOVA One-Way (`anova-oneway`)  
**Süre:** Tam 60 saniye  
**Gereksinim:** Ekran kaydı aracı (OBS Studio, Loom, ShareX veya Windows `Win + G`)

---

## 1. 60 Saniyelik Zaman Akışı ve Konuşma Metni

| Zaman | Ekranda Yapılacak İşlem | Seslendirilecek / Anlatılacak Metin |
|---|---|---|
| **00:00 - 00:10** | Terminal açılır, `.\gpower-clone.bat --version` yazılır ve çalıştırılır. | *"Merhaba, YZM301 Teardown Sprint ödevimizde K3 tek yönlü ANOVA test ailesini G*Power 3.1.9.7 binary'sinden tersine mühendislikle söküp temiz odada yeniden yazdık. Sürüm sorgumuz sözleşmeye uygun tek satır JSON dönüyor."* |
| **00:10 - 00:25** | Public a-priori komutu çalıştırılır: <br>`.\gpower-clone.bat --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.95 --groups 5` | *"G*Power kılavuzundaki açık referans vektörümüzü çalıştırıyoruz: f=0.25, alfa=0.05, güç=0.95 ve 5 grup. REA ile bulduğumuz dengeli grup tasarımı kuralıyla N değeri 305 olarak G*Power ile kuruşu kuruşuna tam eşleşiyor."* |
| **00:25 - 00:35** | Hata durumu komutu çalıştırılır: <br>`.\gpower-clone.bat --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.03 --groups 5` | *"Sözleşmeye uygun hata yakalama mekanizmamız: Güç alfa değerinden küçük verildiğinde sistemimiz INCONSISTENT hata kodu ve exit code 2 ile çıkıyor."* |
| **00:35 - 00:45** | Diferansiyel testler koşturulur: <br>`python -m pytest tests/test_differential.py -v` | *"35 kâhin vektörümüz ve 360 kombinasyonluk grid diferansiyel testlerimizi koşturuyoruz. N eşleşme oranımız yüzde 100 ile yüzde 90 kapı barajını rahatça geçiyor."* |
| **00:45 - 00:55** | Bonus katmanlar: MCP testi ve AI Ajanı gösterilir: <br>`python -m src.agent --eval` | *"Bonus katmanlarımız: MCP sunucumuz ve Türkçe klinik soruyu MCP aracına bağlayan AI ajanımız. 10 soruluk klinik test setinde yüzde 100 doğrulukla araç çağrılarını logluyor."* |
| **00:55 - 01:00** | Proje GitHub reposu gösterilir, kapanış. | *"G*Power'ı başarıyla ajan çağına taşıdık. Teşekkürler."* |

---

## 2. Otomatik Demo Çalıştırıcı

Kullanıcı videoyu çekerken elle komut yazmakla vakit kaybetmesin diye adımları sırayla, renkli ve açıklamalı olarak ekrana basan `demo/run_demo.bat` betiği hazırlanmıştır:

```cmd
demo\run_demo.bat
```
