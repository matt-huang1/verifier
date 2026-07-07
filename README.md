# Verifier

> **AI agents cite sources that don't exist, or that don't say what the agent claims.
> Verifier lets an agent independently fact-check its own citations before you trust
> them.**

*Pre-alpha — under active construction. Interfaces will change.*

Give Verifier a **claim** and the **source URL** an agent cited. It fetches that source
itself and tells you whether the source actually supports the claim — with the evidence
that justifies the verdict. It checks **fidelity to the cited source**, not truth about
the world. The model proposes; deterministic code judges.

## Verifier does

- ✅ Verify a claim against its cited source
- ✅ Verify a quoted passage genuinely appears in the source
- ✅ Cross-check numbers, dates, and named entities: claimed vs found
- ✅ (next) Verify source authenticity — real domain or a lookalike/spoof

## Verifier deliberately does not

- ❌ Decide whether a claim is true in reality
- ❌ Search the internet to find a source
- ❌ Replace human judgement
- ❌ Verify opinions
- ❌ Rank or score sources
- ❌ Generate answers

## Status

See [docs/CURRENT_STATUS.md](docs/CURRENT_STATUS.md) for what's built,
[docs/ROADMAP.md](docs/ROADMAP.md) for what's next, and
[docs/decisions/](docs/decisions/) for why it's shaped this way.

## Quickstart

_CLI and install instructions land with the first vertical slice (step C)._

## License

MIT — see [LICENSE](LICENSE).
