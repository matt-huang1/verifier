# Current Status

> **Status: live.** What is actually built, tested, and verified today. Update on
> every meaningful change. Only list what exists.

## What's built

- Repository scaffold, CLAUDE.md, ADRs 0001–0006.
- **Judgment core** — `src/verifier/models.py` (Status/MatchKind/EntityKind/
  EntityResult enums; frozen SourceReport/Evidence/EntityCheck models) and
  `src/verifier/judgment.py` (`derive_status`, pure and total). 100% covered by a
  truth-table suite; 17 tests green on Python 3.13.

## What's not built yet

- The Verdict wrapper (computed-status model over `derive_status`).
- The matcher (quote + entity extraction, region-scoped) and the fetcher (httpx).
- The CLI (still a stub) and the MCP tool. See [ROADMAP.md](ROADMAP.md).