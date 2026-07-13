# ADR-0010: Entity extraction scope

- **Status:** Accepted
- **Date:** 2026-07-13
- **Amended:** 2026-07-13 — year/number disambiguation replaced (see [Amendment](#amendment-2026-07-13))

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

**Kind disambiguation:** a four-digit number in year range (1000–2999) is *always* a
year. There is no trailing-word demotion. (Superseded the original rule; see the
[Amendment](#amendment-2026-07-13) for why the "carries a word → number" heuristic was
withdrawn.)

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
- **Accepted cost of the amended rule:** a literal count that happens to be a four-digit
  number in year range ("2035 cars") is extracted as a *year*, not a number. A false
  `agree` would require a contrived collision — a claim counting 2035 things checked
  against a source discussing the year 2035. That is far cheaper than the failure the
  original rule caused: losing the headline catch on ordinary prose (see Amendment).
- Requires tests: "20 million" agrees with "20,000,000"; "60%" agrees with "60 percent";
  "$5bn" does *not* agree with "€5bn" (unit mismatch); a bare "2035" extracts as a year;
  "2035 cars" also extracts as a year (the accepted cost above); thousands separators are
  stripped.

## Alternatives considered

- **Comparing surface strings rather than canonical values.** Rejected: "20 million" vs
  "20,000,000" would be a false conflict — a formatting difference reported as a
  contradiction.
- **Including named entities in V1 via spaCy.** Rejected for now: heavy install (0007
  makes the same argument for segmentation), and the comparison itself is ambiguous, so
  the extraction would outrun the conflict rule's ability to judge it safely.
- **The original trailing-word demotion rule** (a year-range number followed by a word is
  a number). Withdrawn in the Amendment below — it broke the primary use case, not an
  edge case.

## Amendment (2026-07-13)

The original disambiguation rule read: "a bare four-digit number in year range is a year;
the same digits carrying a scale word or unit ('2035 cars') are a number." Implementing it
as *demote a year-range number to a number whenever a word follows* was found to misfire on
ordinary prose, because most years in running text are followed by a word:

- "by 2050 the company will act" → 2050 followed by "the" → number (wrong)
- "in 2035 Tesla plans to expand" → 2035 followed by "Tesla" → number (wrong)
- "committed by 2035." → sentence-final → year (correct, but only by luck of punctuation)

This is fatal, not cosmetic. Because different `EntityKind`s never compare (0009 slot
matching), a claim phrased "by 2050 the company…" (number) and a source region ending
"…by 2035." (year) land in **different slots**: no comparison runs, the check is `absent`,
and the verdict is `supported` instead of `contradicted`. The headline Tesla catch silently
fails on the most natural phrasing — the rule defeated the very use case the extractor
exists to serve.

**New rule (this supersedes the original):** a four-digit number in year range is *always*
a year. No trailing-word demotion. The accepted cost — a literal count like "2035 cars"
read as a year — is recorded under Consequences and is far cheaper than losing the catch on
normal prose. Scale words and currency units still classify their numbers as before; this
amendment changes only the bare four-digit case.
