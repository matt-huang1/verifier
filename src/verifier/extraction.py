"""Deterministic entity extraction (ADR-0010).

Given a text string, find the *checkable* entities in it — years, numbers, percentages
and currencies — and return each with a canonical value for comparison and the exact
surface text for the evidence excerpt.

The single most important property: the *same* ``extract_entities`` runs on both the
claim and the matched region, so both sides are canonicalised identically. That symmetry
is what makes the matcher's later comparison sound — two entities ``agree`` iff they share
a ``kind`` (the slot) *and* a ``value`` (the canonical key). Surface strings are never
compared ("20 million" and "20,000,000" must agree; "$5bn" and "€5bn" must not).

Regex-only and total: no I/O, no clock, no network — same input, same output. Whatever
this cannot extract cannot be checked, so the in/out-of-scope boundary here is a real
bound on what the verifier can catch (ADR-0010).

``ExtractedEntity`` lives here, not in ``models``: it is an intermediate of the
extractor/matcher path, never a leaf of the verdict schema (that is ``EntityCheck``).
"""

from __future__ import annotations

import re
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator

from verifier.models import EntityKind


class ExtractedEntity(BaseModel):
    """One checkable entity found in a text (ADR-0010).

    Immutable and closed (``extra="forbid"``) like every boundary object in this codebase.
    Equality within a slot is decided *entirely* by ``value``: it is the canonical
    comparison key and already folds in whatever distinguishes two values (e.g. the
    currency unit), so the matcher never has to re-canonicalise or compare surface text.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: EntityKind
    # Surface text exactly as it appeared, for the evidence excerpt (traceability).
    raw: str
    # Canonical comparison key. NEVER compare surface strings (ADR-0010). Within a kind,
    # equal ``value`` ⟺ same entity; currency folds its unit in ("USD 5000000000").
    value: str
    # [start, end) char offsets into the *input* text, so the matcher can scope a region.
    span: tuple[int, int]

    @model_validator(mode="after")
    def _span_is_ordered(self) -> ExtractedEntity:
        start, end = self.span
        if start < 0 or start > end:
            raise ValueError(f"span must be a non-negative, ordered range, got {self.span}")
        return self


# --- canonicalisation tables ----------------------------------------------------------
#
# Scale words and their multipliers. Full words appear on their own ("20 million");
# abbreviations only attach to a currency amount ("$5bn", "£2m"), where the leading
# symbol removes the ambiguity a bare "5m" (metres? millions?) would carry.
_SCALE_FACTORS: dict[str, Decimal] = {
    "thousand": Decimal(1_000),
    "k": Decimal(1_000),
    "million": Decimal(1_000_000),
    "m": Decimal(1_000_000),
    "billion": Decimal(1_000_000_000),
    "bn": Decimal(1_000_000_000),
    "b": Decimal(1_000_000_000),
    "trillion": Decimal(1_000_000_000_000),
    "t": Decimal(1_000_000_000_000),
}

# Currency symbol -> ISO unit token. The unit is part of the canonical value, so $5bn and
# €5bn resolve to different keys and cannot agree (ADR-0010).
_CURRENCY_UNITS: dict[str, str] = {
    "$": "USD",
    "£": "GBP",
    "€": "EUR",
    "¥": "JPY",
}

# A 4-digit integer in this inclusive range, standing alone, is read as a year (ADR-0010).
_YEAR_MIN = 1000
_YEAR_MAX = 2999


# --- the master pattern ---------------------------------------------------------------
#
# One regex, one left-to-right pass. The alternatives are ordered by specificity so the
# most-specific reading wins the position and consumes it: currency and percentage before
# a scaled number, and any of those before a bare number. finditer then yields matches in
# document order with correct spans.
_NUM = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"  # 47 | 3.5 | 1,200 | 20,000,000
_FULL_SCALE = r"(?:trillion|billion|million|thousand)"
_ABBR_SCALE = r"(?:bn|[kmbt])"

_ENTITY_RE = re.compile(
    rf"""
      (?P<currency>                                   # $5 billion | £2m | $1,200
          (?P<cur_sym>[$£€¥])\s?
          (?P<cur_num>{_NUM})\s?
          (?:(?P<cur_scale>{_FULL_SCALE}|{_ABBR_SCALE})(?![A-Za-z]))?
      )
    | (?P<percent>                                    # 60% | 60 percent
          (?P<pct_num>{_NUM})\s?
          (?:%|percent(?![A-Za-z]))
      )
    | (?P<scaled>                                     # 20 million | 1.5 billion
          (?P<sc_num>{_NUM})\s
          (?P<sc_scale>{_FULL_SCALE})(?![A-Za-z])
      )
    | (?P<plain>{_NUM})                               # 47 | 3.5 | 1,200 | 2035
    """,
    re.IGNORECASE | re.VERBOSE,
)


def extract_entities(text: str) -> list[ExtractedEntity]:
    """Extract every checkable entity from ``text``, in document order.

    Returns an empty list when there is nothing to check — never an error. The same
    function is applied to both the claim and the matched region (ADR-0010).
    """
    entities: list[ExtractedEntity] = []
    for m in _ENTITY_RE.finditer(text):
        if m.group("currency") is not None:
            entities.append(_build_currency(m))
        elif m.group("percent") is not None:
            entities.append(_build_percent(m))
        elif m.group("scaled") is not None:
            entities.append(_build_scaled(m))
        else:  # plain number — may be a year
            entities.append(_build_plain(m))
    return entities


# --- per-branch builders --------------------------------------------------------------


def _build_currency(m: re.Match[str]) -> ExtractedEntity:
    unit = _CURRENCY_UNITS[m.group("cur_sym")]
    amount = _parse_number(m.group("cur_num"))
    scale = m.group("cur_scale")
    if scale is not None:
        amount *= _SCALE_FACTORS[scale.lower()]
    # Unit first so it is part of the key: "USD 5000000000" != "EUR 5000000000".
    return ExtractedEntity(
        kind=EntityKind.CURRENCY,
        raw=m.group("currency"),
        value=f"{unit} {_canonical(amount)}",
        span=m.span("currency"),
    )


def _build_percent(m: re.Match[str]) -> ExtractedEntity:
    return ExtractedEntity(
        kind=EntityKind.PERCENTAGE,
        raw=m.group("percent"),
        value=_canonical(_parse_number(m.group("pct_num"))),
        span=m.span("percent"),
    )


def _build_scaled(m: re.Match[str]) -> ExtractedEntity:
    amount = _parse_number(m.group("sc_num")) * _SCALE_FACTORS[m.group("sc_scale").lower()]
    return ExtractedEntity(
        kind=EntityKind.NUMBER,
        raw=m.group("scaled"),
        value=_canonical(amount),
        span=m.span("scaled"),
    )


def _build_plain(m: re.Match[str]) -> ExtractedEntity:
    raw = m.group("plain")
    amount = _parse_number(raw)
    # Disambiguation (ADR-0010, amended 2026-07-13): a 4-digit year-range integer is
    # *always* a YEAR — no trailing-word demotion. The original "a following word makes it
    # a number" rule demoted ordinary years in prose ("by 2050 the company…"), splitting a
    # claim and its source into different slots and defeating the ADR-0009 conflict rule.
    if _is_year_form(raw):
        return ExtractedEntity(
            kind=EntityKind.YEAR,
            raw=raw,
            value=str(int(amount)),
            span=m.span("plain"),
        )
    return ExtractedEntity(
        kind=EntityKind.NUMBER,
        raw=raw,
        value=_canonical(amount),
        span=m.span("plain"),
    )


# --- helpers --------------------------------------------------------------------------


def _parse_number(token: str) -> Decimal:
    """Strip thousands separators and parse. ``Decimal`` keeps decimals exact and the
    canonicalisation deterministic (this text is decimal-dense)."""
    return Decimal(token.replace(",", ""))


def _canonical(amount: Decimal) -> str:
    """Canonical string for a magnitude: trailing zeros dropped, no exponent notation.
    ``20 million`` and ``20,000,000`` both land on ``"20000000"``; ``3.5`` stays ``"3.5"``.
    """
    return f"{amount.normalize():f}"


def _is_year_form(raw: str) -> bool:
    return raw.isdigit() and len(raw) == 4 and _YEAR_MIN <= int(raw) <= _YEAR_MAX
