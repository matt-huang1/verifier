"""Smoke test: the package imports and exposes a version. Real tests arrive in step C."""

import verifier


def test_package_imports() -> None:
    assert verifier.__version__
