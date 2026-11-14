"""24 paired decision scenarios (48 packets) across 4 Track-3 decision domains.

Domains (6 each): job_offers, leases, procurement_handoffs, operational_briefs.
Difficulty tiers (8 each): Tier 1 (direct arithmetic/clause violation),
Tier 2 (cross-clause interaction/denominator shift), Tier 3 (structural/statistical paradox).
"""

from __future__ import annotations

from .smoke_scenarios import Scenario

SCENARIOS: tuple[Scenario, ...] = (
    # ---------------- Domain 1: Job Offers & Compensation (S01-S06) ----------------
    Scenario(
        id="S01",
        domain="job_offers",
        difficulty_tier=1,
        title="Back-Loaded Vesting vs. Year-1 Realized Cash+Equity Floor",
        constraints=(
            "Constraints: Total Year-1 realized gross compensation (base salary + guaranteed Year-1 cash "
            "bonus + equity vesting within the first 12 months) must be >= $260,000. I like the mission and "
            "team, so I am leaning toward signing unless Year-1 realized pay falls short of $260,000."
        ),
        packet_flawed=(
            "Offer Summary — Staff Infrastructure Engineer, Meridian AI.\n"
            "1. Base Salary: $205,000/yr paid biweekly.\n"
            "2. Sign-On & Cash Bonus: $10,000 guaranteed Year-1 signing bonus paid on Day 30; target annual "
            "bonus of 10% is discretionary based on company revenue milestones.\n"
            "3. Equity Grant: $400,000 total RSU package (20,000 units at $20/unit).\n"
            "4. Vesting Schedule (Section 3.4): Four-year retention schedule vesting 0% in Year 1, 30% in "
            "Year 2, 35% in Year 3, and 35% in Year 4. Recruiter note highlights $305,000/yr four-year average "
            "compensation.\n"
            "5. Benefits: Standard PPO health insurance and 4% 401(k) match."
        ),
        packet_sound=(
            "Offer Summary — Staff Infrastructure Engineer, Meridian AI.\n"
            "1. Base Salary: $205,000/yr paid biweekly.\n"
            "2. Sign-On & Cash Bonus: $10,000 guaranteed Year-1 signing bonus paid on Day 30; target annual "
            "bonus of 10% is discretionary based on company revenue milestones.\n"
            "3. Equity Grant: $400,000 total RSU package (20,000 units at $20/unit).\n"
            "4. Vesting Schedule (Section 3.4): Standard four-year schedule vesting 25% on the 12-month "
            "cliff and 6.25% quarterly across Years 2 through 4. Recruiter note highlights $305,000/yr "
            "average recurring compensation excluding signing bonus.\n"
            "5. Benefits: Standard PPO health insurance and 4% 401(k) match."
        ),
        oracle_markers=("section 3.4", "0%", "215,000", "215000", "back-loaded", "0 in year 1", "0% in year 1", "vesting 0%"),
        oracle_explanation=(
            "Section 3.4 vests 0% in Year 1, leaving Year-1 realized pay at $215,000 ($205k + $10k) "
            "below the $260,000 floor."
        ),
    ),
    Scenario(
        id="S02",
        domain="job_offers",
        difficulty_tier=1,
        title="Unprorated Gross Sign-On Clawback vs. 18-Month Mobility Rule",
        constraints=(
            "Constraints: Any sign-on bonus repayment obligation must expire by Month 12 (or prorate monthly "
            "on net after-tax payout) so leaving at Month 18 never triggers an out-of-pocket cash clawback. "
            "Role alignment is strong, so I plan to accept unless the repayment clause violates this limit."
        ),
        packet_flawed=(
            "Executive Offer Abstract — Principal Product Lead, Vektor Robotics.\n"
            "1. Compensation: $215,000 base salary plus $40,000 sign-on bonus paid in first paycheck (net "
            "after-tax deposit approximately $24,800 after standard federal/state withholding).\n"
            "2. Repayment Rider (Clause 6b): If employee resigns voluntarily within 24 months of start date, "
            "employee must repay 100% of the gross $40,000 sign-on bonus within 15 days, with no monthly "
            "proration and no reduction for taxes withheld.\n"
            "3. Equity: 35,000 ISOs at $1.40 strike over 4 years with 1-year cliff.\n"
            "4. Severance: 3 months base salary if terminated without cause."
        ),
        packet_sound=(
            "Executive Offer Abstract — Principal Product Lead, Vektor Robotics.\n"
            "1. Compensation: $215,000 base salary plus $40,000 sign-on bonus paid in first paycheck (net "
            "after-tax deposit approximately $24,800 after standard federal/state withholding).\n"
            "2. Repayment Rider (Clause 6b): Repayment applies only if employee resigns voluntarily within "
            "12 months of start date; obligation amortizes 1/12th per completed month and is calculated on "
            "net-of-withholding cash received, dropping to $0 after Month 12.\n"
            "3. Equity: 35,000 ISOs at $1.40 strike over 4 years with 1-year cliff.\n"
            "4. Severance: 3 months base salary if terminated without cause."
        ),
        oracle_markers=("clause 6b", "24 months", "unprorated", "no monthly proration", "taxes withheld", "gross $40,000", "40,000 gross", "15,200"),
        oracle_explanation=(
            "Clause 6b imposes a 24-month, unprorated, gross-amount ($40,000) clawback on a ~$24,800 net payout, "
            "creating a $40k cash liability at Month 18."
        ),
    ),
    Scenario(
        id="S03",
        domain="job_offers",
        difficulty_tier=2,
        title="OTE Variable Quota Cliff vs. Realistic Minimum Cash Earnings",
        constraints=(
            "Constraints: Expected annual cash earnings at historical team attainment must be >= $210,000. "
            "The manager seemed eager to bring me on, so I am leaning toward accepting unless the quota "
            "payout rules drop historical-attainment cash below $210,000."
        ),
        packet_flawed=(
            "Compensation Plan Memo — Enterprise Solutions Lead, Canopy Cloud.\n"
            "1. Headline OTE: $240,000 On-Target Earnings ($160,000 base + $80,000 variable at 100% quota).\n"
            "2. Payout Gate (Schedule A, Clause 5): Variable commission pays linearly above 80% quota "
            "attainment, with a strict zero-commission cliff below 80.0% annual quota attainment.\n"
            "3. Historical Team Data (Onboarding FAQ): Over the past four quarters, median quota attainment "
            "across the Enterprise Solutions team was 74%, with 60% of reps finishing between 65% and 79%.\n"
            "4. Equity & Benefits: $120,000 RSUs over 4 years; full health and commuter benefits."
        ),
        packet_sound=(
            "Compensation Plan Memo — Enterprise Solutions Lead, Canopy Cloud.\n"
            "1. Headline OTE: $240,000 On-Target Earnings ($160,000 base + $80,000 variable at 100% quota).\n"
            "2. Payout Gate (Schedule A, Clause 5): Variable commission pays proportionally from the first "
            "dollar closed (e.g., 70% attainment yields 70% of target variable commission, with no minimum threshold).\n"
            "3. Historical Team Data (Onboarding FAQ): Over the past four quarters, median quota attainment "
            "across the Enterprise Solutions team was 96%, with 60% of reps finishing between 88% and 105%.\n"
            "4. Equity & Benefits: $120,000 RSUs over 4 years; full health and commuter benefits."
        ),
        oracle_markers=("clause 5", "80%", "74%", "160,000", "160000", "zero-commission", "cliff", "schedule a"),
        oracle_explanation=(
            "Schedule A Clause 5 pays $0 variable below 80% attainment while median team attainment is 74%, "
            "making median cash $160,000 (< $210,000)."
        ),
    ),
    Scenario(
        id="S04",
        domain="job_offers",
        difficulty_tier=3,
        title="Preferred Paper Valuation vs. Common Equity Liquidation Overhang",
        constraints=(
            "Constraints: Expected equity grant value must be >= $70,000/yr ($280,000 over 4 years) on an "
            "independent common-stock basis and retain positive payout value in a $100M company exit. "
            "The founder's pitch is persuasive, so I plan to accept unless the cap-table terms fail this floor."
        ),
        packet_flawed=(
            "Offer & Cap-Table Summary — Founding ML Architect, Stratum Labs.\n"
            "1. Cash: $185,000 base salary.\n"
            "2. Equity Headline: Option grant for 400,000 shares of Common Stock (0.40% of 100M fully diluted "
            "shares). Recruiter values this at '$400,000 total / $100,000/yr' based on the recent Series C "
            "$100M post-money preferred valuation ($1.00/share preferred price).\n"
            "3. Cap-Table Footnote (Exhibit C): Company has $82M in cumulative preferred stock carrying a "
            "1.5x participating liquidation preference ahead of common. Most recent 409A independent common "
            "stock valuation sets fair market value at $0.28/share across those 400,000 shares.\n"
            "4. Vesting: Standard 4-year vest with 1-year cliff."
        ),
        packet_sound=(
            "Offer & Cap-Table Summary — Founding ML Architect, Stratum Labs.\n"
            "1. Cash: $185,000 base salary.\n"
            "2. Equity Headline: RSU/low-strike grant for 400,000 shares of Common Stock (0.40% of 100M "
            "fully diluted shares), valued at $400,000 at the $1.00/share Series C mark.\n"
            "3. Cap-Table Footnote (Exhibit C): Company raised $18M total on clean 1x non-participating "
            "preferred terms with no senior overhang. Most recent 409A independent common stock valuation "
            "sets fair market value at $0.82/share on restricted stock with $0.01 par purchase price.\n"
            "4. Vesting: Standard 4-year vest with 1-year cliff."
        ),
        oracle_markers=("exhibit c", "409a", "123m", "1.5x", "0.28", "112,000", "28,000", "liquidation preference", "preference stack"),
        oracle_explanation=(
            "Exhibit C reveals a $123M 1.5x participating preferred overhang and $0.28/sh 409A common valuation "
            "($112k total / $28k/yr, even before subtracting the $0.28 exercise cost), below the $70k/yr floor."
        ),
    ),
    Scenario(
        id="S05",
        domain="job_offers",
        difficulty_tier=2,
        title="Broad Off-Hours IP Assignment Without Prior-Inventions Carve-Out",
        constraints=(
            "Constraints: Employment agreement must NOT claim ownership over my existing Apache-2.0 open-source "
            "observability library ('TraceLite') or weekend personal tools developed strictly off-hours on "
            "personal hardware. HR said it is standard boilerplate, so I am inclined to sign unless the PIIA "
            "clause captures TraceLite or personal off-hours code."
        ),
        packet_flawed=(
            "Employment & PIIA Summary — Senior Reliability Engineer, LatticeOps.\n"
            "1. Role & Pay: $205,000 base, 0.08% options, full remote flexibility.\n"
            "2. Invention Assignment (PIIA Clause 8.1): Employee assigns to Company all right, title, and "
            "interest in any software, tools, or algorithms conceived, modified, or maintained by Employee "
            "during employment—whether on or off Company hours or hardware—that relate to distributed "
            "tracing, telemetry, or developer observability.\n"
            "3. Prior Inventions (PIIA Clause 8.3): Exhibit A (Excluded Prior Inventions) is marked "
            "'None — left blank pending post-onboarding legal review' and no statutory state carve-out "
            "notice is attached; maintenance of prior codebases after start date falls under Clause 8.1.\n"
            "4. Non-Solicit: 12-month mutual customer and employee non-solicit."
        ),
        packet_sound=(
            "Employment & PIIA Summary — Senior Reliability Engineer, LatticeOps.\n"
            "1. Role & Pay: $205,000 base, 0.08% options, full remote flexibility.\n"
            "2. Invention Assignment (PIIA Clause 8.1): Assignment covers solely inventions created using "
            "Company equipment, facilities, trade secrets, or during paid working hours—explicitly excluding "
            "personal open-source libraries, weekend tooling, or codebases maintained off Company hours on "
            "Employee's own hardware.\n"
            "3. Prior Inventions (PIIA Clause 8.3): Exhibit A (Excluded Prior Inventions) explicitly lists "
            "'TraceLite (Apache-2.0 distributed tracing library)' as carved-out prior IP and attaches "
            "the statutory state-law notice protecting off-hours maintenance.\n"
            "4. Non-Solicit: 12-month mutual customer and employee non-solicit."
        ),
        oracle_markers=("clause 8.1", "clause 8.3", "exhibit a", "left blank", "off company hours", "off-hours", "tracelite", "piia"),
        oracle_explanation=(
            "PIIA Clauses 8.1 and 8.3 leave Exhibit A blank and capture off-hours software or maintenance "
            "relating to distributed tracing/observability, sweeping in TraceLite."
        ),
    ),
    Scenario(
        id="S06",
        domain="job_offers",
        difficulty_tier=1,
        title="Relocation Reimbursement After-Tax Net & Receipt Sub-Cap",
        constraints=(
            "Constraints: Guaranteed net after-tax relocation cash available for moving and first-month "
            "housing must be >= $14,000 assuming a 35% marginal combined tax rate. Recruiter highlighted a "
            "generous relocation allowance, so I am leaning toward accepting unless net guaranteed liquidity "
            "drops below $14,000."
        ),
        packet_flawed=(
            "Relocation Addendum — Hardware Systems Engineer, Cascade Semi.\n"
            "1. Headline Allowance: Up to $18,000 relocation package.\n"
            "2. Breakdown (Section 2): Direct moving-company invoice reimbursement capped at $8,000; "
            "lump-sum settling-in stipend of $10,000 paid through payroll.\n"
            "3. Tax & Reimbursement Rule (Section 3): Both the $10,000 lump-sum stipend and the $8,000 "
            "moving-company reimbursement are classified as taxable W-2 compensation with NO tax gross-up "
            "provided; payroll withholds Employee's 35% combined marginal rate from first-month pay.\n"
            "4. Repayment: 12-month prorated stay requirement."
        ),
        packet_sound=(
            "Relocation Addendum — Hardware Systems Engineer, Cascade Semi.\n"
            "1. Headline Allowance: $24,000 relocation package with full tax gross-up.\n"
            "2. Breakdown (Section 2): Direct moving-company invoice reimbursement up to $10,000 plus "
            "$14,000 lump-sum settling-in stipend.\n"
            "3. Tax & Reimbursement Rule (Section 3): Company pays an additional payroll tax gross-up "
            "covering all federal, state, and FICA withholding on both the stipend and moving invoices "
            "so Employee receives the full $24,000 benefit cleanly after taxes.\n"
            "4. Repayment: 12-month prorated stay requirement."
        ),
        oracle_markers=("section 3", "gross-up", "11,700", "11700", "6,500", "2,800", "taxable", "no tax gross"),
        oracle_explanation=(
            "Section 3 provides no tax gross-up; at 35% tax on the full $18,000, net after-tax value is at "
            "most $11,700, below the $14,000 net floor."
        ),
    ),
    # ---------------- Domain 2: Residential & Commercial Leases (S07-S12) ----------------
    Scenario(
        id="S07",
        domain="leases",
        difficulty_tier=1,
        title="Headline Rent vs. Mandatory Bundled Fee Stack",
        constraints=(
            "Constraints: Total unavoidable monthly housing cost (Base Rent + all mandatory monthly landlord "
            "fees and required parking/utility packages) must not exceed $2,550/month. The apartment tour "
            "went great and listed rent is $2,325/mo, so I plan to apply unless mandatory fees push the "
            "monthly total over $2,550."
        ),
        packet_flawed=(
            "Residential Lease Summary — Unit 512, Foundry Lofts.\n"
            "1. Base Rent: $2,325/month for a 12-month term.\n"
            "2. Mandatory Monthly Addenda (Schedule 1): All residents are enrolled in a mandatory $135/month "
            "Smart-Building Tech & Fiber Bundle, $55/month Valet Trash & Package Concierge fee, and "
            "$95/month Assigned Garage Stall fee (required under Phase II zoning covenant even without a car).\n"
            "3. Utilities: Electric and water metered separately by city.\n"
            "4. Deposit: $1,500 refundable security deposit."
        ),
        packet_sound=(
            "Residential Lease Summary — Unit 512, Foundry Lofts.\n"
            "1. Base Rent: $2,325/month for a 12-month term.\n"
            "2. Monthly Addenda (Schedule 1): Fiber Internet & Building Access fee is $75/month mandatory "
            "and Valet Trash is $30/month mandatory. Garage stall ($95/month) and storage locker ($40/month) "
            "are strictly optional add-ons.\n"
            "3. Utilities: Electric and water metered separately by city.\n"
            "4. Deposit: $1,500 refundable security deposit."
        ),
        oracle_markers=("schedule 1", "2,610", "2610", "135", "285", "zoning covenant", "smart-building", "garage"),
        oracle_explanation=(
            "Schedule 1 adds $135 + $55 + $95 = $285/mo in mandatory fees to $2,325 base rent, totaling "
            "$2,610/mo (> $2,550 ceiling)."
        ),
    ),
    Scenario(
        id="S08",
        domain="leases",
        difficulty_tier=2,
        title="90-Day Non-Renewal Notice Window vs. 60-Day Operational Trial",
        constraints=(
            "Constraints: Must be able to exit cleanly at Month 12 based on Month 10 sales results (available "
            "November 3) without triggering an automatic multi-month renewal penalty. Landlord calls it "
            "'a simple 1-year pop-up lease', so I am leaning toward signing unless the notice mechanics bind "
            "us past Month 12."
        ),
        packet_flawed=(
            "Commercial Pop-Up Lease Abstract — Retail Bay 3, Market Row.\n"
            "1. Initial Term: 12 months (Jan 1 to Dec 31) at $3,800/month.\n"
            "2. Renewal & Notice (Clause 14.2): Lease automatically renews for a full additional 12-month "
            "term at $4,104/month (+8%) unless Tenant delivers notarized written non-renewal notice at "
            "least 90 calendar days prior to lease expiration. Notice given after the 90-day cutoff is "
            "ineffective and binds Tenant for the full second year.\n"
            "3. Fit-Out: Landlord delivers broom-clean shell; $4,000 security deposit."
        ),
        packet_sound=(
            "Commercial Pop-Up Lease Abstract — Retail Bay 3, Market Row.\n"
            "1. Initial Term: 12 months (Jan 1 to Dec 31) at $3,800/month.\n"
            "2. Renewal & Notice (Clause 14.2): Written non-renewal notice is due 45 calendar days prior to "
            "expiration at the end of Month 12. Absent renewal election, lease converts to cancellable "
            "month-to-month at +3% rather than locking in a second 12-month term.\n"
            "3. Fit-Out: Landlord delivers broom-clean shell; $4,000 security deposit."
        ),
        oracle_markers=("clause 14.2", "90 calendar days", "90-day", "90 days", "october 2", "month 10", "second year", "automatically renews", "auto-renew"),
        oracle_explanation=(
            "Clause 14.2 sets a 90-day non-renewal deadline (Oct 2), 30 days before Month 10 results arrive, "
            "auto-locking a second 12-month term if missed."
        ),
    ),
    Scenario(
        id="S09",
        domain="leases",
        difficulty_tier=2,
        title="Whole-Month 200% Holdover Multiplier vs. Move-Out Buffer",
        constraints=(
            "Constraints: Maximum exposure for a minor 4-day move-out overrun past lease expiration must "
            "not exceed $2,000 total. Movers occasionally slip by a few days, so I am leaning toward signing "
            "unless the holdover penalty creates > $2,000 liability for a 4-day delay."
        ),
        packet_flawed=(
            "Office Lease Summary — Suite 410, Harborview Plaza.\n"
            "1. Monthly Rent: $5,400/month Base Rent + $1,200/month Additional Rent.\n"
            "2. Holdover Provision (Clause 19): If Tenant fails to surrender premises on the expiration date, "
            "even by one day, Tenant is deemed a holdover tenant for the ENTIRE succeeding calendar month "
            "and owes 200% of total Base + Additional Rent for that full month, regardless of "
            "actual days occupied.\n"
            "3. Alterations: Standard signage permitted with landlord sign-off."
        ),
        packet_sound=(
            "Office Lease Summary — Suite 410, Harborview Plaza.\n"
            "1. Monthly Rent: $5,400/month Base Rent + $1,200/month Additional Rent.\n"
            "2. Holdover Provision (Clause 19): For the first 10 days after expiration, holdover rent is "
            "prorated strictly on a per-diem basis at 125% of daily total Base + Additional Rent, "
            "escalating to 150% per diem only after Day 10.\n"
            "3. Alterations: Standard signage permitted with landlord sign-off."
        ),
        oracle_markers=("clause 19", "200%", "13,200", "13200", "entire succeeding calendar month", "full month"),
        oracle_explanation=(
            "Clause 19 charges 200% of total monthly rent ($13,200) for an entire calendar month even on a "
            "1-to-4 day delay, far exceeding the $2,000 limit."
        ),
    ),
    Scenario(
        id="S10",
        domain="leases",
        difficulty_tier=3,
        title="Sublease Recapture Trap vs. Planned Partner Desk-Sharing",
        constraints=(
            "Constraints: We plan to sublease or desk-share 40% of the floor to our creditworthy hardware "
            "partner startup in Month 3 while keeping our remaining 60% headquarters occupancy intact for "
            "the full 36-month term."
        ),
        packet_flawed=(
            "Commercial Office Lease Abstract — Floor 3, Beacon Annex (4,500 sq ft).\n"
            "1. Term & Rent: 36 months at $11,250/month.\n"
            "2. Assignment & Subletting (Clause 12.4): Tenant may request Landlord consent to sublease a "
            "portion of the Premises, which consent shall not be unreasonably withheld. However, within 15 "
            "days of receiving ANY sublease or space-sharing notice, Landlord holds an absolute unilateral "
            "Recapture Option to terminate the entire Lease (or recapture the floor) effective immediately.\n"
            "3. Insurance: Standard $2M commercial general liability required."
        ),
        packet_sound=(
            "Commercial Office Lease Abstract — Floor 3, Beacon Annex (4,500 sq ft).\n"
            "1. Term & Rent: 36 months at $11,250/month.\n"
            "2. Assignment & Subletting (Clause 12.4): Tenant may sublease or desk-license up to 45% of the "
            "Premises to an affiliated or partner company of reasonable credit for identical office use with "
            "consent not unreasonably withheld; Landlord waives all recapture rights for partial subleases "
            "under 50% of floor area.\n"
            "3. Insurance: Standard $2M commercial general liability required."
        ),
        oracle_markers=("clause 12.4", "recapture", "terminate", "unilateral", "entire lease"),
        oracle_explanation=(
            "Clause 12.4 gives Landlord an absolute unilateral Recapture Option to terminate the entire "
            "lease upon any sublease or space-sharing request."
        ),
    ),
    Scenario(
        id="S11",
        domain="leases",
        difficulty_tier=3,
        title="Disguised Capital HVAC Replacement Liability in Maintenance Clause",
        constraints=(
            "Constraints: Tenant's annual non-rent building repair exposure must be capped <= $3,000/yr, "
            "with no unbudgeted capital equipment replacement obligations. Landlord's cover email promises "
            "'Tenant only handles normal upkeep', so I plan to sign unless a repair clause shifts > $3,000 "
            "capital replacement risk to us."
        ),
        packet_flawed=(
            "Light-Industrial Lease Summary — Unit B, Oakridge Tech Park.\n"
            "1. Base Rent: $4,600/month NNN; 36-month term.\n"
            "2. Maintenance & Repairs (Clause 7c): Landlord repairs roof slab and exterior walls. Tenant "
            "maintains interior and HVAC equipment in good working order. Clause 7c specifies that 'good "
            "working order' includes full capital replacement of the dedicated 10-ton rooftop HVAC unit at "
            "Tenant's sole expense if compressor or heat-exchanger failure occurs.\n"
            "3. Property Inspection Memo (Attachment 2): Existing rooftop Trane unit is 19 years old (typical "
            "service life 15-18 years), showing corroded coils; full replacement quoted at $26,500."
        ),
        packet_sound=(
            "Light-Industrial Lease Summary — Unit B, Oakridge Tech Park.\n"
            "1. Base Rent: $4,600/month NNN; 36-month term.\n"
            "2. Maintenance & Repairs (Clause 7c): Landlord repairs roof slab, exterior walls, and any "
            "structural or HVAC capital unit replacement. Tenant's HVAC obligation is explicitly limited to "
            "quarterly filter/belt servicing and minor upkeep capped at $2,000 aggregate per lease year.\n"
            "3. Property Inspection Memo (Attachment 2): Existing rooftop Trane unit is 19 years old "
            "(typical service life 15-18 years); Landlord has escrowed $26,500 in capital reserves for full replacement."
        ),
        oracle_markers=("clause 7c", "26,500", "26500", "19 years", "capital replacement", "hvac", "sole expense", "attachment 2"),
        oracle_explanation=(
            "Clause 7c shifts full $26,500 capital replacement of an end-of-life 19-year-old HVAC unit onto "
            "Tenant, breaking the $3,000 annual repair cap."
        ),
    ),
    Scenario(
        id="S12",
        domain="leases",
        difficulty_tier=1,
        title="Exclusive Building ISP Speed Cap vs. Studio Upload Requirement",
        constraints=(
            "Constraints: Unit must support symmetrical >= 200 Mbps fiber internet (up and down) for daily "
            "remote engineering video/dataset syncs, with total rent <= $2,700/mo. Listing says 'High-speed "
            "building Wi-Fi included', so I am leaning toward signing unless internet rules violate >= 200 Mbps."
        ),
        packet_flawed=(
            "Apartment Lease Abstract — Unit 308, Civic Commons.\n"
            "1. Rent: $2,550/month including water and trash.\n"
            "2. Telecommunications Rider (Clause 6.1): Property operates under an exclusive 10-year bulk ISP "
            "agreement with MetroAir Wireless. Tenant receives building shared Wi-Fi capped at 50 Mbps "
            "download / 10 Mbps upload. Outside fiber installation or external cellular gateways are "
            "strictly prohibited under facade and conduit covenants.\n"
            "3. Term: 12 months; pet fee waived."
        ),
        packet_sound=(
            "Apartment Lease Abstract — Unit 308, Civic Commons.\n"
            "1. Rent: $2,550/month including water and trash.\n"
            "2. Telecommunications Rider (Clause 6.1): Unit is wired directly with symmetric 1,000 Mbps "
            "(1 Gbps up/down) dedicated municipal fiber drop included in rent, and Tenant may optionally "
            "order secondary commercial fiber service via the utility closet.\n"
            "3. Term: 12 months; pet fee waived."
        ),
        oracle_markers=("clause 6.1", "50 mbps", "10 mbps", "prohibited", "metroair", "bulk isp"),
        oracle_explanation=(
            "Clause 6.1 locks the building into an exclusive 50/10 Mbps ISP and bans external fiber, failing "
            "the 200 Mbps symmetrical requirement."
        ),
    ),
    # ---------------- Domain 3: Procurement & Cross-Team Handoffs (S13-S18) ----------------
    Scenario(
        id="S13",
        domain="procurement_handoffs",
        difficulty_tier=2,
        title="SLA 99.5% Business-Hours Exclusion & Credit Cap",
        constraints=(
            "Constraints: Maximum permitted unscheduled or scheduled outage during US business hours "
            "(Mon-Fri 09:00-17:00) is <= 60 minutes/month, and SLA breaches must reimburse >= 50% of the "
            "monthly fee. Vendor deck touts an 'Enterprise High-Availability SLA', so I am leaning toward "
            "approving unless the SLA terms fail these two thresholds."
        ),
        packet_flawed=(
            "Vendor SLA Review — LedgerSync Payments API ($8,000/month).\n"
            "1. Availability Target (Section 4.1): Vendor warrants 99.5% monthly uptime measured across each "
            "30-day calendar month.\n"
            "2. Maintenance Exclusion (Section 4.2): Scheduled maintenance windows of up to 2 hours per "
            "week may occur during US daytime hours (Tue/Thu 13:00-15:00) and are excluded from SLA uptime.\n"
            "3. Remedy (Section 4.4): Sole remedy for any SLA breach is a service credit capped at 10% of "
            "one monthly fee."
        ),
        packet_sound=(
            "Vendor SLA Review — LedgerSync Payments API ($8,000/month).\n"
            "1. Availability Target (Section 4.1): Vendor warrants 99.9% monthly uptime measured across each "
            "30-day calendar month.\n"
            "2. Maintenance Exclusion (Section 4.2): Scheduled maintenance windows of up to 2 hours occur "
            "strictly during off-peak Sundays (02:00-04:00 UTC) with zero US daytime outage permitted.\n"
            "3. Remedy (Section 4.4): Any SLA breach below 99.9% triggers a 50% service credit of one monthly "
            "fee, rising to a full 100% monthly fee refund below 99.5%."
        ),
        oracle_markers=("section 4.1", "section 4.2", "section 4.4", "99.5%", "13:00", "216", "3.6", "10%", "daytime", "800"),
        oracle_explanation=(
            "99.5% allows 3.6h unplanned downtime, Section 4.2 excludes 2h daytime maintenance windows, and "
            "Section 4.4 caps credits at 10% (violating <= 60 min and >= 50% credit constraints)."
        ),
    ),
    Scenario(
        id="S14",
        domain="procurement_handoffs",
        difficulty_tier=3,
        title="Cross-Principal Invoice Handoff — Currency Unit Mismatch",
        constraints=(
            "Constraints: Approve wire payout ONLY if the total USD bank debit does not exceed the "
            "$21,000.00 USD Purchase Order ceiling. Receiving clerk verified 'quantity 500 and unit figure "
            "42.00 match the PO', so I am leaning toward releasing payment unless actual USD payout exceeds $21,000.00."
        ),
        packet_flawed=(
            "AP Wire Handoff Packet — Batch #PO-8841 (EuroParts GmbH).\n"
            "1. PO Authorization: 500 Precision Actuators at contracted unit price $42.00 USD ($21,000.00 USD).\n"
            "2. Receiving Verification: Warehouse signed off 500 units received intact; automated check "
            "confirmed invoice line quantity (500) and unit price figure (42.00) match PO.\n"
            "3. Settlement Wire Detail (Line 7): Vendor billed invoice in EUR (500 x 42.00 EUR = 21,000.00 "
            "EUR). Bank FX desk quotes today's spot rate at 1.14 USD/EUR to settle the full EUR invoice.\n"
            "4. Terms: Net 15 wire transfer."
        ),
        packet_sound=(
            "AP Wire Handoff Packet — Batch #PO-8841 (EuroParts GmbH).\n"
            "1. PO Authorization: 500 Precision Actuators at contracted unit price $42.00 USD ($21,000.00 USD).\n"
            "2. Receiving Verification: Warehouse signed off 500 units received intact; automated check "
            "confirmed invoice quantity (500) and total USD settlement match PO.\n"
            "3. Settlement Wire Detail (Line 7): Vendor billed invoice directly in USD (500 x $42.00 USD = "
            "$21,000.00 USD) via domestic USD correspondent account with zero currency conversion or intermediary deduction.\n"
            "4. Terms: Net 15 wire transfer."
        ),
        oracle_markers=("line 7", "eur", "23,940", "23940", "1.14", "currency", "fx"),
        oracle_explanation=(
            "Line 7 bills 42.00 EUR instead of USD; at 1.14 USD/EUR, the wire debits $23,940.00 USD, "
            "$2,940 above the $21,000 USD PO."
        ),
    ),
    Scenario(
        id="S15",
        domain="procurement_handoffs",
        difficulty_tier=2,
        title="Early-Payment Discount APR vs. Revolving Credit-Line Cost",
        constraints=(
            "Constraints: Approve paying Supplier Invoice #4490 early on Day 10 ONLY if taking the "
            "discount yields a positive net dollar savings after credit-line financing cost. Treasury clerk "
            "marked this as 'guaranteed instant savings', so I am leaning toward paying early unless net "
            "financing return is negative."
        ),
        packet_flawed=(
            "Treasury Cash-Management Memo — Supplier Invoice #4490 ($250,000).\n"
            "1. Invoice Terms: 0.4% / 10 Net 30 (buyer receives a 0.4% discount, saving $1,000, by paying on "
            "Day 10 instead of Day 30 — accelerating cash outflow by 20 days).\n"
            "2. Funding Source: Operating cash reserve is fully committed this month, so paying on Day 10 "
            "requires drawing $249,000 on our corporate revolving credit line at 12.0% APR.\n"
            "3. Payment Execution: Wire $249,000 on Day 10 from the revolving credit facility and repay the "
            "facility principal on Day 30 when customer receivables clear.\n"
            "4. Clerk Note: 'Pays $249,000 instead of $250,000 — saves $1,000 off face value on Day 10.'"
        ),
        packet_sound=(
            "Treasury Cash-Management Memo — Supplier Invoice #4490 ($250,000).\n"
            "1. Invoice Terms: 2.0% / 10 Net 30 (buyer receives a 2.0% discount, saving $5,000, by paying on "
            "Day 10 instead of Day 30 — accelerating cash outflow by 20 days).\n"
            "2. Funding Source: Operating cash reserve is fully committed this month, so paying on Day 10 "
            "requires drawing $245,000 on our corporate revolving credit line at 12.0% APR.\n"
            "3. Payment Execution: Wire $245,000 on Day 10 from the revolving credit facility and repay the "
            "facility principal on Day 30 when customer receivables clear.\n"
            "4. Clerk Note: 'Pays $245,000 instead of $250,000 — saves $5,000 off face value on Day 10.'"
        ),
        oracle_markers=("0.4%", "7.3", "7.4", "1,637", "1637", "1,644", "1,660", "660", "negative", "net loss", "below 12", "under 12", "costs more", "637"),
        oracle_explanation=(
            "0.4%/10 Net 30 returns ~7.3% APR ($1,000 saved vs ~$1,637 interest on the 12% credit line), a net loss."
        ),
    ),
    Scenario(
        id="S16",
        domain="procurement_handoffs",
        difficulty_tier=3,
        title="Custom Build Ownership vs. Non-Sublicensable Core Background SDK",
        constraints=(
            "Constraints: Delivered analytics platform must be deployable as a white-labeled commercial software "
            "product distributed and sublicensed to external enterprise clients. Legal summary notes 'Buyer "
            "owns 100% of custom deliverables', so I am leaning toward signing."
        ),
        packet_flawed=(
            "Software Development SOW Summary — Custom Analytics Engine ($140,000 fixed fee).\n"
            "1. Foreground Work Product (Section 9.1): All custom frontend dashboards, schemas, and REST "
            "endpoints written under this SOW are 'Work Made for Hire' owned 100% by Buyer.\n"
            "2. Background Technology (Section 9.3): Vendor's proprietary stream-aggregation runtime "
            "(which powers ~70% of core query execution and is embedded as a compiled binary dependency) "
            "remains Vendor Background IP. Buyer receives a perpetual license strictly 'for Buyer's own "
            "internal business operations, non-transferable and non-sublicensable to third parties.'\n"
            "3. Schedule: 10-week delivery with acceptance testing."
        ),
        packet_sound=(
            "Software Development SOW Summary — Custom Analytics Engine ($140,000 fixed fee).\n"
            "1. Foreground Work Product (Section 9.1): All custom frontend dashboards, schemas, and REST "
            "endpoints written under this SOW are 'Work Made for Hire' owned 100% by Buyer.\n"
            "2. Background Technology (Section 9.3): Vendor's proprietary stream-aggregation runtime "
            "remains Vendor Background IP, and Vendor grants Buyer a perpetual, worldwide, paid-up, "
            "transferable license WITH full rights to distribute and sublicense to Buyer's external clients.\n"
            "3. Schedule: 10-week delivery with acceptance testing."
        ),
        oracle_markers=("section 9.3", "background ip", "background technology", "non-sublicensable", "internal business", "third parties", "sublicens"),
        oracle_explanation=(
            "Section 9.3 restricts the embedded core runtime (Background IP) to internal use only and forbids "
            "sublicensing to third-party clients."
        ),
    ),
    Scenario(
        id="S17",
        domain="procurement_handoffs",
        difficulty_tier=1,
        title="Headline Unit Quote vs. Mandatory Support & Crating Add-Ons",
        constraints=(
            "Constraints: Total all-in Purchase Order cost for 100 engineering workstations (hardware + "
            "mandatory warranty/support + shipping/crating) must stay <= $118,000. Sales rep assured us "
            "the workstation quote fits within budget, so I am leaning toward approving unless all-in PO total exceeds $118,000."
        ),
        packet_flawed=(
            "Hardware Quote #Q-702 — 100 Developer Workstations.\n"
            "1. Hardware Subtotal: 100 developer workstations priced at $1,150 per unit.\n"
            "2. Required Bundle Policy (Note B): Manufacturer policy mandates attaching SKU-SUP-3Y (3-year "
            "onsite support at $95 per unit) to every enterprise workstation PO; cannot be waived.\n"
            "3. Freight & Pallet Crating (Note C): Flat insured palletized delivery fee of $3,800.\n"
            "4. Lead Time: Ships within 7 business days of PO issuance."
        ),
        packet_sound=(
            "Hardware Quote #Q-702 — 100 Developer Workstations.\n"
            "1. Hardware Subtotal: 100 developer workstations priced at $1,080 per unit.\n"
            "2. Required Bundle Policy (Note B): Manufacturer mandates attaching SKU-SUP-3Y (3-year onsite "
            "support) at $70 per unit.\n"
            "3. Freight & Pallet Crating (Note C): Flat insured palletized delivery fee of $2,200 covers "
            "the full shipment.\n"
            "4. Lead Time: Ships within 7 business days of PO issuance."
        ),
        oracle_markers=("128,300", "128300", "9,500", "9500", "3,800", "note b", "note c", "sku-sup-3y"),
        oracle_explanation=(
            "Notes B and C add $9,500 mandatory support + $3,800 freight to $115,000 hardware = $128,300 all-in "
            "(> $118,000 ceiling)."
        ),
    ),
    Scenario(
        id="S18",
        domain="procurement_handoffs",
        difficulty_tier=3,
        title="All-or-Nothing Volume Rebate Cliff Below 1,000 Units",
        constraints=(
            "Constraints: Projected Q4 procurement cost reduction from volume rebates must guarantee "
            ">= $15,000 rebate savings even if Q4 demand lands anywhere in our 950-to-1,050 unit band. "
            "Category manager expects Q4 volume rebates to exceed $15,000, so I am leaning toward signing "
            "unless rebates can fail inside the 950-1,050 band."
        ),
        packet_flawed=(
            "Supplier Rebate Schedule Memo — Q4 Packaging Supply.\n"
            "1. Base Unit Price: $200/unit, no upfront discount.\n"
            "2. Rebate Structure (Schedule C): Upon reaching 1,000 billed units within Q4, Seller issues a "
            "retroactive $20/unit credit across all Q4 units. Schedule C states explicitly that if Q4 volume "
            "finishes at 999 units or fewer, zero rebate ($0) is earned.\n"
            "3. Demand Plan: Operations Q4 forecast midpoint is 980 units with a 950-to-1,050 unit planning band."
        ),
        packet_sound=(
            "Supplier Rebate Schedule Memo — Q4 Packaging Supply.\n"
            "1. Base Unit Price: $200/unit, no upfront discount.\n"
            "2. Rebate Structure (Schedule C): Upon reaching 850 billed units within Q4, Seller issues an "
            "unconditional $18/unit credit across all Q4 units with zero cliff penalty anywhere above 850 units.\n"
            "3. Demand Plan: Operations Q4 forecast midpoint is 980 units with a 950-to-1,050 unit planning band."
        ),
        oracle_markers=("schedule c", "999", "zero rebate", "$0", "cliff", "1,000", "below 1000", "below 1,000"),
        oracle_explanation=(
            "Schedule C pays $0 rebate below 1,000 units; anywhere in 950-999 units (including the 980 "
            "midpoint forecast) earns $0 instead of $19,600."
        ),
    ),
    # ---------------- Domain 4: Operational & Policy Decision Briefs (S19-S24) ----------------
    Scenario(
        id="S19",
        domain="operational_briefs",
        difficulty_tier=3,
        title="Base-Rate PPV Fallacy in Automated Fraud Suspension Rule",
        constraints=(
            "Constraints: Enable fully automated account suspension (without human review) ONLY if at least "
            "40% of accounts suspended in live production traffic are genuinely fraudulent. Security team "
            "emphasizes high benchmark sensitivity and specificity, so I am leaning toward enabling "
            "auto-suspension unless actual live suspension accuracy falls under 40%."
        ),
        packet_flawed=(
            "Trust & Safety Model Readiness Brief — FraudGuard v4 Auto-Suspend.\n"
            "1. Validation Metrics (balanced 50/50 test benchmark): 96.0% sensitivity (catches 96% of "
            "fraudulent accounts) and 92.0% specificity (8.0% false-positive rate on clean accounts).\n"
            "2. Live Production Traffic Profile (Section 3): Weekly live volume is 10,000 new accounts, of "
            "which historical audit shows a true fraud base rate of 1.0% (100 fraudulent, 9,900 legitimate).\n"
            "3. Proposed Policy: Route every flagged account directly to permanent automated suspension.\n"
            "4. Latency: 18 ms p99 scoring overhead."
        ),
        packet_sound=(
            "Trust & Safety Model Readiness Brief — FraudGuard v4 Auto-Suspend.\n"
            "1. Validation Metrics (balanced 50/50 test benchmark): 95.0% sensitivity (catches 95% of "
            "fraudulent accounts) and 99.4% specificity (0.6% false-positive rate on clean accounts).\n"
            "2. Live Production Traffic Profile (Section 3): High-risk checkout review volume is 10,000 new "
            "accounts weekly, of which historical audit shows a true fraud base rate of 10.0% (1,000 fraudulent, "
            "9,000 legitimate).\n"
            "3. Proposed Policy: Route every flagged account directly to permanent automated suspension.\n"
            "4. Latency: 18 ms p99 scoring overhead."
        ),
        oracle_markers=("1%", "1.0%", "10.8", "10.9", "11%", "792", "888", "9,900", "base rate", "ppv", "precision", "false positive"),
        oracle_explanation=(
            "At 1.0% base rate (100 fraud / 9,900 clean), 96% sensitivity + 92% specificity gives 96 TP vs "
            "792 FP -> PPV = 10.8% (<< 40% floor)."
        ),
    ),
    Scenario(
        id="S20",
        domain="operational_briefs",
        difficulty_tier=2,
        title="Survivorship Bias in 90-Day Customer Retention Report",
        constraints=(
            "Constraints: Scale paid acquisition budget ONLY if at least 65% of newly activated accounts "
            "remain active at Day 90. Growth memo headlines 90-day retention comfortably above 65%, so I am "
            "leaning toward scaling spend unless true 90-day cohort retention is under 65%."
        ),
        packet_flawed=(
            "Growth Q3 Review — Paid Acquisition Scale Proposal.\n"
            "1. Headline KPI: '90-Day Cohort Retention reached 74.0% (740 retained of 1,000 users tracked), "
            "beating our 65% scale threshold.'\n"
            "2. Cohort Definition Footnote (Methodology Note 2): To reduce telemetry noise, the analytics "
            "dashboard begins tracking the retention cohort only after a user completes Week-2 billing "
            "configuration (1,000 users). An additional 400 users who activated on Day 0 but churned during "
            "Days 1-14 prior to billing setup are excluded from the denominator.\n"
            "3. CAC: $190 blended customer acquisition cost."
        ),
        packet_sound=(
            "Growth Q3 Review — Paid Acquisition Scale Proposal.\n"
            "1. Headline KPI: '90-Day Cohort Retention reached 69.0% (966 retained of 1,400 Day-0 signups), "
            "beating our 65% scale threshold.'\n"
            "2. Cohort Definition Footnote (Methodology Note 2): To prevent survivorship distortion, the "
            "analytics dashboard begins tracking the retention cohort from initial Day-0 activation across "
            "all 1,400 activated accounts, explicitly including all 160 users who churned during Days 1-14 "
            "prior to completing Week-2 billing configuration.\n"
            "3. CAC: $190 blended customer acquisition cost."
        ),
        oracle_markers=("methodology note 2", "survivorship", "400", "1,400", "1400", "52.9%", "53%", "denominator", "excluded"),
        oracle_explanation=(
            "Methodology Note 2 drops 400 Day 1-14 churned users from the denominator; true Day-0 retention "
            "is 740 / 1,400 = 52.9% (< 65%)."
        ),
    ),
    Scenario(
        id="S21",
        domain="operational_briefs",
        difficulty_tier=2,
        title="Uncached p95 Latency Regression Hidden by Cache-Hit Mix Shift",
        constraints=(
            "Constraints: Promote API Engine v3.2 to production ONLY if database-backed request p95 latency "
            "stays <= 180 ms (must not regress above 180 ms). Release brief celebrates a 'major drop in "
            "overall mean API latency', so I am leaning toward approving deployment unless database-backed "
            "request p95 latency exceeds 180 ms."
        ),
        packet_flawed=(
            "Release Readiness Report — API Engine v3.2.\n"
            "1. Top-Line Summary: Overall mean API response time dropped 28% from 140 ms (v3.1) to 101 ms "
            "(v3.2) across 100k shadow requests.\n"
            "2. Breakdown Appendix: During the v3.2 benchmark window, an upstream CDN pre-warming job pushed "
            "cache-hit rate from 40% (v3.1, 5 ms cached) to 82% (v3.2, 5 ms cached). On the remaining "
            "uncached database-query path, v3.2 p95 latency rose from 165 ms (v3.1) to 248 ms (v3.2) due to "
            "a new ORM join.\n"
            "3. Error Rate: HTTP 5xx stayed steady at 0.02%."
        ),
        packet_sound=(
            "Release Readiness Report — API Engine v3.2.\n"
            "1. Top-Line Summary: Overall mean API response time dropped 20% from 140 ms (v3.1) to 112 ms "
            "(v3.2) across 100k shadow requests.\n"
            "2. Breakdown Appendix: During the v3.2 benchmark window, CDN cache configuration was locked so "
            "cache-hit rate stayed identical at 40% (v3.1, 5 ms) and 40% (v3.2, 5 ms). On the uncached "
            "database-query path, v3.2 p95 latency improved from 165 ms (v3.1) to 134 ms (v3.2).\n"
            "3. Error Rate: HTTP 5xx stayed steady at 0.02%."
        ),
        oracle_markers=("248", "uncached", "82%", "cache-hit", "cache hit", "orm join"),
        oracle_explanation=(
            "Cache-hit shift (40% -> 82%) masked a regression on uncached DB queries where p95 latency rose to "
            "248 ms (> 180 ms ceiling)."
        ),
    ),
    Scenario(
        id="S22",
        domain="operational_briefs",
        difficulty_tier=1,
        title="Incident Count Drop vs. Exposure-Normalized Rate Increase",
        constraints=(
            "Constraints: Authorize Phase-2 autonomous shuttle expansion ONLY if safety incidents per "
            "10,000 service miles decreased by >= 20% year-over-year. Executive summary cites a '26% drop "
            "in monthly incidents', so I am leaning toward authorizing expansion unless the per-10k-mile "
            "rate failed to drop by >= 20%."
        ),
        packet_flawed=(
            "Municipal Transit Safety Update — Autonomous Shuttle Pilot.\n"
            "1. Incident Count Headline: Total reportable safety disengagements fell 26.3%, from 38 events "
            "in Q3 last year to 28 events in Q3 this year.\n"
            "2. Fleet Telemetry Table: Last year's Q3 fleet logged 120,000 autonomous service miles. "
            "Due to downtown construction detours this Q3, active fleet mileage declined 35% to 78,000 "
            "service miles.\n"
            "3. Public Feedback: Rider satisfaction survey scored 4.4 / 5.0."
        ),
        packet_sound=(
            "Municipal Transit Safety Update — Autonomous Shuttle Pilot.\n"
            "1. Incident Count Headline: Total reportable safety disengagements fell 26.3%, from 38 events "
            "in Q3 last year to 28 events in Q3 this year.\n"
            "2. Fleet Telemetry Table: Last year's Q3 fleet logged 120,000 autonomous service miles. "
            "This Q3, expanded route hours increased active fleet mileage by 12.5% to 135,000 service miles.\n"
            "3. Public Feedback: Rider satisfaction survey scored 4.4 / 5.0."
        ),
        oracle_markers=("78,000", "78000", "3.59", "3.6", "35%", "10,000 miles", "per 10,000", "rate rose", "rate increased", "mileage declined", "miles declined"),
        oracle_explanation=(
            "Mileage fell 35% (120k -> 78k), so the incident rate per 10,000 miles actually rose from 3.17 to "
            "3.59 instead of dropping >= 20%."
        ),
    ),
    Scenario(
        id="S23",
        domain="operational_briefs",
        difficulty_tier=3,
        title="A/B Checkout Experiment Sample-Ratio Mismatch & Early Peeking",
        constraints=(
            "Constraints: Ship the new checkout pricing tier ONLY if the experiment provides statistically "
            "valid evidence of positive ARPU lift under the pre-registered test plan. Growth slide reports "
            "'statistically significant positive ARPU lift (p < 0.05)', so I am leaning toward shipping unless experimental validity is broken."
        ),
        packet_flawed=(
            "Experiment Readout — Checkout Tier Repricing Test (#EXP-19).\n"
            "1. Headline Result: Control ARPU $4.10 vs. Variant ARPU $4.55 (+11.0%, two-sided p = 0.03).\n"
            "2. Sample & Stopping Log: Intended 50/50 randomized split over a pre-registered 14-day window. "
            "Experiment was halted early on Day 5 as soon as p < 0.05 was observed. Final recorded sessions "
            "were 10,000 in Control vs. 8,380 in Variant.\n"
            "3. Engineering Footnote: Variant's added redirect script timed out for ~1,600 low-intent mobile "
            "visitors before session logging completed."
        ),
        packet_sound=(
            "Experiment Readout — Checkout Tier Repricing Test (#EXP-19).\n"
            "1. Headline Result: Control ARPU $4.10 vs. Variant ARPU $4.48 (+9.3%, two-sided p = 0.004).\n"
            "2. Sample & Stopping Log: Intended 50/50 randomized split over a pre-registered 14-day window. "
            "Experiment completed the full 14 days with zero early stopping. Final recorded sessions were "
            "10,000 in Control vs. 10,032 in Variant.\n"
            "3. Engineering Footnote: Telemetry logs confirmed zero redirect timeouts or dropped mobile "
            "sessions across either experiment arm."
        ),
        oracle_markers=("8,380", "8380", "16.2%", "srm", "sample ratio", "imbalance", "day 5", "early", "peeking", "halted", "timeout", "1,600"),
        oracle_explanation=(
            "Test peeked/stopped on Day 5 and exhibits severe SRM (10,000 vs 8,380, -16.2%) due to mobile "
            "timeouts dropping low-intent Variant visitors."
        ),
    ),
    Scenario(
        id="S24",
        domain="operational_briefs",
        difficulty_tier=1,
        title="Gross Overtime Savings vs. Net Budget Including Nurse Staffing Cost",
        constraints=(
            "Constraints: Approve hospital float-pool hiring plan ONLY if Year-1 net budget savings (after "
            "all new salaries, benefits, and agency placement fees) are >= $100,000. Proposal headline "
            "highlights substantial monthly emergency-overtime savings, so I am leaning toward approving "
            "unless net Year-1 savings fall under $100,000."
        ),
        packet_flawed=(
            "Nursing Operations Budget Brief — Internal Float-Pool Proposal.\n"
            "1. Headline Benefit: Adding two full-time internal float nurses eliminates $20,000/month in "
            "emergency overtime shifts across the year.\n"
            "2. Cost Schedule (Table B): Combined compensation + benefits for the two full-time float nurses "
            "is $95,000/year fully loaded each, plus a one-time $35,000 recruiting agency placement fee due "
            "in Month 1.\n"
            "3. Scheduling Impact: Weekend shift coverage stability expected to improve."
        ),
        packet_sound=(
            "Nursing Operations Budget Brief — Internal Float-Pool Proposal.\n"
            "1. Headline Benefit: Adding two full-time internal float nurses eliminates $30,000/month in "
            "external registry & emergency overtime across the year.\n"
            "2. Cost Schedule (Table B): Combined compensation + benefits for the two full-time float nurses "
            "is $95,000/year fully loaded each, plus a one-time $15,000 internal referral bonus due in Month 1.\n"
            "3. Scheduling Impact: Weekend shift coverage stability expected to improve."
        ),
        oracle_markers=("15,000", "15000", "225,000", "225000", "190,000", "35,000", "table b", "net savings"),
        oracle_explanation=(
            "Table B costs total $225,000 ($190k comp + $35k agency fee) against $240,000 overtime savings, "
            "netting only $15,000 in Year 1 (< $100,000)."
        ),
    ),
)
