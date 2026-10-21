"""
Model Context Protocol (MCP) Server for G*Power Clone
Module: src.mcp_server

Exposes the 'power_analysis' tool according to CONTRACT.md Section 7.
Wraps the exact same calculation engine (src.engine) without logic duplication.
"""

import json
from typing import Optional, Dict, Any
from mcp.server.mcpserver import MCPServer
from src.engine import AnovaOneWayEngine, EngineError

# Initialize MCP Server instance
mcp_server = MCPServer("gpower-clone-mcp")


def execute_power_analysis(
    test: str,
    mode: str,
    f: Optional[float] = None,
    alpha: Optional[float] = None,
    power: Optional[float] = None,
    groups: Optional[int] = None,
    n_total: Optional[int] = None,
    beta_alpha_ratio: Optional[float] = None,
) -> str:
    """
    Core executor that calls AnovaOneWayEngine.
    Returns exact single-line JSON string identical to CLI stdout.
    """
    # Test validation
    if test != AnovaOneWayEngine.TEST_ID:
        err = {
            "error": f"Desteklenmeyen test ailesi: '{test}'. Bu sunucu yalnızca '{AnovaOneWayEngine.TEST_ID}' destekler.",
            "code": "UNSUPPORTED",
            "field": "test"
        }
        return json.dumps(err, ensure_ascii=False)

    # Collect provided parameters
    raw_params: Dict[str, Any] = {}
    if f is not None:
        raw_params["f"] = f
    if alpha is not None:
        raw_params["alpha"] = alpha
    if power is not None:
        raw_params["power"] = power
    if groups is not None:
        raw_params["groups"] = groups
    if n_total is not None:
        raw_params["n_total"] = n_total
    if beta_alpha_ratio is not None:
        raw_params["beta_alpha_ratio"] = beta_alpha_ratio

    try:
        res = AnovaOneWayEngine.calculate(mode, raw_params)
        return json.dumps(res, ensure_ascii=False)
    except EngineError as ee:
        return json.dumps(ee.to_dict(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Beklenmeyen hata: {str(e)}", "code": "INTERNAL_ERROR"}, ensure_ascii=False)


@mcp_server.tool(name="power_analysis")
def power_analysis(
    test: str,
    mode: str,
    f: Optional[float] = None,
    alpha: Optional[float] = None,
    power: Optional[float] = None,
    groups: Optional[int] = None,
    n_total: Optional[int] = None,
    beta_alpha_ratio: Optional[float] = None,
) -> str:
    """
    Performs statistical power and sample size calculation for One-Way ANOVA (anova-oneway).

    Args:
        test: Test family identifier (must be 'anova-oneway')
        mode: Analysis mode ('a-priori', 'post-hoc', 'compromise', 'criterion', 'sensitivity')
        f: Cohen's effect size f (> 0)
        alpha: Significance level Type I error probability (0 < alpha < 1)
        power: Statistical power 1 - beta (0 < power < 1)
        groups: Number of comparison groups / treatment arms (integer >= 2)
        n_total: Total sample size across all groups (integer >= 2, and > groups)
        beta_alpha_ratio: Ratio of beta/alpha for compromise analysis (> 0)

    Returns:
        A JSON string containing the calculation results or error details.
    """
    return execute_power_analysis(
        test=test,
        mode=mode,
        f=f,
        alpha=alpha,
        power=power,
        groups=groups,
        n_total=n_total,
        beta_alpha_ratio=beta_alpha_ratio
    )


if __name__ == "__main__":
    # Runs the stdio MCP server transport
    mcp_server.run()
