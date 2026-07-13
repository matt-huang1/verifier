# ADR-0008: Length-preserving normalization

- **Status:** Accepted
- **Date:** 2026-07-13

## Context

The matcher must locate a caller-supplied quote in the extracted source text. To match
robustly it normalizes the text first — case, smart quotes, dashes, non-breaking spaces
— so that cosmetic differences do not defeat an otherwise faithful quote.

But the matcher also needs the match's *position in the original text*, for two reasons:
`Evidence.char_span` is reported for traceability (see 0005), and 0007's region scoping
locates the containing sentence by offset.

Normalization that changes the text's *length* shifts every subsequent character, so a
position found in normalized text no longer corresponds to the same position in the
original. Worked example: original `"Tesla  will   make\n20 million cars."` (double
space, triple space, newline). After collapsing whitespace, "20 million" is found at
normalized position 16 — but it sits at position 26 in the original. Reporting 16 points
at the wrong text and can select the *wrong sentence*, silently corrupting the region
and thus the contradiction check (0007).

## Decision

Normalization is **length-preserving only**: every substitution maps one character to
exactly one character, so normalized offsets are identical to original offsets by
construction.

- Permitted: lowercasing; smart quotes → straight quotes; en/em dash → hyphen;
  non-breaking space → regular space.
- Not permitted: collapsing runs of whitespace; collapsing newlines; NFKC/Unicode
  normalization that expands or contracts characters (e.g. the ligature `ﬁ` → `f` + `i`).

Consequences of this for matching:

- **Whitespace variance is absorbed by the fuzzy rung, not by normalization.** A quote
  wrapped across a line break, or a double space from HTML extraction, is handled by
  fuzzy similarity: `"Tesla  will make"` vs `"Tesla will make"` is ~98% similar,
  comfortably above the 0.90 threshold.
- **This is cosmetically lossy but verdict-neutral.** `derive_status` only distinguishes
  found from absent (it reads `MatchKind.is_found`), so a whitespace-mangled quote
  landing as `fuzzy` rather than `exact` produces the same status. The loss is confined
  to the reported `match_kind` label.
- **Case is asymmetric by design.** Matching is case-insensitive, but the reported
  `source_excerpt` preserves the *original* casing, so the evidence shows the real text.

## Consequences

- Some quotes that could have matched `exact`/`normalized` will be labelled `fuzzy`. The
  verdict is unaffected.
- A quote with *severe* whitespace mangling could fall below the 0.90 threshold and be
  reported `absent` → `not_found_in_source`. This is an under-claim — the honest failure
  direction (CLAUDE.md, "precision over recall"), not a false `supported`.
- Requires tests: a quote differing from the source only by whitespace still matches (as
  `fuzzy`); and a `char_span` reported from a normalized match points at the correct text
  in the *original* string.

## Alternatives considered

- **Offset mapping** — normalize freely, and maintain an index from normalized positions
  back to original positions. Rejected: it buys better `match_kind` fidelity at the cost
  of ~20–40 lines of fiddly index-keeping whose failure mode is *silent*. A subtly wrong
  map does not raise; it reports slightly-off spans and occasionally selects the wrong
  sentence. That is a silent failure mode in the precision path — the same category
  rejected in 0007 for the hand-rolled sentence splitter. May be revisited if real-world
  use shows quotes falling below threshold due to whitespace alone, at which point there
  will be failing examples to test against.
