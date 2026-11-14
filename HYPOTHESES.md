# Pre-Registered Hypotheses and Analysis Plan (`crux-brief`)

**Status:** Locked on `main` prior to executing `python3 -u -m crux_brief.sweep --suite full --out runs/full`.
**Track:** Apart Research AI x Epistemics Research Sprint — Track 3: Epistemic Products.

## 1. Experimental Design

We evaluate whether surfacing structured cross-model disagreements (`crux`) helps a downstream decision maker detect subtle planted premise flaws better than no advisory brief (`raw`), a single independent advisor (`single`), or a Habermas-style deliberative common-ground brief (`consensus`), without triggering excessive false alarms on paired sound controls.

- **Benchmark (`S01`–`S24`, 24 pairs / 48 packets):** Four consequential domains (`job_offers`, `leases`, `procurement_handoffs`, `operational_briefs`; 6 pairs per domain) across three difficulty tiers. Each scenario `S_i` consists of shared decision `constraints` and two length-matched packets (`<= 0.16` normalized length delta): `packet_flawed` (one planted numeric, deadline, unit, governance, or logical defect verified by `oracle_markers`) and `packet_sound` (the repaired sound control).
- **Stage-1 Advisory Panel (3 distinct model families):** `qwen3.6:27b-coding-mxfp8`, `nemotron3:33b`, and `gemma4:latest` evaluate each packet independently with `ADVISOR_SYSTEM` (`summary`, `key_claims`, `recommendation`, `risks_or_flaws`, `verification_question`, `confidence`) at `temperature=0.3`, `seed=0`, `num_ctx=8192`, `think=False`, `format="json"`. Inactive Ollama models are unloaded (`keep_alive: 0`) between stages.
- **Stage-2 Cross-Family Aggregation (blinded to `packet_text`):** Synthesizer receives ONLY `constraints` and shuffled, anonymized Stage-1 advisor JSON objects (`format_panel_input`, excluding raw `packet_text`). It produces:
  - `consensus` (`CONSENSUS_SYSTEM`): Habermas-style common-ground synthesis centering shared framing and majority opinion.
  - `crux` (`CRUX_SYSTEM`): Crux-Brief isolating pivotal `cruxes` and `unverified_premises` when advisors hold/disagree, calibrated to emit `cruxes=[]` on unanimous `proceed` panels.
- **Stage-3 Decision Maker (4 blinded arms):** All briefed arms (`single`, `consensus`, `crux`) share identical 3-section headings (`ASSESSMENT OVERVIEW:`, `POINTS OF NOTE:`, `SUGGESTED NEXT STEP:`) and a `220`-word cap so Stage-3 cannot key off surface labels:
  - `raw`: `constraints` + packet only.
  - `single`: `constraints` + packet + one rotating Stage-1 advisor brief.
  - `consensus`: `constraints` + packet + Stage-2 Habermas consensus brief.
  - `crux`: `constraints` + packet + Stage-2 Crux brief.
- **Cross-Family Pairings (primary):**
  1. `gemma4:latest -> nemotron3:33b` (`synth=gemma4`, `decider=nemotron3`)
  2. `nemotron3:33b -> gemma4:latest` (`synth=nemotron3`, `decider=gemma4`)
- **Same-Model Ablation (`ablation_same_model`):**
  - `gemma4:latest -> gemma4:latest` (`synth=gemma4`, `decider=gemma4`), reusing `gemma4` `raw`/`single` Stage-3 baselines and re-running `consensus` and `crux` to test Stage-2/3 same-family coupling (reported in Table 6).

## 2. Pre-Registered Metrics & Statistical Rules

Flawed and sound outcomes are never pooled into a single error rate:

1. **Flawed verified catch** (`flawed` only): `action == "hold"` AND oracle marker match (`decision_verified_catch` in `reason` + `target_clause`).
2. **Flawed untargeted hold** (`flawed` only): `action == "hold"` WITHOUT oracle marker match.
3. **Sound false alarm** (`sound` only): `action == "hold"` on `packet_sound`.
4. **Paired twin accuracy** (scenario-pair level, `n=24` per decider): Pair `S_i` succeeds iff `packet_flawed` gets a verified catch AND `packet_sound` receives `action == "go"`.
5. **Net Youden's $J$ (`Net J`)**: `flawed_verified_catch_rate - sound_false_alarm_rate`.
6. **Mechanism & calibration metrics**: Stage-2 flaw survival (`brief_survived`), conditional verified catch given `brief_survived`, briefing median word count parity, and **comfort gap** (mean confidence and mean brief endorsement on missed flawed packets).
7. **Uncertainty & Hypothesis Testing**: 95% Wilson score intervals (`wilson_ci`) on proportions; two-sided exact McNemar tests (`mcnemar_exact_p`) on discordant scenario pairs (`crux_only / other_only`), reported both per cross-family decider (`n=24`) and pooled across both cross-family deciders (`n=48`, noting same-scenario clustering).

## 3. Hypotheses

- **H1 (Overall Flawed Catch vs `raw` and `single`):** Across both cross-family `(synth -> decider)` evaluations (`n=24` each, `48` pooled), `crux` achieves higher **flawed verified catch** and **paired twin accuracy** than `raw`, and outperforms `single` when individual Stage-1 advisors miss flaws (evaluated via discordant McNemar tests and `Net J`).
- **H2 (Split-Panel Mechanism vs `consensus`):** On split-panel flawed scenarios where only `k in {1, 2}` of 3 Stage-1 advisors spot the planted flaw, `crux` preserves the flaw into the Stage-2 brief (`brief_survived`) more often than `consensus`, producing higher `flawed verified catch` than `consensus` rather than washing minority objections out into common-ground framing or generic untargeted holds. (When `k=3`, both multi-advisor briefs should succeed; when `k=0`, neither can inherit a Stage-1 catch without `packet_text`.)
- **H3 (False-Alarm Restraint on Paired Sound Controls):** With calibrated Stage-1 field ordering and explicit unanimous-`proceed` handling in `CRUX_SYSTEM`, `crux` does not achieve flawed catches merely via indiscriminate caution: sound false alarms under `crux` stay bounded (`<=` or comparable to `consensus`), yielding higher **paired twin accuracy** and **Net $J$** than `raw` and `consensus`.
- **H4 (Cross-Family vs Same-Model Ablation & Comfort Gap):**
  - **H4a:** Comparing `gemma4 -> gemma4` (`ablation_same_model`) against cross-family `nemotron3 -> gemma4` reveals whether sharing synthesizer/decider weights alters agreement bias or `crux` vs `consensus` separation.
  - **H4b:** Decision makers that miss flawed premises under `raw` or `consensus` exhibit substantial confidence and high brief endorsement ("comfort gap") under word-length-matched blinded formatting.

## 4. Pre-Lock Smoke Verification (`runs/smoke_calibration_v3`)

Prior to locking this plan, the 4-pair smoke calibration suite (`runs/smoke_calibration_v3`, gitignored) satisfied all pre-registered calibration checks:
- `qwen3.6:27b-coding-mxfp8` Stage-1 latency: mean `50.35s`, max `72.89s` (`< 90s` threshold).
- `crux` sound false alarms: `1/4 = 0.25 [0.05, 0.70]` on both cross-family deciders (`<= 1/4` threshold), with `4/4` flawed verified catches, `3/4` paired twin accuracy, and `Net J = +0.75` (`consensus` on `nemotron3 -> gemma4`: `3/4` verified catch with `1/4` untargeted hold).

## Changes after the lock

- **2026-11-14 (visual chart layout only):** Adjusted `make_figure1` in [`crux_brief/figures.py`](crux_brief/figures.py) so numeric bar labels sit cleanly above each 95% Wilson CI whisker cap (`min(1.08, h + hi_err + 0.015)`, `ylim(0, 1.18)`) rather than colliding with error bars. Zero changes were made to `runs/full`, prompts, scenarios, metrics, or `results/tables.md`.
