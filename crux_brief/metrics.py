"""Oracle matching, Wilson 95% confidence intervals, and paired McNemar tests."""

from __future__ import annotations

import math
import re
from typing import Iterable


def normalize_text(text: str) -> str:
    """Lowercase and normalize commas/punctuation/whitespace for marker matching."""
    t = text.lower()
    # Strip commas inside numbers so 4,460 matches 4460.
    t = re.sub(r"(?<=\d),(?=\d)", "", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def matches_oracle(text: str, oracle_markers: Iterable[str]) -> list[str]:
    """Return all oracle markers matched in text (empty list if none)."""
    norm = normalize_text(text)
    matched: list[str] = []
    for raw_marker in oracle_markers:
        m = normalize_text(raw_marker)
        if not m:
            continue
        if len(m) <= 4 and m.isalnum():
            if re.search(rf"(?<![a-z0-9]){re.escape(m)}(?![a-z0-9])", norm):
                matched.append(raw_marker)
        elif m in norm:
            matched.append(raw_marker)
    return matched


def advisor_flagged_flaw(advisor_out: dict, oracle_markers: Iterable[str]) -> bool:
    """Return True iff advisor recommends hold_to_verify AND cites an oracle marker."""
    if advisor_out.get("recommendation") != "hold_to_verify":
        return False
    combined = " ".join(
        [
            str(advisor_out.get("summary", "")),
            " ".join(str(x) for x in (advisor_out.get("risks_or_flaws") or [])),
            str(advisor_out.get("verification_question", "")),
        ]
    )
    return bool(matches_oracle(combined, oracle_markers))


def decision_verified_catch(decision_out: dict, oracle_markers: Iterable[str]) -> bool:
    """Return True iff Stage-3 chooses hold_to_verify AND reason/target hits an oracle marker."""
    if decision_out.get("action") != "hold_to_verify":
        return False
    combined = " ".join(
        [
            str(decision_out.get("primary_reason", "")),
            str(decision_out.get("target_clause_or_metric", "")),
        ]
    )
    return bool(matches_oracle(combined, oracle_markers))


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    """Return (proportion, low, high) 95% Wilson interval."""
    if n <= 0:
        return 0.0, 0.0, 0.0
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return p, max(0.0, centre - half), min(1.0, centre + half)


def format_wilson(k: int, n: int) -> str:
    """Format k/n = p [lo, hi]."""
    if n == 0:
        return "n/a (0)"
    p, lo, hi = wilson_ci(k, n)
    return f"{k}/{n} = {p:.2f} [{lo:.2f}, {hi:.2f}]"


def mcnemar_exact_p(b: int, c: int) -> float:
    """Exact two-sided binomial sign/McNemar test on discordant pairs (b, c)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    return min(1.0, 2.0 * tail)
