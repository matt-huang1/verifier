# ADR-0002: CLI before MCP, over a surface-agnostic core

- **Status:** Accepted
- **Date:** 2026-07-07

## Context

The product's headline surface is an MCP tool an agent calls. But MCP is the one
genuinely unfamiliar piece of the stack, its Python SDK is mid-transition (a v2 rework
and a new spec land within this project's build window), and a protocol surface is
awkward to iterate and test against while the verification logic is still settling.

## Decision

Build a **surface-agnostic core** — `verify(claim, url, quote) -> Verdict` — with no
protocol or I/O concerns in it. Ship a **CLI** over that core first. Add the **MCP
tool** as a second thin adapter over the identical core once the logic is proven.

The hello-world MCP ramp proceeds in parallel purely as protocol learning; it does not
touch the real engine until the CLI slice works end to end.

## Consequences

- The verification logic is exercised and tested through the CLI without any protocol
  in the loop — fast feedback, trivial to test, no client restart cycle.
- The killer demo works as a terminal one-liner (`verifier verify --claim ... --url
  ...`) and is recordable without any MCP setup.
- MCP-version churn (SDK v1 pin vs standalone fastmcp 3.x vs the new spec) is contained
  to one thin adapter, decided separately, and cannot force a rewrite of the core.
- Slight duplication of surface plumbing (CLI args + MCP tool signature) — accepted;
  both are thin.

## Alternatives considered

- **MCP first.** Rejected: couples the unknown (protocol) to the unsettled
  (verification logic) and makes iteration slow.
- **CLI only.** Rejected: MCP is the actual thesis and distribution story; CLI is the
  on-ramp, not the destination.
