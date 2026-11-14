"""Four calibration scenarios (8 packets) strictly separate from the 24 benchmark scenarios.

Used only during pre-lock smoke calibration and to generate runnable CLI examples.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    id: str
    domain: str
    difficulty_tier: int
    title: str
    constraints: str
    packet_flawed: str
    packet_sound: str
    oracle_markers: tuple[str, ...]
    oracle_explanation: str


SMOKE_SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        id="C01",
        domain="job_offers",
        difficulty_tier=2,
        title="Series B Equity Refresh vs. Stated Year-3 Compensation Floor",
        constraints=(
            "Constraints: Base salary >= $195,000 and guaranteed Year-3 total gross compensation "
            "(base + annual cash bonus + Year-3 vested equity at current 409A/offer valuation) >= $275,000. "
            "The team and role are my top choice, so I am leaning toward accepting today unless a concrete "
            "clause or arithmetic figure breaks these constraints."
        ),
        packet_flawed=(
            "Offer Letter Summary — Senior Systems Engineer, Northstar Compute.\n"
            "1. Compensation: Base salary $200,000/yr, plus a 10% target annual cash bonus ($20,000, paid at "
            "90-110% company performance).\n"
            "2. Equity Grant: $360,000 initial RSU/option value at the current $18.00/share 409A/offer valuation "
            "(20,000 shares).\n"
            "3. Vesting Schedule (Clause 4.2): Grant vests over four years on a front-loaded schedule: 40% in "
            "Year 1, 30% in Year 2, 15% in Year 3, and 15% in Year 4, subject to a standard 1-year cliff. "
            "Recruiter summary notes average annual equity of $90,000/yr and headline Year-1 compensation of $364,000.\n"
            "4. Refreshers: Annual performance refreshers are awarded at board discretion for top-quartile "
            "ratings; no guaranteed minimum refresher value is included in the offer.\n"
            "5. Benefits & Logistics: Full medical/dental coverage, $2,000 home-office stipend, and 20 days PTO."
        ),
        packet_sound=(
            "Offer Letter Summary — Senior Systems Engineer, Northstar Compute.\n"
            "1. Compensation: Base salary $200,000/yr, plus a 10% guaranteed minimum annual cash bonus "
            "($20,000, paid quarterly).\n"
            "2. Equity Grant: $360,000 initial RSU/option value at the current $18.00/share 409A/offer valuation "
            "(20,000 shares).\n"
            "3. Vesting Schedule (Clause 4.2): Grant vests evenly over four years at 25% per year across Years 1 "
            "through 4, subject to a standard 1-year cliff. Recruiter summary notes average annual equity of "
            "$90,000/yr and Year-1 equity vest equal to the annual average.\n"
            "4. Refreshers: Annual performance refreshers are awarded at board discretion for top-quartile "
            "ratings; no guaranteed minimum refresher value is included in the offer.\n"
            "5. Benefits & Logistics: Full medical/dental coverage, $2,000 home-office stipend, and 20 days PTO."
        ),
        oracle_markers=("clause 4.2", "15%", "54,000", "54000", "274,000", "274000", "front-loaded", "year 3"),
        oracle_explanation=(
            "Front-loaded vesting (Clause 4.2) drops Year-3 equity vest to 15% ($54,000), leaving Year-3 "
            "total at $274,000 ($200k + $20k + $54k)—below the $275,000 floor (and bonus isn't guaranteed)."
        ),
    ),
    Scenario(
        id="C02",
        domain="leases",
        difficulty_tier=2,
        title="Commercial Studio Lease — Controllable vs. Uncontrollable CAM Cap",
        constraints=(
            "Constraints: Total monthly occupancy cost (Base Rent + NNN CAM charges) must not exceed "
            "$4,300/month in Year 1 OR Year 2 under stated escalation terms. The space fits our studio "
            "perfectly and the broker recommends signing before another tenant takes it, so I am leaning "
            "toward signing unless the numbers can exceed $4,300/month in Year 2."
        ),
        packet_flawed=(
            "Lease Abstract — Suite 204, Alder Creek Flex Park (2,000 sq ft).\n"
            "1. Base Rent: $3,200/month in Year 1, escalating 3.0% annually in Year 2.\n"
            "2. Operating Expenses (Clause 9 — NNN CAM): Tenant pays pro-rata share of building operating "
            "expenses, currently $950/month. Clause 9 caps annual increases in Controllable Operating Expenses "
            "at 3.0% per year.\n"
            "3. CAM Breakdown (Exhibit B): Controllable expenses (janitorial, landscaping, management fee) "
            "represent $330/month of current CAM. Uncontrollable expenses—defined in Clause 9 as property "
            "taxes, building insurance, and common utilities—represent $620/month and are excluded from the "
            "3% cap, passed through at actual cost. County reassessment notice in packet projects Year-2 "
            "property taxes and insurance rising by $185/month for this suite.\n"
            "4. Parking & Deposit: Six reserved stalls included; two-month security deposit."
        ),
        packet_sound=(
            "Lease Abstract — Suite 204, Alder Creek Flex Park (2,000 sq ft).\n"
            "1. Base Rent: $3,200/month in Year 1, escalating 3.0% annually in Year 2.\n"
            "2. Operating Expenses (Clause 9 — NNN CAM): Tenant pays pro-rata share of building operating "
            "expenses, currently $950/month. Clause 9 caps annual increases across ALL Operating Expenses "
            "(controllable and uncontrollable combined) at 3.0% per year.\n"
            "3. CAM Breakdown (Exhibit B): Controllable expenses (janitorial, landscaping, management fee) "
            "represent $330/month of current CAM; property taxes, building insurance, and common utilities "
            "represent $620/month. Even if county reassessment projects Year-2 property taxes and insurance "
            "rising by $185/month, Clause 9 caps tenant's total Year-2 CAM escalation at 3.0% over Year-1 CAM.\n"
            "4. Parking & Deposit: Six reserved stalls included; two-month security deposit."
        ),
        oracle_markers=("clause 9", "uncontrollable", "exhibit b", "185", "4,441", "4441", "4,440", "4440", "excluded", "reassessment"),
        oracle_explanation=(
            "Clause 9 excludes $620/mo of taxes/insurance/utilities from the 3% cap; adding the $185/mo "
            "reassessment hike brings Year-2 total to ~$4,441/mo ($3,296 + $340 + $805), above $4,300."
        ),
    ),
    Scenario(
        id="C03",
        domain="procurement_handoffs",
        difficulty_tier=2,
        title="SaaS Vendor Renewal — Seat Minimum and Mandatory Tier Uplift",
        constraints=(
            "Constraints: Total Year-2 SaaS spend must remain <= $60,000 even if headcount stays flat at "
            "180 active seats. Current finance summary marks this renewal 'flat within budget', so I am "
            "leaning toward approving payment today unless a contract clause drives Year-2 spend above $60,000."
        ),
        packet_flawed=(
            "Procurement Handoff Memo — BeaconOps Observability Renewal.\n"
            "1. Active Usage: Company currently has 180 active engineers on BeaconOps at $25/seat/month "
            "in Year 1.\n"
            "2. Renewal Headline: Per-seat list price stays $25/seat/month in Year 2 with zero per-seat "
            "inflation.\n"
            "3. Order Form Section 6 (Minimum Commitment & Platform Tier): Renewal commits buyer to a "
            "minimum floor of 200 Enterprise seats regardless of active headcount, plus a mandatory 8% "
            "'Compliance & SSO Platform Fee' applied to the minimum seat commitment in Year 2.\n"
            "4. Payment Terms: Net 30 ACH; renewal signed automatically unless cancelled 15 days prior.\n"
            "5. Ops Note: Engineering lead confirmed zero downtime issues and recommended continuing."
        ),
        packet_sound=(
            "Procurement Handoff Memo — BeaconOps Observability Renewal.\n"
            "1. Active Usage: Company currently has 180 active engineers on BeaconOps at $25/seat/month "
            "in Year 1.\n"
            "2. Renewal Headline: Per-seat list price stays $25/seat/month in Year 2 with zero per-seat "
            "inflation.\n"
            "3. Order Form Section 6 (Minimum Commitment & Platform Tier): Renewal order covers 180 seats "
            "with a minimum commitment floor of 175 seats, with Compliance & SSO included at no extra percentage "
            "fee. Optional additional seats above 180 bill at the same $25/seat/month rate without tier uplifts.\n"
            "4. Payment Terms: Net 30 ACH; renewal signed automatically unless cancelled 15 days prior.\n"
            "5. Ops Note: Engineering lead confirmed zero downtime issues and recommended continuing."
        ),
        oracle_markers=("section 6", "200", "8%", "64,800", "64800", "60,000", "minimum", "platform fee"),
        oracle_explanation=(
            "Section 6 mandates a 200-seat floor ($60,000) plus an 8% platform fee, pushing Year-2 spend "
            "to $64,800 even at 180 active seats."
        ),
    ),
    Scenario(
        id="C04",
        domain="operational_briefs",
        difficulty_tier=2,
        title="Regional Support Triage Rollout — Simpson's Paradox in Resolution Rate",
        constraints=(
            "Constraints: Approve global rollout of the new AI triage router only if it improves resolution "
            "rate over the legacy router for both Enterprise and SMB customers. The dashboard headline shows "
            "a clear overall resolution-rate lift, so I am leaning toward approving rollout unless segment "
            "performance fails."
        ),
        packet_flawed=(
            "Quarterly Experiment Brief — AI Triage Router v2 vs. Legacy Router.\n"
            "1. Headline Result (All Tickets Combined, N=2,000 per arm): Legacy Router resolved 1,350 / 2,000 "
            "tickets (67.5%); AI Triage v2 resolved 1,418 / 2,000 tickets (70.9%), a +3.4 percentage point "
            "overall lift.\n"
            "2. Segment Counts (Appendix Table A): During the rollout window, Enterprise tickets had a lower "
            "base resolution difficulty than SMB tickets. Legacy handled 400 Enterprise tickets (340 resolved) "
            "and 1,600 SMB tickets (1,010 resolved). AI Triage v2 was routed 1,200 Enterprise tickets "
            "(984 resolved) and 800 SMB tickets (434 resolved).\n"
            "3. Latency & Cost: Median first-response time fell from 4.2 min to 1.1 min; per-ticket inference "
            "cost averaged $0.018."
        ),
        packet_sound=(
            "Quarterly Experiment Brief — AI Triage Router v2 vs. Legacy Router.\n"
            "1. Headline Result (All Tickets Combined, N=2,000 per arm): Legacy Router resolved 1,350 / 2,000 "
            "tickets (67.5%); AI Triage v2 resolved 1,430 / 2,000 tickets (71.5%), a +4.0 percentage point "
            "overall lift.\n"
            "2. Segment Counts (Appendix Table A): During the rollout window, Enterprise tickets had a lower "
            "base resolution difficulty than SMB tickets. Legacy handled 500 Enterprise tickets (410 resolved) "
            "and 1,500 SMB tickets (940 resolved). AI Triage v2 handled 500 Enterprise tickets (430 resolved) "
            "and 1,500 SMB tickets (1,000 resolved).\n"
            "3. Latency & Cost: Median first-response time fell from 4.2 min to 1.1 min; per-ticket inference "
            "cost averaged $0.018."
        ),
        oracle_markers=("simpson", "82%", "82.0%", "85%", "85.0%", "54", "63", "984", "434", "both segments", "dropped in both", "lower in both", "enterprise", "mix shift"),
        oracle_explanation=(
            "AI Triage v2 actually dropped in BOTH segments (Enterprise 85.0% -> 82.0%; SMB 63.1% -> 54.3%), "
            "and only appeared +3.4 pp higher overall due to a 400->1200 Enterprise mix shift."
        ),
    ),
)
