
# Nano-plastic → BBB via ApoE3 — Conceptual Probability Calculator

This is a **Streamlit** app that implements a **conceptual / educational model** for the probability that
nano-plastic particles cross the **Blood–Brain Barrier (BBB)** via a lipid carrier such as **ApoE3**.

> ⚠️ **Important disclaimer**  
> This repository is for **educational and exploratory use only**.  
> None of the equations are calibrated to real experimental or clinical data.  
> Do **not** use this to make medical, regulatory, or safety decisions.

---

## Features

- Interactive sliders for:
  - Particle size (nm)
  - ApoE3 binding affinity (0–1)
  - Effective logP (lipophilicity)
  - Zeta potential (mV)
  - Relative dose
  - ApoE3 expression
  - BBB tightness / integrity
  - Neurovascular inflammation
- A **logistic probability model** that combines these factors with user-tunable weights.
- A breakdown table showing each factor's **0–1 score**.
- A plot of the **size suitability window** for ApoE3-mediated BBB crossing.
- All model logic separated into `bbb_model.py` so you can plug in more realistic functions later.

---

## Local development

```bash
# create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# run the app
streamlit run app.py
```

Then open the URL Streamlit prints in your terminal (e.g. `http://localhost:8501`).

---

## Deploying on Streamlit Cloud

1. Push this folder to a **GitHub** repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app.
3. Point it at your GitHub repo and select:
   - **Main file path**: `app.py`
4. Click **Deploy**.

You can then share the Streamlit Cloud URL in your project or poster.

---

## How the model works (short version)

We estimate a relative probability

\[
P(\text{BBB crossing}) = \frac{1}{1 + e^{-Z}},
\]

with

\[
Z = \sum_i w_i f_i - \text{offset},
\]

where each \(f_i\) is a 0–1 factor score (size window, affinity, lipophilicity, charge, etc.) and each \(w_i\)
is a weight that you can adjust in the sidebar.

The transfer functions (implemented in `bbb_model.py`) are **heuristic**:
- Size window: Gaussian in log-space, peaking around ~50 nm.
- Lipophilicity: Gaussian around logP ≈ 3.
- Charge: triangular penalty away from ~0 mV.
- BBB tightness: inverted so tighter BBB → lower probability.
- Inflammation: nonlinear function where more inflammation → higher permeability.
- Dose: saturating Michaelis–Menten–like curve.
- ApoE3 affinity & expression: linear 0–1 scores.

To make this model more realistic, replace these transfer functions with ones fit to your experimental data.

---

## License

MIT — feel free to fork, modify, and adapt for your own educational work.
