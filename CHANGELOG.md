# Changelog

All notable changes are recorded here. Format follows Keep a Changelog; this project
adheres to semantic versioning once it reaches a first release.

## [Unreleased]

### Added
- Repository scaffold: CLAUDE.md, PROJECT.md, docs skeleton, CI.
- ADR-0001..0004 (accepted decisions), ADR-0005 (proposed V1 contract).
- CLI stub pinning the intended `verifier verify` interface.
- Judgment core: the typed verdict leaves (`models.py`) and `derive_status`, the
  pure judge that computes a `Status` from fetch state and anchored evidence.
- Verdict wrapper: binds a claim to its anchored evidence, with `status` computed
  from that evidence on every access (never stored, so it cannot drift). Frozen and
  `extra="forbid"` make the status uninjectable; `entity_checks` is a tuple so an
  issued verdict cannot be mutated.
