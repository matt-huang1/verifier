# ADR-0005: The V1 verify_citation contract

- **Status:** Proposed  (to be finalised in the "contract design" chat — step B)
- **Date:** 2026-07-07

## Context

`verify_citation` needs a precise typed input and output before implementation. This
ADR holds the open questions so the decision is made deliberately, not defaulted into.

## Sketch (not yet decided)

```
verify_citation(claim: str, url: str, quote: str | None) -> Verdict

Verdict:
  status: supported | contradicted | not_found_in_source | source_unreachable
  evidence: list[Evidence]          # matched / mismatched passages
  entity_checks: list[EntityCheck]  # each number/date/name: claimed vs found
  notes: str                        # human-readable "why"
  # NB: no confidence float (see 0003). Overall status computed from evidence,
  # never settable directly.
```

## Open questions for step B

1. **Input semantics.** The agent supplies the URL directly, so the search→propose→
   url_compare front half of the original pipeline drops out. Confirm verify_citation
   fetches *the given URL* and checks against it, with no search in the loop.
2. **Computed status.** Carry over the "overall_status is a read-only computed property"
   pattern from the prior repo. In Pydantic this is a computed field / model validator,
   not a settable field — decide the exact mechanism.
3. **Evidence shape.** What each `Evidence` and `EntityCheck` carries (matched text,
   location/offset, match kind: exact | normalized | fuzzy — see 0003 sub-question).
4. **Quote absent vs present.** With a quote: highest-precision path (quote match).
   Without: entity/number cross-check only. Define both paths' status logic.
5. **partially_supported.** Deferred from the V1 status set (0003); confirm it stays
   deferred.

## Decision

_Pending._
