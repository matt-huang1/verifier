"""Shared pytest helpers.

The ``quote``/``entity`` builders live here so both the ``derive_status`` truth table and the
``Verdict`` tests feed the judge exactly the same hand-built, already-anchored evidence — one
definition, no drift between the two suites.
"""

from __future__ import annotations

from verifier.models import (
    EntityCheck,
    EntityKind,
    EntityResult,
    Evidence,
    MatchKind,
)


def quote(match_kind: MatchKind) -> Evidence:
    """A quote Evidence in the given match state. Found matches carry a span; the absent
    one does not (the model enforces this)."""
    if match_kind.is_found:
        return Evidence(
            claimed_text="Tesla committed to net zero by 2035",
            source_excerpt="Tesla committed to net zero by 2050",
            match_kind=match_kind,
            char_span=(0, 35),
        )
    return Evidence(
        claimed_text="Tesla committed to net zero by 2035",
        source_excerpt="",
        match_kind=MatchKind.ABSENT,
    )


def entity(
    result: EntityResult, *, claimed: str = "2050", found: str | None = "2050"
) -> EntityCheck:
    if result is EntityResult.ABSENT:
        found = None
    return EntityCheck(
        kind=EntityKind.NUMBER,
        claimed=claimed,
        found=found,
        result=result,
        source_excerpt="Tesla committed to net zero by 2050",
    )
