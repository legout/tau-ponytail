"""Default-mode and quiet-startup configuration resolution and persistence.

Derived from upstream ``@dietrichgebert/ponytail`` 4.10.0
(``hooks/ponytail-config.js``), MIT License, Copyright (c) 2026 DietrichGebert,
https://github.com/DietrichGebert/ponytail. The complete upstream MIT notice is
preserved in this repository's ``LICENSE``.
"""

from __future__ import annotations

import json
import os
import tempfile
import typing
from pathlib import Path
from typing import Any

from .modes import _RUNTIME_MODE_SET, DEFAULT_MODE, Mode


def config_dir() -> Path:
    """Return the Ponytail configuration directory for this platform."""
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "ponytail"
    if os.name == "nt":
        appdata = os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming"
        return Path(appdata) / "ponytail"
    return Path.home() / ".config" / "ponytail"


def config_path() -> Path:
    """Return the Ponytail ``config.json`` path for this platform."""
    return config_dir() / "config.json"


def read_config() -> tuple[dict[str, Any], str | None]:
    """Read the configuration file tolerantly.

    Returns ``(config, problem)``. A missing file is normal and yields
    ``({}, None)``; an unreadable, unparseable, or non-object file yields an
    actionable ``problem`` message instead of raising.
    """
    path = config_path()
    try:
        # A leading UTF-8 BOM (common on Windows editors) must not break JSON.
        raw = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return {}, None
    except OSError as exc:
        return {}, f"Could not read Ponytail config {path}: {exc}"
    try:
        config = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {}, f"Could not parse Ponytail config {path}: {exc}"
    if not isinstance(config, dict):
        return {}, f"Ponytail config {path} must contain a JSON object"
    return config, None


def _persisted_mode(value: object) -> Mode | None:
    """Normalize a persisted mode like upstream: lowercased, never trimmed."""
    if not isinstance(value, str):
        return None
    lowered = value.lower()
    # ponytail: membership above cannot narrow ``str`` to the Literal; the
    # value is a checked member by construction, so the cast is sound.
    return typing.cast(Mode, lowered) if lowered in _RUNTIME_MODE_SET else None


def default_mode() -> tuple[Mode, str | None]:
    """Resolve the configured default mode: environment, then config, then `full`.

    Returns ``(mode, problem)`` where ``problem`` is an actionable diagnostic
    when configured values exist but are unsupported; resolution still falls
    back exactly as specified.
    """
    problems: list[str] = []
    env = os.environ.get("PONYTAIL_DEFAULT_MODE")
    if env is not None:
        mode = _persisted_mode(env)
        if mode is not None:
            return mode, None
        problems.append(f"Ignoring unsupported PONYTAIL_DEFAULT_MODE={env!r}")
    config, problem = read_config()
    if problem is not None:
        problems.append(problem)
    stored = config.get("defaultMode")
    mode = _persisted_mode(stored)
    if mode is not None:
        return mode, _join(problems)
    if stored is not None:
        problems.append(f"Ignoring unsupported defaultMode={stored!r} in {config_path()}")
    return DEFAULT_MODE, _join(problems)


def quiet_startup() -> tuple[bool, str | None]:
    """Resolve the quiet-startup flag: environment override, then config.

    Empty, ``0``, ``false``, and ``no`` mean false; any other non-empty
    environment value means true. The config value must be JSON ``true``.
    """
    env = os.environ.get("PONYTAIL_QUIET_STARTUP")
    if env is not None:
        value = env.strip().lower()
        return value not in ("", "0", "false", "no"), None
    config, problem = read_config()
    return config.get("quietStartup") is True, problem


def write_default_mode(mode: Mode) -> Path:
    """Persist ``defaultMode`` atomically, preserving unrelated JSON keys.

    Parent directories are created as needed; an unusable previous file starts
    a fresh object like upstream. Raises ``OSError`` on failure so callers can
    produce an actionable diagnostic without crashing.
    """
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    config: dict[str, Any] = {}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(parsed, dict):
            config = parsed
    except (OSError, json.JSONDecodeError):
        pass
    config["defaultMode"] = mode
    text = json.dumps(config, indent=2)
    # Atomic replacement: a failed write must never truncate existing config.
    handle_fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".ponytail-", suffix=".json")
    try:
        with os.fdopen(handle_fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
    return path


def _join(problems: list[str]) -> str | None:
    return "; ".join(problems) if problems else None
