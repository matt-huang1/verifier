"""The issued verdict: claim + anchored evidence, with a status computed from them.

``Verdict`` is the top of the judgment layer. It lives here rather than in ``models`` so
that ``models`` stays free of any judgment dependency: ``judgment.derive_status`` imports
the leaf types from ``models``, and this wrapper imports *both* — a one-directional layering
(models → judgment → verdict) with no import cycle.

The status is never stored. It re-derives from the attached evidence on every access, so a
``supported`` cannot exist without the evidence that makes it true (ADR-0005 b). The model is
frozen and forbids extra fields, which is what makes that guarantee hold at the boundary.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, computed_field

from verifier.judgment import derive_status
from verifier.models import EntityCheck, Evidence, SourceReport, Status


class Verdict(BaseModel):
    """A self-describing verdict: the claim, what was fetched, and the anchored evidence.

    ``frozen=True`` blocks attribute reassignment; ``extra="forbid"`` blocks smuggling a
    ``status`` (or anything else) in through the constructor. Together they make the computed
    ``status`` the *only* source of the verdict — it can never be asserted, only derived
    (ADR-0005 b).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    # The claim is stored so a persisted verdict is self-describing (ADR-0006).
    claim: str
    source: SourceReport
    quote_evidence: Evidence | None
    # A tuple, not a list: frozen=True stops attribute *reassignment* but not in-place
    # mutation, so a list would let someone append evidence to an issued verdict and flip its
    # computed status. The tuple closes that hole.
    entity_checks: tuple[EntityCheck, ...]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def status(self) -> Status:
        """The verdict, re-derived from the evidence on every access — never stored, so it
        cannot drift from what the evidence supports (ADR-0005 b).

        ``partially_supported`` is unreachable by construction: ``derive_status`` never
        returns it, so no verdict can carry it.
        """
        return derive_status(
            reachable=self.source.reachable,
            quote_evidence=self.quote_evidence,
            entity_checks=self.entity_checks,
        )
