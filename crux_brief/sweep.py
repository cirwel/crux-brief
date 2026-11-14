"""Batched cross-family evaluation sweep runner for crux-brief.

Batches all packets per model to minimize Ollama weight swaps (5 loads total)
and separates Stage-2 synthesis from Stage-3 decision making across distinct
model families. Fully resumable per output JSON file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .metrics import advisor_flagged_flaw, decision_verified_catch, matches_oracle
from .ollama_client import chat_json, model_slug, unload_model
from .prompts import (
    ADVISOR_SYSTEM,
    CONSENSUS_SYSTEM,
    CRUX_SYSTEM,
    DECISION_SYSTEM,
    format_advisor_user,
    format_consensus_brief,
    format_crux_brief,
    format_decision_user,
    format_panel_input,
    format_single_brief,
    shuffle_advisors,
)
from .scenarios import SCENARIOS
from .smoke_scenarios import SMOKE_SCENARIOS, Scenario

ADVISOR_MODELS = ("gemma4:latest", "nemotron3:33b", "qwen3.6:27b-coding-mxfp8")
# Order Stage-1 loads so gemma4:latest finishes warm right before Stage 2 starts.
STAGE1_LOAD_ORDER = ("qwen3.6:27b-coding-mxfp8", "nemotron3:33b", "gemma4:latest")
SYNTH_MODELS = ("gemma4:latest", "nemotron3:33b")
CROSS_PAIRS = (
    ("gemma4:latest", "nemotron3:33b"),
    ("nemotron3:33b", "gemma4:latest"),
)
ARMS = ("raw", "single", "consensus", "crux")


def iter_packets(scenarios: tuple[Scenario, ...]) -> list[tuple[Scenario, str, str]]:
    """Return [(scenario, variant, packet_text), ...]."""
    out: list[tuple[Scenario, str, str]] = []
    for s in scenarios:
        out.append((s, "flawed", s.packet_flawed))
        out.append((s, "sound", s.packet_sound))
    return out


def _save_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def run_stage1_batched(
    packets: list[tuple[Scenario, str, str]],
    *,
    out_dir: Path,
    advisor_models: tuple[str, ...] = ADVISOR_MODELS,
    load_order: tuple[str, ...] = STAGE1_LOAD_ORDER,
    base_seed: int = 100,
) -> None:
    """Pass 1: run Stage-1 advisors batched by model across all packets."""
    ordered = [m for m in load_order if m in advisor_models] + [
        m for m in advisor_models if m not in load_order
    ]
    for model in ordered:
        m_idx = advisor_models.index(model)
        slug = model_slug(model)
        pending = [
            (p_idx, scen, var, txt)
            for p_idx, (scen, var, txt) in enumerate(packets)
            if not (out_dir / "stage1" / slug / f"{scen.id}_{var}.json").exists()
        ]
        if not pending:
            continue
        for other in ordered:
            if other != model:
                unload_model(other)
        print(f"[stage1] model={model} ({len(pending)}/{len(packets)} pending)", flush=True)
        for p_idx, scenario, variant, packet_text in pending:
            out_path = out_dir / "stage1" / slug / f"{scenario.id}_{variant}.json"
            seed = base_seed + m_idx * 1000 + p_idx
            user_prompt = format_advisor_user(scenario.constraints, packet_text)
            out, meta = chat_json(model, ADVISOR_SYSTEM, user_prompt, seed=seed, temperature=0.3)
            caught = advisor_flagged_flaw(out, scenario.oracle_markers) if variant == "flawed" else None
            record = {
                "scenario_id": scenario.id,
                "variant": variant,
                "domain": scenario.domain,
                "difficulty_tier": scenario.difficulty_tier,
                "model": model,
                "seed": seed,
                "output": out,
                "meta": meta,
                "advisor_caught": caught,
            }
            _save_json(out_path, record)
            print(
                f"  {scenario.id}_{variant}: rec={out.get('recommendation')} "
                f"caught={caught} ({meta['seconds']}s)",
                flush=True,
            )
        if model != "gemma4:latest":
            unload_model(model)


def run_stage2_batched(
    packets: list[tuple[Scenario, str, str]],
    *,
    out_dir: Path,
    synth_model: str,
    advisor_models: tuple[str, ...] = ADVISOR_MODELS,
    base_seed: int = 5000,
) -> None:
    """Pass 2: synthesize Arm B (consensus) and Arm C (crux) without raw packet_text."""
    synth_slug = model_slug(synth_model)
    s_idx = SYNTH_MODELS.index(synth_model) if synth_model in SYNTH_MODELS else 0
    print(f"[stage2] synth_model={synth_model} ({len(packets)} packets)", flush=True)

    for p_idx, (scenario, variant, _packet_text) in enumerate(packets):
        out_path = out_dir / "stage2" / synth_slug / f"{scenario.id}_{variant}.json"
        if out_path.exists():
            continue

        advisors: list[dict[str, Any]] = []
        for adv_model in advisor_models:
            s1_path = out_dir / "stage1" / model_slug(adv_model) / f"{scenario.id}_{variant}.json"
            advisors.append(json.loads(s1_path.read_text()))

        anon = shuffle_advisors(advisors, seed=base_seed + p_idx)
        panel_input = format_panel_input(scenario.constraints, anon)

        c_seed = base_seed + s_idx * 10000 + p_idx * 10
        cons_raw, cons_meta = chat_json(
            synth_model, CONSENSUS_SYSTEM, panel_input, seed=c_seed + 1, temperature=0.2
        )
        cons_text = format_consensus_brief(cons_raw)

        crux_raw, crux_meta = chat_json(
            synth_model, CRUX_SYSTEM, panel_input, seed=c_seed + 2, temperature=0.2
        )
        crux_text = format_crux_brief(crux_raw)

        k_spotted = (
            sum(1 for a in advisors if a.get("advisor_caught"))
            if variant == "flawed"
            else None
        )

        record = {
            "scenario_id": scenario.id,
            "variant": variant,
            "domain": scenario.domain,
            "difficulty_tier": scenario.difficulty_tier,
            "synth_model": synth_model,
            "k_spotted": k_spotted,
            "advisor_caught_by_model": {a["model"]: a.get("advisor_caught") for a in advisors},
            "briefs": {
                "consensus": {
                    "raw": cons_raw,
                    "text": cons_text,
                    "words": len(cons_text.split()),
                    "meta": cons_meta,
                },
                "crux": {
                    "raw": crux_raw,
                    "text": crux_text,
                    "words": len(crux_text.split()),
                    "meta": crux_meta,
                },
            },
        }
        _save_json(out_path, record)
        print(
            f"  {scenario.id}_{variant} (k={k_spotted}): "
            f"cons={len(cons_text.split())}w/{cons_meta['seconds']}s "
            f"crux={len(crux_text.split())}w/{crux_meta['seconds']}s",
            flush=True,
        )


def _eval_decision(
    decider_model: str,
    scenario: Scenario,
    variant: str,
    packet_text: str,
    brief_text: str | None,
    seed: int,
) -> dict[str, Any]:
    dec_user = format_decision_user(scenario.constraints, packet_text, brief_text)
    dec_out, dec_meta = chat_json(
        decider_model,
        DECISION_SYSTEM,
        dec_user,
        seed=seed,
        temperature=0.2,
    )
    is_hold = dec_out.get("action") == "hold_to_verify"
    v_catch = (
        decision_verified_catch(dec_out, scenario.oracle_markers)
        if variant == "flawed"
        else None
    )
    return {
        "output": dec_out,
        "meta": dec_meta,
        "hold": is_hold,
        "verified_catch": v_catch,
        "untargeted_hold": bool(is_hold and not v_catch) if variant == "flawed" else None,
        "false_alarm": is_hold if variant == "sound" else None,
    }


def run_stage3_for_pair(
    packets: list[tuple[Scenario, str, str]],
    *,
    out_dir: Path,
    synth_model: str,
    decider_model: str,
    out_subdir: str = "eval",
    advisor_models: tuple[str, ...] = ADVISOR_MODELS,
    base_seed: int = 7000,
    reuse_raw_single_subdir: str | None = None,
) -> None:
    """Pass 3: run blinded Stage-3 decisions for one (synth_model, decider_model) pair."""
    dec_slug = model_slug(decider_model)
    synth_slug = model_slug(synth_model)
    d_offset = SYNTH_MODELS.index(decider_model) * 10000 if decider_model in SYNTH_MODELS else 20000
    print(
        f"[stage3:{out_subdir}] synth={synth_model} -> decider={decider_model} ({len(packets)} packets)",
        flush=True,
    )

    for p_idx, (scenario, variant, packet_text) in enumerate(packets):
        out_path = out_dir / out_subdir / dec_slug / f"{scenario.id}_{variant}.json"
        if out_path.exists():
            continue

        advisors: list[dict[str, Any]] = []
        for adv_model in advisor_models:
            s1_path = out_dir / "stage1" / model_slug(adv_model) / f"{scenario.id}_{variant}.json"
            advisors.append(json.loads(s1_path.read_text()))

        s2_path = out_dir / "stage2" / synth_slug / f"{scenario.id}_{variant}.json"
        s2_rec = json.loads(s2_path.read_text())

        # Pair flawed/sound twins onto the exact same rotating single-advisor family.
        scenario_idx = p_idx // 2
        single_adv = advisors[scenario_idx % len(advisor_models)]
        single_text = format_single_brief(single_adv["output"])
        cons_entry = s2_rec["briefs"]["consensus"]
        crux_entry = s2_rec["briefs"]["crux"]

        briefs: dict[str, str | None] = {
            "raw": None,
            "single": single_text,
            "consensus": cons_entry["text"],
            "crux": crux_entry["text"],
        }

        prior_rec: dict[str, Any] | None = None
        if reuse_raw_single_subdir:
            prior_path = out_dir / reuse_raw_single_subdir / dec_slug / f"{scenario.id}_{variant}.json"
            if prior_path.exists():
                prior_rec = json.loads(prior_path.read_text())

        d_seed = base_seed + d_offset + p_idx * 10
        decisions: dict[str, Any] = {}
        for a_idx, arm in enumerate(ARMS):
            if prior_rec and arm in ("raw", "single"):
                decisions[arm] = prior_rec["decisions"][arm]
                continue
            decisions[arm] = _eval_decision(
                decider_model,
                scenario,
                variant,
                packet_text,
                briefs[arm],
                seed=d_seed + a_idx,
            )

        k_spotted = s2_rec.get("k_spotted")
        crux_survived = {
            arm: bool(matches_oracle(briefs[arm] or "", scenario.oracle_markers))
            for arm in ("single", "consensus", "crux")
        } if variant == "flawed" else None

        record = {
            "scenario_id": scenario.id,
            "variant": variant,
            "domain": scenario.domain,
            "difficulty_tier": scenario.difficulty_tier,
            "eval_model": decider_model,
            "synth_model": synth_model,
            "single_advisor_model": single_adv["model"],
            "k_spotted": k_spotted,
            "advisor_caught_by_model": s2_rec["advisor_caught_by_model"],
            "briefs": {
                "single": {"text": single_text, "words": len(single_text.split())},
                "consensus": cons_entry,
                "crux": crux_entry,
            },
            "crux_survived": crux_survived,
            "decisions": decisions,
        }
        _save_json(out_path, record)
        print(
            f"  {scenario.id}_{variant} (k={k_spotted}): "
            + " ".join(
                f"{arm}={'CATCH' if decisions[arm]['verified_catch'] else ('HOLD' if decisions[arm]['hold'] else 'go')}"
                for arm in ARMS
            ),
            flush=True,
        )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run crux-brief evaluation sweep.")
    parser.add_argument("--suite", choices=("smoke", "full"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    scenarios = SMOKE_SCENARIOS if args.suite == "smoke" else SCENARIOS
    packets = iter_packets(scenarios)

    # 1. Stage 1: loads qwen3.6 -> nemotron3 -> gemma4 (leaving gemma4 warm).
    run_stage1_batched(packets, out_dir=args.out)

    # 2. Stage 2 synthesis with warm gemma4:latest, then unload before nemotron3.
    run_stage2_batched(packets, out_dir=args.out, synth_model="gemma4:latest")
    unload_model("gemma4:latest")

    # 3. Switch to nemotron3:33b: synthesize + cross-family decide (gemma4 -> nemotron3), then unload.
    run_stage2_batched(packets, out_dir=args.out, synth_model="nemotron3:33b")
    run_stage3_for_pair(
        packets,
        out_dir=args.out,
        synth_model="gemma4:latest",
        decider_model="nemotron3:33b",
        out_subdir="eval",
    )
    unload_model("nemotron3:33b")

    # 4. Switch back to gemma4:latest: cross-family decide (nemotron3 -> gemma4) + full-only same-model ablation.
    run_stage3_for_pair(
        packets,
        out_dir=args.out,
        synth_model="nemotron3:33b",
        decider_model="gemma4:latest",
        out_subdir="eval",
    )
    if args.suite == "full":
        run_stage3_for_pair(
            packets,
            out_dir=args.out,
            synth_model="gemma4:latest",
            decider_model="gemma4:latest",
            out_subdir="ablation_same_model",
            base_seed=9000,
            reuse_raw_single_subdir="eval",
        )


if __name__ == "__main__":
    main()
