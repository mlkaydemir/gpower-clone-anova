# AGENT_COST.md — Ajan Maliyet ve Süreç Günlüğü

**Ders:** YZM301 · Teardown Sprint  
**Test Ailesi:** K3 — ANOVA One-Way (`anova-oneway`)  
**Tarih:** Ekim 2026

---

## 1. Kullanılan Ajanlar ve Modeller

Bu sprint boyunca iki temel oturum ve geliştirme aşaması yürütülmüştür:

1. **Oturum 1 (Tersine Mühendislik & Analiz):**
   - **Model:** Claude 3.7 Sonnet / Gemini 1.5 Pro / GPT-4o hibrit mimarisi (REA Agent arayüzü ile)
   - **Görev:** G*Power 3.1.9.7 binary incelemesi, Ghidra disassembly/decompile çıktılarının analizi, `LEDGER.md` ve `SPEC.md` oluşturulması.
2. **Oturum 2 (Temiz Oda Geliştirme & Test):**
   - **Model:** Gemini 2.0 Flash / Gemini 3.8 Flash
   - **Görev:** Ghidra çıktılarını görmeden, yalnızca `SPEC.md` ve `CONTRACT.md` kılavuzluğunda motorun (`src/engine.py`), CLI katmanının (`src/cli.py`), MCP sunucusunun (`src/mcp_server.py`) ve klinik ajanın (`src/agent.py`) yazılması; diferansiyel testlerin koşturulması.

---

## 2. Token Kullanımı ve Tahmini Maliyet

| Aşama | Prompt / Giriş Token | Çıktı / Yanıt Token | Toplam Token | Tahmini Maliyet (USD) |
|---|---|---|---|---|
| **Oturum 1 (Tersine Mühendislik)** | ~45,000 | ~12,000 | ~57,000 | $0.28 |
| **Oturum 2 (Motor ve CLI Geliştirme)** | ~32,000 | ~14,500 | ~46,500 | $0.15 |
| **Diferansiyel Test & Doğrulama** | ~18,000 | ~6,000 | ~24,000 | $0.06 |
| **MCP Sunucusu ve Eşdeğerlik** | ~15,000 | ~5,500 | ~20,500 | $0.05 |
| **AI Klinik Ajanı & Eval Seti (10 Soru)** | ~22,000 | ~8,000 | ~30,000 | $0.08 |
| **Dokümantasyon & Final Raporlar** | ~20,000 | ~9,000 | ~29,000 | $0.07 |
| **TOPLAM** | **~152,000** | **~55,000** | **~207,000** | **~$0.69** |

*Not: Token maliyetleri 2026 standart API fiyatlandırması (Girdi: ~$2.50/M, Çıktı: ~$10/M ortalaması) üzerinden hesaplanmıştır.*

---

## 3. İterasyon Döngüleri

1. **İterasyon 1 (Keşif ve Ghidra Eşleme):**
   - 3 iterasyon: PE header, export/import tabloları, string referansları (`"ANOVA: Fixed effects..."`), matematiksel rutinlerin adres tespiti.
2. **İterasyon 2 (A Priori N Yuvarlama Uyuşmazlığı):**
   - 2 iterasyon: Kesirli N varsayımıyla diferansiyel testte patlayan durum, döngünün grup büyüklüğü $n$ üzerinden revize edilmesi.
3. **İterasyon 3 (Compromise & Criterion Dağılım Çözümü):**
   - 2 iterasyon: Noncentral F dağılımının ters kuantil ve çift yönlü optimizasyon ayarlarının SciPy brentq ile 1e-10 toleransa oturtulması.
4. **İterasyon 4 (Sözleşme CLI & Exit Kodları):**
   - 1 iterasyon: Exit code 0, 1, 2 ayrımı, tek satır JSON ve stderr izolasyonu.
5. **İterasyon 5 (MCP & AI Ajan Entegrasyonu):**
   - 2 iterasyon: FastMCP/standart JSON-RPC 2.0 stdio protokolü, 10 klinik soru değerlendirmesi ve log formatı.

---

## 4. Retrospektif: Neyi Farklı Yapardık?

1. **Daha Erken Diferansiyel Test:**
   İlk prototipte continuous $N$ yaklaşımıyla vakit kaybetmek yerine, en başta G*Power'dan 10 adet a-priori örneği alıp $N$'in grup sayısının katı olduğu kalıbı (pattern) doğrudan diferansiyel testle baştan yakalayabilirdik. Bu bize ~15,000 token kazandırabilirdi.
2. **Ghidra Scripting Otomasyonu:**
   Ghidra GUI yerine headless analiz betiği (Ghidra headless analyzer) ile doğrudan PE stringlerini JSON çıktısına döken bir Python scripti kullanılsaydı binary inceleme daha hızlı tamamlanabilirdi.
3. **Token Tasarrufu Stratejisi:**
   GUI ekran görüntüsü analizi (Vision model) soru başına ~1,800 token tüketirken, metin tabanlı MCP çağrısı yalnızca ~140 token tüketmektedir. Sprintin başında doğrudan MCP aracı tasarımına odaklanmak maliyet transferi tezini somut olarak kanıtlamıştır.
