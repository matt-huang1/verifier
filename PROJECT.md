# PROJECT.md

Not documentation — a working memo. Open it every session. Answers "what should I work
on today?" Keep it to a few lines; update as you go.

---

**Current milestone:** Project set up + step B (finalise the `verify_citation` contract).

**Current blocker:** None. Contract sub-questions are listed in ADR-0005.

**Next milestone:** Step C — thin vertical slice: surface-agnostic `verify()` core + CLI,
catching one real hallucinated citation end to end.

**Current risks:**
- MCP SDK mid-transition (v2 + new spec land ~2026-07-28). Deciding SDK strategy in the
  contract/MCP step; MCP surface is isolated so churn can't reach the core (ADR-0002).
- `check_source` allowlist-free authenticity is real design work, not a port (ADR-0004).

**Pending**
- Hello-world MCP ramp (protocol learning).

**Recently finished:**
- Repo scaffold, CLAUDE.md, ADRs 0001–0004 (decisions), 0005 (contract, proposed) - committed.

---

## Chat map (Claude Project)

Keep chats focused; start a new one when one hits ~100–150 messages. Spin these up
**as work reaches them**, not all at once:

- **architecture / decisions** — this one. High-level shape, ADRs.
- **mcp-learning** — protocol ramp; kept separate so its dead-ends don't pollute design.
- **core-implementation** — the engine (start at step C).
- **testing** — adversarial harness, property tests.
- **docs** · **packaging** · **distribution** · **backlog/ideas** — later phases.
