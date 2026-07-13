# ADR-0009: Single-candidate entity conflict

- **Status:** Accepted
- **Date:** 2026-07-13

## Context

`derive_status` escalates to `contradicted` when an `EntityCheck` within the matched
region (0007) has result `conflict`. This ADR defines when an entity check is allowed to
be a `conflict` rather than merely `absent`.

The distinction is load-bearing. `absent` does not trigger `contradicted` (see the
truth-table case `pathA_entity_absent_is_not_conflict`), so a rule that is too weak
misses real contradictions entirely — a naive "is the claimed value present? no →
absent" rule would return `supported` for the Tesla case, defeating the project's
headline catch. A rule that is too aggressive manufactures false contradictions, which
tell an agent its *correct* citation is wrong.

## Decision

An entity **conflicts** when the region contains exactly one entity of the same kind and
its value differs from the claimed value — same kind, different value, unambiguous slot →
`conflict`.

- If the region contains **more than one** entity of that kind, the check is ambiguous:
  it is reported `absent`, never `conflict`. The matcher declines to guess which one the
  claim refers to.
- If the region contains **no** entity of that kind, the check is `absent`.
- If the values match, the check is `agree`.

`EntityKind` is the slot-matching mechanism: entities of different kinds are never
compared (a claimed number is not compared against a year).

Worked examples:

- Region "Tesla will make 20 million cars a year by 2035", claim says 2050. Region has
  exactly one year → `conflict` → `contradicted`. (The headline catch; preserved.)
- Region "Tesla will make 20 million cars by 2035, up from its 2019 baseline", claim
  says 2050. Region has two years; which one the claim addresses cannot be determined
  without semantic parsing → `absent` → not contradicted. The entity checks still appear
  in the evidence with their excerpts, so a human reading the verdict sees both years and
  can judge.
- Region contains no year at all, claim says 2050 → `absent`. Nothing to contradict.

## Consequences

- The rule **misses** some real contradictions in multi-entity sentences, returning
  `supported` there. This is an accepted cost. It arises from declining to judge an
  ambiguous case, not from asserting something the evidence did not show, and it is
  mitigated by traceability: the entity checks and their source excerpts appear in the
  verdict regardless (see 0005, 0007), so the discrepancy is visible to a reader even
  when the rule declines to call it.
- Requires tests: the single-year Tesla case → `conflict`; the two-year ambiguous case →
  `absent` (not `conflict`); no-entity-of-kind → `absent`; matching value → `agree`; and
  cross-kind values are never compared.

## Alternatives considered

- **Any-mismatch** — conflict whenever the claimed value is not among the region's
  entities of that kind. Rejected: it fires on ambiguous multi-entity sentences where the
  claim is genuinely about neither value, manufacturing false contradictions. A false
  `contradicted` is close in cost to a false `supported` — it tells the agent a correct
  citation is wrong — and this project's stance is that over-claiming is the more
  expensive failure (CLAUDE.md, "precision over recall", "never guess").
- **Positional / slot alignment** — parse the sentence to determine which entity the
  claim refers to. Rejected: this is semantic parsing, soft judgment of exactly the kind
  refused in 0001.
