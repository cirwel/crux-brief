"""Tabulate crux-brief runs against HYPOTHESES.md definitions.

Usage:
    python3 -m crux_brief.analyze runs/full > results/tables.md
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from .metrics import (
    advisor_flagged_flaw,
    decision_verified_catch,
    format_wilson,
    matches_oracle,
    mcnemar_exact_p,
)
from .scenarios import SCENARIOS
from .smoke_scenarios import SMOKE_SCENARIOS

ARMS = ("raw", "single", "consensus", "crux")
DOMAINS = ("job_offers", "leases", "procurement_handoffs", "operational_briefs")


def _scenario_map() -> dict[str, Any]:
    return {s.id: s for s in (*SMOKE_SCENARIOS, *SCENARIOS)}


def _load_stage1(root: Path) -> list[dict[str, Any]]:
    smap = _scenario_map()
    rows: list[dict[str, Any]] = []
    for p in sorted((root / "stage1").rglob("*.json")):
        rec = json.loads(p.read_text())
        s = smap[rec["scenario_id"]]
        rec["recomputed_caught"] = (
            advisor_flagged_flaw(rec["output"], s.oracle_markers)
            if rec["variant"] == "flawed"
            else None
        )
        rec["recomputed_hold"] = rec["output"].get("recommendation") == "hold_to_verify"
        rows.append(rec)
    return rows


def _load_eval(root: Path, subdir: str = "eval") -> list[dict[str, Any]]:
    smap = _scenario_map()
    rows: list[dict[str, Any]] = []
    target = root / subdir
    if not target.exists():
        return rows
    for p in sorted(target.rglob("*.json")):
        rec = json.loads(p.read_text())
        s = smap[rec["scenario_id"]]
        for arm in ARMS:
            d = rec["decisions"][arm]
            out = d["output"]
            is_hold = out.get("action") == "hold_to_verify"
            d["hold"] = is_hold
            if rec["variant"] == "flawed":
                vc = decision_verified_catch(out, s.oracle_markers)
                d["verified_catch"] = vc
                d["untargeted_hold"] = bool(is_hold and not vc)
            else:
                d["false_alarm"] = is_hold
        if rec["variant"] == "flawed":
            rec["recomputed_survived"] = {
                arm: bool(matches_oracle(rec["briefs"][arm]["text"], s.oracle_markers))
                for arm in ("single", "consensus", "crux")
            }
        rows.append(rec)
    return rows


def _med(xs: list[float]) -> float:
    if not xs:
        return float("nan")
    s = sorted(xs)
    mid = len(s) // 2
    return s[mid] if len(s) % 2 == 1 else (s[mid - 1] + s[mid]) / 2.0


def _mean(xs: list[float]) -> str:
    if not xs:
        return "n/a (0)"
    return f"{sum(xs) / len(xs):.2f} (n={len(xs)})" if max(xs) <= 5.0 else f"{sum(xs) / len(xs):.1f} (n={len(xs)})"


def _mcnemar_pair(rows: list[dict[str, Any]], arm_a: str, arm_b: str, field: str) -> tuple[int, int, float]:
    """Return (a_only, b_only, exact_p) across paired records."""
    a_only = sum(bool(r["decisions"][arm_a][field]) and not bool(r["decisions"][arm_b][field]) for r in rows)
    b_only = sum(bool(r["decisions"][arm_b][field]) and not bool(r["decisions"][arm_a][field]) for r in rows)
    return a_only, b_only, mcnemar_exact_p(a_only, b_only)


def _pair_twin_outcomes(rows: list[dict[str, Any]], arm: str) -> list[bool]:
    """Return list of bools (one per scenario pair) where flawed caught AND sound not held."""
    by_pair: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for r in rows:
        key = (r["eval_model"], r["scenario_id"])
        by_pair[key][r["variant"]] = r
    outcomes: list[bool] = []
    for key in sorted(by_pair):
        pair = by_pair[key]
        if "flawed" in pair and "sound" in pair:
            ok = bool(pair["flawed"]["decisions"][arm]["verified_catch"]) and not bool(
                pair["sound"]["decisions"][arm]["false_alarm"]
            )
            outcomes.append(ok)
    return outcomes


def _mcnemar_twin_pair(rows: list[dict[str, Any]], arm_a: str, arm_b: str) -> tuple[int, int, float]:
    """Exact McNemar discordant twin counts (a_only_both_ok, b_only_both_ok, p)."""
    ok_a = _pair_twin_outcomes(rows, arm_a)
    ok_b = _pair_twin_outcomes(rows, arm_b)
    a_only = sum(a and not b for a, b in zip(ok_a, ok_b))
    b_only = sum(b and not a for a, b in zip(ok_a, ok_b))
    return a_only, b_only, mcnemar_exact_p(a_only, b_only)


def _short_label(rec: dict[str, Any]) -> str:
    synth = rec.get("synth_model")
    dec = rec["eval_model"]
    return f"{synth} -> {dec}" if synth else dec


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/full")
    s1 = _load_stage1(root)
    ev = _load_eval(root, "eval")

    print(f"# Results from `{root}` ({len(s1)} Stage-1 calls, {len(ev)} cross-family Stage-3 evaluations)\n")
    print("Rates are `k/n = p [95% Wilson CI]`. Flawed and sound packets are never pooled.\n")

    # ---------------- Table 1: Stage-1 Advisor Panel & Splits ----------------
    print("## Table 1. Stage-1 independent advisor accuracy and panel split distribution\n")
    print("| Advisor model | Flawed caught (`hold` + oracle match) | Flawed raw holds | Sound false alarms |")
    print("|---|---|---|---|")
    by_adv: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in s1:
        by_adv[r["model"]].append(r)
    for model, rs in sorted(by_adv.items()):
        fl = [r for r in rs if r["variant"] == "flawed"]
        so = [r for r in rs if r["variant"] == "sound"]
        caught = sum(bool(r["recomputed_caught"]) for r in fl)
        raw_hold = sum(bool(r["recomputed_hold"]) for r in fl)
        fa = sum(bool(r["recomputed_hold"]) for r in so)
        print(f"| {model} | {format_wilson(caught, len(fl))} | {format_wilson(raw_hold, len(fl))} | {format_wilson(fa, len(so))} |")

    flawed_by_scen: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in s1:
        if r["variant"] == "flawed":
            flawed_by_scen[r["scenario_id"]].append(r)
    split_counts = {k: 0 for k in (0, 1, 2, 3)}
    for sid, rs in sorted(flawed_by_scen.items()):
        k = sum(bool(r["recomputed_caught"]) for r in rs)
        split_counts[k] = split_counts.get(k, 0) + 1
    n_scens = len(flawed_by_scen)
    print(
        f"\nPanel split distribution across `{n_scens}` flawed scenarios (`k_spotted` of 3 advisors): "
        + ", ".join(f"`k={k}`: {split_counts[k]}/{n_scens}" for k in (0, 1, 2, 3))
        + f" (split panel `k in {{1,2}}`: {split_counts[1] + split_counts[2]}/{n_scens}).\n"
    )

    # ---------------- Table 2: Headline Stage-3 Paired Results ----------------
    print("## Table 2. Cross-family Stage-3 decision outcomes by `(synth -> decider)` and arm\n")
    print("| Synth -> Decider | Arm | Flawed verified catch | Flawed untargeted hold | Sound false alarm | Paired twin accuracy | Net J |")
    print("|---|---|---|---|---|---|---|")
    by_eval: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in ev:
        by_eval[r["eval_model"]].append(r)

    for eval_model, rs in sorted(by_eval.items()):
        pair_label = _short_label(rs[0])
        fl = [r for r in rs if r["variant"] == "flawed"]
        so = [r for r in rs if r["variant"] == "sound"]
        for arm in ARMS:
            vc = sum(bool(r["decisions"][arm]["verified_catch"]) for r in fl)
            uh = sum(bool(r["decisions"][arm]["untargeted_hold"]) for r in fl)
            fa = sum(bool(r["decisions"][arm]["false_alarm"]) for r in so)
            twins = _pair_twin_outcomes(rs, arm)
            twin_ok = sum(twins)
            j_val = (vc / len(fl) if fl else 0.0) - (fa / len(so) if so else 0.0)
            print(
                f"| {pair_label} | {arm} | {format_wilson(vc, len(fl))} | "
                f"{format_wilson(uh, len(fl))} | {format_wilson(fa, len(so))} | "
                f"{format_wilson(twin_ok, len(twins))} | {j_val:+.2f} |"
            )

    print("\n### Paired exact McNemar comparisons (discordant `crux_only / other_only`, two-sided exact p)\n")
    print("Note: `Pooled (2 deciders)` pools observations across both cross-family deciders on the same scenario set; per-decider rows test exact paired differences within one model.\n")
    print("| Scope | Comparison | Flawed verified catch | Sound false alarm | Paired twin accuracy |")
    print("|---|---|---|---|---|")
    scopes: list[tuple[str, list[dict[str, Any]]]] = [
        (_short_label(rs[0]), rs) for _, rs in sorted(by_eval.items())
    ]
    if len(by_eval) > 1:
        scopes.append(("Pooled (2 deciders)", ev))
    for scope_label, rs in scopes:
        fl = [r for r in rs if r["variant"] == "flawed"]
        so = [r for r in rs if r["variant"] == "sound"]
        for other in ("raw", "single", "consensus"):
            b1, c1, p1 = _mcnemar_pair(fl, "crux", other, "verified_catch")
            b2, c2, p2 = _mcnemar_pair(so, "crux", other, "false_alarm")
            b3, c3, p3 = _mcnemar_twin_pair(rs, "crux", other)
            print(
                f"| {scope_label} | crux vs {other} | "
                f"{b1} / {c1} (p={p1:.4f}) | {b2} / {c2} (p={p2:.4f}) | {b3} / {c3} (p={p3:.4f}) |"
            )

    # ---------------- Table 3: Mechanism Stratified by Panel Split ----------------
    print("\n## Table 3. Mechanism by advisor panel split (`k_spotted` on flawed packets)\n")
    print("| Decider model | Stratum (`k_spotted`) | n | Brief survived: consensus vs crux | Verified catch: single / consensus / crux |")
    print("|---|---|---|---|---|")
    strata = [("k=0", (0,)), ("k=1", (1,)), ("k=2", (2,)), ("k=3", (3,)), ("split (1 or 2)", (1, 2))]
    for eval_model, rs in sorted(by_eval.items()):
        fl = [r for r in rs if r["variant"] == "flawed"]
        for label, ks in strata:
            sub = [r for r in fl if r.get("k_spotted") in ks]
            n = len(sub)
            if n == 0:
                print(f"| {eval_model} | {label} | 0 | n/a | n/a |")
                continue
            surv_b = sum(bool(r["recomputed_survived"]["consensus"]) for r in sub)
            surv_c = sum(bool(r["recomputed_survived"]["crux"]) for r in sub)
            vc_s = sum(bool(r["decisions"]["single"]["verified_catch"]) for r in sub)
            vc_b = sum(bool(r["decisions"]["consensus"]["verified_catch"]) for r in sub)
            vc_c = sum(bool(r["decisions"]["crux"]["verified_catch"]) for r in sub)
            print(
                f"| {eval_model} | {label} | {n} | "
                f"{surv_b}/{n} vs {surv_c}/{n} | {vc_s}/{n} / {vc_b}/{n} / {vc_c}/{n} |"
            )

    print("\n### Stage-3 flawed verified catch conditioned on whether the brief already named an oracle marker\n")
    print("| Decider model | Arm | Catch when brief named flaw (`survived=True`) | Catch when brief missed flaw (`survived=False`) |")
    print("|---|---|---|---|")
    for eval_model, rs in sorted(by_eval.items()):
        fl = [r for r in rs if r["variant"] == "flawed"]
        for arm in ("single", "consensus", "crux"):
            pos = [r for r in fl if r["recomputed_survived"][arm]]
            neg = [r for r in fl if not r["recomputed_survived"][arm]]
            vc_pos = sum(bool(r["decisions"][arm]["verified_catch"]) for r in pos)
            vc_neg = sum(bool(r["decisions"][arm]["verified_catch"]) for r in neg)
            print(
                f"| {eval_model} | {arm} | {format_wilson(vc_pos, len(pos))} | {format_wilson(vc_neg, len(neg))} |"
            )

    # ---------------- Table 4: Domain Breakdown ----------------
    print("\n## Table 4. Domain breakdown (flawed verified catch / sound false alarm)\n")
    print("| Decider model | Domain | raw | single | consensus | crux |")
    print("|---|---|---|---|---|---|")
    for eval_model, rs in sorted(by_eval.items()):
        for dom in DOMAINS:
            fl = [r for r in rs if r["variant"] == "flawed" and r["domain"] == dom]
            so = [r for r in rs if r["variant"] == "sound" and r["domain"] == dom]
            cells = []
            for arm in ARMS:
                vc = sum(bool(r["decisions"][arm]["verified_catch"]) for r in fl)
                fa = sum(bool(r["decisions"][arm]["false_alarm"]) for r in so)
                cells.append(f"{vc}/{len(fl)} catch, {fa}/{len(so)} FA")
            print(f"| {eval_model} | {dom} | " + " | ".join(cells) + " |")

    # ---------------- Table 5: Length Control, Cost, and Comfort Gap ----------------
    print("\n## Table 5. Briefing length parity, runtime cost, and comfort gap\n")
    print("| Decider model | Arm | Median brief words | Median synth+decide s | Mean conf (missed flawed) | Mean endorse (missed flawed) | Mean endorse (all) |")
    print("|---|---|---|---|---|---|---|")
    for eval_model, rs in sorted(by_eval.items()):
        fl = [r for r in rs if r["variant"] == "flawed"]
        for arm in ARMS:
            words = [float(r["briefs"][arm]["words"]) for r in rs] if arm != "raw" else []
            w_str = f"{_med(words):.0f}" if words else "0 (no brief)"
            secs = []
            for r in rs:
                d_sec = float(r["decisions"][arm]["meta"]["seconds"])
                s_sec = float(r["briefs"][arm]["meta"]["seconds"]) if arm in ("consensus", "crux") else 0.0
                secs.append(d_sec + s_sec)
            missed = [r for r in fl if not r["decisions"][arm]["hold"]]
            conf_missed = [float(r["decisions"][arm]["output"].get("confidence") or 0) for r in missed]
            end_missed = [
                float(r["decisions"][arm]["output"]["brief_endorsement"])
                for r in missed
                if r["decisions"][arm]["output"].get("brief_endorsement") is not None
            ]
            end_all = [
                float(r["decisions"][arm]["output"]["brief_endorsement"])
                for r in rs
                if r["decisions"][arm]["output"].get("brief_endorsement") is not None
            ]
            print(
                f"| {eval_model} | {arm} | {w_str} | {_med(secs):.1f} | "
                f"{_mean(conf_missed)} | {_mean(end_missed)} | {_mean(end_all)} |"
            )

    # ---------------- Table 6: Same-Family vs Cross-Family Synthesizer Ablation ----------------
    ab_rows = _load_eval(root, "ablation_same_model")
    if ab_rows:
        print("\n## Table 6. Same-family (`gemma4 -> gemma4`) vs. Cross-family (`nemotron3 -> gemma4`) synthesizer check\n")
        print("| Pair | Arm | Flawed verified catch | Sound false alarm | Paired twin accuracy | Net J | Mean endorse (all) |")
        print("|---|---|---|---|---|---|---|")
        gemma_cross = by_eval.get("gemma4:latest", [])
        for pair_name, rs in (("Cross: nemotron3 -> gemma4", gemma_cross), ("Same: gemma4 -> gemma4", ab_rows)):
            if not rs:
                continue
            fl = [r for r in rs if r["variant"] == "flawed"]
            so = [r for r in rs if r["variant"] == "sound"]
            for arm in ("consensus", "crux"):
                vc = sum(bool(r["decisions"][arm]["verified_catch"]) for r in fl)
                fa = sum(bool(r["decisions"][arm]["false_alarm"]) for r in so)
                twins = _pair_twin_outcomes(rs, arm)
                j_val = (vc / len(fl) if fl else 0.0) - (fa / len(so) if so else 0.0)
                end_all = [
                    float(r["decisions"][arm]["output"]["brief_endorsement"])
                    for r in rs
                    if r["decisions"][arm]["output"].get("brief_endorsement") is not None
                ]
                print(
                    f"| {pair_name} | {arm} | {format_wilson(vc, len(fl))} | "
                    f"{format_wilson(fa, len(so))} | {format_wilson(sum(twins), len(twins))} | "
                    f"{j_val:+.2f} | {_mean(end_all)} |"
                )


if __name__ == "__main__":
    main()
