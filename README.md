# Dynamic Load Balancing in Multi-Agent Task Orchestration

> **IEEE Paper** — Hybrid Adaptive Scheduler (HAS): A novel algorithm for minimizing makespan across heterogeneous multi-agent systems.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

This repository contains the complete source code, simulation framework, and LaTeX paper for our research on dynamic load balancing in multi-agent task orchestration.

**Key Contribution**: The **Hybrid Adaptive Scheduler (HAS)** — a parameterized algorithm that interpolates between offline LPT scheduling (α=1) and online greedy scheduling (α=0) via a tunable batch fraction α ∈ [0,1].

### Key Results

| Algorithm | Identical Machines | Uniform Speeds | Bimodal Speeds |
|---|---|---|---|
| Random | 1.337 ± 0.100 | 3.551 ± 0.706 | 4.128 ± 0.371 |
| Round Robin | 1.165 ± 0.052 | 3.550 ± 0.386 | 3.741 ± 0.186 |
| Online Greedy (ECT) | 1.032 ± 0.009 | 1.027 ± 0.007 | 1.025 ± 0.006 |
| Offline LPT | 1.001 ± 0.000 | 1.001 ± 0.000 | 1.001 ± 0.000 |
| **HAS (α=0.3)** | **1.032 ± 0.009** | **1.026 ± 0.008** | **1.024 ± 0.006** |
| **HAS (α=0.5)** | **1.032 ± 0.009** | **1.027 ± 0.008** | **1.025 ± 0.007** |

*Competitive ratios (C_alg / C*) — lower is better. Values near 1.0 indicate near-optimal performance.*

## Repository Structure

```
research/
├── main.py                         # Experiment runner (generates all figures)
├── references.bib                  # BibTeX references (46 entries)
├── simulator/
│   ├── agents.py                   # Agent pool models (identical/uniform/bimodal)
│   ├── tasks.py                    # Task generators (uniform/Pareto/bimodal/adversarial)
│   └── schedulers/
│       ├── online_greedy.py        # Online ECT baseline
│       ├── offline_lpt.py          # Offline LPT baseline
│       ├── offline_optimal.py      # Brute-force / LP lower bound
│       ├── hybrid_has.py           # ★ Novel HAS algorithm
│       ├── random_assign.py        # Random assignment baseline
│       └── round_robin.py          # Round-robin baseline
└── paper/
    ├── paper.tex                   # IEEE-format LaTeX paper
    ├── paper.pdf                   # Compiled paper (5 pages)
    ├── references.bib              # BibTeX (copy for LaTeX)
    ├── verify_checklist.py         # Automated submission checklist
    └── figures/
        ├── fig1_identical_machines.png
        ├── fig2_competitive_ratio_vs_n.png
        ├── fig3_alpha_sweep.png
        ├── fig4_heterogeneity_impact.png
        └── fig5_scalability.png
```

## Quick Start

### Prerequisites

- Python 3.8+
- NumPy
- Matplotlib

### Installation

```bash
git clone https://github.com/Purushotham-Prajapati-24/Load-Balancing-in-Multi-Agent.git
cd Load-Balancing-in-Multi-Agent/research
pip install numpy matplotlib
```

### Run Experiments

```bash
python main.py
```

This executes all 5 experiments and saves publication-quality figures to `paper/figures/`.

### Compile Paper

```bash
cd paper
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

## Experiments

| # | Experiment | What It Measures |
|---|---|---|
| E1 | Identical Machines (P\|\|C_max) | Makespan comparison across all algorithms |
| E2 | Competitive Ratio vs N | How performance scales with task count |
| E3 | Alpha Sweep | HAS parameter sensitivity analysis |
| E4 | Heterogeneity Impact | Effect of agent speed distribution |
| E5 | Scalability | Runtime growth with N |

## The HAS Algorithm

```
Algorithm: Hybrid Adaptive Scheduler (HAS)
Input:  M agents with speeds s_1,...,s_M
        N tasks with processing requirements p_1,...,p_N
        Batch parameter α ∈ [0,1]

Phase 1 (Batch-LPT):
  1. Collect first ⌊α·N⌋ tasks into buffer B
  2. Sort B by p_j in decreasing order (LPT)
  3. For each task in B:
       Assign to agent i* = argmin_i (L_i + p_j/s_i)

Phase 2 (Online-ECT):
  4. For each remaining task j:
       Assign to agent i* = argmin_i (L_i + p_j/s_i)
```

**Theoretical guarantees:**
- α = 0 → Online List Scheduling: competitive ratio (2 - 1/M)
- α = 1 → Offline LPT: approximation ratio (4/3 - 1/3M)
- 0 < α < 1 → Interpolation with monotonically improving bounds

## Citation

If you use this code in your research, please cite:

```bibtex
@inproceedings{prajapati2025has,
  author    = {Purushotham Prajapati},
  title     = {Dynamic Load Balancing in Multi-Agent Task Orchestration:
               A Hybrid Adaptive Scheduling Approach},
  booktitle = {Proceedings of IEEE Conference},
  year      = {2025},
  institution = {VNRVJIET, Hyderabad, India}
}
```

## Author

**Purushotham Prajapati**
- Department of Computer Science and Engineering
- VNRVJIET, Hyderabad, India
- purushothamprajapati7473@gmail.com

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
