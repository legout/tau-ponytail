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
    ExtensionCommandContext,
    ExtensionContext,
)

from .commands import parse_ponytail_command
from .config import default_mode, quiet_startup, write_default_mode
from .instructions import instructions_for_mode
from .modes import Mode

_NOTIFY_WARNING: Final = "warning"


def setup(tau: ExtensionAPI) -> None:
    """Create one extension generation and register its public handlers."""
    configured_default: Mode = default_mode()[0]
    current_mode: Mode = configured_default

    def ponytail_command(args: str, context: ExtensionCommandContext) -> str:
        """Handle ``/ponytail`` arguments through the public command contract."""
        del context
        nonlocal current_mode, configured_default
        parsed = parse_ponytail_command(args, configured_default)

        if parsed.action == "set-mode" and parsed.mode is not None:
            current_mode = parsed.mode
            return f"Ponytail mode set to {parsed.mode}."

        if parsed.action == "status":
            return f"Ponytail: current {current_mode} • default {configured_default}"

        if parsed.action == "set-default" and parsed.mode is not None:
            try:
                write_default_mode(parsed.mode)
            except OSError as exc:
                return f"Failed to save default mode: {exc}"
            configured_default = default_mode()[0]
            if configured_default == parsed.mode:
                return f"Default Ponytail mode set to {parsed.mode}."
            return (
                f"Saved default {parsed.mode}, but env override keeps "
                f"default at {configured_default}."
            )

        return (
            "Unknown or unsupported /ponytail mode. "
            "Usage: /ponytail [lite|full|ultra|off|status|default <mode>]"
        )

    tau.register_command(
        "ponytail",
        ponytail_command,
        description="Set mode: off|lite|full|ultra. Commands: status, default <mode>",
    )

    def on_session_start(event: object, context: ExtensionContext) -> None:
        del event, context
        nonlocal current_mode, configured_default
        configured_default, problem = default_mode()
        current_mode = configured_default
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
