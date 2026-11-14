"""User-facing CLI for generating a Pre-Decision Crux Brief card."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from .ollama_client import chat_json
from .prompts import (
    ADVISOR_SYSTEM,
    CONSENSUS_SYSTEM,
    CRUX_SYSTEM,
    format_advisor_user,
    format_consensus_brief,
    format_crux_brief,
    format_panel_input,
    shuffle_advisors,
)
from .render_html import render_brief_html

DEFAULT_PANEL = ("gemma4:latest", "qwen3.6:27b-coding-mxfp8", "nemotron3:33b")


def parse_markdown_packet(text: str, fallback_title: str) -> tuple[str, str, str]:
    """Extract (title, constraints, packet_body) from a markdown decision file."""
    title = fallback_title
    m_title = re.search(r"^#\s+(.+)$", text, flags=re.M)
    if m_title:
        title = m_title.group(1).strip()

    m_const = re.search(r"^##\s*Constraints?\s*\n(.*?)(?=^##\s|\Z)", text, flags=re.M | re.S | re.I)
    m_pack = re.search(r"^##\s*Packet\s*\n(.*)\Z", text, flags=re.M | re.S | re.I)
    if m_const and m_pack:
        return title, m_const.group(1).strip(), m_pack.group(1).strip()
    return title, "Verify all stated terms, figures, and feasibility constraints.", text.strip()


def run_crux_brief(
    *,
    title: str,
    constraints: str,
    packet: str,
    panel_models: list[str],
    synth_model: str,
    seed: int = 0,
    include_consensus: bool = False,
) -> dict[str, Any]:
    """Execute Stage-1 advisor panel + Stage-2 crux synthesis."""
    adv_user = format_advisor_user(constraints, packet)
    advisors: list[dict[str, Any]] = []
    for m in panel_models:
        out, meta = chat_json(m, ADVISOR_SYSTEM, adv_user, seed=seed, temperature=0.3)
        advisors.append({"model": m, "output": out, "meta": meta})

    anon = shuffle_advisors(advisors, seed=seed)
    panel_input = format_panel_input(constraints, anon)
    crux_obj, crux_meta = chat_json(synth_model, CRUX_SYSTEM, panel_input, seed=seed, temperature=0.2)
    brief_text = format_crux_brief(crux_obj)

    consensus_text = None
    consensus_meta = None
    if include_consensus:
        c_obj, consensus_meta = chat_json(synth_model, CONSENSUS_SYSTEM, panel_input, seed=seed, temperature=0.2)
        consensus_text = format_consensus_brief(c_obj)

    return {
        "title": title,
        "constraints": constraints,
        "panel_models": panel_models,
        "synth_model": synth_model,
        "advisors": advisors,
        "crux": crux_obj,
        "brief_text": brief_text,
        "brief_word_count": len(brief_text.split()),
        "crux_meta": crux_meta,
        "consensus_text": consensus_text,
        "consensus_meta": consensus_meta,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="crux_brief")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_brief = sub.add_parser("brief", help="Generate a Pre-Decision Crux Brief from a packet file")
    p_brief.add_argument("packet_path", type=Path, help="Path to markdown/text decision packet")
    p_brief.add_argument("--constraints", default="", help="Override constraints string")
    p_brief.add_argument("--models", default=",".join(DEFAULT_PANEL), help="Comma-separated advisor models")
    p_brief.add_argument("--synth-model", default="gemma4:latest", help="Synthesizer model")
    p_brief.add_argument("--seed", type=int, default=0)
    p_brief.add_argument("--compare-consensus", action="store_true", help="Also generate consensus baseline")
    p_brief.add_argument("--out-html", type=Path, required=True)
    p_brief.add_argument("--out-json", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.cmd == "brief":
        raw = args.packet_path.read_text()
        title, constraints, packet = parse_markdown_packet(raw, args.packet_path.stem)
        if args.constraints:
            constraints = args.constraints
        models = [m.strip() for m in args.models.split(",") if m.strip()]
        result = run_crux_brief(
            title=title,
            constraints=constraints,
            packet=packet,
            panel_models=models,
            synth_model=args.synth_model,
            seed=args.seed,
            include_consensus=args.compare_consensus,
        )
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_html.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(result, indent=2) + "\n")
        args.out_html.write_text(
            render_brief_html(
                title=title,
                constraints=constraints,
                advisors=result["advisors"],
                crux_obj=result["crux"],
                brief_text=result["brief_text"],
                consensus_text=result["consensus_text"],
            )
        )
        print(f"Wrote {args.out_json} and {args.out_html} ({result['brief_word_count']} words)")


if __name__ == "__main__":
    main()
