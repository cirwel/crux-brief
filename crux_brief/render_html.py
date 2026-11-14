"""Render a self-contained HTML Pre-Decision Crux Brief card."""

from __future__ import annotations

import html
from typing import Any


def _esc(val: Any) -> str:
    return html.escape(str(val or ""))


def render_brief_html(
    *,
    title: str,
    constraints: str,
    advisors: list[dict[str, Any]],
    crux_obj: dict[str, Any],
    brief_text: str,
    consensus_text: str | None = None,
) -> str:
    """Render a standalone HTML card showing panel splits, cruxes, and decisive check."""
    holds = sum(1 for a in advisors if a["output"].get("recommendation") == "hold_to_verify")
    proceeds = len(advisors) - holds
    split_badge = f"{holds} Hold / {proceeds} Proceed"
    badge_cls = "badge-warn" if holds > 0 else "badge-ok"

    advisor_pills = []
    for idx, adv in enumerate(advisors, start=1):
        out = adv["output"]
        rec = _esc(out.get("recommendation", "unknown")).replace("_", " ")
        conf = _esc(out.get("confidence", "?"))
        m = _esc(adv.get("model", f"Advisor {idx}"))
        pill_cls = "pill-hold" if out.get("recommendation") == "hold_to_verify" else "pill-go"
        advisor_pills.append(f'<span class="pill {pill_cls}">{m}: {rec} ({conf}%)</span>')

    shared_items = "".join(
        f"<li>{_esc(s)}</li>" for s in (crux_obj.get("shared_ground") or [])
    ) or "<li>None stated.</li>"

    crux_cards = []
    for c in crux_obj.get("cruxes") or []:
        if not isinstance(c, dict):
            continue
        crux_cards.append(
            f"""
            <div class="crux-card">
              <div class="crux-topic">{_esc(c.get("topic", "Disagreement"))}</div>
              <div class="crux-grid">
                <div class="side side-a"><strong>Side A</strong><p>{_esc(c.get("side_a", ""))}</p></div>
                <div class="side side-b"><strong>Side B</strong><p>{_esc(c.get("side_b", ""))}</p></div>
              </div>
              <div class="stake"><strong>Premise at stake:</strong> {_esc(c.get("premise_at_stake", ""))}</div>
            </div>
            """
        )
    cruxes_html = "".join(crux_cards) or '<p class="muted">No factual disagreement surfaced among advisors.</p>'

    unverified_items = "".join(
        f"<li>{_esc(u)}</li>" for u in (crux_obj.get("unverified_premises") or [])
    ) or "<li>None flagged.</li>"

    consensus_section = ""
    if consensus_text:
        consensus_section = f"""
        <section class="panel muted-box">
          <h2>Baseline Comparison: Common-Ground Summary</h2>
          <pre>{_esc(consensus_text)}</pre>
        </section>
        """

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Crux Brief — {_esc(title)}</title>
<style>
  :root {{ --fg:#182026; --muted:#5c7080; --border:#d8e1e8; --bg:#f7f9fb; --warn:#d97706; --hold:#b91c1c; --ok:#15803d; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: var(--fg); background: var(--bg); margin: 0; padding: 24px; line-height: 1.48; }}
  .wrap {{ max-width: 860px; margin: 0 auto; background: #fff; border: 1px solid var(--border); border-radius: 10px; padding: 24px 28px; box-shadow: 0 2px 10px rgba(0,0,0,.04); }}
  header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; border-bottom: 1px solid var(--border); padding-bottom: 14px; margin-bottom: 18px; }}
  h1 {{ font-size: 20px; margin: 0 0 4px; }}
  h2 {{ font-size: 14px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); margin: 0 0 8px; }}
  .badge {{ font-size: 13px; font-weight: 600; padding: 5px 10px; border-radius: 999px; white-space: nowrap; }}
  .badge-warn {{ background: #fef3c7; color: #92400e; border: 1px solid #f59e0b; }}
  .badge-ok {{ background: #dcfce7; color: #166534; border: 1px solid #22c55e; }}
  .pills {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }}
  .pill {{ font-size: 12px; padding: 3px 9px; border-radius: 6px; border: 1px solid var(--border); }}
  .pill-hold {{ background: #fee2e2; color: #991b1b; border-color: #fca5a5; }}
  .pill-go {{ background: #ecfdf5; color: #065f46; border-color: #a7f3d0; }}
  .panel {{ margin-bottom: 16px; padding: 12px 14px; border: 1px solid var(--border); border-radius: 8px; background: #fff; }}
  .check-box {{ background: #eff6ff; border-color: #93c5fd; }}
  .muted-box {{ background: #f8fafc; }}
  .crux-card {{ border: 1px solid #fcd34d; background: #fffbeb; border-radius: 8px; padding: 12px; margin-bottom: 10px; }}
  .crux-topic {{ font-weight: 700; margin-bottom: 8px; }}
  .crux-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
  .side {{ background: #fff; border: 1px solid var(--border); border-radius: 6px; padding: 8px 10px; font-size: 13px; }}
  .side p {{ margin: 4px 0 0; }}
  .stake {{ margin-top: 8px; font-size: 13px; color: #78350f; }}
  ul {{ margin: 0; padding-left: 18px; }}
  .muted {{ color: var(--muted); font-size: 13px; }}
  pre {{ white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; background: #f1f5f9; padding: 10px; border-radius: 6px; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>Pre-Decision Crux Brief: {_esc(title)}</h1>
      <div class="muted">{_esc(constraints)}</div>
    </div>
    <span class="badge {badge_cls}">Panel Split: {_esc(split_badge)}</span>
  </header>
  <div class="pills">{"".join(advisor_pills)}</div>

  <section class="panel">
    <h2>Shared Ground</h2>
    <ul>{shared_items}</ul>
  </section>

  <section class="panel">
    <h2>Active Cruxes (Preserved Minority &amp; Split Claims)</h2>
    {cruxes_html}
  </section>

  <section class="panel">
    <h2>Load-Bearing Unverified Premises</h2>
    <ul>{unverified_items}</ul>
  </section>

  <section class="panel check-box">
    <h2>Decisive Check Before Committing</h2>
    <p>{_esc(crux_obj.get("decisive_check", "None specified."))}</p>
  </section>

  <section class="panel">
    <h2>Rendered Text Brief (Word-Matched Output)</h2>
    <pre>{_esc(brief_text)}</pre>
  </section>
  {consensus_section}
</div>
</body>
</html>
"""
