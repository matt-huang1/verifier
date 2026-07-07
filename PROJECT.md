# PROJECT.md

Not documentation — a working memo. Open it every session. Answers "what should I work
on today?" Keep it to a few lines; update as you go.

---

**Current milestone:** Step C — thin vertical slice: surface-agnostic `verify()` core +
CLI, catching one real hallucinated citation end to end.

**Current blocker:** None. The V1 contract is locked (ADR-0005, accepted).

**Next milestone:** Wrap the `verify()` core as the MCP `verify_citation` tool, then
`check_source`.

**Current risks:**
- MCP SDK mid-transition (v2 + new spec land ~2026-07-28). MCP surface is isolated so
  churn can't reach the core (ADR-0002); SDK-version choice still open for the MCP step.
- `check_source` allowlist-free authenticity is real design work, not a port (ADR-0004).

**For step C — start here:**
- Build `derive_status` first: signature + truth-table tests before any fetch code.
  It's the heart of the engine; don't skip it for plumbing.
- One source of truth for "quote absent" — Path A reads it from the Evidence object's
  `match_kind`, not a second independent check.

**Backlog (don't forget, not yet scheduled):**
- Lock the killer-demo fixture (Tesla 2035-vs-2050): one artifact reused as the Path A
  unit test, the `examples/` script, and the README demo.
- `check_source`: allowlist-free authenticity ("expected domain" derivation) needs its
  own contract pass before coding (ADR-0004).

**Recently finished:**
- V1 `verify_citation` contract locked (ADR-0005 accepted); ADR-0001 refined; CLAUDE.md
  + KNOWN_LIMITATIONS updated — committed.
- Hello-world MCP ramp (step A) — echo discovered and called end-to-end in Claude Desktop.
- Repo scaffold, CLAUDE.md, ADRs 0001–0004, 0005 (proposed) — committed.

---

## Chat map (Claude Project)

Keep chats focused; start a new one when one hits ~100–150 messages. Spin these up
**as work reaches them**, not all at once:

- **architecture / decisions** — this one. High-level shape, ADRs.
- **mcp-learning** — protocol ramp; kept separate so its dead-ends don't pollute design.
- **core-implementation** — the engine (start at step C).
- **testing** — adversarial harness, property tests.
- **docs** · **packaging** · **distribution** · **backlog/ideas** — later phases.