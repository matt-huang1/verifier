# CLAUDE.md

The working brief for this project. Read at the start of any focused chat so the
context is set without re-deriving it. This file is for the builder first; Claude
second.

## Mission

Verifier is a tool that lets an AI agent independently fact-check the citations it
produces. Given a claim and the source URL the agent cited, Verifier fetches that
source itself and reports whether the source actually supports the claim — with the
evidence that justifies the verdict. It checks **fidelity to the cited source**, not
truth about the world. The model proposes; deterministic code judges.

## Design principles

- **The model proposes, deterministic code judges.** An LLM may locate or draft; it
  never issues the verdict. A check only counts if it would give a different answer
  in the world where the claim is false.
- **Evidence always accompanies a conclusion.** No bare verdict. Every status is
  backed by the matched/mismatched passage and the entity-level checks that produced
  it. Auditability is the product, not a nicety.
- **Precision over recall.** When unsure, return "couldn't confirm" — never a
  confident "supported." A false "verified" is fatal to trust; an honest "not found"
  is not.
- **Never guess.** Distinct failure mechanisms get distinct, named statuses. A source
  that couldn't be fetched is not the same as a claim that wasn't supported, and the
  output must not blur them.
- **The verdict is computed, never asserted.** Overall status is derived from the
  attached evidence, so "supported" cannot exist without the evidence that makes it
  true.
- **Anchoring inputs are explicit, never inferred.** The claim, the URL, and any quote
  are caller-supplied. If the tool inferred them, a hallucinated source could validate
  itself.
- **Trust is earned.** The adversarial harness proves the checks catch what they claim
  to; clean controls prove they don't pass by rejecting everything.

## Non-goals (what Verifier deliberately does not do)

- Decide whether a claim is **true in reality**. It verifies fidelity to the cited
  source only.
- **Search the internet** to find a source. The agent supplies the URL; Verifier checks
  that URL. (No search in the verify loop.)
- **Replace human judgement** on framework alignment, quality, or "good enough."
- **Verify opinions** or non-checkable/forward-looking claims.
- **Rank or score sources** by quality or reputation.
- **Generate answers.** It is a checker, not a producer.

## Scope

**V1 (now):** `verify_citation(claim, url, quote?) -> Verdict`. A typed verdict with a
named status, the evidence, and entity-level checks (numbers, dates, named entities:
claimed vs found).

**Next:** `check_source(url) -> authenticity report` — the spoof/lookalike-domain
differentiator. Not cut from scope; sequenced second. (See decisions/0004.)

**Deferred (v2+):** semantic/NLI support layer, hosted HTTP server + web demo,
PDF/JS-rendered sources, observability. Named in ROADMAP, not built early.

## Architecture (short)

A **surface-agnostic core** does the verification: `verify(claim, url, quote) ->
Verdict`. The **CLI** and the **MCP tool** are thin adapters over that same core — no
verification logic lives in either surface. This is why the CLI can ship first and MCP
wraps the identical engine later. (See decisions/0002.)

## Coding standards

- Type hints on everything; `mypy` clean.
- Pydantic models at every boundary (tool inputs, the verdict schema).
- Evidence objects are immutable; no hidden or global mutable state.
- No magic numbers — thresholds are named constants with a comment or an ADR.
- Deterministic by default; any nondeterminism is isolated and named.
- Tests first. `ruff` clean. CI green before merge.

## Definition of Done (per feature)

A change is done only when it has: unit tests (plus a property test where an invariant
exists); updated docs; a CLI surface; an MCP tool (once MCP exists); a CHANGELOG entry;
an ADR if a meaningful decision was made; no lint or type errors; CI passing. This
prevents "I'll document it later."

## Where things live

- Decisions: `docs/decisions/` (ADRs — written when the decision is made, not after).
- What's built vs planned vs missing: `docs/CURRENT_STATUS.md`, `ROADMAP.md`,
  `KNOWN_LIMITATIONS.md`.
- What to work on today: `PROJECT.md` (open it every session).
