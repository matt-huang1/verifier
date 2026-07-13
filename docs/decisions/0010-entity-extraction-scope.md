# ADR-0010: Entity extraction scope

- **Status:** Accepted
- **Date:** 2026-07-13

## Context

0009 defines *when* an entity check is a conflict. This ADR defines *which* entities are
extracted in the first place, and how their values are compared.

The extractor runs on both the claim and the matched region (0007). Whatever it cannot
extract cannot be checked, so its scope directly bounds what the verifier can catch.

The governing constraint: extract only what can be compared *unambiguously*. Numbers and
dates have canonical forms and a clear notion of "different value". Named entities do not
— "Tesla" vs "Tesla Inc." vs "Tesla, Inc." is a judgment call about same-or-different,
and judgment is what this project refuses (0001).

## Decision

In scope for V1 (all regex-based, all deterministic):

- **Years** — four digits in a plausible range (e.g. 1000–2999). The highest-value case
  and the headline Tesla catch.
- **Numbers with scale words** — "20 million", "1.5 billion".
- **Plain numbers** — "47", "3.5", "1,200" (thousands separators stripped).
- **Percentages** — "60%" and "60 percent" (the same value, two spellings).
- **Currencies** — "$5 billion", "£2m". The value *and* the currency unit must match
  ($5bn is not €5bn).

Comparison is on a **canonical value**, never the surface string. "20 million" in the
claim and "20,000,000" in the source are the same value and must `agree`, not `conflict`.
Each extracted entity therefore carries: `kind` (the slot, per 0009), `raw` (the text as
it appeared — used for the evidence excerpt, for traceability), and `value` (the
canonical form — used for comparison). The *same* extractor runs on both the claim and
the region, so both sides are canonicalised identically; that symmetry is what makes the
comparison sound.

**Kind disambiguation:** a bare four-digit number in year range is a year. The same
digits carrying a scale word or unit ("2035 cars") are a number. Crude but stateable and
testable.

**Placement:** the extractor lives in its own module (e.g. `extraction.py`), separate
from the matcher. The matcher locates and compares; the extractor finds entities in text.
This keeps the boundary clean for a future alternative proposer (see Alternatives).

Out of scope for V1 (stated so they are not quietly added):

- **Named entities** (people, organisations, places). Comparison is ambiguous and would
  manufacture false conflicts ("Tesla" vs "Tesla Inc."), precisely the over-claiming
  rejected in 0009. This is the natural home for a future LLM/spaCy *proposer* — one that
  proposes candidate entities which then pass through the *same* deterministic conflict
  rule (0009). The proposer never issues a verdict; the code still judges (0001).
- **Full dates** ("3 March 2035"). Multiple formats, needs a date parser. Years alone
  catch most real errors; defer.
- **Relative quantities** ("doubled", "a third of"). Not comparable without semantics.

## Consequences

- The verifier cannot catch a misattributed organisation or person in V1 — only numeric
  and year errors. This is an accepted, stated limitation; record it in
  `docs/KNOWN_LIMITATIONS.md`.
- Requires tests: "20 million" agrees with "20,000,000"; "60%" agrees with "60 percent";
  "$5bn" does *not* agree with "€5bn" (unit mismatch); a bare "2035" extracts as a year;
  "2035 cars" extracts as a number; thousands separators are stripped.

## Alternatives considered

- **Comparing surface strings rather than canonical values.** Rejected: "20 million" vs
  "20,000,000" would be a false conflict — a formatting difference reported as a
  contradiction.
- **Including named entities in V1 via spaCy.** Rejected for now: heavy install (0007
  makes the same argument for segmentation), and the comparison itself is ambiguous, so
  the extraction would outrun the conflict rule's ability to judge it safely.
