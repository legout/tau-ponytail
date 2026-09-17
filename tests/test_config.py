"""Focused tests for configuration resolution and atomic persistence (spec: Default resolution)."""

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from tau_ponytail.config import config_path, default_mode, quiet_startup, write_default_mode


def fake_windows_os() -> SimpleNamespace:
    """Stub ``os`` view running config's Windows branch without pathlib seeing nt."""
    return SimpleNamespace(name="nt", environ=os.environ)


def seed_config(tmp_path: Path, data: object, *, bom: bool = False) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data)
    path.write_text(("\ufeff" + text) if bom else text, encoding="utf-8")


def test_config_path_prefers_xdg_config_home(tmp_path: Path) -> None:
    assert config_path() == tmp_path / "xdg-config" / "ponytail" / "config.json"


def test_posix_fallback_uses_home_dot_config(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("XDG_CONFIG_HOME")
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    assert config_path() == tmp_path / "home" / ".config" / "ponytail" / "config.json"


def test_windows_fallback_uses_appdata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from tau_ponytail import config as config_module

    monkeypatch.delenv("XDG_CONFIG_HOME")
    monkeypatch.setattr(config_module, "os", fake_windows_os())
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    assert config_path() == tmp_path / "appdata" / "ponytail" / "config.json"


def test_windows_fallback_without_appdata_uses_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from tau_ponytail import config as config_module

    monkeypatch.delenv("XDG_CONFIG_HOME")
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr(config_module, "os", fake_windows_os())
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "home"))
    assert config_path() == tmp_path / "home" / "AppData" / "Roaming" / "ponytail" / "config.json"


def test_missing_config_resolves_full_without_diagnostic() -> None:
    assert default_mode() == ("full", None)
    assert quiet_startup() == (False, None)


def test_env_default_mode_has_highest_precedence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PONYTAIL_DEFAULT_MODE", "off")
    seed_config(tmp_path, {"defaultMode": "lite"})
    assert default_mode() == ("off", None)


def test_env_value_is_lowercased_without_trimming(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PONYTAIL_DEFAULT_MODE", "FULL")
    assert default_mode() == ("full", None)
    monkeypatch.setenv("PONYTAIL_DEFAULT_MODE", " full ")
    mode, problem = default_mode()
    assert (mode, problem is not None) == ("full", True)


def test_unsupported_env_value_falls_back_with_diagnostic(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PONYTAIL_DEFAULT_MODE", "review")
    seed_config(tmp_path, {"defaultMode": "ultra"})
    mode, problem = default_mode()
    assert mode == "ultra"
    assert problem is not None and "PONYTAIL_DEFAULT_MODE" in problem


def test_config_default_mode_used_when_env_absent(tmp_path: Path) -> None:
    seed_config(tmp_path, {"defaultMode": "ULTRA"})
    assert default_mode() == ("ultra", None)


def test_bom_prefixed_config_still_parses(tmp_path: Path) -> None:
    seed_config(tmp_path, {"defaultMode": "lite"}, bom=True)
    assert default_mode() == ("lite", None)


def test_invalid_json_resolves_full_with_diagnostic(tmp_path: Path) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json", encoding="utf-8")
    mode, problem = default_mode()
    assert mode == "full"
    assert problem is not None and "Could not parse" in problem
    assert quiet_startup() == (False, problem)


def test_non_object_config_resolves_full_with_diagnostic(tmp_path: Path) -> None:
    seed_config(tmp_path, [1, 2])
    mode, problem = default_mode()
    assert (mode, problem is not None) == ("full", True)


def test_unsupported_config_default_mode_falls_back_with_diagnostic(
    tmp_path: Path,
) -> None:
    seed_config(tmp_path, {"defaultMode": "review"})
    mode, problem = default_mode()
    assert (mode, problem is not None) == ("full", True)
    assert problem is not None and "defaultMode" in problem


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        ("1", True),
        ("yes", True),
        (" TRUE ", True),
        ("0", False),
        ("false", False),
        ("no", False),
        ("", False),
    ],
)
def test_quiet_startup_env_truthiness(
    monkeypatch: pytest.MonkeyPatch, env: str, expected: bool
) -> None:
    monkeypatch.setenv("PONYTAIL_QUIET_STARTUP", env)
    assert quiet_startup() == (expected, None)


@pytest.mark.parametrize(
    ("value", "expected"),
    [(True, True), (False, False), (1, False), ("true", False), (None, False)],
)
def test_quiet_startup_config_requires_strict_json_true(
    tmp_path: Path, value: object, expected: bool
) -> None:
    seed_config(tmp_path, {"quietStartup": value})
    assert quiet_startup() == (expected, None)


def test_quiet_env_overrides_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    seed_config(tmp_path, {"quietStartup": True})
    monkeypatch.setenv("PONYTAIL_QUIET_STARTUP", "0")
    assert quiet_startup() == (False, None)


def test_write_creates_parents_preserves_unrelated_keys(tmp_path: Path) -> None:
    seed_config(tmp_path, {"quietStartup": True, "defaultMode": "lite"})
    written = write_default_mode("ultra")
    assert written == config_path()
    assert json.loads(written.read_text(encoding="utf-8")) == {
        "quietStartup": True,
        "defaultMode": "ultra",
    }


def test_write_over_unusable_file_starts_fresh(tmp_path: Path) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("garbage{", encoding="utf-8")
    write_default_mode("lite")
    assert json.loads(path.read_text(encoding="utf-8")) == {"defaultMode": "lite"}


def test_failed_write_never_truncates_existing_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from tau_ponytail import config as config_module

    seed_config(tmp_path, {"defaultMode": "lite", "keep": "me"})
    before = config_path().read_text(encoding="utf-8")

    def broken_replace(src: object, dst: object) -> None:
        raise OSError("disk on fire")

    monkeypatch.setattr(config_module.os, "replace", broken_replace)
    with pytest.raises(OSError, match="disk on fire"):
        write_default_mode("ultra")
    assert config_path().read_text(encoding="utf-8") == before
    assert not list(config_path().parent.glob(".ponytail-*"))
