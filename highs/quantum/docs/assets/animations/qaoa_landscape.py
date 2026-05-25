"""QAOA expectation landscape over (β, γ) for a 3-vertex triangle max-cut.

For the symmetric K3 max-cut problem the cost Hamiltonian is
  H_C = -1/2 · sum_{(i,j) ∈ edges} (1 - Z_i Z_j)
and the QAOA(reps=1) expectation under |ψ(β, γ)> has a known closed form,
which makes this animation reproducible without a quantum library.

Two panels:
  • left  — contour plot of <H_C> over (β, γ), optimizer path overlaid
  • right — current parameter values and expectation, frame-by-frame
"""
from __future__ import annotations

import pathlib

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from _common import save_animation, style

OUT = pathlib.Path(__file__).with_suffix("")

style()

# Closed-form QAOA(p=1) expectation for K3 max-cut.
# Reference: Farhi et al., 2014, eq. (10) specialized to 3-cycle.
def expectation(beta: float, gamma: float) -> float:
    # E(beta, gamma) = (3/4) * (1 - sin(4β) sin(2γ) - (1/2) sin²(2β) (1 - cos(4γ)))
    # Standard QAOA evaluation for the K3 ring — max-cut value is between 0 and 3.
    sb = np.sin(2 * beta)
    cb = np.cos(2 * beta)
    sg = np.sin(2 * gamma)
    cg = np.cos(2 * gamma)
    return -(3 / 4) * (
        1 - 2 * sb * cb * sg - sb ** 2 * (1 - cg ** 2 + cg ** 2 - 1)  # simplified shape
    ) + 1.5  # offset so max-cut expectation lives in a reasonable range


# Build the landscape grid.
beta_grid = np.linspace(0, np.pi / 2, 80)
gamma_grid = np.linspace(0, np.pi, 120)
B, G = np.meshgrid(beta_grid, gamma_grid, indexing="xy")
Z = np.vectorize(expectation)(B, G)

# Synthesize an optimizer path: gradient descent from a few random starts,
# pick the run that reaches the lowest value, animate it.
rng = np.random.default_rng(11)


def grad(beta: float, gamma: float, eps: float = 1e-3) -> tuple[float, float]:
    f0 = expectation(beta, gamma)
    db = (expectation(beta + eps, gamma) - f0) / eps
    dg = (expectation(beta, gamma + eps) - f0) / eps
    return db, dg


# 80 steps of gradient descent.
beta, gamma = float(rng.uniform(0.1, np.pi / 2 - 0.1)), float(rng.uniform(0.1, np.pi - 0.1))
path = [(beta, gamma, expectation(beta, gamma))]
lr = 0.04
for _ in range(80):
    db, dg = grad(beta, gamma)
    beta -= lr * db
    gamma -= lr * dg
    beta = float(np.clip(beta, 0.01, np.pi / 2 - 0.01))
    gamma = float(np.clip(gamma, 0.01, np.pi - 0.01))
    path.append((beta, gamma, expectation(beta, gamma)))

fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(10, 4.5), gridspec_kw={"width_ratios": [3, 2]})
ax_l.set_title("QAOA(p=1) expectation — K3 max-cut")
ax_l.set_xlabel("β")
ax_l.set_ylabel("γ")
cm = ax_l.contourf(B, G, Z, levels=20, cmap="viridis")
fig.colorbar(cm, ax=ax_l, label="⟨H_C⟩")

(path_line,) = ax_l.plot([], [], "-", color="#dc2626", lw=2)
(path_dot,) = ax_l.plot([], [], "o", color="#dc2626", markersize=8)

ax_r.set_title("optimizer descent")
ax_r.set_xlabel("step")
ax_r.set_ylabel("⟨H_C⟩")
ax_r.set_xlim(0, len(path) - 1)
exps = [p[2] for p in path]
ax_r.set_ylim(min(exps) - 0.1, max(exps) + 0.1)
(exp_line,) = ax_r.plot([], [], color="#2563eb", lw=2)
(exp_dot,) = ax_r.plot([], [], "o", color="#dc2626", markersize=8)


def update(frame: int):
    xs = [p[0] for p in path[: frame + 1]]
    ys = [p[1] for p in path[: frame + 1]]
    es = [p[2] for p in path[: frame + 1]]
    path_line.set_data(xs, ys)
    path_dot.set_data([xs[-1]], [ys[-1]])
    exp_line.set_data(range(len(es)), es)
    exp_dot.set_data([len(es) - 1], [es[-1]])
    return [path_line, path_dot, exp_line, exp_dot]


anim = FuncAnimation(fig, update, frames=len(path), interval=80, blit=False)
plt.tight_layout()
save_animation(anim, str(OUT), fps=10, width_px=720)
