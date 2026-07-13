# ADR-0007: Sentence-scoped contradiction regions

- **Status:** Accepted
- **Date:** 2026-07-13

## Context

`derive_status` returns `contradicted` when any `EntityCheck` in `entity_checks`
conflicts. Its rules already require those checks to be scoped to "the matched region
only" (see 0005 (d)) — but "region" was never defined. This ADR defines it.

This is the precision knob of the whole system. A conflict too far from the matched
quote is not a contradiction of the quoted proposition; a region drawn too wide sweeps
in unrelated entities and lets an irrelevant agreement mask a real conflict — or an
irrelevant conflict manufacture a false one. Get the region wrong and the
high-precision contradiction the project is built on collapses.

## Decision

### (a) The region is the sentence(s) the matched quote span overlaps

Only entities inside that region may trigger `contradicted`. If the quote is a fragment
of a single sentence, the region is that whole sentence — the rest of it is the same
proposition. If the quote span crosses a sentence boundary, the region is both
sentences.

Rationale: the sentence is the linguistic unit of a proposition, and contradiction is a
relation between propositions. Scoping to the sentence(s) the quote touches binds the
check to the proposition the caller anchored on, and to nothing else on the page.

### (b) Segmentation uses `pysbd`

`pysbd` is deterministic and rule-based, not statistical: same text in, same boundaries
out. That clears the 0001 bar for anything in the judgment path — reproducible,
traceable, bounded failure modes.

### (c) The splitter sits behind a local interface

Segmentation is reached through a local function,
`segment_sentences(text) -> list[tuple[int, int]]`, returning character spans. The
library is an implementation detail behind that seam and can be swapped without touching
the matcher.

### (d) The region span is recorded on the evidence

The region's char span is written onto the evidence, so the scoping used for a verdict
is auditable: a reader can see exactly which text was considered when the entity checks
ran. Nothing in the verdict is free-floating (see CLAUDE.md, "Everything is traceable to
its source").

## Consequences

- Adds one small dependency, `pysbd`, to the core.
- Requires unit tests asserting boundaries on adversarial text: `Dr.`, `3.5`, `U.S.`,
  `J.P. Morgan`, and a period inside quotation marks. These convert the library's
  claimed accuracy into a demonstrated property on *our* text — which is unusually
  decimal- and abbreviation-dense because the tool checks numbers and dates.
- The region span on the evidence slightly widens the Evidence/wire shape; the JSON
  snapshot test will need updating when the matcher lands.

## Alternatives considered

- **Character window (matched span ± N chars).** Rejected as unsound, not merely
  inelegant: widening the region can flip a correct verdict. Worked example — source =
  "Tesla will make 20 million cars a year by 2035. The Shanghai plant opened in 2019.
  Analysts expect grid parity by 2050." The claim says 2050; the quote matches
  sentence 1. Sentence-scoped, the region contains 2035, which conflicts with the
  claimed 2050 → correctly `contradicted`. With a wide window the region swallows
  sentence 3, whose "2050" now appears to *agree* with the claim → falsely `supported`.
  `N` would also be an arbitrary magic number (CLAUDE.md forbids these), and characters
  do not track propositions.
- **Combining multiple region definitions and arbitrating between them.** Rejected: any
  tiebreak is either "take the narrowest" (so why compute the others?) or a heuristic
  vote — soft judgment wearing arithmetic. One rule, stated plainly, is testable.
- **Hand-rolled regex splitter.** Rejected: a known-incomplete heuristic in the
  precision path. Abbreviations (`Dr.`, `Inc.`, `U.S.`, `J.P. Morgan`), decimals
  (`3.5`), initials, ellipses, and periods inside quotes all break it. Its failure
  modes are open-ended and silent — a wrong region, not an error — which contradicts the
  0001 "bounded failure modes" bar.
- **spaCy sentencizer/parser.** Not rejected, but not chosen now. The model download
  works against the frictionless one-line-install goal, and the statistical parser's
  boundaries are version-dependent. If spaCy later earns its place for *entity
  extraction* (a different job), revisit whether to consolidate segmentation onto it —
  that is a future decision, not a deferred upgrade. `pysbd` may well remain the better
  segmentation tool regardless.
