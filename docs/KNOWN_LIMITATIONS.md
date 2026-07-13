# Known Limitations

> **Status: scaffold.** Real, current gaps in what *is* built — named honestly, not
> hidden. Populate as the engine grows.

## Fuzzy quote match does not catch semantic drift

A fuzzy quote match that drifts in *meaning* while staying above the similarity
threshold is not caught in V1. V1 treats an above-threshold fuzzy match as "found" and
relies on the entity check (numbers, dates, names) to catch disagreement — so a drift
that changes the sense without changing any checked entity passes as supported.
Detecting meaning-level drift is the deferred NLI layer (see ROADMAP; 0003).

## Named entities are not checked

V1 checks numeric and year entities only. It cannot catch a misattributed organisation,
person, or place ("Tesla" vs "Ford"), because comparing named entities is ambiguous
("Tesla" vs "Tesla Inc.") and would manufacture false conflicts (0010, 0009). A future
proposer (LLM or spaCy) may supply candidate named entities, which would still pass
through the same deterministic conflict rule.

## Full dates are not extracted

Only years are extracted in V1. A full date such as "3 March 2035" is not parsed as a
date; a wrong day or month with the right year is not caught (see 0010).

## Relative quantities are not comparable

Relative quantities such as "doubled" or "a third of" carry no canonical value to compare
and are not extracted in V1 (see 0010).
