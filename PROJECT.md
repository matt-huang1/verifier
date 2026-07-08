# PROJECT.md

Not documentation — a working memo. Open it every session. Answers "what should I work
on today?" Keep it to a few lines; update as you go.

---

**Current milestone:** Step C — the engine. Judgment core done; next is the Verdict
wrapper, then the matcher + fetcher, then the CLI slice catching one real hallucinated
citation end to end.

**Current blocker:** None.

**Next milestone:** Wrap the `verify()` core as the MCP `verify_citation` tool, then
`check_source`.

**Current risks:**
- MCP SDK mid-transition (v2 + new spec land ~2026-07-28). MCP surface is isolated so
  churn can't reach the core (ADR-0002); SDK-version choice still open for the MCP step.
- `check_source` allowlist-free authenticity is real design work, not a port (ADR-0004).

**Now — start here:**
- Verdict wrapper: a Pydantic model carrying the evidence with `status` as a computed
  field calling `derive_status`, so a verdict can't exist with a status its evidence
  doesn't justify. Design in the brainstorm chat, execute via Claude Code.

**Backlog (don't forget, not yet scheduled):**
- Region-scoping guard test: page-wide conflicting number + faithful quote of a
  different sentence → must be `supported`, not `contradicted` (build with the matcher).
- Lock the killer-demo fixture (Tesla 2035-vs-2050): one artifact reused as the Path A
  unit test, the `examples/` script, and the README demo.
- `check_source`: allowlist-free authenticity ("expected domain" derivation) needs its
  own contract pass — likely its own chat (ADR-0004).

**Recently finished:**
- Judgment core (models + `derive_status`) — committed, pushed, 100% covered, 17 tests green.
- ADR-0006 (logging + verdict persistence); `.gitignore` + `uv.lock` committed.
- V1 contract locked (ADR-0005); ADR-0001 refined; CLAUDE.md + KNOWN_LIMITATIONS updated.
- Hello-world MCP ramp (step A) — echo called end-to-end in Claude Desktop.

---

## Chat map (Claude Project)

One brainstorm chat (this one) + Claude Code as executor is the default. Separate chats
only for genuinely divergent threads (e.g. `check_source` authentication design). Don't
split the decide → hand-off → review loop across chats — it just forces context re-uploads.