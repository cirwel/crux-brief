"""Unit tests for scenarios, oracle matching, formatting, blinding, and statistical helpers."""

from __future__ import annotations

import unittest

from crux_brief import prompts
from crux_brief.metrics import (
    advisor_flagged_flaw,
    decision_verified_catch,
    matches_oracle,
    mcnemar_exact_p,
    wilson_ci,
)
from crux_brief.scenarios import SCENARIOS
from crux_brief.smoke_scenarios import SMOKE_SCENARIOS

BANNED_GIVEAWAYS = ("flawed", "trap", "trick", "planted", "hidden flaw")
NEUTRAL_HEADINGS = ("ASSESSMENT OVERVIEW:", "POINTS OF NOTE:", "SUGGESTED NEXT STEP:")


class ScenarioSuiteTests(unittest.TestCase):
    def test_scenario_counts_domains_and_tiers(self) -> None:
        self.assertEqual(len(SCENARIOS), 24)
        self.assertEqual(len(SMOKE_SCENARIOS), 4)
        domains = {}
        tiers = {}
        for s in SCENARIOS:
            domains[s.domain] = domains.get(s.domain, 0) + 1
            tiers[s.difficulty_tier] = tiers.get(s.difficulty_tier, 0) + 1
        self.assertEqual(
            domains,
            {"job_offers": 6, "leases": 6, "procurement_handoffs": 6, "operational_briefs": 6},
        )
        self.assertEqual(tiers, {1: 8, 2: 8, 3: 8})

    def test_word_parity_and_no_giveaways(self) -> None:
        for s in (*SMOKE_SCENARIOS, *SCENARIOS):
            w_f = len(s.packet_flawed.split())
            w_s = len(s.packet_sound.split())
            ratio = abs(w_f - w_s) / max(w_f, w_s)
            self.assertLessEqual(ratio, 0.16, f"{s.id} word parity drift: {w_f} vs {w_s}")
            combined = f"{s.constraints}\n{s.packet_flawed}\n{s.packet_sound}".lower()
            for word in BANNED_GIVEAWAYS:
                self.assertNotIn(word, combined, f"Banned word {word!r} in {s.id}")

        for p_text in (
            prompts.ADVISOR_SYSTEM,
            prompts.CONSENSUS_SYSTEM,
            prompts.CRUX_SYSTEM,
            prompts.DECISION_SYSTEM,
        ):
            for word in BANNED_GIVEAWAYS:
                self.assertNotIn(word, p_text.lower())

    def test_oracle_markers_are_meaningful(self) -> None:
        for s in (*SMOKE_SCENARIOS, *SCENARIOS):
            self.assertTrue(len(s.oracle_markers) >= 4, f"{s.id} needs >= 4 oracle markers")
            hits = matches_oracle(s.packet_flawed + " " + s.oracle_explanation, s.oracle_markers)
            self.assertTrue(len(hits) >= 2, f"{s.id} oracle markers barely match own explanation/flaw")


class MetricsAndFormatTests(unittest.TestCase):
    def test_wilson_reference_values(self) -> None:
        p, lo, hi = wilson_ci(0, 40)
        self.assertEqual(p, 0.0)
        self.assertAlmostEqual(lo, 0.0, places=3)
        self.assertAlmostEqual(hi, 0.0876, places=3)

        p2, lo2, hi2 = wilson_ci(40, 40)
        self.assertEqual(p2, 1.0)
        self.assertAlmostEqual(lo2, 0.9124, places=3)
        self.assertAlmostEqual(hi2, 1.0, places=3)

    def test_mcnemar_exact(self) -> None:
        self.assertEqual(mcnemar_exact_p(0, 0), 1.0)
        self.assertAlmostEqual(mcnemar_exact_p(8, 0), 2.0 * (0.5**8), places=6)

    def test_oracle_matching_and_number_commas(self) -> None:
        self.assertTrue(matches_oracle("Year-2 cost reaches $4441/mo.", ("4,441",)))
        self.assertFalse(matches_oracle("96% sensitivity looks strong.", ("1.0%", "ppv", "792")))
        self.assertTrue(
            advisor_flagged_flaw(
                {
                    "recommendation": "hold_to_verify",
                    "summary": "Clause 9 excludes uncontrollable taxes.",
                    "risks_or_flaws": ["Year-2 hits $4,441/mo"],
                    "verification_question": "Check cap.",
                },
                ("clause 9", "4,441"),
            )
        )
        self.assertFalse(
            decision_verified_catch(
                {
                    "action": "hold_to_verify",
                    "primary_reason": "Need more general context.",
                    "target_clause_or_metric": "none",
                },
                ("clause 9", "4,441"),
            )
        )

    def test_neutral_template_and_stage2_isolation(self) -> None:
        anon = [
            {
                "label": "Advisor 1",
                "output": {
                    "recommendation": "proceed",
                    "confidence": 92,
                    "key_claims": ["Rent is $3,200/mo"],
                    "risks_or_flaws": ["none"],
                    "summary": "Meets budget constraints cleanly.",
                    "verification_question": "none",
                },
            }
        ]
        panel_in = prompts.format_panel_input("Stay under $4,300/month.", anon)
        self.assertNotIn("DECISION PACKET", panel_in)
        self.assertIn("Advisor 1", panel_in)

        single = prompts.format_single_brief(anon[0]["output"], max_words=220)
        consensus = prompts.format_consensus_brief(
            {
                "overview": "All three advisors report costs remain below $4,300/month.",
                "points_of_note": "No material issues flagged across reports.",
                "suggested_next_step": "None required; constraints appear satisfied.",
            },
            max_words=220,
        )
        crux_clean = prompts.format_crux_brief(
            {
                "shared_ground": ["Costs stay under $4,300/month."],
                "cruxes": [],
                "unverified_premises": [],
                "decisive_check": "None required; advisors concur stated constraints are satisfied.",
            },
            max_words=220,
        )
        for text in (single, consensus, crux_clean):
            self.assertLessEqual(len(text.split()), 220)
            self.assertNotIn("Advisor leaning", text)
            self.assertNotIn("ACTIVE CRUXES", text)
            for heading in NEUTRAL_HEADINGS:
                self.assertIn(heading, text)

    def test_brief_word_budget_caps(self) -> None:
        long_crux = {
            "shared_ground": ["All advisors note attractive base pay and standard medical benefits. " * 4],
            "cruxes": [
                {
                    "topic": "Vesting Schedule",
                    "side_a": "Advisors 1 & 2 treat the $305k four-year average as meeting the floor.",
                    "side_b": "Advisor 3 flags Section 3.4 vests 0% in Year 1 ($215k < $260k).",
                    "premise_at_stake": "Year-1 realized floor.",
                },
                {
                    "topic": "Discretionary Bonus",
                    "side_a": "Treated as expected cash.",
                    "side_b": "Marked non-guaranteed.",
                    "premise_at_stake": "Guaranteed cash.",
                },
            ],
            "unverified_premises": ["Assumes no termination prior to Year 2."],
            "decisive_check": "Confirm Section 3.4 Year-1 cliff vesting schedule in writing.",
        }
        rendered = prompts.format_crux_brief(long_crux, max_words=220)
        self.assertLessEqual(len(rendered.split()), 220)
        for heading in NEUTRAL_HEADINGS:
            self.assertIn(heading, rendered)

        single = prompts.format_single_brief(
            {
                "recommendation": "proceed",
                "confidence": 88,
                "summary": "word " * 250,
                "key_claims": ["a", "b"],
                "risks_or_flaws": ["none"],
                "verification_question": "none",
            },
            max_words=220,
        )
        self.assertLessEqual(len(single.split()), 220)
        for heading in NEUTRAL_HEADINGS:
            self.assertIn(heading, single)


if __name__ == "__main__":
    unittest.main()
