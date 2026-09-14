# ABLKM: Hybrid BB84 QKD and Geometric Indexing Framework

This repository contains the reproducibility artifact accompanying:

> **ABLKM: A Hybrid BB84 QKD and Geometric Indexing Framework for Secure Local Key Registries**

## Contents

```text
ABLKM_submission_artifact/
├── paper/
│   ├── ABLKM_IEEE_final_draft.tex
│   └── ABLKM_IEEE_final_draft.pdf
├── src/
│   ├── qkd_bb84.py
│   ├── lattice_crypto_v2.py
│   ├── hybrid_qkd_ablkm.py
│   └── README.md
├── web_demo/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── README.md
├── experiments/
│   └── benchmark_ablkm.py
├── results/
│   ├── benchmark_results.csv
│   └── benchmark_environment.txt
├── requirements.txt
├── .gitignore
└── README.md
```

## Scope and claims

ABLKM is presented as a secret-parameterized geometric indexing mechanism combined with standard cryptographic primitives. This artifact does **not** claim that ABLKM itself is a post-quantum cryptographic primitive, nor does it claim security from CVP, SVP, Module-LWE, or another lattice-hardness assumption.

The BB84 component is a software simulation. It should not be interpreted as a complete deployed QKD stack or as a composable security proof.

The current Python retrieval path uses an internal HMAC-derived registry dictionary for direct lookup. Therefore, the benchmark does not yet measure a true bucket-scan retrieval/search implementation. This limitation is stated in the paper and is a target for future work.

The browser demo is intentionally separate from the Python security prototype and is for visualization/interaction only.

## Requirements

- Python 3.11 or later
- `cryptography` (see `requirements.txt`)

The paper's target experimental environment is Windows 11, Intel Core i7-1165G7 @ 2.80 GHz, 16 GB RAM, Python 3.11. The packaged benchmark results are a separate reference run and must not be represented as measurements from that target machine.

## Install

```bash
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
```

On Linux/macOS, activate with:

```bash
source .venv/bin/activate
```

## Run the end-to-end prototype

From the repository root:

```bash
python src/hybrid_qkd_ablkm.py
```

The script demonstrates BB84 simulation, encrypted transfer of the ABLKM reference parameter, simulated registry transfer, retrieval, and a negative lookup using a mismatched reference parameter.

## Reproduce the benchmark

Run:

```bash
python experiments/benchmark_ablkm.py
```

The script performs 10 warm-up trials followed by 100 measured trials and writes:

- `experiments/benchmark_results.csv` (generated/updated benchmark results)
- `experiments/benchmark_environment.txt` (Python/platform/runtime metadata)

Timing uses `time.perf_counter_ns`. BB84 console output is suppressed during timing so that console I/O is not included in the BB84 measurement.

The benchmark compares ABLKM operations against an authenticated dictionary baseline. The baseline is a local indexing baseline rather than a cryptographic equivalence claim; it retains HMAC-SHA256, HKDF-SHA256, and AES-256-GCM while removing the geometric indexing step.

## Paper compilation

The paper is supplied as both `.tex` and compiled `.pdf`. To rebuild with a standard IEEE LaTeX installation, compile the `.tex` file with the IEEEtran class and run LaTeX twice if required for references.

## Browser demo

Open `web_demo/index.html` directly in a browser. No build system is required.

The demo uses a simplified JavaScript model for visualization and should not be used for cryptographic protection of real data.

## Reproducibility notes

The artifact intentionally preserves the distinction between:

1. the conceptual ABLKM mechanism,
2. the Python security-relevant prototype,
3. the simplified browser visualization, and
4. the benchmark implementation.

This separation prevents the visualization's simplified cryptographic logic from being confused with the Python implementation evaluated in the paper.

## License

No open-source license is asserted by this artifact. If the work is released publicly, add the license selected by the author before publication.
