"""
G*Power Clone Calculation Engine
Module: src.engine
Focus: F tests - ANOVA: Fixed effects, omnibus, one-way (test id: anova-oneway)

Implements clean-room mathematical calculations reverse engineered from G*Power 3.1.9.7.
Follows CONTRACT.md v1.0.0.
"""

from typing import Dict, Any, Tuple
import math
import scipy.stats as stats
from scipy.optimize import brentq


class EngineError(Exception):
    """Custom exception representing calculation and input validation errors."""
    def __init__(self, message: str, code: str = "INVALID_VALUE", field: str = None, exit_code: int = 2):
        super().__init__(message)
        self.message = message
        self.code = code
        self.field = field
        self.exit_code = exit_code

    def to_dict(self) -> Dict[str, Any]:
        res = {"error": self.message, "code": self.code}
        if self.field:
            res["field"] = self.field
        return res


class AnovaOneWayEngine:
    """Calculation engine for ANOVA: Fixed effects, omnibus, one-way (anova-oneway)."""

    TEST_ID = "anova-oneway"
    SUPPORTED_MODES = {"a-priori", "post-hoc", "compromise", "criterion", "sensitivity"}

    # Parametre gereksinimleri (CONTRACT.md Bölüm 4.3)
    MODE_REQUIRED_PARAMS = {
        "a-priori": ["f", "alpha", "power", "groups"],
        "post-hoc": ["f", "alpha", "n_total", "groups"],
        "compromise": ["f", "beta_alpha_ratio", "n_total", "groups"],
        "criterion": ["f", "power", "n_total", "groups"],
        "sensitivity": ["alpha", "power", "n_total", "groups"],
    }

    @classmethod
    def validate_and_convert(cls, mode: str, raw_params: Dict[str, Any]) -> Dict[str, Any]:
        """Validates input parameters according to CONTRACT.md sections 2, 4.3, and 5."""
        if mode not in cls.SUPPORTED_MODES:
            raise EngineError(
                f"Desteklenmeyen mod: '{mode}'. Desteklenen modlar: {sorted(list(cls.SUPPORTED_MODES))}",
                code="UNSUPPORTED",
                field="mode",
                exit_code=2
            )

        required = cls.MODE_REQUIRED_PARAMS[mode]

        # Eksik parametre kontrolü
        for req in required:
            if req not in raw_params or raw_params[req] is None:
                raise EngineError(
                    f"'{mode}' modu için zorunlu parametre eksik: '{req}'",
                    code="MISSING_PARAM",
                    field=req,
                    exit_code=2
                )

        # Tanınmayan ya da bu modla ilgisiz parametre kontrolü
        for param_key in raw_params.keys():
            if param_key not in required:
                raise EngineError(
                    f"'{mode}' modunda tanınmayan ya da ilgisiz parametre: '{param_key}'",
                    code="UNKNOWN_PARAM",
                    field=param_key,
                    exit_code=2
                )

        parsed: Dict[str, Any] = {}

        # Tip ve aralık dönüşümleri
        # 1. groups
        if "groups" in raw_params:
            try:
                g_val = float(raw_params["groups"])
                if not g_val.is_integer():
                    raise ValueError()
                groups = int(g_val)
            except (ValueError, TypeError):
                raise EngineError(
                    "Grup sayısı tamsayı olmalıdır",
                    code="INVALID_VALUE",
                    field="groups",
                    exit_code=2
                )
            if groups < 2:
                raise EngineError(
                    "Grup sayısı en az 2 olmalıdır (groups >= 2)",
                    code="OUT_OF_RANGE",
                    field="groups",
                    exit_code=2
                )
            parsed["groups"] = groups

        # 2. n_total
        if "n_total" in raw_params:
            try:
                n_val = float(raw_params["n_total"])
                if not n_val.is_integer():
                    raise ValueError()
                n_total = int(n_val)
            except (ValueError, TypeError):
                raise EngineError(
                    "Toplam örneklem büyüklüğü (n_total) tamsayı olmalıdır",
                    code="INVALID_VALUE",
                    field="n_total",
                    exit_code=2
                )
            if n_total < 2:
                raise EngineError(
                    "Toplam örneklem büyüklüğü en az 2 olmalıdır (n_total >= 2)",
                    code="OUT_OF_RANGE",
                    field="n_total",
                    exit_code=2
                )
            # ANOVA serbestlik derecesi kısıtı: df2 = n_total - groups >= 1
            if "groups" in parsed and n_total <= parsed["groups"]:
                raise EngineError(
                    f"Toplam örneklem grup sayısından büyük olmalı (df2 = n_total - groups >= 1; n_total={n_total}, groups={parsed['groups']})",
                    code="INCONSISTENT",
                    field="n_total",
                    exit_code=2
                )
            parsed["n_total"] = n_total

        # 3. f (Effect size f)
        if "f" in raw_params:
            try:
                f_val = float(raw_params["f"])
            except (ValueError, TypeError):
                raise EngineError("Etki büyüklüğü 'f' sayısal olmalıdır", code="INVALID_VALUE", field="f", exit_code=2)
            if f_val <= 0:
                raise EngineError("Etki büyüklüğü 'f' 0'dan büyük olmalıdır (f > 0)", code="OUT_OF_RANGE", field="f", exit_code=2)
            parsed["f"] = f_val

        # 4. alpha
        if "alpha" in raw_params:
            try:
                alpha_val = float(raw_params["alpha"])
            except (ValueError, TypeError):
                raise EngineError("Alfa (alpha) sayısal olmalıdır", code="INVALID_VALUE", field="alpha", exit_code=2)
            if not (0 < alpha_val < 1):
                raise EngineError("Alfa 0 ile 1 arasında olmalıdır (0 < alpha < 1)", code="OUT_OF_RANGE", field="alpha", exit_code=2)
            parsed["alpha"] = alpha_val

        # 5. power
        if "power" in raw_params:
            try:
                power_val = float(raw_params["power"])
            except (ValueError, TypeError):
                raise EngineError("Güç (power) sayısal olmalıdır", code="INVALID_VALUE", field="power", exit_code=2)
            if not (0 < power_val < 1):
                raise EngineError("Güç 0 ile 1 arasında olmalıdır (0 < power < 1)", code="OUT_OF_RANGE", field="power", exit_code=2)
            if "alpha" in parsed and power_val <= parsed["alpha"]:
                raise EngineError(
                    f"Power, alpha değerinden büyük olmalı (power={power_val}, alpha={parsed['alpha']})",
                    code="INCONSISTENT",
                    field="power",
                    exit_code=2
                )
            parsed["power"] = power_val

        # 6. beta_alpha_ratio
        if "beta_alpha_ratio" in raw_params:
            try:
                bar_val = float(raw_params["beta_alpha_ratio"])
            except (ValueError, TypeError):
                raise EngineError("beta_alpha_ratio sayısal olmalıdır", code="INVALID_VALUE", field="beta_alpha_ratio", exit_code=2)
            if bar_val <= 0:
                raise EngineError("beta_alpha_ratio 0'dan büyük olmalıdır (> 0)", code="OUT_OF_RANGE", field="beta_alpha_ratio", exit_code=2)
            parsed["beta_alpha_ratio"] = bar_val

        return parsed

    @classmethod
    def calculate(cls, mode: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates power analysis metrics for anova-oneway."""
        p = cls.validate_and_convert(mode, params)

        try:
            if mode == "a-priori":
                return cls._compute_apriori(p["f"], p["alpha"], p["power"], p["groups"])
            elif mode == "post-hoc":
                return cls._compute_posthoc(p["f"], p["alpha"], p["n_total"], p["groups"])
            elif mode == "compromise":
                return cls._compute_compromise(p["f"], p["beta_alpha_ratio"], p["n_total"], p["groups"])
            elif mode == "criterion":
                return cls._compute_criterion(p["f"], p["power"], p["n_total"], p["groups"])
            elif mode == "sensitivity":
                return cls._compute_sensitivity(p["alpha"], p["power"], p["n_total"], p["groups"])
            else:
                raise EngineError(f"Bilinmeyen mod: {mode}", code="UNSUPPORTED", field="mode", exit_code=2)
        except EngineError:
            raise
        except Exception as e:
            raise EngineError(f"Hesaplama hatası: {str(e)}", code="NO_SOLUTION", exit_code=1)

    @classmethod
    def _compute_apriori(cls, f: float, alpha: float, power: float, groups: int) -> Dict[str, Any]:
        """
        A priori: Gerekli örneklem büyüklüğü N'i hesaplar.
        G*Power [REA] bulgusu: ANOVA dengeli tasarım kuralı gereğince n_per_group
        tamsayı olarak 2'den başlayarak artırılır. N = n_per_group * groups.
        """
        df1 = groups - 1
        max_n_per_group = 500000

        for n_pg in range(2, max_n_per_group + 1):
            N = n_pg * groups
            df2 = N - groups
            ncp = (f ** 2) * N
            crit_f = float(stats.f.ppf(1.0 - alpha, df1, df2))
            actual_power = float(1.0 - stats.ncf.cdf(crit_f, df1, df2, ncp))

            if actual_power >= power:
                return {
                    "ncp": float(ncp),
                    "critical_f": float(crit_f),
                    "df1": int(df1),
                    "df2": int(df2),
                    "n_total": int(N),
                    "actual_power": float(actual_power),
                }

        raise EngineError("Örneklem büyüklüğü makul aralıkta çözülemedi", code="NO_SOLUTION", exit_code=1)

    @classmethod
    def _compute_posthoc(cls, f: float, alpha: float, n_total: int, groups: int) -> Dict[str, Any]:
        """Post hoc: Verilen parametrelerle ulaşılan gücü hesaplar."""
        df1 = groups - 1
        df2 = n_total - groups
        ncp = (f ** 2) * n_total
        crit_f = float(stats.f.ppf(1.0 - alpha, df1, df2))
        power = float(1.0 - stats.ncf.cdf(crit_f, df1, df2, ncp))

        return {
            "ncp": float(ncp),
            "critical_f": float(crit_f),
            "df1": int(df1),
            "df2": int(df2),
            "power": float(power),
        }

    @classmethod
    def _compute_compromise(cls, f: float, beta_alpha_ratio: float, n_total: int, groups: int) -> Dict[str, Any]:
        """Compromise: beta / alpha oranına göre örtük alfa, beta ve gücü hesaplar."""
        df1 = groups - 1
        df2 = n_total - groups
        ncp = (f ** 2) * n_total
        q = beta_alpha_ratio

        def objective(fc: float) -> float:
            # alpha = 1 - F_central(fc)
            # beta = F_noncentral(fc)
            # beta - q * alpha = 0
            a = 1.0 - stats.f.cdf(fc, df1, df2)
            b = stats.ncf.cdf(fc, df1, df2, ncp)
            return float(b - q * a)

        # G*Power kök aralığı
        low = 1e-6
        high = 50.0

        # Genişletme / daraltma
        f_low = objective(low)
        f_high = objective(high)
        if f_low * f_high > 0:
            high = 150.0
            f_high = objective(high)

        fc_crit = float(brentq(objective, low, high, xtol=1e-12, rtol=1e-12))
        alpha = float(1.0 - stats.f.cdf(fc_crit, df1, df2))
        beta = float(stats.ncf.cdf(fc_crit, df1, df2, ncp))
        power = float(1.0 - beta)

        return {
            "ncp": float(ncp),
            "critical_f": float(fc_crit),
            "df1": int(df1),
            "df2": int(df2),
            "alpha": float(alpha),
            "beta": float(beta),
            "power": float(power),
        }

    @classmethod
    def _compute_criterion(cls, f: float, power: float, n_total: int, groups: int) -> Dict[str, Any]:
        """Criterion: Verilen hedef güç için gereken alfayı hesaplar."""
        df1 = groups - 1
        df2 = n_total - groups
        ncp = (f ** 2) * n_total
        beta_target = 1.0 - power

        # beta = F_noncentral(fc) => fc = F_noncentral_inv(beta)
        crit_f = float(stats.ncf.ppf(beta_target, df1, df2, ncp))
        alpha = float(1.0 - stats.f.cdf(crit_f, df1, df2))

        return {
            "ncp": float(ncp),
            "critical_f": float(crit_f),
            "df1": int(df1),
            "df2": int(df2),
            "alpha": float(alpha),
        }

    @classmethod
    def _compute_sensitivity(cls, alpha: float, power: float, n_total: int, groups: int) -> Dict[str, Any]:
        """Sensitivity: Verilen alpha, güç ve N için saptanabilir minimum f etki büyüklüğünü hesaplar."""
        df1 = groups - 1
        df2 = n_total - groups
        crit_f = float(stats.f.ppf(1.0 - alpha, df1, df2))

        def objective(lmb: float) -> float:
            # 1 - F_noncentral(crit_f, df1, df2, lmb) - power = 0
            act_p = 1.0 - stats.ncf.cdf(crit_f, df1, df2, lmb)
            return float(act_p - power)

        # lambda kök araması
        low = 1e-6
        high = 150.0
        lmb_sens = float(brentq(objective, low, high, xtol=1e-12, rtol=1e-12))
        f_sens = float(math.sqrt(lmb_sens / n_total))

        return {
            "ncp": float(lmb_sens),
            "critical_f": float(crit_f),
            "df1": int(df1),
            "df2": int(df2),
            "f": float(f_sens),
        }
