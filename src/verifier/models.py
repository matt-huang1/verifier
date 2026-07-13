"""Typed boundaries for the verify_citation contract (ADR-0005).

Every object here is a leaf of the verdict schema: immutable, JSON-serialisable, and
anchored to a span of the fetched source. The judgment itself is *not* here — it lives
in ``judgment.derive_status``. These types only describe what was found; they never decide
what it means.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, model_validator


class Status(str, Enum):
    """The verdict.

    Computed by ``derive_status`` and never asserted directly (ADR-0005 b): a
    ``supported`` cannot exist without the evidence that makes it true. Four distinct,
    named mechanisms — a fetch failure and a support failure must never blur (CLAUDE.md,
    "Never guess").
    """

    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    NOT_FOUND_IN_SOURCE = "not_found_in_source"
    SOURCE_UNREACHABLE = "source_unreachable"


class MatchKind(str, Enum):
    """How the caller's quote was located in the fetched source.

    ``ABSENT`` is the *single source of truth* for "quote not found": Path A reads it
    from here, never from a second independent check.
    """

    EXACT = "exact"
    NORMALIZED = "normalized"
    FUZZY = "fuzzy"
    ABSENT = "absent"

    @property
    def is_found(self) -> bool:
        """Found ⟺ not absent. The one place "quote absent" is defined."""
        return self is not MatchKind.ABSENT


class EntityKind(str, Enum):
    """The class of a checked entity — the *slot* two values are compared within.

    Extensible. The extractor (ADR-0010) fills ``YEAR``, ``NUMBER``, ``PERCENTAGE`` and
    ``CURRENCY``; ``DATE`` (full dates) and ``NAME`` are reserved for the deferred date
    parser and the future named-entity proposer. The slot is load-bearing: a value only
    ``agree``s with another of the *same* kind, so a ``YEAR`` 2035 and a ``NUMBER`` 2035
    ("2035 cars") never compare equal — that is what the year/number disambiguation buys.
    """

    YEAR = "year"
    NUMBER = "number"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    DATE = "date"
    NAME = "name"


class EntityResult(str, Enum):
    """Outcome of one entity check: claimed value vs. what the source says."""

    AGREE = "agree"
    CONFLICT = "conflict"
    ABSENT = "absent"


class Evidence(BaseModel):
    """A passage the caller's text was matched against, anchored to the source span.

    A found match (``match_kind.is_found``) MUST carry a ``char_span``; an absent match
    MUST NOT, because there is nothing to point at. This makes "everything traceable to
    its source" a structural invariant rather than a convention.
    """

    model_config = ConfigDict(frozen=True)

    claimed_text: str
    source_excerpt: str
    match_kind: MatchKind
    char_span: tuple[int, int] | None = None
    # A mechanical similarity ratio MAY accompany a fuzzy match — a measurement, not a
    # confidence judgment (ADR-0003).
    fuzzy_ratio: float | None = None

    @model_validator(mode="after")
    def _span_agrees_with_match(self) -> Evidence:
        if self.match_kind.is_found and self.char_span is None:
            raise ValueError("a found match must carry a char_span")
        if not self.match_kind.is_found and self.char_span is not None:
            raise ValueError("an absent match must not carry a char_span")
        if self.char_span is not None:
            start, end = self.char_span
            if start < 0 or start > end:
                raise ValueError(
                    f"char_span must be a non-negative, ordered range, got {self.char_span}"
                )
        return self


class EntityCheck(BaseModel):
    """One number/date/name: what the claim said vs. what the source says, with the
    source excerpt that justifies the result.

    An ``ABSENT`` result has no ``found`` value; an ``AGREE``/``CONFLICT`` must have one.
    """

    model_config = ConfigDict(frozen=True)

    kind: EntityKind
    claimed: str
    found: str | None
    result: EntityResult
    source_excerpt: str

    @model_validator(mode="after")
    def _found_agrees_with_result(self) -> EntityCheck:
        if self.result is EntityResult.ABSENT and self.found is not None:
            raise ValueError("an absent entity must not carry a found value")
        if self.result is not EntityResult.ABSENT and self.found is None:
            raise ValueError("an agree/conflict result requires a found value")
        return self


class SourceReport(BaseModel):
    """What happened when Verifier fetched the URL.

    Fetch state is an *input* to the judgment so ``source_unreachable`` is honest and can
    never be faked as ``not_found_in_source`` (ADR-0005 b). NB: no full page text is
    retained here (ADR-0005 c) — the report records the fetch, not the page.
    """

    model_config = ConfigDict(frozen=True)

    requested_url: str
    resolved_url: str
    redirect_chain: tuple[str, ...] = ()
    reachable: bool
    status_code: int | None = None
    error: str | None = None
    fetched_at: datetime
