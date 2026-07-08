"""Truth table for the judgment core, ``derive_status``.

One row per branch of the ADR-0005 (d) rules. The point of this file is coverage of the
*decision surface*, not of any fetching or matching — every input here is a hand-built,
already-anchored piece of evidence, exactly as the pure judge expects to receive it.
"""

from __future__ import annotations

import pytest

from verifier.judgment import derive_status
from verifier.models import (
    EntityCheck,
    EntityKind,
    EntityResult,
    Evidence,
    MatchKind,
    Status,
)

# --- builders -------------------------------------------------------------------------
# Tiny factories so each test row reads as "these inputs -> this status" and nothing else.


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


# --- the truth table ------------------------------------------------------------------

CASES = [
    # id, reachable, quote_evidence, entity_checks, expected
    # Reachability dominates: even a found quote with a conflict cannot mask a fetch
    # failure. A failure to fetch is never a content verdict.
    ("unreachable_dominates", False, quote(MatchKind.EXACT), [entity(EntityResult.CONFLICT)],
     Status.SOURCE_UNREACHABLE),
    # Path B (no quote) — conservative cap at not_found, whatever the entities say.
    ("pathB_entities_agree", True, None, [entity(EntityResult.AGREE)],
     Status.NOT_FOUND_IN_SOURCE),
    ("pathB_entities_conflict", True, None, [entity(EntityResult.CONFLICT)],
     Status.NOT_FOUND_IN_SOURCE),  # conflict without an anchored quote still cannot contradict
    ("pathB_no_entities", True, None, [],
     Status.NOT_FOUND_IN_SOURCE),
    # Path A — quote absent from source (read straight off match_kind).
    ("pathA_quote_absent", True, quote(MatchKind.ABSENT), [],
     Status.NOT_FOUND_IN_SOURCE),
    # Path A — quote found by each match kind, no conflict -> supported.
    ("pathA_exact_no_entities", True, quote(MatchKind.EXACT), [],
     Status.SUPPORTED),
    ("pathA_normalized_agree", True, quote(MatchKind.NORMALIZED), [entity(EntityResult.AGREE)],
     Status.SUPPORTED),
    ("pathA_fuzzy_agree", True, quote(MatchKind.FUZZY), [entity(EntityResult.AGREE)],
     Status.SUPPORTED),
    # Path A — an absent entity is not a conflict; a faithful quote still stands.
    ("pathA_entity_absent_is_not_conflict", True, quote(MatchKind.EXACT),
     [entity(EntityResult.ABSENT)], Status.SUPPORTED),
    # Path A — any conflict within the matched region contradicts.
    ("pathA_mixed_conflict_wins", True, quote(MatchKind.EXACT),
     [entity(EntityResult.AGREE), entity(EntityResult.CONFLICT)],
     Status.CONTRADICTED),
]


@pytest.mark.parametrize(
    ("reachable", "quote_evidence", "entity_checks", "expected"),
    [pytest.param(*c[1:], id=c[0]) for c in CASES],
)
def test_derive_status_truth_table(
    reachable: bool,
    quote_evidence: Evidence | None,
    entity_checks: list[EntityCheck],
    expected: Status,
) -> None:
    assert derive_status(
        reachable=reachable,
        quote_evidence=quote_evidence,
        entity_checks=entity_checks,
    ) == expected


def test_tesla_2035_vs_2050_contradicts() -> None:
    """The killer demo, spelled out. The caller quoted the sentence faithfully — the
    quote matches — but the claim's figure (2035) disagrees with the source's (2050).
    A conflicting entity under a matched quote is a contradiction, not a support."""
    matched_quote = Evidence(
        claimed_text="Tesla committed to net zero by 2035",
        source_excerpt="Tesla committed to net zero by 2050",
        match_kind=MatchKind.FUZZY,  # the sentence matches; only the number differs
        char_span=(0, 35),
        fuzzy_ratio=0.94,
    )
    year_conflict = EntityCheck(
        kind=EntityKind.NUMBER,
        claimed="2035",
        found="2050",
        result=EntityResult.CONFLICT,
        source_excerpt="Tesla committed to net zero by 2050",
    )

    verdict = derive_status(
        reachable=True,
        quote_evidence=matched_quote,
        entity_checks=[year_conflict],
    )

    assert verdict is Status.CONTRADICTED


# --- model invariants (traceability enforced structurally) ----------------------------


def test_found_evidence_requires_span() -> None:
    with pytest.raises(ValueError, match="found match must carry a char_span"):
        Evidence(
            claimed_text="x",
            source_excerpt="x",
            match_kind=MatchKind.EXACT,
            char_span=None,
        )


def test_absent_evidence_forbids_span() -> None:
    with pytest.raises(ValueError, match="absent match must not carry a char_span"):
        Evidence(
            claimed_text="x",
            source_excerpt="",
            match_kind=MatchKind.ABSENT,
            char_span=(0, 1),
        )


def test_conflict_entity_requires_found_value() -> None:
    with pytest.raises(ValueError, match="requires a found value"):
        EntityCheck(
            kind=EntityKind.NUMBER,
            claimed="2035",
            found=None,
            result=EntityResult.CONFLICT,
            source_excerpt="...",
        )


def test_absent_entity_forbids_found_value() -> None:
    with pytest.raises(ValueError, match="absent entity must not carry a found value"):
        EntityCheck(
            kind=EntityKind.NUMBER,
            claimed="2035",
            found="2050",
            result=EntityResult.ABSENT,
            source_excerpt="...",
        )


def test_evidence_span_must_be_ordered() -> None:
    with pytest.raises(ValueError, match="non-negative, ordered range"):
        Evidence(
            claimed_text="x",
            source_excerpt="x",
            match_kind=MatchKind.EXACT,
            char_span=(40, 10),
        )
