# Known Limitations

> **Status: scaffold.** Real, current gaps in what *is* built — named honestly, not
> hidden. Populate as the engine grows.

## Fuzzy quote match does not catch semantic drift

A fuzzy quote match that drifts in *meaning* while staying above the similarity
threshold is not caught in V1. V1 treats an above-threshold fuzzy match as "found" and
relies on the entity check (numbers, dates, names) to catch disagreement — so a drift
that changes the sense without changing any checked entity passes as supported.
Detecting meaning-level drift is the deferred NLI layer (see ROADMAP; 0003).
