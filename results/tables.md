# Results from `runs/full` (144 Stage-1 calls, 96 cross-family Stage-3 evaluations)

Rates are `k/n = p [95% Wilson CI]`. Flawed and sound packets are never pooled.

## Table 1. Stage-1 independent advisor accuracy and panel split distribution

| Advisor model | Flawed caught (`hold` + oracle match) | Flawed raw holds | Sound false alarms |
|---|---|---|---|
| gemma4:latest | 23/24 = 0.96 [0.80, 0.99] | 23/24 = 0.96 [0.80, 0.99] | 3/24 = 0.12 [0.04, 0.31] |
| nemotron3:33b | 23/24 = 0.96 [0.80, 0.99] | 23/24 = 0.96 [0.80, 0.99] | 0/24 = 0.00 [0.00, 0.14] |
| qwen3.6:27b-coding-mxfp8 | 24/24 = 1.00 [0.86, 1.00] | 24/24 = 1.00 [0.86, 1.00] | 0/24 = 0.00 [0.00, 0.14] |

Panel split distribution across `24` flawed scenarios (`k_spotted` of 3 advisors): `k=0`: 0/24, `k=1`: 1/24, `k=2`: 0/24, `k=3`: 23/24 (split panel `k in {1,2}`: 1/24).

## Table 2. Cross-family Stage-3 decision outcomes by `(synth -> decider)` and arm

| Synth -> Decider | Arm | Flawed verified catch | Flawed untargeted hold | Sound false alarm | Paired twin accuracy | Net J |
|---|---|---|---|---|---|---|
| nemotron3:33b -> gemma4:latest | raw | 20/24 = 0.83 [0.64, 0.93] | 2/24 = 0.08 [0.02, 0.26] | 7/24 = 0.29 [0.15, 0.49] | 14/24 = 0.58 [0.39, 0.76] | +0.54 |
| nemotron3:33b -> gemma4:latest | single | 23/24 = 0.96 [0.80, 0.99] | 0/24 = 0.00 [0.00, 0.14] | 1/24 = 0.04 [0.01, 0.20] | 22/24 = 0.92 [0.74, 0.98] | +0.92 |
| nemotron3:33b -> gemma4:latest | consensus | 24/24 = 1.00 [0.86, 1.00] | 0/24 = 0.00 [0.00, 0.14] | 0/24 = 0.00 [0.00, 0.14] | 24/24 = 1.00 [0.86, 1.00] | +1.00 |
| nemotron3:33b -> gemma4:latest | crux | 23/24 = 0.96 [0.80, 0.99] | 1/24 = 0.04 [0.01, 0.20] | 5/24 = 0.21 [0.09, 0.40] | 19/24 = 0.79 [0.60, 0.91] | +0.75 |
| gemma4:latest -> nemotron3:33b | raw | 22/24 = 0.92 [0.74, 0.98] | 0/24 = 0.00 [0.00, 0.14] | 5/24 = 0.21 [0.09, 0.40] | 17/24 = 0.71 [0.51, 0.85] | +0.71 |
| gemma4:latest -> nemotron3:33b | single | 23/24 = 0.96 [0.80, 0.99] | 0/24 = 0.00 [0.00, 0.14] | 1/24 = 0.04 [0.01, 0.20] | 22/24 = 0.92 [0.74, 0.98] | +0.92 |
| gemma4:latest -> nemotron3:33b | consensus | 24/24 = 1.00 [0.86, 1.00] | 0/24 = 0.00 [0.00, 0.14] | 1/24 = 0.04 [0.01, 0.20] | 23/24 = 0.96 [0.80, 0.99] | +0.96 |
| gemma4:latest -> nemotron3:33b | crux | 23/24 = 0.96 [0.80, 0.99] | 1/24 = 0.04 [0.01, 0.20] | 3/24 = 0.12 [0.04, 0.31] | 21/24 = 0.88 [0.69, 0.96] | +0.83 |

### Paired exact McNemar comparisons (discordant `crux_only / other_only`, two-sided exact p)

Note: `Pooled (2 deciders)` pools observations across both cross-family deciders on the same scenario set; per-decider rows test exact paired differences within one model.

| Scope | Comparison | Flawed verified catch | Sound false alarm | Paired twin accuracy |
|---|---|---|---|---|
| nemotron3:33b -> gemma4:latest | crux vs raw | 3 / 0 (p=0.2500) | 2 / 4 (p=0.6875) | 6 / 1 (p=0.1250) |
| nemotron3:33b -> gemma4:latest | crux vs single | 1 / 1 (p=1.0000) | 5 / 1 (p=0.2188) | 2 / 5 (p=0.4531) |
| nemotron3:33b -> gemma4:latest | crux vs consensus | 0 / 1 (p=1.0000) | 5 / 0 (p=0.0625) | 0 / 5 (p=0.0625) |
| gemma4:latest -> nemotron3:33b | crux vs raw | 2 / 1 (p=1.0000) | 1 / 3 (p=0.6250) | 4 / 0 (p=0.1250) |
| gemma4:latest -> nemotron3:33b | crux vs single | 1 / 1 (p=1.0000) | 2 / 0 (p=0.5000) | 1 / 2 (p=1.0000) |
| gemma4:latest -> nemotron3:33b | crux vs consensus | 0 / 1 (p=1.0000) | 3 / 1 (p=0.6250) | 1 / 3 (p=0.6250) |
| Pooled (2 deciders) | crux vs raw | 5 / 1 (p=0.2188) | 3 / 7 (p=0.3438) | 10 / 1 (p=0.0117) |
| Pooled (2 deciders) | crux vs single | 2 / 2 (p=1.0000) | 7 / 1 (p=0.0703) | 3 / 7 (p=0.3438) |
| Pooled (2 deciders) | crux vs consensus | 0 / 2 (p=0.5000) | 8 / 1 (p=0.0391) | 1 / 8 (p=0.0391) |

## Table 3. Mechanism by advisor panel split (`k_spotted` on flawed packets)

| Decider model | Stratum (`k_spotted`) | n | Brief survived: consensus vs crux | Verified catch: single / consensus / crux |
|---|---|---|---|---|
| gemma4:latest | k=0 | 0 | n/a | n/a |
| gemma4:latest | k=1 | 1 | 1/1 vs 1/1 | 0/1 / 1/1 / 1/1 |
| gemma4:latest | k=2 | 0 | n/a | n/a |
| gemma4:latest | k=3 | 23 | 23/23 vs 23/23 | 23/23 / 23/23 / 22/23 |
| gemma4:latest | split (1 or 2) | 1 | 1/1 vs 1/1 | 0/1 / 1/1 / 1/1 |
| nemotron3:33b | k=0 | 0 | n/a | n/a |
| nemotron3:33b | k=1 | 1 | 1/1 vs 1/1 | 0/1 / 1/1 / 1/1 |
| nemotron3:33b | k=2 | 0 | n/a | n/a |
| nemotron3:33b | k=3 | 23 | 23/23 vs 23/23 | 23/23 / 23/23 / 22/23 |
| nemotron3:33b | split (1 or 2) | 1 | 1/1 vs 1/1 | 0/1 / 1/1 / 1/1 |

### Stage-3 flawed verified catch conditioned on whether the brief already named an oracle marker

| Decider model | Arm | Catch when brief named flaw (`survived=True`) | Catch when brief missed flaw (`survived=False`) |
|---|---|---|---|
| gemma4:latest | single | 23/24 = 0.96 [0.80, 0.99] | n/a (0) |
| gemma4:latest | consensus | 24/24 = 1.00 [0.86, 1.00] | n/a (0) |
| gemma4:latest | crux | 23/24 = 0.96 [0.80, 0.99] | n/a (0) |
| nemotron3:33b | single | 23/24 = 0.96 [0.80, 0.99] | n/a (0) |
| nemotron3:33b | consensus | 24/24 = 1.00 [0.86, 1.00] | n/a (0) |
| nemotron3:33b | crux | 23/24 = 0.96 [0.80, 0.99] | n/a (0) |

## Table 4. Domain breakdown (flawed verified catch / sound false alarm)

| Decider model | Domain | raw | single | consensus | crux |
|---|---|---|---|---|---|
| gemma4:latest | job_offers | 6/6 catch, 2/6 FA | 6/6 catch, 1/6 FA | 6/6 catch, 0/6 FA | 6/6 catch, 0/6 FA |
| gemma4:latest | leases | 5/6 catch, 1/6 FA | 6/6 catch, 0/6 FA | 6/6 catch, 0/6 FA | 6/6 catch, 2/6 FA |
| gemma4:latest | procurement_handoffs | 4/6 catch, 2/6 FA | 6/6 catch, 0/6 FA | 6/6 catch, 0/6 FA | 5/6 catch, 2/6 FA |
| gemma4:latest | operational_briefs | 5/6 catch, 2/6 FA | 5/6 catch, 0/6 FA | 6/6 catch, 0/6 FA | 6/6 catch, 1/6 FA |
| nemotron3:33b | job_offers | 6/6 catch, 1/6 FA | 6/6 catch, 1/6 FA | 6/6 catch, 0/6 FA | 6/6 catch, 1/6 FA |
| nemotron3:33b | leases | 6/6 catch, 1/6 FA | 6/6 catch, 0/6 FA | 6/6 catch, 1/6 FA | 6/6 catch, 0/6 FA |
| nemotron3:33b | procurement_handoffs | 6/6 catch, 2/6 FA | 6/6 catch, 0/6 FA | 6/6 catch, 0/6 FA | 5/6 catch, 1/6 FA |
| nemotron3:33b | operational_briefs | 4/6 catch, 1/6 FA | 5/6 catch, 0/6 FA | 6/6 catch, 0/6 FA | 6/6 catch, 1/6 FA |

## Table 5. Briefing length parity, runtime cost, and comfort gap

| Decider model | Arm | Median brief words | Median synth+decide s | Mean conf (missed flawed) | Mean endorse (missed flawed) | Mean endorse (all) |
|---|---|---|---|---|---|---|
| gemma4:latest | raw | 0 (no brief) | 4.5 | 100.0 (n=2) | n/a (0) | n/a (0) |
| gemma4:latest | single | 130 | 4.2 | 100.0 (n=1) | 5.00 (n=1) | 5.00 (n=48) |
| gemma4:latest | consensus | 154 | 13.8 | n/a (0) | n/a (0) | 5.00 (n=48) |
| gemma4:latest | crux | 100 | 12.2 | n/a (0) | n/a (0) | 4.90 (n=48) |
| nemotron3:33b | raw | 0 (no brief) | 4.3 | 100.0 (n=2) | n/a (0) | n/a (0) |
| nemotron3:33b | single | 130 | 4.6 | 100.0 (n=1) | 5.00 (n=1) | 5.00 (n=48) |
| nemotron3:33b | consensus | 180 | 16.0 | n/a (0) | n/a (0) | 5.00 (n=48) |
| nemotron3:33b | crux | 124 | 15.0 | n/a (0) | n/a (0) | 4.94 (n=48) |

## Table 6. Same-family (`gemma4 -> gemma4`) vs. Cross-family (`nemotron3 -> gemma4`) synthesizer check

| Pair | Arm | Flawed verified catch | Sound false alarm | Paired twin accuracy | Net J | Mean endorse (all) |
|---|---|---|---|---|---|---|
| Cross: nemotron3 -> gemma4 | consensus | 24/24 = 1.00 [0.86, 1.00] | 0/24 = 0.00 [0.00, 0.14] | 24/24 = 1.00 [0.86, 1.00] | +1.00 | 5.00 (n=48) |
| Cross: nemotron3 -> gemma4 | crux | 23/24 = 0.96 [0.80, 0.99] | 5/24 = 0.21 [0.09, 0.40] | 19/24 = 0.79 [0.60, 0.91] | +0.75 | 4.90 (n=48) |
| Same: gemma4 -> gemma4 | consensus | 24/24 = 1.00 [0.86, 1.00] | 1/24 = 0.04 [0.01, 0.20] | 23/24 = 0.96 [0.80, 0.99] | +0.96 | 5.00 (n=48) |
| Same: gemma4 -> gemma4 | crux | 23/24 = 0.96 [0.80, 0.99] | 6/24 = 0.25 [0.12, 0.45] | 18/24 = 0.75 [0.55, 0.88] | +0.71 | 5.00 (n=48) |
