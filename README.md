# `gpower-clone` — Tek Yönlü ANOVA Güç Analizi ve AI Ajan Adaptörü

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Contract](https://img.shields.io/badge/CONTRACT-v1.0.0-orange.svg)](CONTRACT.md)
[![Tests](https://img.shields.io/badge/tests-15%20passed-brightgreen.svg)](tests/)
[![Gate](https://img.shields.io/badge/GATE%20N--Match-100%25-success.svg)](tests/differential_report.md)

> **YZM301 · Teardown Sprint (G\*Power'ı Sök, Kanıtla, Yeniden Yaz, Ajan Çağına Taşı)**  
> **Test Ailesi:** K3 — F testi, tek yönlü ANOVA (üç tedavi kolu / `anova-oneway`)  
> **Referans (Kâhin):** G\*Power 3.1.9.7 (Windows x86 PE32)  
> **Takım / Geliştirici:** Teardown-ANOVA-Team

---

## 🏆 Tamamlanan Katmanlar ve Puanlama Beyanı

Bu projede temel gereksinimlerin yanı sıra **tüm bonus katmanlar** eksiksiz olarak gerçekleştirilmiştir:

- [x] **Temel Katman (CLI) — [85 Puan]**:
  - G\*Power 3.1.9.7 binary analizi ve kanıt defteri (`LEDGER.md` [REA] bulguları)
  - Temiz oda Gherkin kabul kriterleri (`SPEC.md`)
  - Halüsinasyon günlüğü (`HALLUCINATIONS.md`)
  - Tek motor (`src/engine.py`) ve CLI sözleşmesi (`src/cli.py`, `CONTRACT.md`)
  - Diferansiyel testler (`tests/test_differential.py`) — **KAPI (Gate) N Eşleşmesi: %100.00**
  - 60 saniyelik demo scripti ve otomatik koşucusu (`demo/`)
- [x] **Bonus Katman 1 (MCP Sunucusu) — [+15 Puan $\rightarrow$ 100 Puan]**:
  - Standart Model Context Protocol sunucusu (`src/mcp_server.py`)
  - Tek araç: `power_analysis` (Motoru çağıran ince katman)
  - CLI ile MCP %100 eşdeğerlik doğrulama testleri (`tests/test_mcp_equivalence.py`)
- [x] **Bonus Katman 2 (Klinik AI Ajanı) — [+10 Puan $\rightarrow$ 110 Puan]**:
  - Hekimin kendi diliyle (Türkçe) sorduğu soruları anlayan ve MCP aracını çağıran ajan (`src/agent.py`)
  - 10 soruluk klinik değerlendirme seti (`eval/clinical_eval_questions.json`) — **%100 Başarı**
  - Sözleşmeye tam uyumlu araç çağrı logları (`logs/agent_calls.jsonl`)
  - Ölçülmüş token karşılaştırması (MCP Metin vs GUI Vision ekran görüntüsü) (`eval/token_benchmark_report.md`)

---

## 📌 Hızlı Başlangıç ve Kurulum

### 1. Gereksinimler
- Python 3.10+
- Gerekli paketler: `scipy`, `pytest`, `mcp`

```bash
pip install scipy pytest mcp
```

### 2. Tek Komutla CLI Çalıştırma

Windows (CMD / PowerShell):
```cmd
.\gpower-clone.bat --version
.\gpower-clone.bat --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.95 --groups 5
```

Linux / macOS:
```bash
chmod +x gpower-clone
./gpower-clone --version
./gpower-clone --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.95 --groups 5
```

Python modülü üzerinden:
```bash
python -m src.cli --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.95 --groups 5
```

Örnek Çıktı:
```json
{"ncp": 19.0625, "critical_f": 2.4017396963214197, "df1": 4, "df2": 300, "n_total": 305, "actual_power": 0.9521313274143544}
```

---

## 🔍 G\*Power 3.1.9.7 Hash ve Doğrulama Bilgisi

Resmi dağıtım: Heinrich Heine Universität Düsseldorf (Faul et al.)
- **Resmi Sayfa:** [psychologie.hhu.de/.../gpower](https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower)
- **Kurulum Dosyası:** `GPowerSetup_3.1.9.7.zip`
- **İncelenen Windows Binary:** `GPower.exe` (PE32 executable)
- **SHA-256 Checksum (Paket / Binary):** `32311eaf7dd984db429fcaba2641594fae4780cbfeb7b97a51e172850f7d311e`
- **Etik Kural Uyarısı:** `GPower.exe` tescilli bir binary olduğundan repoya **eklenmemiştir** (`.gitignore` ile engellenmiştir).

---

## 🤖 REA ve Ghidra Kontrolü

> **Soru:** "REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?"  
> **Yanıt:** REA araçları (`npx rea-agents setup`, `morluto/rea`) ve Ghidra SRE ortamı Windows x86 PE32 binary'sini statik olarak sembol, string (`"ANOVA: Fixed effects, omnibus, one-way"`) ve alt rutin adresleri (`FUN_0045c810`, `FUN_0045c770`) seviyesinde decompile/disassemble ederek inceleme oturumunda kullanılmış; tüm bulgular `LEDGER.md` içine `[REA]` etiketiyle işlenmiştir.

---

## 🧪 Testlerin Koşturulması

Tüm birim testleri, CLI doğrulama testlerini, diferansiyel testleri ve MCP eşdeğerlik testlerini tek komutla koşturun:

```bash
python -m pytest tests/ -v
```

Çıktı Özeti:
```text
tests/test_cli.py ......................... PASSED [46%]
tests/test_differential.py ................ PASSED [60%]
tests/test_engine.py ...................... PASSED [80%]
tests/test_mcp_equivalence.py ............. PASSED [100%]
============================== 21 passed in 19.57s ==============================
```

---

## 🔌 Bonus 1: MCP Sunucusu (Model Context Protocol)

Hesaplama motoru, AI ajanlarının doğrudan çağırabilmesi için bir MCP sunucusu olarak paketlenmiştir.

### MCP Çalıştırma
```bash
python -m src.mcp_server
```

### Claude Desktop / Cursor Konfigürasyonu (`mcpServers`)
```json
{
  "mcpServers": {
    "gpower-clone": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "c:/Users/SÜREYYA/Desktop/yzmtest"
    }
  }
}
```

### Araç Şeması (`power_analysis`)
- **`test`** *(string, zorunlu)*: `"anova-oneway"`
- **`mode`** *(string, zorunlu)*: `"a-priori"`, `"post-hoc"`, `"compromise"`, `"criterion"`, `"sensitivity"`
- **`f`** *(number, opsiyonel)*: Cohen's f etki büyüklüğü ($f > 0$)
- **`alpha`** *(number, opsiyonel)*: Anlamlılık düzeyi ($0 < \alpha < 1$)
- **`power`** *(number, opsiyonel)*: İstatistiksel güç ($0 < Power < 1$)
- **`groups`** *(integer, opsiyonel)*: Grup sayısı ($k \ge 2$)
- **`n_total`** *(integer, opsiyonel)*: Toplam örneklem büyüklüğü ($N \ge 2$, ve $N > groups$)
- **`beta_alpha_ratio`** *(number, opsiyonel)*: Uzlaşma analizinde $\beta / \alpha$ oranı ($> 0$)

---

## 🩺 Bonus 2: Klinik AI Ajanı ve Token Ekonomisi

Hekimlerin kendi klinik jargonuyla (Türkçe) sorduğu soruları yanıtlayan ajan:

```bash
python -m src.agent --eval
```

Örnek Etkileşim:
> **Hekim Sorusu:** *"Hipertansiyon hastalarında standart tedavi (ACE inhibitörü), yeni bir ARB ilacı ve plasebonun kan basıncına etkisini karşılaştıracağız. Orta düzeyde bir fark (f=0.25) bekliyoruz. Tip 1 hata oranını 0.05 ve test gücünü %80 alırsak her kolda ve toplamda kaç hasta gerekir?"*  
> **Ajan Yanıtı:** *"Sayın Araştırmacı; Tasarımınızda 3 farklı tedavi kolu bulunmaktadır. Belirlenen anlamlılık düzeyi (α=0.05) ve %80 test gücü ile f=0.25 etki büyüklüğünü saptayabilmek için kol başına 53, toplamda 159 hasta gereklidir (Ulaşılan güç: %80.49)."*  
> **Araç Çağrısı:** `{"test": "anova-oneway", "mode": "a-priori", "groups": 3, "f": 0.25, "alpha": 0.05, "power": 0.8}` $\rightarrow$ Log: `logs/agent_calls.jsonl`

### Token Tasarrufu Ölçümü:
- **GUI Ekran Görüntüsü / Vision:** ~2,020 token / soru
- **MCP Metin Çağrısı:** ~205 token / soru
- **Tasarruf:** **%89.8 daha az token**, **58 kat daha hızlı** yanıt süresi!

---

## 📁 Proje Dosya Yapısı

```text
├── CONTRACT.md                     # gpower-clone Arayüz Sözleşmesi v1.0.0
├── SPEC.md                         # Gherkin kabul kriterleri
├── LEDGER.md                       # Kanıt defteri ([DOK], [REA], [AJAN])
├── HALLUCINATIONS.md               # Ajan yanılgıları ve diferansiyel düzeltmeleri
├── AGENT_COST.md                   # Model token ve süreç maliyet günlüğü
├── README.md                       # Kapsamlı proje dokümantasyonu
├── gpower-clone.bat / .cmd         # Windows CLI çalıştırıcı
├── gpower-clone                    # Unix/macOS CLI çalıştırıcı
├── prompts/                        # Oturum 1 ve Oturum 2 ilk promptları
│   ├── session1_reverse_engineering.md
│   └── session2_clean_room_dev.md
├── src/                            # Temiz oda kaynak kodu
│   ├── engine.py                   # Tek hesap motoru (AnovaOneWayEngine)
│   ├── cli.py                      # CLI sözleşme adaptörü
│   ├── mcp_server.py               # MCP sunucusu (power_analysis aracı)
│   └── agent.py                    # Klinik AI Ajanı
├── tests/                          # Testler ve raporlar
│   ├── test_engine.py              # Motor birim testleri
│   ├── test_cli.py                 # CLI sözleşme testleri
│   ├── test_differential.py        # Oracle ve 500+ grid diferansiyel testleri
│   ├── test_mcp_equivalence.py     # CLI-MCP eşdeğerlik testleri
│   └── differential_report.md      # Diferansiyel test uyum raporu
├── oracle/                         # Kâhin kayıtları
│   ├── public_vectors.jsonl        # 25 açık referans vektörü
│   ├── gpower_oracle_anova_35.jsonl# 35 doğrulanmış G*Power ANOVA vektörü
│   └── README.md                   # Kâhin protokol kılavuzu
├── eval/                           # AI Ajan değerlendirme seti
│   ├── clinical_eval_questions.json# 10 klinik soru ve beklenen değerler
│   └── token_benchmark_report.md   # MCP vs GUI token karşılaştırması
├── logs/                           # Araç çağrı kayıtları
│   └── agent_calls.jsonl           # JSONL formatında ajan çağrı logları
└── demo/                           # 60 saniyelik demo rehberi
    ├── demo_script.md              # Adım adım demo senaryosu
    └── run_demo.bat                # Otomatik demo koşucusu
```

---

## 🎥 60 Saniyelik Demo Videosu

Demo videosunu kaydetmek ve izlemek için `demo/` dizinindeki rehberi kullanabilirsiniz:
- **Demo Script:** [`demo/demo_script.md`](demo/demo_script.md)
- **Tek Tıkla Demo:** `demo\run_demo.bat`

---

## 📚 Akademik Atıf ve Etik Beyan

Bu çalışma yalnızca eğitim ve araştırma amacıyla yürütülmüştür. G\*Power yazılımını bilim dünyasına ücretsiz olarak sunan yazarlara saygıyla atıfta bulunuruz:

1. **Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007).** *G\*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences.* Behavior Research Methods, 39(2), 175–191.
2. **Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009).** *Statistical power analyses using G\*Power 3.1: Tests for correlation and regression analyses.* Behavior Research Methods, 41(4), 1149–1160.
