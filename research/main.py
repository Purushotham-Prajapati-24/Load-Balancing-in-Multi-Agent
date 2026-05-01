"""
Main experiment runner for the IEEE paper:
"Dynamic Load Balancing in Multi-Agent Task Orchestration"

Runs all 5 experiment configurations, computes competitive ratios,
and generates publication-quality figures.
"""

import sys
import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Configure publication-quality plots
rcParams['font.family'] = 'serif'
rcParams['font.size'] = 10
rcParams['axes.labelsize'] = 11
rcParams['legend.fontsize'] = 9
rcParams['figure.dpi'] = 300

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulator.agents import AgentPool
from simulator.tasks import TaskGenerator
from simulator.schedulers import (
    OnlineGreedyScheduler,
    OfflineLPTScheduler,
    HybridAdaptiveScheduler,
    RandomScheduler,
    RoundRobinScheduler,
    OfflineOptimalScheduler,
)

# ── Output directory ──────────────────────────────────────────
FIG_DIR = os.path.join(os.path.dirname(__file__), "paper", "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def run_experiment_1():
    """E1: Identical machines — Makespan comparison across algorithms."""
    print("\n" + "="*60)
    print("EXPERIMENT 1: Identical Machines (P||Cmax)")
    print("="*60)

    M_values = [4, 8, 16]
    N = 200
    n_trials = 30
    results = {}

    schedulers = [
        RandomScheduler(seed=0),
        RoundRobinScheduler(),
        OnlineGreedyScheduler(),
        OfflineLPTScheduler(),
        HybridAdaptiveScheduler(alpha=0.3),
        HybridAdaptiveScheduler(alpha=0.5),
        HybridAdaptiveScheduler(alpha=0.7),
    ]

    for M in M_values:
        results[M] = {s.name: [] for s in schedulers}
        for trial in range(n_trials):
            tg = TaskGenerator(seed=trial)
            tasks = tg.uniform(N, 1.0, 100.0)
            for sched in schedulers:
                agents = AgentPool.identical(M)
                ms = sched.schedule(agents, tasks)
                results[M][sched.name].append(ms)

    # ── Plot: Grouped bar chart ───────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=False)
    colors = ['#e74c3c', '#e67e22', '#3498db', '#2ecc71', '#9b59b6', '#1abc9c', '#34495e']

    for idx, M in enumerate(M_values):
        ax = axes[idx]
        names = list(results[M].keys())
        means = [np.mean(results[M][n]) for n in names]
        stds = [np.std(results[M][n]) for n in names]
        short_names = [n.replace("Online Greedy (ECT)", "Greedy")
                        .replace("Offline LPT", "LPT")
                        .replace("HAS (a=", "HAS a=")
                        .replace(")", "") for n in names]

        bars = ax.bar(range(len(names)), means, yerr=stds, color=colors,
                      capsize=3, edgecolor='black', linewidth=0.5)
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(short_names, rotation=45, ha='right', fontsize=7)
        ax.set_title(f'M = {M} agents', fontweight='bold')
        ax.set_ylabel('Makespan' if idx == 0 else '')
        ax.grid(axis='y', alpha=0.3)

    fig.suptitle('Experiment 1: Makespan on Identical Machines (N=200)', fontweight='bold', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig1_identical_machines.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  -> Saved fig1_identical_machines.png")


def run_experiment_2():
    """E2: Competitive ratio vs N for heterogeneous machines."""
    print("\n" + "="*60)
    print("EXPERIMENT 2: Competitive Ratio vs N (Uniform Speeds)")
    print("="*60)

    M = 8
    N_values = [20, 50, 100, 200, 500]
    n_trials = 20

    schedulers = [
        OnlineGreedyScheduler(),
        OfflineLPTScheduler(),
        HybridAdaptiveScheduler(alpha=0.3),
        HybridAdaptiveScheduler(alpha=0.5),
        HybridAdaptiveScheduler(alpha=0.7),
    ]
    optimal = OfflineOptimalScheduler(max_brute_force=15)

    ratios = {s.name: {N: [] for N in N_values} for s in schedulers}

    for N in N_values:
        print(f"  N={N}...", end=" ", flush=True)
        for trial in range(n_trials):
            tg = TaskGenerator(seed=trial * 100 + N)
            tasks = tg.uniform(N, 1.0, 100.0)

            # Compute optimal/lower bound
            agents_opt = AgentPool.uniform(M, seed=42)
            c_star = optimal.schedule(agents_opt, tasks)

            for sched in schedulers:
                agents = AgentPool.uniform(M, seed=42)
                ms = sched.schedule(agents, tasks)
                ratio = ms / c_star if c_star > 0 else 1.0
                ratios[sched.name][N].append(ratio)
        print("done")

    # ── Plot: Line plot with error bars ───────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    markers = ['o', 's', '^', 'D', 'v']
    colors = ['#e74c3c', '#2ecc71', '#9b59b6', '#3498db', '#1abc9c']

    for idx, sched in enumerate(schedulers):
        means = [np.mean(ratios[sched.name][N]) for N in N_values]
        stds = [np.std(ratios[sched.name][N]) for N in N_values]
        ax.errorbar(N_values, means, yerr=stds, marker=markers[idx],
                    color=colors[idx], label=sched.name, capsize=3, linewidth=1.5)

    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Optimal (C*/C*=1)')
    ax.set_xlabel('Number of Tasks (N)')
    ax.set_ylabel('Competitive Ratio (C_alg / C*)')
    ax.set_title('Experiment 2: Competitive Ratio vs Task Count (M=8, Uniform Speeds)', fontweight='bold')
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(alpha=0.3)
    ax.set_ylim(bottom=0.9)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig2_competitive_ratio_vs_n.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  -> Saved fig2_competitive_ratio_vs_n.png")


def run_experiment_3():
    """E3: Alpha sweep — HAS performance as function of batch fraction."""
    print("\n" + "="*60)
    print("EXPERIMENT 3: Alpha Sweep (HAS Parameter Sensitivity)")
    print("="*60)

    M = 8
    N = 200
    n_trials = 30
    alpha_values = np.arange(0.0, 1.05, 0.05)

    optimal = OfflineOptimalScheduler(max_brute_force=15)
    ratios_uniform = {a: [] for a in alpha_values}
    ratios_pareto = {a: [] for a in alpha_values}

    for trial in range(n_trials):
        # Uniform tasks
        tg1 = TaskGenerator(seed=trial)
        tasks_u = tg1.uniform(N, 1.0, 100.0)
        agents_opt = AgentPool.uniform(M, seed=42)
        c_star_u = optimal.schedule(agents_opt, tasks_u)

        # Pareto tasks
        tg2 = TaskGenerator(seed=trial + 1000)
        tasks_p = tg2.pareto(N, alpha=1.5, scale=10.0)
        agents_opt2 = AgentPool.uniform(M, seed=42)
        c_star_p = optimal.schedule(agents_opt2, tasks_p)

        for alpha in alpha_values:
            has = HybridAdaptiveScheduler(alpha=round(alpha, 2))

            agents = AgentPool.uniform(M, seed=42)
            ms = has.schedule(agents, tasks_u)
            ratios_uniform[alpha].append(ms / c_star_u if c_star_u > 0 else 1.0)

            agents2 = AgentPool.uniform(M, seed=42)
            ms2 = has.schedule(agents2, tasks_p)
            ratios_pareto[alpha].append(ms2 / c_star_p if c_star_p > 0 else 1.0)

    # ── Plot ──────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))

    alphas = sorted(ratios_uniform.keys())
    means_u = [np.mean(ratios_uniform[a]) for a in alphas]
    stds_u = [np.std(ratios_uniform[a]) for a in alphas]
    means_p = [np.mean(ratios_pareto[a]) for a in alphas]
    stds_p = [np.std(ratios_pareto[a]) for a in alphas]

    ax.fill_between(alphas, [m-s for m,s in zip(means_u, stds_u)],
                     [m+s for m,s in zip(means_u, stds_u)], alpha=0.2, color='#3498db')
    ax.plot(alphas, means_u, 'o-', color='#3498db', label='Uniform Tasks', linewidth=2, markersize=4)

    ax.fill_between(alphas, [m-s for m,s in zip(means_p, stds_p)],
                     [m+s for m,s in zip(means_p, stds_p)], alpha=0.2, color='#e74c3c')
    ax.plot(alphas, means_p, 's-', color='#e74c3c', label='Pareto Tasks', linewidth=2, markersize=4)

    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('Batch Parameter alpha')
    ax.set_ylabel('Competitive Ratio (C_HAS / C*)')
    ax.set_title('Experiment 3: HAS Performance vs Batch Parameter alpha (M=8, N=200)', fontweight='bold')
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig3_alpha_sweep.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  -> Saved fig3_alpha_sweep.png")


def run_experiment_4():
    """E4: Heterogeneity impact — identical vs uniform vs bimodal agents."""
    print("\n" + "="*60)
    print("EXPERIMENT 4: Impact of Agent Heterogeneity")
    print("="*60)

    M = 8
    N = 200
    n_trials = 30

    agent_configs = {
        "Identical": lambda: AgentPool.identical(M),
        "Uniform\n(1-10x)": lambda: AgentPool.uniform(M, (1.0, 10.0), seed=42),
        "Bimodal\n(1x/10x)": lambda: AgentPool.bimodal(M, 1.0, 10.0, 0.3, seed=42),
    }

    schedulers = [
        OnlineGreedyScheduler(),
        OfflineLPTScheduler(),
        HybridAdaptiveScheduler(alpha=0.5),
    ]
    optimal = OfflineOptimalScheduler(max_brute_force=15)

    results = {}
    for config_name in agent_configs:
        results[config_name] = {s.name: [] for s in schedulers}

    for config_name, make_agents in agent_configs.items():
        for trial in range(n_trials):
            tg = TaskGenerator(seed=trial)
            tasks = tg.uniform(N, 1.0, 100.0)

            agents_opt = make_agents()
            c_star = optimal.schedule(agents_opt, tasks)

            for sched in schedulers:
                agents = make_agents()
                ms = sched.schedule(agents, tasks)
                ratio = ms / c_star if c_star > 0 else 1.0
                results[config_name][sched.name].append(ratio)

    # ── Plot: Grouped bar chart ───────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    configs = list(agent_configs.keys())
    sched_names = [s.name for s in schedulers]
    x = np.arange(len(configs))
    width = 0.25
    colors = ['#e74c3c', '#2ecc71', '#3498db']

    for idx, sname in enumerate(sched_names):
        means = [np.mean(results[c][sname]) for c in configs]
        stds = [np.std(results[c][sname]) for c in configs]
        short = sname.replace("Online Greedy (ECT)", "Online Greedy").replace("HAS (a=0.50)", "HAS (a=0.5)")
        ax.bar(x + idx * width, means, width, yerr=stds, label=short,
               color=colors[idx], capsize=3, edgecolor='black', linewidth=0.5)

    ax.set_xticks(x + width)
    ax.set_xticklabels(configs)
    ax.set_ylabel('Competitive Ratio (C_alg / C*)')
    ax.set_title('Experiment 4: Impact of Agent Heterogeneity (M=8, N=200)', fontweight='bold')
    ax.legend(framealpha=0.9)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(bottom=0.9)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig4_heterogeneity_impact.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  -> Saved fig4_heterogeneity_impact.png")


def run_experiment_5():
    """E5: Scalability — runtime and makespan vs N."""
    print("\n" + "="*60)
    print("EXPERIMENT 5: Scalability Analysis")
    print("="*60)

    M = 8
    N_values = [50, 100, 200, 500, 1000, 2000, 5000]
    n_trials = 5

    schedulers = [
        OnlineGreedyScheduler(),
        OfflineLPTScheduler(),
        HybridAdaptiveScheduler(alpha=0.5),
    ]

    runtimes = {s.name: {N: [] for N in N_values} for s in schedulers}

    for N in N_values:
        print(f"  N={N}...", end=" ", flush=True)
        for trial in range(n_trials):
            tg = TaskGenerator(seed=trial)
            tasks = tg.uniform(N, 1.0, 100.0)

            for sched in schedulers:
                agents = AgentPool.uniform(M, seed=42)
                t0 = time.perf_counter()
                sched.schedule(agents, tasks)
                elapsed = time.perf_counter() - t0
                runtimes[sched.name][N].append(elapsed * 1000)  # ms
        print("done")

    # ── Plot ──────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    markers = ['o', 's', '^']
    colors = ['#e74c3c', '#2ecc71', '#3498db']

    for idx, sched in enumerate(schedulers):
        means = [np.mean(runtimes[sched.name][N]) for N in N_values]
        short = sched.name.replace("Online Greedy (ECT)", "Online Greedy").replace("HAS (a=0.50)", "HAS (a=0.5)")
        ax.plot(N_values, means, f'{markers[idx]}-', color=colors[idx],
                label=short, linewidth=1.5, markersize=5)

    ax.set_xlabel('Number of Tasks (N)')
    ax.set_ylabel('Runtime (ms)')
    ax.set_title('Experiment 5: Scheduler Runtime Scalability (M=8)', fontweight='bold')
    ax.legend(framealpha=0.9)
    ax.grid(alpha=0.3)
    ax.set_xscale('log')
    ax.set_yscale('log')

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig5_scalability.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  -> Saved fig5_scalability.png")


def print_summary_table():
    """Generate summary table for the paper (Table II)."""
    print("\n" + "="*60)
    print("SUMMARY TABLE: Empirical Competitive Ratios")
    print("="*60)

    M = 8
    N = 200
    n_trials = 50

    schedulers = [
        RandomScheduler(seed=0),
        RoundRobinScheduler(),
        OnlineGreedyScheduler(),
        OfflineLPTScheduler(),
        HybridAdaptiveScheduler(alpha=0.3),
        HybridAdaptiveScheduler(alpha=0.5),
        HybridAdaptiveScheduler(alpha=0.7),
    ]
    optimal = OfflineOptimalScheduler(max_brute_force=15)

    configs = {
        "Identical": lambda: AgentPool.identical(M),
        "Uniform": lambda: AgentPool.uniform(M, (1.0, 10.0), seed=42),
        "Bimodal": lambda: AgentPool.bimodal(M, 1.0, 10.0, 0.3, seed=42),
    }

    print(f"\n{'Algorithm':<25}", end="")
    for cfg in configs:
        print(f"  {cfg:>15}", end="")
    print()
    print("-" * 75)

    for sched in schedulers:
        short_name = sched.name[:24]
        print(f"{short_name:<25}", end="")
        for cfg_name, make_agents in configs.items():
            ratios = []
            for trial in range(n_trials):
                tg = TaskGenerator(seed=trial)
                tasks = tg.uniform(N, 1.0, 100.0)
                agents_opt = make_agents()
                c_star = optimal.schedule(agents_opt, tasks)
                agents = make_agents()
                ms = sched.schedule(agents, tasks)
                ratios.append(ms / c_star if c_star > 0 else 1.0)
            mean_r = np.mean(ratios)
            std_r = np.std(ratios)
            print(f"  {mean_r:>6.3f}±{std_r:.3f}", end="")
        print()


if __name__ == "__main__":
    print("=" * 60)
    print("MAS TASK ORCHESTRATION -- EXPERIMENT SUITE")
    print("Paper: Dynamic Load Balancing in Multi-Agent Task Orchestration")
    print("=" * 60)

    run_experiment_1()
    run_experiment_2()
    run_experiment_3()
    run_experiment_4()
    run_experiment_5()
    print_summary_table()

    print("\n[DONE] All experiments complete. Figures saved to:", FIG_DIR)
