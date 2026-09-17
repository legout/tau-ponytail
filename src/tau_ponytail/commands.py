"""``/ponytail`` command parsing.

Derived from upstream ``@dietrichgebert/ponytail`` 4.10.0
(``pi-extension/index.js``), MIT License, Copyright (c) 2026 DietrichGebert,
https://github.com/DietrichGebert/ponytail. The complete upstream MIT notice is
preserved in this repository's ``LICENSE``.
"""

from __future__ import annotations

import re
import typing
from dataclasses import dataclass

from .modes import Mode, normalize_mode


@dataclass(frozen=True, slots=True)
class ParsedCommand:
    """One parsed ``/ponytail`` argument payload."""

    action: typing.Literal["set-mode", "status", "set-default", "invalid"]
    mode: Mode | None = None
    reason: str | None = None


def parse_ponytail_command(text: str, default_mode: Mode) -> ParsedCommand:
    """Parse ``/ponytail`` arguments like upstream ``parsePonytailCommand``.

    An empty argument enables the resolved default, except a default of ``off``
    enables ``full`` (upstream parity).
    """
    normalized = text.strip().lower()
    if not normalized:
        return ParsedCommand("set-mode", mode="full" if default_mode == "off" else default_mode)

    parts = normalized.split()
    primary = parts[0]
    secondary = parts[1] if len(parts) > 1 else None

    if primary == "status":
        return ParsedCommand("status")

    if primary == "default":
        mode = normalize_mode(secondary)
        if mode is None:
            return ParsedCommand("invalid", reason="invalid-default-mode")
        return ParsedCommand("set-default", mode=mode)

    mode = normalize_mode(primary)
    if mode is None:
        return ParsedCommand("invalid", reason="invalid-mode")
    return ParsedCommand("set-mode", mode=mode)


# "stop ponytail" / "normal mode" turn Ponytail off, but only as a standalone
# command. Matching the phrase anywhere swallowed ordinary requests like
# "add a normal mode toggle", so the whole input must be the command, ignoring
# case and trailing punctuation (upstream ``isDeactivationCommand``).
_DEACTIVATION_PHRASES = frozenset({"stop ponytail", "normal mode"})
_TRAILING_NOISE = re.compile(r"[.!?\s]+$")


def is_deactivation_command(text: str) -> bool:
    """True only for a whole-input deactivation phrase.

    Case- and whitespace-tolerant with optional trailing ``.``, ``!``, or
    ``?``; comma/semicolon suffixes do not match.
    """
    return _TRAILING_NOISE.sub("", text.strip().lower()) in _DEACTIVATION_PHRASES


SHORTCUT_SKILLS: typing.Final = ("review", "audit", "debt", "gain", "help")


def shortcut_request(skill: str, args: str = "") -> str:
    """Build the ``/skill:ponytail-*`` request message for one shortcut."""
    normalized = args.strip()
    return f"/skill:ponytail-{skill} {normalized}" if normalized else f"/skill:ponytail-{skill}"
