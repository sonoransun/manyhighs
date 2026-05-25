"""Simulated annealing on a 10-bit max-cut Ising instance.

Two panels:
  • left  — energy vs SA step (line plot, with current step highlighted)
  • right — current bit string (10 colored squares), flipped bits flash

The trajectory comes from a real SA run on a small random Ising; the
animation is the first 200 steps of one descent.
"""
from __future__ import annotations

import os
import pathlib

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

from _common import save_animation, style

OUT = pathlib.Path(__file__).with_suffix("")

style()

# Build a 10-bit Ising instance: small random complete graph weights.
N = 10
rng = np.random.default_rng(7)
J = rng.normal(0, 1, size=(N, N))
J = (J + J.T) / 2
np.fill_diagonal(J, 0.0)
h = rng.normal(0, 0.3, size=N)


def energy(x: np.ndarray) -> float:
    # x in {0,1}; spin z = 1 - 2x
    z = 1.0 - 2.0 * x
    return float(h @ z + 0.5 * z @ J @ z)


# Run SA, store the trajectory.
x = rng.integers(0, 2, size=N).astype(np.float64)
e = energy(x)
T_start, T_end = 2.0, 0.05
STEPS = 200
traj_x = [x.copy()]
traj_e = [e]
flip_log = [-1]  # -1 means "no flip" (initial frame)
for k in range(STEPS):
    T = T_start * (T_end / T_start) ** (k / STEPS)
    i = int(rng.integers(0, N))
    flip = 1 - 2 * x[i]  # +1 or -1 spin change
    # delta from flipping x[i]; recompute by direct eval for clarity.
    x_try = x.copy()
    x_try[i] = 1 - x_try[i]
    e_try = energy(x_try)
    delta = e_try - e
    if delta <= 0 or rng.random() < np.exp(-delta / max(T, 1e-9)):
        x = x_try
        e = e_try
        flip_log.append(i)
    else:
        flip_log.append(-1)
    traj_x.append(x.copy())
    traj_e.append(e)

# Plot setup
fig, (ax_e, ax_b) = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={"width_ratios": [3, 2]})
ax_e.set_title("SA energy trajectory")
ax_e.set_xlabel("step")
ax_e.set_ylabel("energy")
ax_e.set_xlim(0, len(traj_e) - 1)
emin = min(traj_e); emax = max(traj_e)
pad = (emax - emin) * 0.1 + 0.01
ax_e.set_ylim(emin - pad, emax + pad)
(line,) = ax_e.plot([], [], color="#2563eb", lw=2)
(cursor,) = ax_e.plot([], [], "o", color="#dc2626", markersize=8)

ax_b.set_title("current bit string")
ax_b.set_xlim(-0.5, N - 0.5)
ax_b.set_ylim(-0.6, 0.6)
ax_b.set_xticks(range(N))
ax_b.set_yticks([])
ax_b.grid(False)
squares = [Rectangle((i - 0.4, -0.4), 0.8, 0.8, lw=1, edgecolor="#374151") for i in range(N)]
for sq in squares:
    ax_b.add_patch(sq)


def update(frame: int):
    line.set_data(range(frame + 1), traj_e[: frame + 1])
    cursor.set_data([frame], [traj_e[frame]])
    x_now = traj_x[frame]
    flipped = flip_log[frame]
    for i, sq in enumerate(squares):
        if i == flipped:
            sq.set_facecolor("#facc15")  # flash yellow on flip
        else:
            sq.set_facecolor("#3b82f6" if x_now[i] > 0.5 else "#e5e7eb")
    return [line, cursor] + squares


# Skip every other frame to keep the GIF tight.
frames = list(range(0, len(traj_e), 2))
anim = FuncAnimation(fig, update, frames=frames, interval=80, blit=False)
plt.tight_layout()
save_animation(anim, str(OUT), fps=10, width_px=720)
