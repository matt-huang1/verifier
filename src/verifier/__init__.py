"""Verifier — independently fact-check the citations an AI agent produces.

Checks fidelity to a cited source, not truth about the world. The model proposes;
deterministic code judges. See CLAUDE.md and docs/decisions/.
"""

from verifier.judgment import derive_status
from verifier.models import (
    EntityCheck,
    EntityKind,
    EntityResult,
    Evidence,
    MatchKind,
    SourceReport,
    Status,
)

__version__ = "0.0.0"

__all__ = [
    "EntityCheck",
    "EntityKind",
    "EntityResult",
    "Evidence",
    "MatchKind",
    "SourceReport",
    "Status",
    "derive_status",
    "__version__",
]
