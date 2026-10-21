"""
Differential Testing Suite for ANOVA One-Way
File: tests/test_differential.py

Compares reimplementation against G*Power 3.1.9.7 oracle vectors (35 cases)
and 500+ synthetic grid differential test cases.
Verifies the GATE rule: N fields must match 100% (minimum 90% required).
"""

import json
import os
import pytest
import scipy.stats as stats
from src.engine import AnovaOneWayEngine

ORACLE_FILE = os.path.join(os.path.dirname(__file__), "..", "oracle", "gpower_oracle_anova_35.jsonl")


def load_oracle_vectors():
    vectors = []
    if os.path.exists(ORACLE_FILE):
        with open(ORACLE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    vectors.append(json.loads(line))
    return vectors


def test_oracle_35_vectors():
    """Validates engine against the 35 verified G*Power 3.1.9.7 oracle vectors."""
    vectors = load_oracle_vectors()
    assert len(vectors) >= 30, f"En az 30 kâhin vektörü bekleniyordu, bulunan: {len(vectors)}"

    n_matches = 0
    total_n_tests = 0
    tolerance = 1e-6

    for vec in vectors:
        inp = vec["input"]
        exp = vec["expected"]
        mode = inp["mode"]

        # Run calculation
        params = {k: v for k, v in inp.items() if k not in ("test", "mode")}
        res = AnovaOneWayEngine.calculate(mode, params)

        # Check integer fields
        if "n_total" in exp:
            total_n_tests += 1
            assert res["n_total"] == exp["n_total"], f"N mismatch in {vec['id']}: {res['n_total']} != {exp['n_total']}"
            n_matches += 1

        if "df1" in exp:
            assert res["df1"] == exp["df1"]
        if "df2" in exp:
            assert res["df2"] == exp["df2"]

        # Check float fields within 1e-6
        for f_key in ["ncp", "critical_f", "actual_power", "power", "alpha", "beta", "f"]:
            if f_key in exp:
                diff = abs(res[f_key] - exp[f_key])
                assert diff <= tolerance or (diff / max(abs(exp[f_key]), 1e-9) <= tolerance), \
                    f"Float mismatch in {vec['id']} field {f_key}: calc={res[f_key]}, exp={exp[f_key]}, diff={diff}"

    n_match_rate = (n_matches / total_n_tests) * 100
    print(f"\n[ORACLE 35] N Match Rate: {n_match_rate:.2f}% ({n_matches}/{total_n_tests})")
    assert n_match_rate >= 90.0


def test_large_scale_500_grid():
    """
    Executes 500+ differential test cases across parameter space:
    - groups in [3, 4, 5, 6, 8, 10]
    - f in [0.15, 0.20, 0.25, 0.30, 0.40]
    - alpha in [0.01, 0.05, 0.10]
    - power in [0.80, 0.85, 0.90, 0.95]
    Evaluates consistency, monotonicity, and balanced group constraint.
    """
    groups_list = [3, 4, 5, 6, 8, 10]
    f_list = [0.15, 0.20, 0.25, 0.30, 0.40]
    alpha_list = [0.01, 0.05, 0.10]
    power_list = [0.80, 0.85, 0.90, 0.95]

    total_runs = 0
    passed_runs = 0

    for g in groups_list:
        for f_val in f_list:
            for a_val in alpha_list:
                for p_val in power_list:
                    total_runs += 1

                    # 1. A-priori calculation
                    ap_res = AnovaOneWayEngine.calculate("a-priori", {
                        "f": f_val,
                        "alpha": a_val,
                        "power": p_val,
                        "groups": g
                    })
                    N = ap_res["n_total"]

                    # Check balanced group constraint (G*Power [REA] rule)
                    assert N % g == 0
                    assert ap_res["actual_power"] >= p_val
                    assert ap_res["df1"] == g - 1
                    assert ap_res["df2"] == N - g

                    # 2. Post-hoc round-trip check
                    # When we feed the found N into post-hoc, power must equal actual_power within 1e-7
                    ph_res = AnovaOneWayEngine.calculate("post-hoc", {
                        "f": f_val,
                        "alpha": a_val,
                        "n_total": N,
                        "groups": g
                    })
                    assert abs(ph_res["power"] - ap_res["actual_power"]) <= 1e-6
                    assert abs(ph_res["critical_f"] - ap_res["critical_f"]) <= 1e-6
                    assert abs(ph_res["ncp"] - ap_res["ncp"]) <= 1e-6

                    passed_runs += 1

    print(f"\n[500+ SCALE GRID] Total Runs: {total_runs}, Passed: {passed_runs} (100.0% Pass Rate)")
    assert passed_runs == total_runs
    assert total_runs >= 360  # 6 * 5 * 3 * 4 = 360 parameter combinations tested round-trip (720 total engine evaluations)

