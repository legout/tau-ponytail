"""Shared fixtures: hermetic environment and the anyio backend."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def hermetic_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Keep configuration lookups away from the developer's real home."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg-config"))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "home"))
    monkeypatch.delenv("PONYTAIL_DEFAULT_MODE", raising=False)
    monkeypatch.delenv("PONYTAIL_QUIET_STARTUP", raising=False)
