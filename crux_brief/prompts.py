"""Prompts, anonymization, and blinded length-matched briefing formatters for crux-brief."""

from __future__ import annotations

import random
from typing import Any

ADVISOR_SYSTEM = """You are an independent pre-decision analyst auditing a decision packet against a user's explicit goal and constraints.

Audit the decision packet against the user's explicit goal and constraints using only the facts in the packet. Verify every stated condition and figure carefully.
Do NOT treat it as a flaw when a packet states component rates, counts, or percentages rather than a pre-summed total—compute the arithmetic yourself from the stated figures and user constraints. Do NOT invent defects when every stated constraint holds.
If every stated constraint is satisfied, recommend "proceed", set risks_or_flaws to ["none"], and set verification_question to "none". Recommend "hold_to_verify" only when a concrete clause, arithmetic calculation, hidden exclusion, or missing premise violates or threatens the user's constraints.

Reply with ONLY one valid JSON object matching this exact schema (complete summary and key_claims before choosing your recommendation):
{
  "summary": "45 to 75 word analytical check computing whether each stated constraint holds",
  "key_claims": ["2 to 3 concise factual or computed figures from the packet"],
  "recommendation": "proceed" or "hold_to_verify",
  "risks_or_flaws": ["concrete constraint violation or missing term ONLY when hold_to_verify; MUST be [\"none\"] when recommendation is proceed"],
  "verification_question": "one concrete check ONLY when hold_to_verify; MUST be \"none\" when recommendation is proceed",
  "confidence": integer 0 to 100
}"""

CONSENSUS_SYSTEM = """You are an impartial deliberation mediator drafting a pre-decision briefing modeled on deliberative common-ground synthesis.

You will read a user's goal/constraints and three anonymized advisor assessments ("Advisor 1", "Advisor 2", "Advisor 3"). You do NOT have the underlying decision packet; rely solely on the advisors' reports and the user's constraints.
Draft ONE cohesive, balanced common-ground briefing spanning 140 to 200 words total across the three sections below:
- overview: synthesize the shared conclusions and overall alignment with constraints in balanced prose.
- points_of_note: weigh advisor points by the specificity of the evidence, terms, and figures cited rather than pure headcount; if an advisor cites a specific term or number that bears on the constraints, address it fairly alongside how the other advisors viewed the packet, weaving nuances into cohesive common ground. When all three advisors recommend "proceed" with no concrete constraint violation, state clearly that no constraint breaches were identified without inventing unnecessary contingencies.
- suggested_next_step: unified practical guidance for the decision maker grounded only in the advisor reports (give clean approval guidance when all three advisors concur constraints hold).

Reply with ONLY one valid JSON object matching this exact schema:
{
  "overview": "concise common-ground overview prose (no lists or JSON inside)",
  "points_of_note": "balanced synthesis of evidence-weighted points and nuances (or state no material issues were flagged)",
  "suggested_next_step": "one cohesive recommended next step"
}"""

CRUX_SYSTEM = """You are an impartial epistemic analyst building a Pre-Decision Crux Brief from three anonymized advisor assessments ("Advisor 1", "Advisor 2", "Advisor 3").

You will read a user's goal/constraints and the three advisor assessments. You do NOT have the underlying decision packet; rely strictly on what the advisors reported without inventing facts or defects.
Rules:
1. shared_ground: 1 to 2 short factual points that the advisors agree on.
2. Unanimous "proceed" rule: If ALL THREE advisors recommend "proceed", do NOT manufacture a disagreement out of stylistic differences or how each advisor derived a passing figure: set cruxes to [], unverified_premises to [], and decisive_check to "None required; all advisors concur stated constraints are satisfied." (unless an advisor explicitly stated a constraint is violated despite writing proceed).
3. Split-panel "cruxes": If the panel is split (1-vs-2 or 2-vs-1 on hold_to_verify vs. proceed) or advisors raise conflicting constraint-relevant claims, list the concrete disagreement(s) in cruxes quoting the specific figures or clauses on side_a vs. side_b plus the premise_at_stake.
4. Unanimous "hold_to_verify" rule: If all three advisors recommend "hold_to_verify" for the same underlying reason with no inter-advisor disagreement, set cruxes to [], summarize the shared blocking issue(s) concisely in unverified_premises (1 to 2 items), and state the concrete decisive_check.
Keep every field crisp so the formatted brief stays within 130 to 205 words.

Reply with ONLY one valid JSON object matching this exact schema:
{
  "shared_ground": ["..."],
  "cruxes": [
    {
      "topic": "short label",
      "side_a": "position and specific figure or term",
      "side_b": "opposing position and specific figure or term",
      "premise_at_stake": "what flips the decision"
    }
  ],
  "unverified_premises": ["..."],
  "decisive_check": "..."
}"""

DECISION_SYSTEM = """You are the final decision maker deciding whether to approve a proposal now ("proceed") or pause to verify a concrete issue ("hold_to_verify").

Read the User Goal & Constraints and the Decision Packet carefully. If a PRE-DECISION BRIEF is included, use it as decision support alongside the packet.
Rules:
- Set "action" to "hold_to_verify" ONLY when a concrete constraint violation or unresolved material discrepancy threatens the stated constraints; otherwise set "action" to "proceed".
- If action is "hold_to_verify", target_clause_or_metric MUST cite the specific clause, section, metric, or figure from the packet that violates or threatens the constraints; otherwise set it to "none".
- If a PRE-DECISION BRIEF was provided, rate brief_endorsement from 1 (unhelpful) to 5 (highly helpful and clear); if no brief was provided, set brief_endorsement to null.

Reply with ONLY one valid JSON object matching this exact schema (complete reasoning and target fields before choosing your final action):
{
  "primary_reason": "1 to 2 concise sentences checking whether the packet satisfies every stated constraint",
  "target_clause_or_metric": "specific clause, section, metric, or figure from the packet, or \"none\"",
  "action": "proceed" or "hold_to_verify",
  "confidence": integer 0 to 100,
  "brief_endorsement": integer 1 to 5, or null if no brief was provided
}"""


def format_advisor_user(constraints: str, packet_text: str) -> str:
    """Format Stage-1 input for an advisor."""
    return (
        "=== USER GOAL & CONSTRAINTS ===\n"
        f"{constraints.strip()}\n\n"
        "=== DECISION PACKET ===\n"
        f"{packet_text.strip()}"
    )


def shuffle_advisors(advisors: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    """Deterministically shuffle and anonymize advisor assessments."""
    items = list(advisors)
    rng = random.Random(seed)
    rng.shuffle(items)
    anonymized: list[dict[str, Any]] = []
    for idx, item in enumerate(items, start=1):
        anonymized.append(
            {
                "label": f"Advisor {idx}",
                "output": item["output"],
            }
        )
    return anonymized


def format_panel_input(constraints: str, anonymized_advisors: list[dict[str, Any]]) -> str:
    """Format Stage-2 input shared identically by Consensus (Arm B) and Crux (Arm C).

    Deliberately excludes the raw packet_text so Stage-2 synthesis cannot act as a
    fourth independent packet auditor.
    """
    blocks = [
        "=== USER GOAL & CONSTRAINTS ===",
        constraints.strip(),
        "",
        "=== ANONYMIZED ADVISOR ASSESSMENTS ===",
    ]
    for adv in anonymized_advisors:
        out = adv["output"]
        blocks.append(f"--- {adv['label']} ---")
        blocks.append(f"Recommendation: {out.get('recommendation')} (confidence {out.get('confidence')}/100)")
        blocks.append(f"Summary: {out.get('summary', '')}")
        claims = out.get("key_claims") or []
        if claims:
            blocks.append("Key claims: " + "; ".join(str(c) for c in claims))
        risks = out.get("risks_or_flaws") or []
        if risks:
            blocks.append("Flagged points: " + "; ".join(str(r) for r in risks))
        vq = out.get("verification_question")
        if vq:
            blocks.append(f"Suggested check: {vq}")
        blocks.append("")
    return "\n".join(blocks).strip()


def _trim_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text.strip()
    if max_words <= 0:
        return ""
    return " ".join(words[:max_words]).rstrip(" ,;") + "..."


def _format_three_sections(
    overview: str,
    points: str,
    next_step: str,
    *,
    max_words: int = 220,
    overview_cap: int = 85,
    points_cap: int = 85,
    step_cap: int = 40,
) -> str:
    """Render the unified 3-section blinded brief strictly within max_words."""
    rendered = "\n".join(
        [
            f"ASSESSMENT OVERVIEW: {overview.strip()}",
            f"POINTS OF NOTE: {points.strip()}",
            f"SUGGESTED NEXT STEP: {next_step.strip()}",
        ]
    )
    if len(rendered.split()) <= max_words:
        return rendered

    comp_overview = _trim_words(overview, overview_cap)
    comp_points = _trim_words(points, points_cap)
    comp_step = _trim_words(next_step, step_cap)
    rendered = "\n".join(
        [
            f"ASSESSMENT OVERVIEW: {comp_overview}",
            f"POINTS OF NOTE: {comp_points}",
            f"SUGGESTED NEXT STEP: {comp_step}",
        ]
    )
    if len(rendered.split()) <= max_words:
        return rendered
    return _trim_words(rendered, max_words)


def _clean_items(raw_items: Any) -> list[str]:
    out: list[str] = []
    for item in raw_items or []:
        s = str(item or "").strip()
        if s and s.lower() not in {"none", "n/a", "none.", "none required"}:
            out.append(s)
    return out


def format_single_brief(advisor_out: dict[str, Any], max_words: int = 220) -> str:
    """Format a single advisor's JSON output into the blinded 3-section template."""
    summary = str(advisor_out.get("summary", "")).strip()
    claims = _clean_items(advisor_out.get("key_claims"))
    risks = _clean_items(advisor_out.get("risks_or_flaws"))
    vq = str(advisor_out.get("verification_question") or "").strip()

    overview_parts = [summary] if summary else []
    if claims:
        overview_parts.append("Key facts: " + "; ".join(claims[:3]) + ".")
    overview = " ".join(overview_parts) or "Advisor completed constraint check."

    points = "; ".join(risks[:3]) + "." if risks else "No concrete constraint violations flagged."
    next_step = (
        vq
        if vq and vq.lower() not in {"none", "none.", "n/a"}
        else "None required; stated constraints appear satisfied."
    )
    return _format_three_sections(overview, points, next_step, max_words=max_words)


def format_consensus_brief(cons_obj: dict[str, Any], max_words: int = 220) -> str:
    """Format Stage-2 consensus JSON into the blinded 3-section template."""
    overview = str(cons_obj.get("overview") or cons_obj.get("brief_text") or "").strip()
    points = str(cons_obj.get("points_of_note") or "").strip()
    next_step = str(cons_obj.get("suggested_next_step") or "").strip()

    if not overview:
        overview = "Advisors reviewed the packet against stated constraints."
    if not points:
        points = "No material disagreements or unresolved constraint issues noted across advisors."
    if not next_step:
        next_step = "None required; advisors agree stated constraints appear satisfied."
    return _format_three_sections(overview, points, next_step, max_words=max_words)


def format_crux_brief(crux_obj: dict[str, Any], max_words: int = 220) -> str:
    """Deterministically format structured crux JSON into the blinded 3-section template."""
    shared = _clean_items(crux_obj.get("shared_ground"))
    cruxes = [c for c in (crux_obj.get("cruxes") or []) if isinstance(c, dict)]
    unverified = _clean_items(crux_obj.get("unverified_premises"))
    check = str(crux_obj.get("decisive_check") or "").strip()

    overview = " ".join(shared[:2]) if shared else "Advisors reviewed the packet against the stated constraints."

    note_segments: list[str] = []
    if cruxes:
        crux_strs = []
        for idx, c in enumerate(cruxes[:3], start=1):
            topic = str(c.get("topic", "Disagreement")).strip()
            a = str(c.get("side_a", "")).strip()
            b = str(c.get("side_b", "")).strip()
            stake = str(c.get("premise_at_stake", "")).strip()
            seg = f"({idx}) {topic}: Side A [{a}] vs. Side B [{b}]"
            if stake:
                seg += f" (at stake: {stake})"
            crux_strs.append(seg)
        note_segments.append("Disagreements: " + " | ".join(crux_strs))
    if unverified:
        note_segments.append("Flagged issues: " + "; ".join(unverified[:2]))
    points = (
        " ".join(note_segments)
        if note_segments
        else "No concrete disagreements or constraint violations flagged across advisors."
    )

    next_step = (
        check
        if check and check.lower() not in {"none", "none."}
        else "None required; advisors concur stated constraints are satisfied."
    )
    # Give Points of Note slightly larger budget under compaction so crux evidence survives.
    return _format_three_sections(
        overview,
        points,
        next_step,
        max_words=max_words,
        overview_cap=55,
        points_cap=115,
        step_cap=38,
    )


def format_decision_user(constraints: str, packet_text: str, brief_text: str | None) -> str:
    """Format Stage-3 input cleanly, blinding arm identity."""
    base = (
        "=== USER GOAL & CONSTRAINTS ===\n"
        f"{constraints.strip()}\n\n"
        "=== DECISION PACKET ===\n"
        f"{packet_text.strip()}"
    )
    if brief_text is None:
        return base + "\n\nNo pre-decision brief was provided (set brief_endorsement to null)."
    return (
        f"{base}\n\n"
        "=== PRE-DECISION BRIEF ===\n"
        f"{brief_text.strip()}\n"
        "=== END BRIEF ==="
    )
