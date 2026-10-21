"""
CLI and CONTRACT validation tests
File: tests/test_cli.py
"""

import subprocess
import json
import sys


def run_cli(args_list):
    """Executes the CLI wrapper and returns stdout, stderr, and exit_code."""
    cmd = [sys.executable, "-m", "src.cli"] + args_list
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.stdout.strip(), proc.stderr.strip(), proc.returncode


def test_cli_version():
    stdout, stderr, code = run_cli(["--version"])
    assert code == 0
    data = json.loads(stdout)
    assert data["contract_version"] == "1.0.0"
    assert "name" in data
    assert "engine" in data


def test_cli_apriori_success():
    stdout, stderr, code = run_cli([
        "--test", "anova-oneway",
        "--mode", "a-priori",
        "--f", "0.25",
        "--alpha", "0.05",
        "--power", "0.95",
        "--groups", "5"
    ])
    assert code == 0
    data = json.loads(stdout)
    assert data["n_total"] == 305
    assert data["df1"] == 4
    assert data["df2"] == 300
    assert abs(data["actual_power"] - 0.9521313) <= 1e-6


def test_cli_missing_param():
    stdout, stderr, code = run_cli([
        "--test", "anova-oneway",
        "--mode", "a-priori",
        "--f", "0.25",
        "--alpha", "0.05"
        # power and groups missing
    ])
    assert code == 2
    data = json.loads(stdout)
    assert data["code"] == "MISSING_PARAM"
    assert "error" in data


def test_cli_unknown_param():
    stdout, stderr, code = run_cli([
        "--test", "anova-oneway",
        "--mode", "a-priori",
        "--f", "0.25",
        "--alpha", "0.05",
        "--power", "0.95",
        "--groups", "5",
        "--tails", "2"  # ANOVA does not have tails parameter
    ])
    assert code == 2
    data = json.loads(stdout)
    assert data["code"] == "UNKNOWN_PARAM"


def test_cli_out_of_range():
    stdout, stderr, code = run_cli([
        "--test", "anova-oneway",
        "--mode", "a-priori",
        "--f", "0.25",
        "--alpha", "1.5",  # alpha > 1
        "--power", "0.95",
        "--groups", "5"
    ])
    assert code == 2
    data = json.loads(stdout)
    assert data["code"] == "OUT_OF_RANGE"
    assert data["field"] == "alpha"


def test_cli_inconsistent():
    stdout, stderr, code = run_cli([
        "--test", "anova-oneway",
        "--mode", "a-priori",
        "--f", "0.25",
        "--alpha", "0.05",
        "--power", "0.03",  # power <= alpha
        "--groups", "5"
    ])
    assert code == 2
    data = json.loads(stdout)
    assert data["code"] == "INCONSISTENT"
    assert data["field"] == "power"


def test_cli_unsupported_test():
    stdout, stderr, code = run_cli([
        "--test", "unknown-test",
        "--mode", "a-priori"
    ])
    assert code == 2
    data = json.loads(stdout)
    assert data["code"] == "UNSUPPORTED"
