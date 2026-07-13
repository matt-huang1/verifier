"""The ``Verdict`` wrapper: a self-describing verdict whose status is *computed*, never stored.

These tests pin the three properties that make the wrapper trustworthy: the status re-derives
from the evidence for every path, it cannot be smuggled in through the constructor, and an
issued verdict cannot be mutated. The final test pins the serialised wire shape.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

# Reuse the truth-table builders so a Verdict is fed exactly the evidence the pure judge sees.
from conftest import entity, quote
from verifier.models import (
    EntityCheck,
    EntityResult,
    Evidence,
    MatchKind,
    SourceReport,
    Status,
)
from verifier.verdict import Verdict

FETCHED_AT = datetime(2026, 1, 1, 12, 0, 0)


def source(*, reachable: bool) -> SourceReport:
    """A minimal SourceReport in the given reachability state."""
    return SourceReport(
        requested_url="https://example.com/a",
        resolved_url="https://example.com/a",
        reachable=reachable,
        status_code=200 if reachable else None,
        error=None if reachable else "connection refused",
        fetched_at=FETCHED_AT,
    )


# --- 1. status computes correctly for every path --------------------------------------

STATUS_CASES = [
    # id, reachable, quote_evidence, entity_checks, expected
    ("unreachable", False, quote(MatchKind.EXACT), (entity(EntityResult.CONFLICT),),
     Status.SOURCE_UNREACHABLE),
    ("pathB_no_quote", True, None, (entity(EntityResult.CONFLICT),),
     Status.NOT_FOUND_IN_SOURCE),
    ("pathA_quote_absent", True, quote(MatchKind.ABSENT), (),
     Status.NOT_FOUND_IN_SOURCE),
    ("pathA_found_conflict", True, quote(MatchKind.EXACT), (entity(EntityResult.CONFLICT),),
     Status.CONTRADICTED),
    ("pathA_found_no_conflict", True, quote(MatchKind.EXACT), (entity(EntityResult.AGREE),),
     Status.SUPPORTED),
]


@pytest.mark.parametrize(
    ("reachable", "quote_evidence", "entity_checks", "expected"),
    [pytest.param(*c[1:], id=c[0]) for c in STATUS_CASES],
)
def test_status_computes_for_every_path(
    reachable: bool,
    quote_evidence: Evidence | None,
    entity_checks: tuple[EntityCheck, ...],
    expected: Status,
) -> None:
    verdict = Verdict(
        claim="Tesla committed to net zero by 2035",
        source=source(reachable=reachable),
        quote_evidence=quote_evidence,
        entity_checks=entity_checks,
    )
    assert verdict.status is expected


# --- 2. status cannot be injected via the constructor ---------------------------------


def test_status_cannot_be_injected() -> None:
    """ADR-0005(b) enforcement: the verdict is computed, never asserted. ``extra="forbid"``
    makes passing a ``status`` to the constructor a hard error, so no caller can hand-wave a
    ``supported`` that the evidence does not produce. This test IS that guarantee."""
    with pytest.raises(ValidationError):
        Verdict(
            claim="Tesla committed to net zero by 2035",
            source=source(reachable=True),
            quote_evidence=quote(MatchKind.ABSENT),
            entity_checks=(),
            status="supported",  # type: ignore[call-arg]
        )


# --- 3. an issued verdict cannot be mutated -------------------------------------------


def test_verdict_is_immutable() -> None:
    """Attribute reassignment is blocked by frozen=True, and entity_checks is a tuple, so an
    issued verdict has no in-place mutation path that could flip its computed status."""
    verdict = Verdict(
        claim="Tesla committed to net zero by 2035",
        source=source(reachable=True),
        quote_evidence=quote(MatchKind.EXACT),
        entity_checks=(entity(EntityResult.AGREE),),
    )

    with pytest.raises(ValidationError):
        verdict.claim = "something else"

    assert isinstance(verdict.entity_checks, tuple)
    assert not hasattr(verdict.entity_checks, "append")


# --- 4. JSON snapshot: pin the wire format --------------------------------------------


def test_json_shape_is_pinned() -> None:
    """model_dump(mode="json") of a known verdict — the exact serialised shape, including the
    computed ``status`` field. This is the wire contract; it must not change unnoticed."""
    verdict = Verdict(
        claim="Tesla committed to net zero by 2035",
        source=SourceReport(
            requested_url="https://example.com/a",
            resolved_url="https://example.com/a",
            reachable=True,
            status_code=200,
            fetched_at=FETCHED_AT,
        ),
        quote_evidence=Evidence(
            claimed_text="Tesla committed to net zero by 2035",
            source_excerpt="Tesla committed to net zero by 2050",
            match_kind=MatchKind.FUZZY,
            char_span=(0, 35),
            fuzzy_ratio=0.94,
        ),
        entity_checks=(entity(EntityResult.CONFLICT, claimed="2035", found="2050"),),
    )

    assert verdict.model_dump(mode="json") == {
        "claim": "Tesla committed to net zero by 2035",
        "source": {
            "requested_url": "https://example.com/a",
            "resolved_url": "https://example.com/a",
            "redirect_chain": [],
            "reachable": True,
            "status_code": 200,
            "error": None,
            "fetched_at": "2026-01-01T12:00:00",
        },
        "quote_evidence": {
            "claimed_text": "Tesla committed to net zero by 2035",
            "source_excerpt": "Tesla committed to net zero by 2050",
            "match_kind": "fuzzy",
            "char_span": [0, 35],
            "fuzzy_ratio": 0.94,
        },
        "entity_checks": [
            {
                "kind": "year",
                "claimed": "2035",
                "found": "2050",
                "result": "conflict",
                "source_excerpt": "Tesla committed to net zero by 2050",
            }
        ],
        "status": "contradicted",
    }
