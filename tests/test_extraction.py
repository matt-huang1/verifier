"""Extractor coverage (ADR-0010).

Every case the ADR requires plus the invariants the matcher will lean on: symmetric
canonicalisation (same value ⟺ would agree), unit-aware currencies, year/number
disambiguation, and spans that point at the exact surface substring.
"""

from __future__ import annotations

from verifier.extraction import ExtractedEntity, extract_entities
from verifier.models import EntityKind


def _only(text: str) -> ExtractedEntity:
    """Extract and assert exactly one entity — sharpens the single-entity cases."""
    entities = extract_entities(text)
    assert len(entities) == 1, f"expected one entity, got {entities}"
    return entities[0]


# --- symmetric canonicalisation: same value ⟺ the matcher would agree -----------------


def test_scale_word_equals_expanded_digits() -> None:
    # "20 million" and "20,000,000" are the same value — a formatting difference must not
    # become a conflict (ADR-0010).
    scaled = _only("20 million")
    expanded = _only("20,000,000")
    assert scaled.kind is EntityKind.NUMBER
    assert expanded.kind is EntityKind.NUMBER
    assert scaled.value == expanded.value == "20000000"


def test_percent_symbol_equals_percent_word() -> None:
    symbol = _only("60%")
    word = _only("60 percent")
    assert symbol.kind is EntityKind.PERCENTAGE
    assert word.kind is EntityKind.PERCENTAGE
    assert symbol.value == word.value == "60"


def test_currency_unit_distinguishes_value() -> None:
    # Same amount, different unit -> different value -> must NOT agree.
    usd = _only("$5bn")
    eur = _only("€5bn")
    assert usd.kind is eur.kind is EntityKind.CURRENCY
    assert usd.value == "USD 5000000000"
    assert eur.value == "EUR 5000000000"
    assert usd.value != eur.value


def test_currency_scale_word_and_expanded_agree() -> None:
    # Unit and magnitude both canonical: "$5bn" == "$5 billion" == "$5,000,000,000".
    assert _only("$5bn").value == _only("$5 billion").value == _only("$5,000,000,000").value


def test_currency_abbreviation_with_pound() -> None:
    entity = _only("£2m")
    assert entity.kind is EntityKind.CURRENCY
    assert entity.value == "GBP 2000000"
    assert entity.raw == "£2m"


# --- year vs number disambiguation ----------------------------------------------------


def test_bare_four_digits_is_a_year() -> None:
    entity = _only("2035")
    assert entity.kind is EntityKind.YEAR
    assert entity.value == "2035"


def test_year_range_boundaries() -> None:
    assert _only("1000").kind is EntityKind.YEAR
    assert _only("2999").kind is EntityKind.YEAR
    # Outside the plausible range: a 4-digit count, not a year.
    assert _only("3050").kind is EntityKind.NUMBER


def test_year_in_prose_stays_a_year() -> None:
    # Regression for the withdrawn trailing-word demotion (ADR-0010 Amendment). Most years
    # in prose are followed by a word; demoting them split claim and source into different
    # slots and silently lost the contradiction. A year-range number is ALWAYS a year now.
    assert _only("by 2050 the company will act").kind is EntityKind.YEAR
    assert _only("in 2035 Tesla plans to expand").kind is EntityKind.YEAR
    # Sentence-final: correct under the old rule too, pinned so it does not regress.
    assert _only("Tesla committed to net zero by 2035.").kind is EntityKind.YEAR


def test_digits_with_trailing_word_still_a_year() -> None:
    # The accepted cost of the amended rule (ADR-0010 Consequences): a literal count that
    # happens to be a year-range 4-digit number is read as a YEAR, not a number. Pinned so
    # the behaviour is deliberate, not incidental.
    entity = _only("2035 cars")
    assert entity.kind is EntityKind.YEAR
    assert entity.value == "2035"
    assert entity.raw == "2035"
    assert entity.span == (0, 4)


# --- number canonicalisation ----------------------------------------------------------


def test_thousands_separator_stripped() -> None:
    entity = _only("1,200")
    assert entity.kind is EntityKind.NUMBER
    assert entity.value == "1200"  # canonical value strips separators
    assert entity.raw == "1,200"  # surface text is preserved for the excerpt


def test_decimal_survives() -> None:
    # This corpus is decimal-dense; a lost decimal point is a silent wrong number.
    entity = _only("3.5")
    assert entity.kind is EntityKind.NUMBER
    assert entity.value == "3.5"


def test_plain_integer() -> None:
    entity = _only("47")
    assert entity.kind is EntityKind.NUMBER
    assert entity.value == "47"


# --- spans, ordering, and the empty case ----------------------------------------------


def test_spans_point_at_the_matched_substring() -> None:
    text = "Revenue rose 47% to $5 billion in 2035, up from 1,200 units and 20 million users."
    for entity in extract_entities(text):
        assert text[entity.span[0] : entity.span[1]] == entity.raw


def test_multiple_entities_extracted_in_order() -> None:
    text = "Revenue rose 47% to $5 billion in 2035, up from 1,200 units and 20 million users."
    entities = extract_entities(text)
    assert [(e.kind, e.value) for e in entities] == [
        (EntityKind.PERCENTAGE, "47"),
        (EntityKind.CURRENCY, "USD 5000000000"),
        (EntityKind.YEAR, "2035"),
        (EntityKind.NUMBER, "1200"),
        (EntityKind.NUMBER, "20000000"),
    ]


def test_no_entities_returns_empty_list() -> None:
    assert extract_entities("no checkable entities here at all") == []


def test_empty_string_returns_empty_list() -> None:
    assert extract_entities("") == []


# --- the killer demo, at the extraction layer -----------------------------------------


def test_tesla_year_claim_and_source_are_comparable_years() -> None:
    # The extractor gives the matcher two same-kind years with differing values; the
    # conflict itself is the matcher's call (ADR-0009), but the basis for it lives here.
    claim = _only("Tesla committed to net zero by 2035")
    source = _only("Tesla committed to net zero by 2050")
    assert claim.kind is source.kind is EntityKind.YEAR
    assert claim.value != source.value


# --- model invariant ------------------------------------------------------------------


def test_extracted_entity_rejects_unordered_span() -> None:
    import pytest

    with pytest.raises(ValueError, match="non-negative, ordered range"):
        ExtractedEntity(kind=EntityKind.NUMBER, raw="47", value="47", span=(9, 2))
