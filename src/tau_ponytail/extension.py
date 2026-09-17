"""Tau extension entry point: generation state, run guidance, and notifications.

Uses only Tau's public extension contract: ``setup(tau)`` registers lifecycle
and ``before_agent_start`` handlers; the active mode belongs to this setup
generation and resets to the resolved default on every ``session_start``.
"""

from __future__ import annotations

from typing import Final

from tau_coding.extensions import (
    BeforeAgentStartEvent,
    BeforeAgentStartHookResult,
    ExtensionAPI,
    ExtensionContext,
)

from .config import default_mode, quiet_startup
from .instructions import instructions_for_mode
from .modes import Mode

_NOTIFY_WARNING: Final = "warning"


def setup(tau: ExtensionAPI) -> None:
    """Create one extension generation and register its public handlers."""
    current_mode: Mode = default_mode()[0]

    def on_session_start(event: object, context: ExtensionContext) -> None:
        del event, context
        nonlocal current_mode
        current_mode, problem = default_mode()
        if problem is not None:
            tau.notify(problem, level=_NOTIFY_WARNING)
        quiet, _ = quiet_startup()
        if not quiet:
            tau.notify(f"Ponytail loaded: {current_mode}")

    def on_before_agent_start(
        event: object,
        context: ExtensionContext,
    ) -> BeforeAgentStartHookResult | None:
        del context
        # Fail open like upstream's null-event guard: an unexpected payload
        # keeps the current prompt instead of breaking the run.
        if not isinstance(event, BeforeAgentStartEvent) or current_mode == "off":
            return None
        # Guard an empty supplied prompt so no ``None``-ish prefix is prepended.
        base = f"{event.system_prompt}\n\n" if event.system_prompt else ""
        return BeforeAgentStartHookResult(
            system_prompt=f"{base}{instructions_for_mode(current_mode)}"
        )

    tau.on("session_start", on_session_start)
    tau.on("before_agent_start", on_before_agent_start)
