"""
MCP and CLI Equivalence Tests
File: tests/test_mcp_equivalence.py

Verifies CONTRACT.md Section 7:
CLI and MCP outputs must be 100% equivalent for identical inputs.
"""

import json
import subprocess
import sys
import pytest
from src.mcp_server import execute_power_analysis


def run_cli_raw(args_list):
    cmd = [sys.executable, "-m", "src.cli"] + args_list
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.stdout.strip(), proc.returncode


def test_mcp_cli_equivalence_apriori():
    """Verifies public vector a-priori equivalence."""
    cli_stdout, cli_code = run_cli_raw([
        "--test", "anova-oneway",
        "--mode", "a-priori",
        "--f", "0.25",
        "--alpha", "0.05",
        "--power", "0.95",
        "--groups", "5"
    ])
    assert cli_code == 0

    mcp_output = execute_power_analysis(
        test="anova-oneway",
        mode="a-priori",
        f=0.25,
        alpha=0.05,
        power=0.95,
        groups=5
    )

    cli_json = json.loads(cli_stdout)
    mcp_json = json.loads(mcp_output)

    assert cli_json == mcp_json
    assert cli_json["n_total"] == 305


def test_mcp_cli_equivalence_posthoc():
    """Verifies public vector post-hoc equivalence."""
    cli_stdout, cli_code = run_cli_raw([
        "--test", "anova-oneway",
        "--mode", "post-hoc",
        "--f", "0.25",
        "--alpha", "0.05",
        "--n_total", "100",
        "--groups", "5"
    ])
    assert cli_code == 0

    mcp_output = execute_power_analysis(
        test="anova-oneway",
        mode="post-hoc",
        f=0.25,
        alpha=0.05,
        n_total=100,
        groups=5
    )

    cli_json = json.loads(cli_stdout)
    mcp_json = json.loads(mcp_output)
    assert cli_json == mcp_json


def test_mcp_cli_equivalence_compromise():
    """Verifies public vector compromise equivalence."""
    cli_stdout, cli_code = run_cli_raw([
        "--test", "anova-oneway",
        "--mode", "compromise",
        "--f", "0.25",
        "--beta_alpha_ratio", "1.0",
        "--n_total", "100",
        "--groups", "5"
    ])
    assert cli_code == 0

    mcp_output = execute_power_analysis(
        test="anova-oneway",
        mode="compromise",
        f=0.25,
        beta_alpha_ratio=1.0,
        n_total=100,
        groups=5
    )

    cli_json = json.loads(cli_stdout)
    mcp_json = json.loads(mcp_output)
    assert cli_json == mcp_json


def test_mcp_cli_equivalence_criterion():
    """Verifies public vector criterion equivalence."""
    cli_stdout, cli_code = run_cli_raw([
        "--test", "anova-oneway",
        "--mode", "criterion",
        "--f", "0.25",
        "--power", "0.95",
        "--n_total", "100",
        "--groups", "5"
    ])
    assert cli_code == 0

    mcp_output = execute_power_analysis(
        test="anova-oneway",
        mode="criterion",
        f=0.25,
        power=0.95,
        n_total=100,
        groups=5
    )

    cli_json = json.loads(cli_stdout)
    mcp_json = json.loads(mcp_output)
    assert cli_json == mcp_json


def test_mcp_cli_equivalence_sensitivity():
    """Verifies public vector sensitivity equivalence."""
    cli_stdout, cli_code = run_cli_raw([
        "--test", "anova-oneway",
        "--mode", "sensitivity",
        "--alpha", "0.05",
        "--power", "0.95",
        "--n_total", "100",
        "--groups", "5"
    ])
    assert cli_code == 0

    mcp_output = execute_power_analysis(
        test="anova-oneway",
        mode="sensitivity",
        alpha=0.05,
        power=0.95,
        n_total=100,
        groups=5
    )

    cli_json = json.loads(cli_stdout)
    mcp_json = json.loads(mcp_output)
    assert cli_json == mcp_json


def test_mcp_cli_equivalence_error_handling():
    """Verifies error responses are equivalent in CLI and MCP."""
    # Inconsistent power <= alpha
    cli_stdout, cli_code = run_cli_raw([
        "--test", "anova-oneway",
        "--mode", "a-priori",
        "--f", "0.25",
        "--alpha", "0.05",
        "--power", "0.03",
        "--groups", "5"
    ])
    assert cli_code == 2

    mcp_output = execute_power_analysis(
        test="anova-oneway",
        mode="a-priori",
        f=0.25,
        alpha=0.05,
        power=0.03,
        groups=5
    )

    cli_json = json.loads(cli_stdout)
    mcp_json = json.loads(mcp_output)
    assert cli_json["code"] == mcp_json["code"] == "INCONSISTENT"
    assert cli_json["field"] == mcp_json["field"] == "power"
