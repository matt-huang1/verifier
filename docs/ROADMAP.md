# Roadmap

> **Status: scaffold.** What's next, and what's deliberately deferred (with the trigger
> for revisiting).

## Next

1. Finalise the `verify_citation` contract (ADR-0005).
2. Vertical slice: `verify()` core + CLI catching one real hallucinated citation.
3. `check_source` (authenticity), incl. the allowlist-free design (ADR-0004).
4. Wrap the core as an MCP tool.

## Deliberately deferred (v2+)

- Semantic / NLI support layer (labelled lower-confidence when added).
- Hosted HTTP server + no-install web demo.
- PDF and JS-rendered sources; headless-browser fallback.
- Observability / usage stats.

_Each gets a stated trigger for revisiting as it firms up._
