"""Generate Figure 1 and Figure 2 for the crux-brief report.

Usage:
    python3 -m crux_brief.figures runs/full results
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .analyze import ARMS, _load_eval  # noqa: E402
from .metrics import wilson_ci  # noqa: E402

ARM_LABELS = {
    "raw": "Raw\n(no brief)",
    "single": "Single\nadvisor",
    "consensus": "Consensus\n(common ground)",
    "crux": "Crux\nBrief",
}
ARM_COLORS = {
    "raw": "#9aa5b1",
    "single": "#64748b",
    "consensus": "#3b82f6",
    "crux": "#16a34a",
}


def make_figure1(ev: list[dict[str, Any]], out_path: Path) -> None:
    """Two-panel bar chart: Verified Flaw Catch Rate vs. Sound False Alarm Rate."""
    by_eval: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in ev:
        by_eval[r["eval_model"]].append(r)

    models = sorted(by_eval)
    fig, axes = plt.subplots(1, len(models), figsize=(5.4 * len(models), 3.7), sharey=True)
    if len(models) == 1:
        axes = [axes]

    width = 0.34
    for ax, model in zip(axes, models):
        rs = by_eval[model]
        fl = [r for r in rs if r["variant"] == "flawed"]
        so = [r for r in rs if r["variant"] == "sound"]

        xs = list(range(len(ARMS)))
        catch_p, catch_lo, catch_hi = [], [], []
        fa_p, fa_lo, fa_hi = [], [], []
        for arm in ARMS:
            vc = sum(bool(r["decisions"][arm]["verified_catch"]) for r in fl)
            p, lo, hi = wilson_ci(vc, len(fl))
            catch_p.append(p)
            catch_lo.append(p - lo)
            catch_hi.append(hi - p)

            fa = sum(bool(r["decisions"][arm]["false_alarm"]) for r in so)
            p2, lo2, hi2 = wilson_ci(fa, len(so))
            fa_p.append(p2)
            fa_lo.append(p2 - lo2)
            fa_hi.append(hi2 - p2)

        b1 = ax.bar(
            [x - width / 2 for x in xs],
            catch_p,
            width,
            yerr=[catch_lo, catch_hi],
            capsize=3,
            color="#16a34a",
            label=f"Verified catch on flawed (n={len(fl)})",
        )
        b2 = ax.bar(
            [x + width / 2 for x in xs],
            fa_p,
            width,
            yerr=[fa_lo, fa_hi],
            capsize=3,
            color="#dc2626",
            alpha=0.82,
            label=f"False alarm on sound (n={len(so)})",
        )
        for bars in (b1, b2):
            for bar in bars:
                h = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    min(1.02, h + 0.03),
                    f"{h:.2f}",
                    ha="center",
                    va="bottom",
                    fontsize=7.5,
                )

        ax.set_xticks(xs)
        ax.set_xticklabels([ARM_LABELS[a] for a in ARMS], fontsize=8.5)
        synth = rs[0].get("synth_model")
        title = f"{synth.split(':')[0]} synth -> {model.split(':')[0]} decider" if synth else model
        ax.set_title(title, fontsize=10)
        ax.set_ylim(0, 1.15)
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel("Proportion of packets")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=8.5, frameon=False, loc="upper center", ncol=2)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def make_figure2(ev: list[dict[str, Any]], out_path: Path) -> None:
    """Mechanism chart: Flaw survival and downstream rescue by advisor panel split k."""
    by_eval: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in ev:
        if r["variant"] == "flawed":
            by_eval[r["eval_model"]].append(r)

    models = sorted(by_eval)
    fig, axes = plt.subplots(1, len(models), figsize=(5.4 * len(models), 3.6), sharey=True)
    if len(models) == 1:
        axes = [axes]

    ks = (0, 1, 2, 3)
    width = 0.20
    for ax, model in zip(axes, models):
        fl = by_eval[model]
        ns = [sum(1 for r in fl if r.get("k_spotted") == k) for k in ks]

        series = [
            ("Brief survived: Consensus", "recomputed_survived", "consensus", "#93c5fd"),
            ("Brief survived: Crux", "recomputed_survived", "crux", "#86efac"),
            ("Verified catch: Consensus", "decisions", "consensus", "#2563eb"),
            ("Verified catch: Crux", "decisions", "crux", "#15803d"),
        ]
        for s_idx, (label, kind, arm, color) in enumerate(series):
            vals = []
            for k in ks:
                sub = [r for r in fl if r.get("k_spotted") == k]
                if not sub:
                    vals.append(0.0)
                    continue
                if kind == "recomputed_survived":
                    hits = sum(bool(r["recomputed_survived"][arm]) for r in sub)
                else:
                    hits = sum(bool(r["decisions"][arm]["verified_catch"]) for r in sub)
                vals.append(hits / len(sub))
            xs = [i + (s_idx - 1.5) * width for i in range(len(ks))]
            ax.bar(xs, vals, width, color=color, label=label)

        ax.set_xticks(range(len(ks)))
        ax.set_xticklabels([f"k={k}/3\n(n={n})" for k, n in zip(ks, ns)], fontsize=8.5)
        synth = fl[0].get("synth_model")
        title = f"{synth.split(':')[0]} synth -> {model.split(':')[0]} decider" if synth else model
        ax.set_title(title, fontsize=10)
        ax.set_ylim(0, 1.12)
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel("Share of flawed packets")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=8, frameon=False, loc="upper center", ncol=2)
    fig.tight_layout(rect=(0, 0, 1, 0.87))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def main() -> None:
    run_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/full")
    out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "results")
    ev = _load_eval(run_dir)
    f1 = out_dir / "figure1.png"
    f2 = out_dir / "figure2.png"
    make_figure1(ev, f1)
    make_figure2(ev, f2)
    print(f1)
    print(f2)


if __name__ == "__main__":
    main()
