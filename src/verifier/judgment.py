"""The judgment core: derive the verdict status from fetch state and evidence.

Pure and total. The same inputs give the same ``Status`` every time — no I/O, no clock,
no network, no randomness in the path (CLAUDE.md: "reproducibility is a testable
property"; "the model proposes, deterministic code judges"). Everything passed in has
already been located and anchored to the source; this function only *decides*.
"""

from __future__ import annotations

from collections.abc import Sequence

from verifier.models import EntityCheck, EntityResult, Evidence, Status


def derive_status(
    *,
    reachable: bool,
    quote_evidence: Evidence | None,
    entity_checks: Sequence[EntityCheck],
) -> Status:
    """Compute the verdict from anchored evidence.

    Args:
        reachable: whether the source was successfully fetched. A distinct input from the
            evidence so a fetch failure can never be laundered into a content verdict
            (ADR-0005 b). It dominates everything below.
        quote_evidence: the match result for the caller-supplied quote, or ``None`` when
            no quote was given. Its presence selects the path (A vs B); its ``match_kind``
            is the *single* source of truth for "quote absent" — this function never runs
            a second, independent absence check.
        entity_checks: for Path A, the entity checks drawn from **within the matched
            region only** — the caller owns that scoping, because a figure disagreeing
            elsewhere on the page must not contradict a faithfully-quoted passage
            (ADR-0005 d). In Path B these are report-only and cannot move the verdict.

    Returns:
        The computed ``Status``.
    """
    # Reachability dominates. A failure to fetch and a failure to support are distinct
    # mechanisms and must never blur (CLAUDE.md, "Never guess").
    if not reachable:
        return Status.SOURCE_UNREACHABLE

    # Path B — no caller-anchored quote. Conservative by construction: without a passage
    # to bind the claim to, we never assert supported or contradicted (ADR-0005 d).
    # Under-claiming ("not found") is a cheaper failure than over-claiming a false
    # "supported" (CLAUDE.md, "Precision over recall"). Entity checks are still reported
    # by the caller, but they cannot lift or lower this verdict.
    if quote_evidence is None:
        return Status.NOT_FOUND_IN_SOURCE

    # Path A — a quote was supplied. "Absent" is read straight off the Evidence, the one
    # place that fact is defined.
    if not quote_evidence.match_kind.is_found:
        return Status.NOT_FOUND_IN_SOURCE

    # Quote found. Any conflicting entity within the matched region contradicts it;
    # otherwise the faithfully-located quote stands as supported.
    if any(check.result is EntityResult.CONFLICT for check in entity_checks):
        return Status.CONTRADICTED

    return Status.SUPPORTED
