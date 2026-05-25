"""Animate RINS-style variable classification.

Twenty binary variables. Each frame the LP relaxation drifts (we synthesize
a sequence of relaxations approaching integrality), and we compare against
a fixed incumbent. Variables whose LP value matches the incumbent (within
tolerance) become "fixed" and drop out of the QUBO subproblem; the rest stay
"free" and form what gets shipped to the backend.

Two panels:
  • top    — LP relaxation values (continuous bars) vs incumbent (markers)
  • bottom — current count of fixed (gray) vs free (blue) cols, plus
             "subproblem size" annotation that shrinks frame by frame
"""
from __future__ import annotations

import pathlib

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from _common import save_animation, style

OUT = pathlib.Path(__file__).with_suffix("")

style()

N = 20
rng = np.random.default_rng(3)
incumbent = rng.integers(0, 2, size=N).astype(np.float64)

# Build a sequence of LP relaxation values that drifts toward the incumbent
# over time — initially fractional, eventually integral. Real B&B doesn't
# quite work this way (more abrupt), but this visualizes the spirit.
STEPS = 80
trajectory = []
lp = rng.uniform(0.05, 0.95, size=N)  # initial fractional relaxation
for k in range(STEPS):
    # Each step, nudge LP values toward the nearest integer.
    target = np.where(lp >= 0.5, 1.0, 0.0)
    lp = 0.93 * lp + 0.07 * target + rng.normal(0, 0.005, size=N)
    lp = np.clip(lp, 0.0, 1.0)
    trajectory.append(lp.copy())

TOL = 0.05  # match tolerance — same default the C++ side uses


def classify(lp_vals: np.ndarray) -> np.ndarray:
    """True if LP value matches incumbent within TOL (→ fixed)."""
    return np.abs(lp_vals - incumbent) <= TOL


fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(10, 5.5),
                                     gridspec_kw={"height_ratios": [3, 1]})
ax_top.set_title("RINS classification: LP relaxation vs incumbent")
ax_top.set_xlim(-0.5, N - 0.5)
ax_top.set_ylim(0, 1.05)
ax_top.set_xticks(range(N))
ax_top.set_xlabel("binary variable index")
ax_top.set_ylabel("value")

bar_container = ax_top.bar(range(N), trajectory[0], color="#3b82f6", edgecolor="#1e3a8a", lw=0.6)
# Incumbent markers (constant across frames).
ax_top.scatter(range(N), incumbent, color="#dc2626", marker="D", s=60, zorder=10, label="incumbent")
ax_top.legend(loc="upper right")

ax_bot.set_xlim(-0.5, N - 0.5)
ax_bot.set_ylim(0, 1)
ax_bot.set_yticks([])
ax_bot.set_xticks([])
ax_bot.set_xlabel("variable classification (gray = fixed → drop, blue = free → subproblem)")
class_bars = ax_bot.bar(range(N), [1] * N, color="#9ca3af", edgecolor="white", lw=1)

size_text = ax_bot.text(0.5, -0.35, "", transform=ax_bot.transAxes,
                        ha="center", fontsize=12, color="#1f2937",
                        fontweight="bold")


def update(frame: int):
    lp_vals = trajectory[frame]
    for i, rect in enumerate(bar_container):
        rect.set_height(lp_vals[i])
    fixed = classify(lp_vals)
    free_count = int((~fixed).sum())
    for i, rect in enumerate(class_bars):
        rect.set_color("#9ca3af" if fixed[i] else "#3b82f6")
    size_text.set_text(f"subproblem: {free_count} free vars (out of {N})")
    return list(bar_container) + list(class_bars) + [size_text]


anim = FuncAnimation(fig, update, frames=STEPS, interval=80, blit=False)
plt.tight_layout()
save_animation(anim, str(OUT), fps=10, width_px=720)
