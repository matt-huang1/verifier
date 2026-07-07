# ADR-0006: Logging and verdict persistence

- **Status:** Accepted
- **Date:** 2026-07-07

## Context

We want to know what happened at every stage of a run — the successes and the
failures — and be able to pull up an unusual case later and inspect it. "Log
everything" sounds like one requirement, but it splits into three layers that
need different treatment and must not be conflated:

- **Operational logging** — the running commentary of a single execution: what
  was fetched, how it redirected, which extraction path ran, how long it took,
  and the real exception behind any failure.
- **Verdict persistence** — the durable, structured record of a completed run,
  kept so a past verdict can be re-inspected and re-derived.
- **Telemetry / usage analytics** — aggregate counts and dashboards across many
  runs.

They differ in lifetime, in format, and in privacy surface, so a single "log
everything" switch would get all three wrong at once.

## Decision

### 1. Operational logging from day one

Via the stdlib `logging` module. Emit the fetch lifecycle, the redirect chain,
the extraction path taken, timings, and the real exception behind a failure —
enough to reconstruct what the run *did* without re-running it.

Logs go to **stderr or a file only, NEVER stdout.** A stdio MCP server speaks
JSON-RPC over stdout; any stray write there corrupts the stream. This is a hard
constraint, not a style preference.

### 2. Verdict persistence

Persist each run's structured record — `SourceReport`, `Evidence`,
`EntityCheck`s, and the inputs to `derive_status`. Include the extracted source
text (or a content hash of it).

Rationale: the judgment logic is reproducible, but its **input is not**. Live
web pages change under us — this is exactly why `SourceReport` carries
`fetched_at` (see 0005). Re-running `verify_citation` against the same URL
tomorrow can fetch different bytes and legitimately reach a different verdict.
Persisting the run against the bytes we actually saw is the only thing that
makes a past verdict re-derivable.

### 3. Telemetry deferred to v2

Counts, dashboards, and hosted observability (Langfuse / Logfire and the like)
are a separate concern with their own privacy implications, and are **deferred
to v2**. Not built in V1.

### 4. Local-only in V1

Nothing phones home. Logs and persisted records may contain fetched source
content and the user's claims, so they stay on the user's machine.

## Consequences

- The judgment core stays **pure**. `derive_status` and the matching functions
  perform no logging and no I/O; logging and persistence live in the
  orchestration layer — `verify()` and the fetcher — around the core. This keeps
  the reproducibility invariant (ADR-0001) intact: the thing under test has no
  side channels.
- A past verdict is re-derivable against the exact bytes that produced it, not
  merely "re-runnable and hopefully the same."
- The stdout prohibition means MCP and CLI share the same logging discipline;
  neither surface can quietly break the JSON-RPC stream.
- Persisted records are a data-retention surface (source content, claims) that
  a future v2 must govern when telemetry and any hosted mode arrive.

## Alternatives considered

- **Full observability stack now** (hosted telemetry, dashboards from day one).
  Rejected: premature for V1, adds a privacy surface before it earns its keep,
  and is cleanly deferrable to v2.
- **No persistence — just re-run to reproduce.** Rejected: the input is not
  reproducible. Because the fetched page can change, re-running cannot re-derive
  a *past* verdict; only persisting the run can.
