# Architecture Decision Records

One record per meaningful decision, written **when the decision is made**, not
reconstructed afterward. Each is one page: Context, Decision, Consequences, Alternatives
considered. Status is one of `Proposed`, `Accepted`, `Superseded by NNNN`.

A decision corrected **in part** stays `Accepted` and records the change in place: an
`**Amended:** <date> — <summary>` line in the header block and a dated `## Amendment`
section at the end (see ADR-0010 for the reference implementation). `Superseded by NNNN` is
reserved for wholesale replacement of an ADR by a new one.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-deterministic-verification-not-llm-judging.md) | Deterministic verification, not LLM judging | Accepted |
| [0002](0002-cli-before-mcp.md) | CLI before MCP, over a surface-agnostic core | Accepted |
| [0003](0003-no-confidence-float-discrete-statuses.md) | No confidence float — statuses carry epistemic state | Accepted |
| [0004](0004-verify-citation-first-check-source-next.md) | verify_citation first; check_source next, not cut | Accepted |
| [0005](0005-v1-verdict-contract.md) | The V1 verify_citation contract | Proposed |
| [0006](0006-logging-and-verdict-persistence.md) | Logging and verdict persistence | Accepted |
| [0007](0007-sentence-scoped-contradiction-regions.md) | Sentence-scoped contradiction regions | Accepted |
| [0008](0008-length-preserving-normalization.md) | Length-preserving normalization | Accepted |
| [0009](0009-single-candidate-entity-conflict.md) | Single-candidate entity conflict | Accepted |
| [0010](0010-entity-extraction-scope.md) | Entity extraction scope | Accepted |

## Template

```markdown
# ADR-NNNN: <title>

- **Status:** Proposed | Accepted | Superseded by NNNN
- **Date:** YYYY-MM-DD
- **Amended:** YYYY-MM-DD — <summary> (see [Amendment](#amendment-yyyy-mm-dd))   ← only if amended

## Context
What forces the decision. The problem, the constraints.

## Decision
What we chose. Stated plainly.

## Consequences
What this makes easy, hard, or impossible. Costs accepted.

## Alternatives considered
What was rejected, and why.

## Amendment (YYYY-MM-DD)   ← only if amended
What was wrong with the original decision, what replaced it, and why. Stays `Accepted`; the
Amended header line points here.
```
