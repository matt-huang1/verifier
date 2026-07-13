# PROJECT.md

Not documentation — a working memo. Open it every session. Answers "what should I work
on today?" Keep it to a few lines; update as you go.

---

**Current milestone:** Step C — the engine. Judgment layer complete and the matcher fully
specified (ADRs 0007–0010). Next: build the extractor, then the matcher, then the fetcher,
then the CLI slice catching one real hallucinated citation end to end.

**Current blocker:** None. No design decisions outstanding for the matcher.

**Next milestone:** Wrap the core as the MCP `verify_citation` tool, then `check_source`.

**Current risks:**
- MCP SDK mid-transition (v2 + new spec land ~2026-07-28). MCP surface is isolated so
  churn can't reach the core (ADR-0002); SDK-version choice still open for the MCP step.
- `check_source` allowlist-free authenticity is real design work, not a port (ADR-0004).

**Now — build in this order:**
1. **Extractor** (`extraction.py`) — regex; years, numbers, percentages, currencies;
   canonical `value` for comparison + `raw` for evidence (ADR-0010). Self-contained and
   provable in isolation — same pattern that worked for `derive_status`.
2. **Matcher** — pysbd segmentation behind a local `segment_sentences` interface (ADR-0007);
   quote cascade exact → normalized → fuzzy → absent with `FUZZY_MATCH_THRESHOLD = 0.90`;
   length-preserving normalization so spans point into the original (ADR-0008); region =
   sentence(s) overlapped by the match; single-candidate conflict rule (ADR-0009). Emits
   `Evidence` + region-scoped `EntityCheck`s.
3. **Fetcher** — httpx + trafilatura → `SourceReport`. Honest failure modes; `reachable`
   is the fetch layer's call, not the judge's.
4. **CLI slice** — wire end to end and catch a real hallucinated citation. North-star
   moment; record it for the demo.

**Must-have tests when the matcher lands:**
- Region-scoping guard: a conflicting number elsewhere on the page + a faithful quote of a
  different sentence → must be `supported`, not `contradicted`. This is the promise
  `derive_status` currently takes on trust; the matcher has to earn it.
- Segmentation on adversarial text: `Dr.`, `3.5`, `U.S.`, `J.P. Morgan`, period inside quotes.
- Span correctness: a char_span from a normalized match points at the right text in the
  *original* string.

**Backlog (don't forget, not yet scheduled):**
- Lock the killer-demo fixture (Tesla 2035-vs-2050): one artifact reused as the matcher
  test, the `examples/` script, and the README demo.
- Fetch cache (diskcache/SQLite keyed by URL). Needs a TTL, and a cached fetch must never
  masquerade as a fresh one — `fetched_at` has to travel with the verdict. Likely its own
  ADR; interacts with ADR-0006.
- LLM/spaCy proposer for named entities — lives in the *extractor*, proposes candidates that
  still pass through the ADR-0009 conflict rule. Never in the judgment path (ADR-0001).
  Ollama models already downloaded locally for this.
- `check_source`: allowlist-free authenticity ("expected domain" derivation) needs its own
  contract pass — likely its own chat (ADR-0004).

**Recently finished:**
- Matcher fully specified: ADR-0007 (sentence-scoped regions), 0008 (length-preserving
  normalization), 0009 (single-candidate conflict), 0010 (entity extraction scope).
- Verdict wrapper — computed status, uninjectable, immutable; 25 tests green, 100% on the
  judgment layer.
- Judgment core (`models` + `derive_status`); ADR-0006 (logging + verdict persistence).
- V1 contract locked (ADR-0005). Hello-world MCP ramp (step A) done.

---

## Chat map (Claude Project)

One brainstorm chat (this one) + Claude Code as executor is the default. Separate chats
only for genuinely divergent threads (e.g. `check_source` authentication design). Don't
split the decide → hand-off → review loop across chats — it just forces context re-uploads.