"""
Unit tests for ANOVA One-Way Calculation Engine
File: tests/test_engine.py
"""

import pytest
import math
from src.engine import AnovaOneWayEngine, EngineError


def test_apriori_public_vector():
    """CONTRACT.md Bölüm 9'daki açık anova-oneway/a-priori vektörü doğrulaması."""
    res = AnovaOneWayEngine.calculate("a-priori", {
        "f": 0.25,
        "alpha": 0.05,
        "power": 0.95,
        "groups": 5
    })
    # Beklenen: {"ncp": 19.0625, "critical_f": 2.4017397, "df1": 4, "df2": 300, "n_total": 305, "actual_power": 0.9521313}
    assert res["n_total"] == 305
    assert res["df1"] == 4
    assert res["df2"] == 300
    assert abs(res["ncp"] - 19.0625000) <= 1e-6
    assert abs(res["critical_f"] - 2.4017397) <= 1e-6
    assert abs(res["actual_power"] - 0.9521313) <= 1e-6


def test_posthoc_public_vector():
    """CONTRACT.md Bölüm 9'daki açık anova-oneway/post-hoc vektörü doğrulaması."""
    res = AnovaOneWayEngine.calculate("post-hoc", {
        "f": 0.25,
        "alpha": 0.05,
        "n_total": 100,
        "groups": 5
    })
    # Beklenen: {"ncp": 6.25, "critical_f": 2.4674936, "df1": 4, "df2": 95, "power": 0.4663312}
    assert res["df1"] == 4
    assert res["df2"] == 95
    assert abs(res["ncp"] - 6.2500000) <= 1e-6
    assert abs(res["critical_f"] - 2.4674936) <= 1e-6
    assert abs(res["power"] - 0.4663312) <= 1e-6


def test_compromise_public_vector():
    """CONTRACT.md Bölüm 9'daki açık anova-oneway/compromise vektörü doğrulaması."""
    res = AnovaOneWayEngine.calculate("compromise", {
        "f": 0.25,
        "beta_alpha_ratio": 1.0,
        "n_total": 100,
        "groups": 5
    })
    # Beklenen: {"ncp": 6.25, "critical_f": 1.4272492, "df1": 4, "df2": 95, "alpha": 0.2309247, "beta": 0.2309247, "power": 0.7690753}
    assert res["df1"] == 4
    assert res["df2"] == 95
    assert abs(res["ncp"] - 6.2500000) <= 1e-6
    assert abs(res["critical_f"] - 1.4272492) <= 1e-6
    assert abs(res["alpha"] - 0.2309247) <= 1e-6
    assert abs(res["beta"] - 0.2309247) <= 1e-6
    assert abs(res["power"] - 0.7690753) <= 1e-6


def test_criterion_public_vector():
    """CONTRACT.md Bölüm 9'daki açık anova-oneway/criterion vektörü doğrulaması."""
    res = AnovaOneWayEngine.calculate("criterion", {
        "f": 0.25,
        "power": 0.95,
        "n_total": 100,
        "groups": 5
    })
    # Beklenen: {"ncp": 6.25, "critical_f": 0.6552638, "df1": 4, "df2": 95, "alpha": 0.6245994}
    assert res["df1"] == 4
    assert res["df2"] == 95
    assert abs(res["ncp"] - 6.2500000) <= 1e-6
    assert abs(res["critical_f"] - 0.6552638) <= 1e-6
    assert abs(res["alpha"] - 0.6245994) <= 1e-6


def test_sensitivity_public_vector():
    """CONTRACT.md Bölüm 9'daki açık anova-oneway/sensitivity vektörü doğrulaması."""
    res = AnovaOneWayEngine.calculate("sensitivity", {
        "alpha": 0.05,
        "power": 0.95,
        "n_total": 100,
        "groups": 5
    })
    # Beklenen: {"ncp": 19.5245874, "critical_f": 2.4674936, "df1": 4, "df2": 95, "f": 0.4418664}
    assert res["df1"] == 4
    assert res["df2"] == 95
    assert abs(res["ncp"] - 19.5245874) <= 1e-6
    assert abs(res["critical_f"] - 2.4674936) <= 1e-6
    assert abs(res["f"] - 0.4418664) <= 1e-6


def test_three_treatment_arms_apriori():
    """3 tedavi kolu (Klinik senaryo: İlaç A, İlaç B, Plasebo)."""
    res = AnovaOneWayEngine.calculate("a-priori", {
        "f": 0.30,
        "alpha": 0.05,
        "power": 0.80,
        "groups": 3
    })
    assert res["df1"] == 2
    assert res["n_total"] % 3 == 0  # 3 kola tam bölünmeli
    assert res["actual_power"] >= 0.80
