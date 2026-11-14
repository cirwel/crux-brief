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

*(Pending completion of `runs/full` and `report/REPORT.md`.)*
