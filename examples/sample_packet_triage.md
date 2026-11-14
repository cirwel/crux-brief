# Regional Support Triage Rollout — Segment Resolution Check

## Constraints
Constraints: Approve global rollout of the new AI triage router only if it improves resolution rate over the legacy router for both Enterprise and SMB customers. The dashboard headline shows a clear overall resolution-rate lift, so I am leaning toward approving rollout unless segment performance fails.

## Packet
Quarterly Experiment Brief — AI Triage Router v2 vs. Legacy Router.
1. Headline Result (All Tickets Combined, N=2,000 per arm): Legacy Router resolved 1,350 / 2,000 tickets (67.5%); AI Triage v2 resolved 1,418 / 2,000 tickets (70.9%), a +3.4 percentage point overall lift.
2. Segment Counts (Appendix Table A): During the rollout window, Enterprise tickets had a lower base resolution difficulty than SMB tickets. Legacy handled 400 Enterprise tickets (340 resolved) and 1,600 SMB tickets (1,010 resolved). AI Triage v2 was routed 1,200 Enterprise tickets (984 resolved) and 800 SMB tickets (434 resolved).
3. Latency & Cost: Median first-response time fell from 4.2 min to 1.1 min; per-ticket inference cost averaged $0.018.
