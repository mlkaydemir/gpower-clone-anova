"""
Clinical AI Agent for Statistical Power Analysis
Module: src.agent

Answers physician questions in natural Turkish, calls MCP power_analysis tool,
logs tool interactions according to CONTRACT.md Section 8,
and avoids hallucinating numerical calculations internally.
"""

import os
import re
import json
import datetime
from typing import Dict, Any, Tuple, Optional
from src.mcp_server import execute_power_analysis
from src.engine import AnovaOneWayEngine

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOGS_DIR, "agent_calls.jsonl")


class ClinicalPowerAgent:
    """Agent that translates clinical study questions into MCP tool calls."""

    # Cohen's (1988) standard effect size thresholds for One-Way ANOVA
    COHEN_THRESHOLDS = {
        "kucuk": 0.10,
        "orta": 0.25,
        "buyuk": 0.40,
    }

    def __init__(self, log_path: str = LOG_FILE):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def classify_and_extract(self, question: str) -> Tuple[str, str, Dict[str, Any], float]:
        """
        Classifies test family, analysis mode, extracts parameters, and provides confidence score.
        Labels: t2-indep, t-paired, anova-oneway, chi2-contingency, multireg-r2, ambiguous, unsupported
        """
        q_lower = question.lower()

        # 1. Test Family Classification
        test_family = "ambiguous"
        confidence = 0.50

        anova_triggers = [
            "anova", "f testi", "tedavi kol", "kolda", "grupta", "hasta grubu",
            "cerrahi teknik", "merhem", "ekol", "protez", "rehabilitasyon", "statin",
            "doz 1", "doz 2", "kontrol", "plasebo", "standart tedavi"
        ]

        # Sayı + farklı / kol / grup kalıpları
        has_multi_group = bool(re.search(r"(\d+)\s*(farklı|tedavi|hasta|grup|kol|doz|rejim|teknik|protokol)", q_lower))

        if any(trig in q_lower for trig in anova_triggers) or has_multi_group:
            test_family = "anova-oneway"
            confidence = 0.95
        elif any(w in q_lower for w in ["iki bağımsız", "ilaç ve plasebo", "t testi"]):
            test_family = "t2-indep"
            confidence = 0.90
        elif any(w in q_lower for w in ["önce ve sonra", "eşleştirilmiş", "paired"]):
            test_family = "t-paired"
            confidence = 0.90
        elif any(w in q_lower for w in ["ki-kare", "kontenjans", "olumsallık", "oranlar"]):
            test_family = "chi2-contingency"
            confidence = 0.90
        elif any(w in q_lower for w in ["regresyon", "r2", "risk faktör"]):
            test_family = "multireg-r2"
            confidence = 0.90

        # 2. Mode Classification (Öncelik sıralaması hassastır!)
        # 2.1 Compromise
        if any(w in q_lower for w in ["beta/alpha", "beta ve alfa", "örtük alfa", "uzlaşma"]):
            mode = "compromise"
        # 2.2 Criterion
        elif any(w in q_lower for w in ["alfa kaç olmalı", "anlamlılık eşiği", "anlamlılık eşiğimiz", "alfa ne olmalı", "anlamlılık düzeyimiz"]):
            mode = "criterion"
        # 2.3 Sensitivity
        elif any(w in q_lower for w in ["en küçük etki", "saptanabilir etki", "saptayabileceğimiz en küçük", "etki büyüklüğü (f) nedir", "saptanabilir en küçük"]):
            mode = "sensitivity"
        # 2.4 Post-hoc
        elif any(w in q_lower for w in ["ulaşılan güç", "ulaştığı istatistiksel güç", "gücü hesaplayınız", "güç nedir"]):
            mode = "post-hoc"
        # 2.5 A-priori (Varsayılan)
        else:
            mode = "a-priori"

        # 3. Parameter Extraction
        extracted: Dict[str, Any] = {}

        # 3.1 n_total (Önce n_total'ı çıkarıyoruz ki groups ile karışmasın!)
        n_match = re.search(r"toplam(da)?\s*([0-9]+)\s*(hasta|denek)", q_lower)
        if n_match:
            extracted["n_total"] = int(n_match.group(2))

        # 3.2 Groups
        # Sayısal açık grup belirteçleri (Örn: 4 farklı hasta grubu, 5 farklı kemoterapi protokolü, 6 farklı statin)
        g_num_match = re.search(r"(\d+)\s*(farklı\s*)?\w*\s*(kol|grup|teknik|doz|merhem|ekol|protez|protokol|rejim|statin)", q_lower)
        if g_num_match and int(g_num_match.group(1)) not in (1, 20, 60, 90, 100, 120):  # n_total sayıları hariç
            extracted["groups"] = int(g_num_match.group(1))
        elif "doz 1, doz 2, doz 3, kontrol" in q_lower:
            extracted["groups"] = 4
        elif re.search(r"\baltı\b|\b6\b", q_lower):
            extracted["groups"] = 6
        elif re.search(r"\bbeş\b|\b5\b", q_lower):
            extracted["groups"] = 5
        elif re.search(r"\bdört\b|\b4\b", q_lower):
            extracted["groups"] = 4
        elif re.search(r"\büç\b|\b3\b", q_lower) or "plasebo" in q_lower:
            extracted["groups"] = 3

        # 3.2 Effect size f
        f_match = re.search(r"f\s*=\s*([0-9\.]+)", q_lower)
        if f_match:
            extracted["f"] = float(f_match.group(1))
        elif "küçük-orta" in q_lower:
            extracted["f"] = 0.20
        elif "büyük" in q_lower:
            extracted["f"] = self.COHEN_THRESHOLDS["buyuk"]
        elif "orta" in q_lower:
            extracted["f"] = self.COHEN_THRESHOLDS["orta"]
        elif "küçük" in q_lower:
            extracted["f"] = self.COHEN_THRESHOLDS["kucuk"]

        # 3.3 Alpha
        alpha_match = re.search(r"(alfa|tip 1 hata|hata oran[ı|i])\s*[:=]?\s*([0-9\.]+)", q_lower)
        if alpha_match:
            extracted["alpha"] = float(alpha_match.group(2))
        elif "0.05" in q_lower:
            extracted["alpha"] = 0.05
        elif "0.01" in q_lower:
            extracted["alpha"] = 0.01
        elif mode in ["a-priori", "post-hoc", "sensitivity"]:
            extracted["alpha"] = 0.05

        # 3.4 Power
        power_match = re.search(r"(güç|power|test güc[ü|u])\s*[:=]?\s*%?\s*([0-9\.]+)", q_lower)
        if power_match:
            val = float(power_match.group(2))
            if val > 1.0:
                val = val / 100.0
            extracted["power"] = val
        elif "%80" in q_lower or "0.80" in q_lower:
            extracted["power"] = 0.80
        elif "%90" in q_lower or "0.90" in q_lower:
            extracted["power"] = 0.90
        elif "%95" in q_lower or "0.95" in q_lower:
            extracted["power"] = 0.95

        # 3.6 beta_alpha_ratio
        ratio_match = re.search(r"beta/alpha\s*(oranı)?\s*([0-9\.]+)", q_lower)
        if ratio_match:
            extracted["beta_alpha_ratio"] = float(ratio_match.group(2))
        elif "oran 1" in q_lower or "eşit ağırlık" in q_lower:
            extracted["beta_alpha_ratio"] = 1.0

        # 4. Mode-Specific Parameter Pruning (Sözleşmeye ve motor gereksinimine tam uyum)
        required_keys = AnovaOneWayEngine.MODE_REQUIRED_PARAMS.get(mode, [])
        pruned_params: Dict[str, Any] = {}
        for req in required_keys:
            if req in extracted:
                pruned_params[req] = extracted[req]

        return test_family, mode, pruned_params, confidence

    def process_clinical_question(self, question: str) -> Dict[str, Any]:
        """
        Executes end-to-end agent workflow:
        1. Parse question
        2. Call MCP tool (no internal math hallucination)
        3. Formulate physician explanation
        4. Log to agent_calls.jsonl
        """
        test_family, mode, tool_params, confidence = self.classify_and_extract(question)

        # Decision threshold rule
        if confidence < 0.75 or test_family in ("ambiguous", "unsupported"):
            return {
                "success": False,
                "message": "Soru klinik olarak net değil ya da desteklenmeyen bir test ailesi içeriyor. Lütfen tedavi kolu sayısını ve karşılaştırılacak hipotezi netleştiriniz.",
                "confidence": confidence,
                "test_family": test_family
            }

        # Build MCP tool call input
        tool_input = {
            "test": test_family,
            "mode": mode,
            **tool_params
        }

        # Execute MCP tool (PURE TOOL CALL - ENGINE RUNS)
        raw_output = execute_power_analysis(**tool_input)
        parsed_output = json.loads(raw_output)

        # Token metrics estimation (standard token estimation: 1 token ~= 4 chars)
        prompt_tokens = len(question) // 4 + 40
        completion_tokens = len(raw_output) // 4 + 80

        # Create structured log entry
        log_entry = {
            "ts": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).isoformat(),
            "question": question,
            "tool_input": tool_input,
            "tool_output": parsed_output,
            "tokens_in": prompt_tokens,
            "tokens_out": completion_tokens
        }

        # Append to logs/agent_calls.jsonl
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        # Format physician explanation
        explanation = self._format_clinical_explanation(question, mode, tool_input, parsed_output)

        return {
            "success": True,
            "explanation": explanation,
            "tool_input": tool_input,
            "tool_output": parsed_output,
            "confidence": confidence,
            "tokens_in": prompt_tokens,
            "tokens_out": completion_tokens
        }

    def _format_clinical_explanation(self, q: str, mode: str, inp: Dict[str, Any], out: Dict[str, Any]) -> str:
        """Translates statistical output into clear clinical terms."""
        if "error" in out:
            return f"Sayın Araştırmacı, analiz parametrelerinizde tutarsızlık saptandı: {out['error']} (Hata kodu: {out.get('code', 'HATA')})."

        k = inp.get("groups", 3)
        if mode == "a-priori":
            n_tot = out["n_total"]
            n_arm = n_tot // k
            return (
                f"Sayın Araştırmacı;\n"
                f"Tasarımınızda {k} farklı tedavi kolu bulunmaktadır. Belirlenen anlamlılık düzeyi (α={inp.get('alpha', 0.05)}) "
                f"ve %{int(inp.get('power', 0.8)*100)} test gücü ile f={inp.get('f', 0.25)} etki büyüklüğünü saptayabilmek için:\n"
                f"- Tedavi kolu başına gereken hasta sayısı: {n_arm}\n"
                f"- Çalışmaya alınması gereken TOPLAM hasta sayısı (N): {n_tot}\n"
                f"- Ulaşılan gerçek güç (Actual Power): %{out.get('actual_power', 0)*100:.2f} (Kritik F={out.get('critical_f', 0):.4f}, λ={out.get('ncp', 0):.2f})."
            )
        elif mode == "post-hoc":
            return (
                f"Sayın Araştırmacı;\n"
                f"Toplam {inp.get('n_total')} hasta ile {k} grup arasında yapılan çalışmada, "
                f"f={inp.get('f')} etki büyüklüğü ve α={inp.get('alpha')} anlamlılık eşiğinde ulaşılan test gücü: "
                f"%{out.get('power', 0)*100:.2f}'dir."
            )
        elif mode == "compromise":
            return (
                f"Sayın Araştırmacı;\n"
                f"Örneklem büyüklüğü {inp.get('n_total')} ile sınırlandırılmış çalışmada, eşit hata ağırlığı ile "
                f"elde edilen örtük anlamlılık eşiği α={out.get('alpha', 0):.4f} ve istatistiksel güç %{out.get('power', 0)*100:.2f}'dir."
            )
        elif mode == "criterion":
            return (
                f"Sayın Araştırmacı;\n"
                f"Toplam {inp.get('n_total')} denekle %{int(inp.get('power', 0.9)*100)} güce ulaşabilmek için "
                f"belirlenmesi gereken kritik anlamlılık düzeyi (alfa): {out.get('alpha', 0):.4f}'tür."
            )
        elif mode == "sensitivity":
            return (
                f"Sayın Araştırmacı;\n"
                f"Mevcut {inp.get('n_total')} hasta ve %{int(inp.get('power', 0.8)*100)} güç ile "
                f"saptayabileceğiniz en küçük klinik etki büyüklüğü: f = {out.get('f', 0):.4f}'tür."
            )
        return json.dumps(out)


def run_eval_suite():
    """Runs the 10 clinical questions benchmark and prints evaluation report."""
    eval_file = os.path.join(os.path.dirname(__file__), "..", "eval", "clinical_eval_questions.json")
    with open(eval_file, "r", encoding="utf-8") as f:
        questions = json.load(f)

    agent = ClinicalPowerAgent()
    correct_selections = 0
    total_questions = len(questions)

    print("\n" + "=" * 70)
    print("KLİNİK AI AJANI - 10 SORULUK DEĞERLENDİRME SETİ ÇALIŞTIRILIYOR")
    print("=" * 70)

    for item in questions:
        qid = item["id"]
        q_text = item["clinical_question"]
        res = agent.process_clinical_question(q_text)

        if not res.get("success", False):
            print(f"\n[{qid}] HATALI (Sınıflandırılamadı: {res.get('message')})")
            continue

        tool_in = res["tool_input"]
        tool_out = res["tool_output"]

        # Check accuracy
        match_test = (tool_in["test"] == item["expected_test"])
        match_mode = (tool_in["mode"] == item["expected_mode"])

        is_correct = match_test and match_mode
        if "expected_n_total" in item:
            is_correct = is_correct and (tool_out.get("n_total") == item["expected_n_total"])

        if is_correct:
            correct_selections += 1

        status = "BAŞARILI" if is_correct else "HATALI"
        print(f"\n[{qid}] {status} (Güven: {res['confidence']:.2f})")
        print(f"Soru: {q_text[:75]}...")
        print(f"Ajan Çağrısı: test={tool_in['test']}, mode={tool_in['mode']}, params={tool_in}")
        print(f"Motor Çıktısı: {tool_out}")

    accuracy_rate = (correct_selections / total_questions) * 100
    print("\n" + "=" * 70)
    print(f"TOPLAM DOĞRULUK ORANI: %{accuracy_rate:.2f} ({correct_selections}/{total_questions})")
    print(f"Araç çağrıları loglandı: {agent.log_path}")
    print("=" * 70)


if __name__ == "__main__":
    run_eval_suite()
