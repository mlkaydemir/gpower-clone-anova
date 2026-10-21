# Prompts: Oturum 2 — Temiz Oda Geliştirme (Clean-Room Implementation)

**Rol:** Temiz Oda Yazılım Geliştiricisi ve Test Mühendisi (Clean-Room Developer)  
**Girdi:** YALNIZCA `SPEC.md` ve `CONTRACT.md` (Ghidra çıktısı, PE disassembly ve decompile kodları kesinlikle kapalıdır).  
**Hedef:** Tek hesap motoru (`src/engine.py`), CLI arayüzü (`src/cli.py`, `gpower-clone`), MCP adaptörü (`src/mcp_server.py`) ve Klinik AI Ajanı (`src/agent.py`) geliştirmek; diferansiyel testlerle %100 uyumu doğrulamak.

---

### Oturum 2 İlk Prompt'u

```text
Sen temiz oda (clean-room) prensibiyle çalışan bir kıdemli yazılım mühendisisin.
Görevin: Elindeki SPEC.md kabul kriterleri ve CONTRACT.md arayüz sözleşmesine dayanarak, "anova-oneway" test ailesi için sıfırdan bir hesaplama motoru, CLI, MCP sunucusu ve AI ajanı geliştirmek.

Sen orijinal binary'yi veya Ghidra çıktılarını asla görmedin ve görmeyeceksin. Tek referansın SPEC.md'de belirtilen davranışlar, matematiksel kurallar ve CONTRACT.md'de tanımlanan CLI/JSON sözleşmesidir.

Uygulaman gereken kurallar:
1. Dil: Python 3. Dağılım fonksiyonları için scipy.stats (f, ncf) ve scipy.optimize (brentq) kullanabilirsin.
2. Mimari:
   - Hesap mantığı TEK BİR MOTORDA (src/engine.py) toplanacak. CLI, MCP ve Ajan bu motoru çağıran ince adaptörler olacak.
   - CLI (src/cli.py): "gpower-clone" komutuyla çalışacak. Başarılı çağrılarda stdout'a tek satır JSON basacak, exit code 0 olacak. Hata durumlarında exit code 2 (girdi hatası) veya 1 (iç hata) ile {"error": "...", "code": "...", "field": "..."} basacak.
   - Sürüm sorgusu: "gpower-clone --version" tek satır JSON sürüm bilgisini verecek.
3. Testler ve Doğrulama:
   - tests/ klasörü altında unit testler, sözleşme doğrulama testleri ve G*Power oracle verileriyle diferansiyel testler yaz.
   - Gizli vektörlerdeki N değerinin en az %90 tam eşleşmesini güvenceye al.
4. Bonus Katmanlar:
   - MCP Sunucusu (src/mcp_server.py): Standart MCP protokolüyle "power_analysis" aracını sunacak, CLI ile aynı motoru çağıracak. CLI-MCP eşdeğerlik testi yazılacak.
   - AI Ajanı (src/agent.py): Hekimin Türkçe doğal dil sorusunu alıp parametreleri çıkaracak, MCP aracını çağırıp sonucu yorumlayacak. 10 soruluk eval setinde doğrulanacak ve logs/agent_calls.jsonl'e kayıt düşecek.
```
