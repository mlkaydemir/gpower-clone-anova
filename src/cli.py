"""
G*Power Clone CLI Interface
Module: src.cli
Executes ANOVA power analysis conforming to CONTRACT.md v1.0.0.
"""

import sys
import json
import platform
from typing import List, Dict, Any, Tuple

from src.engine import AnovaOneWayEngine, EngineError

CONTRACT_VERSION = "1.0.0"
TEAM_NAME = "Teardown-ANOVA-Team"
ENGINE_INFO = f"Python {platform.python_version()} (scipy)"


def parse_cli_args(args: List[str]) -> Tuple[Dict[str, Any], bool]:
    """Parses command line arguments in --<param> <value> format."""
    parsed: Dict[str, Any] = {}
    is_version = False

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--version":
            is_version = True
            i += 1
            continue

        if arg.startswith("--"):
            param_name = arg[2:]
            if not param_name:
                raise EngineError("Geçersiz boş parametre adı '--'", code="INVALID_VALUE", exit_code=2)
            if i + 1 >= len(args) or args[i + 1].startswith("--"):
                raise EngineError(
                    f"'{param_name}' parametresi için bir değer belirtilmedi",
                    code="MISSING_PARAM",
                    field=param_name,
                    exit_code=2
                )
            param_value = args[i + 1]
            parsed[param_name] = param_value
            i += 2
        else:
            raise EngineError(f"Beklenmeyen argüman biçimi: '{arg}'", code="INVALID_VALUE", exit_code=2)

    return parsed, is_version


def main():
    args = sys.argv[1:]

    # Boş çağrı kontrolü
    if not args:
        err = {"error": "Parametre verilmedi. '--version' veya '--test anova-oneway' kullanın.", "code": "MISSING_PARAM"}
        sys.stdout.write(json.dumps(err, ensure_ascii=False) + "\n")
        sys.exit(2)

    try:
        params, is_version = parse_cli_args(args)

        if is_version:
            ver_obj = {
                "contract_version": CONTRACT_VERSION,
                "name": TEAM_NAME,
                "engine": ENGINE_INFO
            }
            sys.stdout.write(json.dumps(ver_obj, ensure_ascii=False) + "\n")
            sys.exit(0)

        # Test kontrolü
        if "test" not in params:
            raise EngineError("Zorunlu '--test' parametresi eksik", code="MISSING_PARAM", field="test", exit_code=2)

        test_id = params.pop("test")
        if test_id != AnovaOneWayEngine.TEST_ID:
            raise EngineError(
                f"Desteklenmeyen test ailesi: '{test_id}'. Bu motor yalnızca '{AnovaOneWayEngine.TEST_ID}' destekler.",
                code="UNSUPPORTED",
                field="test",
                exit_code=2
            )

        # Mode kontrolü
        if "mode" not in params:
            raise EngineError("Zorunlu '--mode' parametresi eksik", code="MISSING_PARAM", field="mode", exit_code=2)

        mode_id = params.pop("mode")

        # Motor çağrısı
        result = AnovaOneWayEngine.calculate(mode_id, params)

        # Başarılı tek satır JSON çıktısı
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        sys.exit(0)

    except EngineError as ee:
        sys.stdout.write(json.dumps(ee.to_dict(), ensure_ascii=False) + "\n")
        sys.exit(ee.exit_code)
    except Exception as e:
        sys.stdout.write(json.dumps({"error": f"Beklenmeyen iç hata: {str(e)}", "code": "INTERNAL_ERROR"}, ensure_ascii=False) + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
