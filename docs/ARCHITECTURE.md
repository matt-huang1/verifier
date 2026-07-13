# Architecture

> **Status: judgment layer built.** The verdict core — `models`, `derive_status`, and
> the `Verdict` wrapper — exists and is described below. The matcher, fetcher, and
> surfaces are not yet built; they are named as "not yet built," not described as if
> they were.

## Core principle

The model proposes; deterministic code judges. See
[decisions/0001](decisions/0001-deterministic-verification-not-llm-judging.md).

## Shape (intended)

A surface-agnostic core — `verify(claim, url, quote) -> Verdict` — with the CLI and the
MCP tool as thin adapters over it. See
[decisions/0002](decisions/0002-cli-before-mcp.md).

## Module map

Layering is strictly one-directional: **`models` -> `judgment` -> `verdict`**. Each layer
imports only from those above it in that chain; nothing imports downward.

- **`models.py`** — the typed leaves: the `Status` / `MatchKind` / `EntityKind` /
  `EntityResult` enums and the frozen `SourceReport` / `Evidence` / `EntityCheck`. Knows
  nothing about judgment.
- **`judgment.py`** — `derive_status`, the pure judge. Imports the leaves; knows nothing
  about `Verdict`.
- **`verdict.py`** — the `Verdict` model. Imports both; exposes `status` as a computed
  field that delegates to `derive_status`, so the verdict is recomputed from its evidence
  on every access and can never be stored or asserted.

**Why `Verdict` is its own module.** Putting it in `models.py` would create an import
cycle: `Verdict.status` needs `derive_status` (in `judgment.py`), and `judgment.py`
already imports the leaves from `models.py` (`models -> judgment -> models`). A separate
module keeps the layering acyclic and keeps `models.py` free of any judgment dependency.

## Not yet built

- **Matcher** — locates the caller's quote in the fetched text and produces the
  `Evidence` plus the region-scoped `EntityCheck`s that feed a `Verdict`.
- **Fetcher** — fetches the cited URL and produces the `SourceReport`.
- **Surfaces** — the CLI and the MCP tool are thin adapters over the same core, not
  separate engines. See [decisions/0002](decisions/0002-cli-before-mcp.md).
