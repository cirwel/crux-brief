# Cross-Track & Cross-Family Collaboration Notes (`crux-brief`)

This project (`crux-brief`, Track 3: Epistemic Products) was developed in parallel with a separate Track 2 project (`signed-is-not-true`, authored by Claude at `/Users/cirwel/projects/apart-epistemics-2026/signed-is-not-true/`, commit `6c05b9c`). Rather than editing each other's repositories directly, both tracks exchanged read-only audits and structured cross-family peer critiques.

## 1. Read-Only Audit of Entry A (`signed-is-not-true`)

- **Audit Artifact:** [`COLLAB-AUDIT-ENTRY-A.md`](../COLLAB-AUDIT-ENTRY-A.md)
- **Target Repo State:** `/Users/cirwel/projects/apart-epistemics-2026/signed-is-not-true` (`main`, `6c05b9c`) — left completely untouched by `crux-brief`.
- **Verified Checks:** Confirmed `320` runs in `runs/full`, consistent counts and Wilson confidence intervals, `5`-page compiled PDF, and `0` occurrences of `"tamper-evident"`.
- **Editorial Nits Reported Back to Author:** Abstract length (`256` words over `250`-word cap), Figure 1 caption split across pages 3–4, and Table 7 appearing before Table 6.

## 2. Checkpoint 1: Pre-Implementation Cross-Family Design Critique

- **Reviewer:** `claude:host-adapter` via `unitares-governance:consult(purpose="critique", privacy="cloud_allowed")`
- **Consultation ID:** `b3f1d96d-dea2-41c4-95dd-61acf80bccf8`
- **Critique Findings & Pre-Lock Architectural Dispositions:**
  1. *Weak `single` arm baseline:* Replaced weak baseline so `single` rotates real Stage-1 advisor outputs from the same 3-model panel (`gemma4:latest`, `nemotron3:33b`, `qwen3.6:27b-coding-mxfp8`), formatted under the same blinded template.
  2. *Raw `packet_text` leakage into Stage 2:* Restricted `format_panel_input(constraints, anonymized_advisors)` in `crux_brief/prompts.py` to `constraints` plus shuffled, anonymized Stage-1 outputs only—ensuring Stage 2 genuinely aggregates advisor output rather than re-reading the raw packet.
  3. *Mandatory doubt inflating sound false alarms:* Resolved across two calibration rounds (`smoke_calibration` -> `smoke_calibration_v2` -> `smoke_calibration_v3`): reordered `ADVISOR_SYSTEM` (`summary`, `key_claims`, `recommendation`, `risks_or_flaws`, `verification_question`, `confidence`) with explicit anti-pedantry rules, instructed `CRUX_SYSTEM` to emit `cruxes=[]` and `unverified_premises=[]` on unanimous `proceed` panels, and scrubbed contradictory headline/pre-computed numbers in paired `constraints` and `packet_sound` (`C04`, `S04`, `S06`, `S08`, `S11`, `S13`, `S16`–`S21`, `S23`, `S24`).
  4. *Unblinded arm headers & cue words:* Standardized `format_single_brief`, `format_consensus_brief`, and `format_crux_brief` onto identical neutral 3-section headings (`ASSESSMENT OVERVIEW:`, `POINTS OF NOTE:`, `SUGGESTED NEXT STEP:`) with a `220`-word budget (enforced in `tests/test_crux_brief.py`).
  5. *Same-model Stage-2/Stage-3 correlation:* Restructured `crux_brief/sweep.py` to evaluate cross-family pairings (`gemma4:latest -> nemotron3:33b` and `nemotron3:33b -> gemma4:latest`) primarily, while isolating same-model `gemma4:latest -> gemma4:latest` into `ablation_same_model` (Table 6). Also added explicit Ollama `unload_model` (`keep_alive: 0`) calls between model switches after diagnosing resident-memory slowdown during v1 calibration.

## 3. Pre-Lock Smoke Calibration Verification (`runs/smoke_calibration_v3`)

- After applying the Checkpoint 1 fixes, `python3 -m unittest discover -s tests -v` passed `8/8` tests, and `runs/smoke_calibration_v3` achieved:
  - `qwen3.6:27b-coding-mxfp8` mean Stage-1 latency `50.35s` (max `72.89s`).
  - Both cross-family `crux` evaluators achieved `4/4` flawed verified catches, `1/4` sound false alarms (`0.25 [0.05, 0.70]`, triggered when Stage 1 itself had a real 2–1 split on `C01_sound`), and `3/4` paired twin accuracy (`Net J = +0.75`).
  - On `nemotron3:33b -> gemma4:latest`, `consensus` produced `3/4` flawed verified catches (`1/4` untargeted hold on `C01_flawed`) vs `4/4` verified catches under `crux`.

## 4. Checkpoint 2: Post-Run & Report Peer Critique

- **Reviewer:** `claude:host-adapter` via `unitares-governance:consult(purpose="critique", effort="thorough", privacy="cloud_allowed")`
- **Consultation ID:** `ed703870-c4df-4176-8a7b-cb9d090cce1c`
- **Critique Verification & Report Dispositions:**
  1. *Verified calculations:* Confirmed all Table 1–6 counts, proportions, 95% Wilson CIs, `Net J`, and exact two-sided McNemar `p`-values against `results/tables.md`.
  2. *Fixed `gemma4 -> nemotron3` trace accounting (`3/24` FAs):* Corrected draft confusion with same-model `gemma4 -> gemma4` (`S13_sound` actually resolved `proceed` on cross-family `nemotron3`; `3/24` FAs are `S04` contagion + `S15`, `S24` unanimous leakage).
  3. *Cluster-adjusted & multiple-testing inference:* Added exact scenario-level sign tests (`n = 24` independent scenario twins: `crux vs. consensus` `b = 0, c = 6`, `p = 0.0312`; `crux vs. raw` `b = 9, c = 1`, `p = 0.0215`; `consensus vs. raw` `b = 12, c = 0`, `p = 0.0005`), marked pooled `n = 48` and `vs. raw` comparisons as nominal/post-hoc, and noted identical `0.0391` FA/twin p-values share the same false-alarm discordance.
  4. *Honest hypothesis status:* Recast H2 (`k in {1, 2}`) as **not evaluable** (`n = 1` split scenario `S20_flawed`, tied `1/1` between `consensus` and `crux`), added post-hoc sound-panel stratification (`21` unanimous `proceed` vs. `3` split `1`-of-`3` Stage-1 hold), added `"any hold on flawed"` sensitivity (`crux` `24/24` on both deciders), and clarified `S20_flawed` (`single` = `0/1` via `nemotron3`, `raw` = `proceed`, both multi-advisor briefs rescued).
  5. *Scoped mechanistic & design claims:* Replaced causal overstatements with qualitative trace analysis, noted shorter `crux` brief word counts (`100`–`124w` vs. `154`–`180w`) and asymmetric Checkpoint 1 `consensus` prompt tuning, framed gating + deterministic arithmetic verification as untested product hypotheses (acknowledging that a decision-boundary gate alone would not stop 2–1 contagion on `S04`/`S08`/`S09`), aligned MASK/Habermas/Angels citations, and updated abstract word count cleanly (`150–250` words).
