# Crux Brief: Structured Disagreement Briefs vs. Common-Ground Summaries

Entry for the Apart Research AI x Epistemics Research Sprint, 13 to 15 November 2026
(Track 3, Epistemic Products).

When a multi-model advisory panel reviews a consequential decision (job offer,
commercial lease, procurement handoff, or operational data readout), one advisor
often spots a flawed premise or hidden constraint violation while the others
accept the headline numbers. Does summarizing the panel into a balanced
common-ground brief smooth away that decisive catch—and does surfacing explicit
side-by-side **cruxes** recover it without triggering false-alarm paralysis?

This repository contains:
1. **`crux_brief` CLI & HTML Card Generator** (`python3 -m crux_brief brief ...`),
   a working Track 3 "Angel-on-the-Shoulder" briefing tool that queries a
   multi-family panel (`gemma4`, `qwen3.6`, `nemotron3`) and renders structured
   crux cards preserving minority claims and concrete verification checks.
2. **Cross-Family Paired Evaluation Harness & Benchmark** (`24` scenarios × `{flawed, sound}`
   = `48` packets across 4 decision domains), comparing 4 length-matched, heading-blinded arms:
   - **`raw`:** Decision maker reads packet with no brief.
   - **`single`:** Brief from one rotating Stage-1 advisor.
   - **`consensus`:** Habermas-style common-ground synthesis of 3 anonymized Stage-1 advisors (Stage-2 synthesizer blinded to raw `packet_text`).
   - **`crux`:** Structured disagreement & crux brief synthesized from the exact same anonymized Stage-1 outputs.

   Primary Stage-2 -> Stage-3 pairings are cross-family (`gemma4:latest -> nemotron3:33b` and `nemotron3:33b -> gemma4:latest`, with `qwen3.6:27b-coding-mxfp8` serving strictly as an independent Stage-1 family), paired with a same-model ablation (`gemma4:latest -> gemma4:latest`). Pre-registered hypotheses are locked in [`HYPOTHESES.md`](HYPOTHESES.md) and cross-track critique notes in [`COLLAB-NOTES.md`](COLLAB-NOTES.md).

## Sprint-Work Disclosure

All code, scenario packets, calibration runs, full evaluation runs, analysis scripts,
figures, and report text in this repository were written during the 13–15 November 2026
Apart AI x Epistemics Research Sprint. No preexisting codebase is reused or bundled here.
(Companion Track 2 submission `signed-is-not-true` lives in a separate repository.)

## Quickstart: Run the Product CLI

Requires Python 3.11+ (`matplotlib` for figures) and [Ollama](https://ollama.com) serving
`gemma4:latest`, `qwen3.6:27b-coding-mxfp8`, and `nemotron3:33b`.

```bash
# Default panel: gemma4:latest, qwen3.6:27b-coding-mxfp8, nemotron3:33b
# Default synthesizer: gemma4:latest (override via --synth-model or --models)
python3 -m crux_brief brief examples/sample_packet.md \
  --compare-consensus \
  --out-html examples/sample_brief.html \
  --out-json examples/sample_brief.json

python3 -m crux_brief brief examples/sample_packet_triage.md \
  --compare-consensus \
  --out-html examples/sample_brief_triage.html \
  --out-json examples/sample_brief_triage.json
```

## Reproduce the Evaluation

```bash
python3 -m unittest discover -s tests -v
python3 -u -m crux_brief.sweep --suite full --out runs/full
python3 -m crux_brief.analyze runs/full > results/tables.md
python3 -m crux_brief.figures runs/full results
```

## AI Assistance

The `crux_brief` implementation, scenario suite, statistical scripts, and report drafts
were built with an AI coding agent working under the author's direction, with peer design
and paper critiques from a separate model family (`anthropic`). The author is responsible
for the repository, runs, and claims.
