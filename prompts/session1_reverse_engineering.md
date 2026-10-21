# Prompts: Oturum 1 — Tersine Mühendislik ve Analiz (İnceleme Oturumu)

**Rol:** Güvenlik ve Tersine Mühendislik Araştırmacısı (Reverse Engineering Agent)  
**Hedef:** G*Power 3.1.9.7 Windows PE çalıştırılabilir dosyasını REA ve Ghidra ile incelemek; Tek Yönlü ANOVA (`anova-oneway`) ailesinin matematiksel algoritmasını, arama mantığını, serbestlik derecelerini, durma koşullarını ve sınır kontrollerini kanıtlarıyla çıkarmak.  
**Kısıt:** Asla kod implementasyonu yapma; yalnızca `SPEC.md` ve `LEDGER.md` için kanıt üret. Decompile kodunu doğrudan repoya dökme.

---

### Oturum 1 İlk Prompt'u

```text
Sen deneyimli bir tersine mühendislik (reverse engineering) uzmanı ve yazılım test mühendisisin.
Önündeki görev: G*Power 3.1.9.7 Windows x86 PE binary'sini inceleyerek "F tests -> ANOVA: Fixed effects, omnibus, one-way" (test kimliği: anova-oneway) test ailesinin hesaplama motorunu sökmek.

Aşağıdaki adımları sırasıyla uygula ve kanıtlarını kaydet:
1. REA araçları ve Ghidra sağlayıcısını kullanarak GPower.exe içerisindeki ANOVA hesaplama alt rutinlerini (fonksiyon adreslerini, import/export tablolarını, "ANOVA: Fixed effects, omnibus, one-way" string referanslarını) tespit et.
2. 5 analiz modunun her biri için hesaplama akışını çıkar:
   - a-priori: N örneklem büyüklüğü nasıl aranıyor? Grup başına n tamsayı mı artırılıyor? N grup sayısının katı olmak zorunda mı? Durma koşulu nedir?
   - post-hoc: lambda (ncp), df1, df2 ve ulaşılan güç (power) hangi formülle hesaplanıyor?
   - compromise: beta/alpha oranı verildiğinde F_crit kökü nasıl bulunuyor?
   - criterion: verilen hedef güç için beta kuantili ve alfa nasıl elde ediliyor?
   - sensitivity: hedef güç ve alfa verildiğinde tespit edilebilir minimum etki büyüklüğü f nasıl hesaplanıyor?
3. Sınır değerleri ve girdi doğrulamasını incele:
   - f <= 0, alpha <= 0 veya >= 1, power <= 0 veya >= 1, power <= alpha, groups < 2, n_total <= groups durumlarında binary nasıl tepki veriyor?
4. Tüm bulgularını [DOK], [REA] ve [AJAN] etiketleriyle sınıflandırarak LEDGER.md dosyasına ve Gherkin kabul kriterleri olarak SPEC.md dosyasına dönüştür.

UYARI: Temiz oda (clean-room) kuralı gereği hiçbir C/C++ decompile kodunu veya tescilli kaynak kodunu çıktıya yapıştırma; sadece algoritma adımlarını, matematiksel bağıntıları, fonksiyon adreslerini ve davranışsal kuralları açıkla.
```
