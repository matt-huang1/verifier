# ADR-0005: The V1 verify_citation contract

- **Status:** Accepted
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

## Decision

### (a) Input semantics

`verify_citation(claim, url, quote?)` fetches *the given* `url`, follows redirects, and
checks fidelity against what it fetches. No web search in the loop. The resolved
(post-redirect) URL is reported as evidence. Authenticity of the URL is **not** judged
here — whether the domain is genuine or a lookalike is `check_source`'s job (see 0004).

### (b) Computed status

`status` is a computed Pydantic field, never settable directly. It is derived by a pure
function `derive_status(source_state, evidence, entity_checks)`. Fetch state is an
*input* to that function so that `source_unreachable` is honest and can never be faked
as `not_found_in_source` — a failure to fetch and a failure to support are distinct
mechanisms and must not blur (see CLAUDE.md, "Never guess").

### (c) Schema objects

```
SourceReport:
  requested_url: str
  resolved_url: str            # after redirects
  redirect_chain: list[str]
  reachable: bool
  status_code: int | None
  error: str | None
  fetched_at: datetime
  # NB: no full page text is retained on the report.

Evidence:
  claimed_text: str
  source_excerpt: str
  match_kind: exact | normalized | fuzzy | absent
  char_span: (int, int)        # span within the fetched source
  # A fuzzy similarity ratio MAY be included as a mechanical measurement,
  # not a confidence judgment (see 0003).

EntityCheck:
  kind: number | date | name | ...
  claimed: str
  found: str | None
  result: agree | conflict | absent
  source_excerpt: str
```

### (d) derive_status rules

- Source unreachable → `source_unreachable`.
- **Quote supplied (Path A — highest precision):**
  - quote absent from source → `not_found_in_source`.
  - quote found **and** a conflicting entity *within the matched region* →
    `contradicted`.
  - quote found, no conflict in the matched region → `supported`.
  - Contradiction is scoped to the matched passage, not the whole page: a figure
    disagreeing elsewhere on the page does not contradict a faithfully-quoted passage.
- **No quote (Path B — conservative):** status maxes out at `not_found_in_source`. It
  never asserts `supported` or `contradicted`. Evidence still lists every entity's
  presence/absence with excerpts. Rationale: without a caller-anchored quote there is no
  passage to bind the claim to, and under-claiming (honest "not found") is a cheaper
  failure than over-claiming (a false "supported").

### (e) partially_supported

Stays deferred (see 0003). Any conflict under a matched quote goes straight to
`contradicted`; there is no partial verdict in V1.
