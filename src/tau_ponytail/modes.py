"""Ponytail runtime modes.

Derived from upstream ``@dietrichgebert/ponytail`` 4.10.0
(``hooks/ponytail-config.js``), MIT License, Copyright (c) 2026 DietrichGebert,
https://github.com/DietrichGebert/ponytail. The complete upstream MIT notice is
preserved in this repository's ``LICENSE``.
"""

from __future__ import annotations

import typing

Mode = typing.Literal["off", "lite", "full", "ultra"]

DEFAULT_MODE: typing.Final = "full"
RUNTIME_MODES: typing.Final = ("off", "lite", "full", "ultra")

# ponytail: ``in`` against the tuple cannot narrow ``str`` to the Literal; the
# value is checked against the same membership test, so the cast is sound.
_RUNTIME_MODE_SET = frozenset(typing.get_args(Mode))


def normalize_mode(value: object) -> Mode | None:
    """Return the trimmed, lowercased runtime mode for ``value`` or ``None``.

    Interactive values (command arguments) are trimmed; persisted values
    (environment/configuration) keep upstream's trim-free comparison and are
    handled by :mod:`tau_ponytail.config`.
    """
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    return typing.cast(Mode, normalized) if normalized in _RUNTIME_MODE_SET else None
