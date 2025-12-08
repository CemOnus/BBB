
import math
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from bbb_model import (
    BBBInputParams,
    compute_bbb_probability,
    size_transfer_function,
    lipophilicity_transfer_function,
    charge_transfer_function,
    integrity_transfer_function,
)


st.set_page_config(
    page_title="Nano-plastic → BBB via ApoE3 — Conceptual Probability Model",
    layout="wide",
)


st.title("Nano-plastic → Blood–Brain Barrier via ApoE3")
st.markdown(
    """
This app is a **conceptual / educational calculator** that estimates the *relative probability* that
nano-plastic particles cross the Blood–Brain Barrier (BBB) via a lipid carrier such as **ApoE3**.

:warning: **This is *not* a real toxicology or clinical risk model.**  
All equations and parameters are heuristic and for **exploration only**, not for real-world decision‑making.
"""
)

st.sidebar.header("Particle & Environment Parameters")

with st.sidebar:
    st.markdown("### Nano-plastic properties")
    size_nm = st.slider(
        "Hydrodynamic diameter (nm)",
        min_value=1.0,
        max_value=500.0,
        value=80.0,
        step=1.0,
        help="Approximate hydrodynamic diameter of the nano-plastic / nano-plastic–corona complex.",
    )

    apoe3_affinity = st.slider(
        "Relative ApoE3 binding affinity (0–1)",
        min_value=0.0,
        max_value=1.0,
        value=0.6,
        step=0.01,
        help="0 = no binding; 1 = very strong/ideal ApoE3 binding.",
    )

    logP = st.slider(
        "Effective logP (lipophilicity)",
        min_value=-2.0,
        max_value=6.0,
        value=2.5,
        step=0.1,
        help="Approximate lipophilicity of the nano-plastic plus protein corona.",
    )

    zeta_mV = st.slider(
        "Zeta potential (mV)",
        min_value=-40.0,
        max_value=40.0,
        value=-5.0,
        step=1.0,
        help="Surface charge; near-neutral often has favorable stealth properties.",
    )

    st.markdown("---")
    st.markdown("### Biological / exposure context")

    dose_relative = st.slider(
        "Relative nano-plastic dose (0–10)",
        min_value=0.0,
        max_value=10.0,
        value=3.0,
        step=0.1,
        help="Arbitrary dose scale: 0 = negligible, 10 = very high.",
    )

    apoe3_expression = st.slider(
        "Relative ApoE3 carrier expression (0–1)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.01,
        help="0 = no ApoE3, 1 = high expression / availability of carriers.",
    )

    bbb_tightness = st.slider(
        "BBB tightness / integrity (0–1)",
        min_value=0.0,
        max_value=1.0,
        value=0.9,
        step=0.01,
        help="1 = very tight & healthy BBB; 0 = highly disrupted.",
    )

    inflammation = st.slider(
        "Neurovascular inflammation level (0–1)",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.01,
        help="0 = no inflammation; 1 = severe inflammation.",  # can alter permeability
    )

    st.markdown("---")
    st.markdown("### Model tuning (advanced)")
    st.caption(
        "Weights below change how strongly each factor influences the probability. "
        "They are dimensionless and purely heuristic."
    )

    w_size = st.slider("Weight: size window", -4.0, 4.0, 2.0, 0.1)
    w_aff = st.slider("Weight: ApoE3 affinity", -4.0, 4.0, 2.5, 0.1)
    w_lip = st.slider("Weight: lipophilicity", -4.0, 4.0, 1.0, 0.1)
    w_charge = st.slider("Weight: charge", -4.0, 4.0, 1.0, 0.1)
    w_int = st.slider("Weight: BBB integrity", -4.0, 4.0, -2.0, 0.1)
    w_inf = st.slider("Weight: inflammation", -4.0, 4.0, 0.5, 0.1)
    w_dose = st.slider("Weight: dose", -4.0, 4.0, 1.5, 0.1)
    w_carrier = st.slider("Weight: ApoE3 expression", -4.0, 4.0, 2.0, 0.1)

params = BBBInputParams(
    size_nm=size_nm,
    apoe3_affinity=apoe3_affinity,
    logP=logP,
    zeta_mV=zeta_mV,
    dose_relative=dose_relative,
    apoe3_expression=apoe3_expression,
    bbb_tightness=bbb_tightness,
    inflammation=inflammation,
    w_size=w_size,
    w_aff=w_aff,
    w_lip=w_lip,
    w_charge=w_charge,
    w_int=w_int,
    w_inf=w_inf,
    w_dose=w_dose,
    w_carrier=w_carrier,
)

prob, components = compute_bbb_probability(params)

col_main, col_details = st.columns([1.2, 1.0])

with col_main:
    st.subheader("Estimated BBB Crossing Probability (Relative)")

    st.metric(
        label="Estimated probability of crossing BBB via ApoE3",
        value=f"{prob * 100:.1f} %",
        help=(
            "This is a **relative** probability on a 0–1 scale. "
            "It is not calibrated to real-world incidence or risk."
        ),
    )

    st.markdown("#### Factor contributions (0–1 scale)")
    df = pd.DataFrame(
        {
            "Factor": [
                "Size window",
                "ApoE3 binding affinity",
                "Lipophilicity",
                "Charge suitability",
                "BBB tightness",
                "Inflammation",
                "Dose (relative)",
                "ApoE3 expression",
            ],
            "Score (0–1)": [
                components["size_score"],
                components["affinity_score"],
                components["lipophilicity_score"],
                components["charge_score"],
                components["integrity_score"],
                components["inflammation_score"],
                components["dose_score"],
                components["carrier_score"],
            ],
        }
    )

    st.dataframe(df, hide_index=True, use_container_width=True)

    st.markdown("#### Sensitivity to particle size")

    size_range = np.linspace(1, 500, 200)
    size_scores = [size_transfer_function(s) for s in size_range]

    fig, ax = plt.subplots()
    ax.plot(size_range, size_scores)
    ax.set_xlabel("Particle size (nm)")
    ax.set_ylabel("Size suitability score (0–1)")
    ax.set_title("Conceptual size window for ApoE3-mediated BBB crossing")

    ax.axvline(size_nm, linestyle="--")
    ax.text(size_nm, 0.05, f"{size_nm:.0f} nm", rotation=90, va="bottom")
    st.pyplot(fig)

with col_details:
    st.subheader("Model details")
    with st.expander("How is the probability calculated?", expanded=True):
        st.markdown(
            r"""
We use a **logistic function** to squash a weighted sum of factors into a 0–1 probability:

\[
P(\text{BBB crossing}) = \frac{1}{1 + e^{-Z}},
\]

where

\[
Z = \sum_i w_i \cdot f_i,
\]

- \(f_i\) are dimensionless factor scores between 0 and 1 (e.g., size window, affinity, lipophilicity).
- \(w_i\) are weights that you control in the sidebar.

The factor scores themselves are heuristic transfer functions:
- **Size window**: Gaussian peak centered around ~50 nm (log-space) to mimic an ApoE3-like lipoprotein size window.
- **Lipophilicity**: Peak around logP ≈ 2–4.
- **Charge**: Highest near-neutral zeta potential; heavily charged particles are penalized.
- **BBB tightness**: Tighter BBB reduces probability (inverted score).
- **Inflammation**: Higher inflammation (more leaky BBB) modestly increases probability.
- **Dose**: Higher dose → higher probability (but capped at a saturating nonlinear function).
- **ApoE3 affinity + expression**: Multiplicative effect on the probability of successful receptor-mediated transcytosis.
"""
        )

    with st.expander("Export & reproducibility"):
        st.markdown(
            """
- All logic lives in `bbb_model.py` so you can swap in more realistic functions or parameter values.
- The code is intentionally **simple and transparent** so you can justify each modeling choice in a poster or report.
- To calibrate to real data, you would replace the heuristic transfer functions with fits to experimental results.
"""
        )

st.markdown("---")
st.markdown(
    """
**Disclaimer**  
This tool is for **educational and exploratory purposes only.**  
It is not validated for risk assessment, clinical decision‑making, or regulatory use.
"""
)
