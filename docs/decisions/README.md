# Architecture Decision Records

One record per meaningful decision, written **when the decision is made**, not
reconstructed afterward. Each is one page: Context, Decision, Consequences, Alternatives
considered. Status is one of `Proposed`, `Accepted`, `Superseded by NNNN`.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-deterministic-verification-not-llm-judging.md) | Deterministic verification, not LLM judging | Accepted |
| [0002](0002-cli-before-mcp.md) | CLI before MCP, over a surface-agnostic core | Accepted |
| [0003](0003-no-confidence-float-discrete-statuses.md) | No confidence float — statuses carry epistemic state | Accepted |
| [0004](0004-verify-citation-first-check-source-next.md) | verify_citation first; check_source next, not cut | Accepted |
| [0005](0005-v1-verdict-contract.md) | The V1 verify_citation contract | Proposed |

## Template

```markdown
# ADR-NNNN: <title>

- **Status:** Proposed | Accepted | Superseded by NNNN
- **Date:** YYYY-MM-DD

## Context
What forces the decision. The problem, the constraints.

## Decision
What we chose. Stated plainly.

## Consequences
What this makes easy, hard, or impossible. Costs accepted.

## Alternatives considered
What was rejected, and why.
```
