
import math
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class BBBInputParams:
    # core inputs
    size_nm: float
    apoe3_affinity: float  # 0–1
    logP: float
    zeta_mV: float
    dose_relative: float  # 0–10 arbitrary
    apoe3_expression: float  # 0–1
    bbb_tightness: float  # 0–1 (1 = tight/healthy)
    inflammation: float  # 0–1

    # weights for each factor in the logistic model
    w_size: float
    w_aff: float
    w_lip: float
    w_charge: float
    w_int: float
    w_inf: float
    w_dose: float
    w_carrier: float


def _gaussian(x: float, mu: float, sigma: float) -> float:
    """Simple Gaussian transfer function, output in [0, 1]."""
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2)


def size_transfer_function(size_nm: float) -> float:
    """
    Heuristic size suitability for ApoE3-mediated BBB crossing.

    We assume an approximate "window" around ~50 nm in log-space,
    with a broad sigma so 20–80 nm are favored but not exclusive.
    """
    # avoid log10 problems
    size_nm = max(size_nm, 0.1)
    x = math.log10(size_nm)
    mu = math.log10(50.0)
    sigma = 0.25
    return max(0.0, min(1.0, _gaussian(x, mu, sigma)))


def lipophilicity_transfer_function(logP: float) -> float:
    """
    Heuristic: peak lipophilicity around logP 2–4, with soft drop-off.
    """
    # center at 3, somewhat broad
    score = _gaussian(logP, mu=3.0, sigma=1.0)
    return max(0.0, min(1.0, score))


def charge_transfer_function(zeta_mV: float) -> float:
    """
    Heuristic: near-neutral charge is favored.
    Use a simple triangular function with max at 0 mV and 0 at ±40 mV.
    """
    max_abs = 40.0
    val = 1.0 - min(max(abs(zeta_mV), 0.0), max_abs) / max_abs
    return max(0.0, min(1.0, val))


def integrity_transfer_function(bbb_tightness: float) -> float:
    """
    Convert tightness (0–1) to a permeability-like score.
    Tighter (1.0) → lower permeability; looser (0.0) → higher.
    """
    tight = max(0.0, min(1.0, bbb_tightness))
    return 1.0 - tight


def dose_transfer_function(dose_relative: float) -> float:
    """
    Simple saturating function: higher dose → asymptotically approach 1.
    """
    dose = max(0.0, dose_relative)
    # Michaelis–Menten-like: f = dose / (K + dose)
    K = 2.0
    return max(0.0, min(1.0, dose / (K + dose)))


def inflammation_transfer_function(inflammation: float) -> float:
    """
    Assume higher inflammation → higher permeability (up to a cap).
    """
    inflam = max(0.0, min(1.0, inflammation))
    # Slightly nonlinear to emphasize moderate-to-high inflammation
    return inflam ** 0.7


def logistic(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))


def compute_bbb_probability(params: BBBInputParams) -> Tuple[float, Dict[str, float]]:
    # factor scores (0–1)
    size_score = size_transfer_function(params.size_nm)
    affinity_score = max(0.0, min(1.0, params.apoe3_affinity))
    lipophilicity_score = lipophilicity_transfer_function(params.logP)
    charge_score = charge_transfer_function(params.zeta_mV)
    integrity_score = integrity_transfer_function(params.bbb_tightness)
    inflammation_score = inflammation_transfer_function(params.inflammation)
    dose_score = dose_transfer_function(params.dose_relative)
    carrier_score = max(0.0, min(1.0, params.apoe3_expression))

    # weighted sum for logistic
    Z = (
        params.w_size * size_score
        + params.w_aff * affinity_score
        + params.w_lip * lipophilicity_score
        + params.w_charge * charge_score
        + params.w_int * integrity_score
        + params.w_inf * inflammation_score
        + params.w_dose * dose_score
        + params.w_carrier * carrier_score
        - 2.0  # global offset to keep probabilities modest by default
    )

    prob = logistic(Z)

    components = {
        "size_score": size_score,
        "affinity_score": affinity_score,
        "lipophilicity_score": lipophilicity_score,
        "charge_score": charge_score,
        "integrity_score": integrity_score,
        "inflammation_score": inflammation_score,
        "dose_score": dose_score,
        "carrier_score": carrier_score,
        "Z": Z,
    }

    return prob, components
