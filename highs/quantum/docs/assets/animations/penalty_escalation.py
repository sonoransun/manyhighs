"""Adaptive penalty escalation on a tiny set-partitioning instance.

Problem: min x0 + x1 + x2 s.t. x0 + x1 + x2 = 2, x ∈ {0,1}^3.
Optimal feasible value = 2 (e.g. (1,1,0)).

We show simulated annealing with three penalty values: P=1 (too weak),
P=4, P=16 (sufficient). For each P, run SA for 60 steps and report the
best-found objective + constraint violation. The animation cycles through
the three penalty levels.
"""
from __future__ import annotations

import pathlib

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

from _common import save_animation, style

OUT = pathlib.Path(__file__).with_suffix("")

style()


def run_sa(penalty: float, seed: int) -> tuple[list[np.ndarray], list[float], list[float]]:
    """Run SA on the penalty-reformulated problem; return (assignments, objs, violations)."""
    rng = np.random.default_rng(seed)
    n = 3
    target_sum = 2
    obj_coefs = np.array([1.0, 1.0, 1.0])

    def evaluate(x: np.ndarray) -> tuple[float, float]:
        """Returns (penalized_energy, raw_violation)."""
        sum_x = float(x.sum())
        viol = (sum_x - target_sum) ** 2
        obj = float(obj_coefs @ x)
        return obj + penalty * viol, viol

    x = rng.integers(0, 2, size=n).astype(np.float64)
    assignments = [x.copy()]
    energies = []
    violations = []
    e, v = evaluate(x)
    energies.append(e); violations.append(v)
    T_start, T_end, steps = 5.0, 0.05, 60
    for k in range(steps):
        T = T_start * (T_end / T_start) ** (k / steps)
        i = int(rng.integers(0, n))
        x_try = x.copy()
        x_try[i] = 1 - x_try[i]
        e_try, v_try = evaluate(x_try)
        delta = e_try - e
        if delta <= 0 or rng.random() < np.exp(-delta / max(T, 1e-9)):
            x = x_try
            e = e_try
            v = v_try
        assignments.append(x.copy())
        energies.append(e)
        violations.append(v)
    return assignments, energies, violations


# Run three penalty levels with the same seed.
runs = {p: run_sa(p, seed=42) for p in [1.0, 4.0, 16.0]}

# Build per-frame list: cycle P=1, P=4, P=16 with title text showing which.
frames_per_run = 60
TOTAL = frames_per_run * 3
penalty_at = []
phase_idx = []
for p in [1.0, 4.0, 16.0]:
    for k in range(frames_per_run):
        penalty_at.append(p)
        phase_idx.append(k)

fig, (ax_b, ax_v) = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={"width_ratios": [2, 3]})
ax_b.set_title("current assignment")
ax_b.set_xlim(-0.5, 2.5)
ax_b.set_ylim(-0.6, 0.6)
ax_b.set_xticks(range(3))
ax_b.set_yticks([])
ax_b.grid(False)
squares = [Rectangle((i - 0.4, -0.4), 0.8, 0.8, lw=1.5, edgecolor="#374151") for i in range(3)]
for sq in squares:
    ax_b.add_patch(sq)

ax_v.set_title("constraint violation by step")
ax_v.set_xlabel("step within run")
ax_v.set_ylabel("(Σx − 2)²")
ax_v.set_xlim(0, frames_per_run)
ax_v.set_ylim(-0.2, 4.5)
(viol_line,) = ax_v.plot([], [], color="#dc2626", lw=2)
(viol_dot,) = ax_v.plot([], [], "o", color="#dc2626", markersize=8)

penalty_text = fig.suptitle("", fontsize=13, fontweight="bold")


def update(frame: int):
    p = penalty_at[frame]
    k = phase_idx[frame]
    assignments, _, violations = runs[p]
    x_now = assignments[k]
    for i, sq in enumerate(squares):
        sq.set_facecolor("#3b82f6" if x_now[i] > 0.5 else "#e5e7eb")
    sum_x = int(x_now.sum())
    feasible = sum_x == 2
    color = "#16a34a" if feasible else "#dc2626"
    label = "feasible" if feasible else f"violation = {violations[k]:.1f}"
    penalty_text.set_text(
        f"penalty escalation:  P = {int(p)}     —     Σx = {sum_x}     [{label}]"
    )
    penalty_text.set_color(color)
    viol_line.set_data(range(k + 1), violations[: k + 1])
    viol_dot.set_data([k], [violations[k]])
    return list(squares) + [viol_line, viol_dot, penalty_text]


anim = FuncAnimation(fig, update, frames=TOTAL, interval=80, blit=False)
plt.tight_layout(rect=(0, 0, 1, 0.94))
save_animation(anim, str(OUT), fps=10, width_px=720)
