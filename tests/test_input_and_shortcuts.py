"""Focused tests for exact deactivation and companion shortcuts (spec criteria 7-9)."""

import pytest
from tau_coding.commands import CommandContext

from helpers import RecordingSession, RecordingUiBridge, load_runtime
from tau_ponytail.commands import is_deactivation_command, shortcut_request
from tau_ponytail.extension import setup
from tau_ponytail.instructions import instructions_for_mode

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("stop ponytail", True),
        ("  NORMAL MODE  ", True),
        ("Stop Ponytail.", True),
        ("normal mode!", True),
        ("stop ponytail ?", True),
        ("normal mode?!", True),
        ("stop ponytail.", title := None) if False else ("stop ponytail.", True),
        ("stop ponytail,", False),
        ("stop ponytail;", False),
        ("please stop ponytail", False),
        ("stop ponytail, then continue", False),
        ("add a normal mode toggle", False),
        ("", False),
    ],
)
def test_deactivation_truth_table(text: str, expected: bool) -> None:
    assert is_deactivation_command(text) is expected


async def test_matching_input_deactivates_and_forwards_unchanged(tmp_path) -> None:
    ui = RecordingUiBridge()
    runtime = load_runtime(tmp_path, setup, ui=ui)
    await runtime.emit_session_start("startup")

    outcome = await runtime.run_input_hooks("Stop Ponytail.")

    assert (outcome.handled, outcome.text) == (False, "Stop Ponytail.")
    assert ui.notifications[-1] == ("Ponytail mode set to off.", "info")
    result = await runtime.run_before_agent_start_hooks(prompt="x", system_prompt="BASE")
    assert result == "BASE"


async def test_embedded_phrase_keeps_mode_and_prompt(tmp_path) -> None:
    runtime = load_runtime(tmp_path, setup)
    await runtime.emit_session_start("startup")

    outcome = await runtime.run_input_hooks("add a normal mode toggle")

    assert (outcome.handled, outcome.text) == (False, "add a normal mode toggle")
    result = await runtime.run_before_agent_start_hooks(prompt="x", system_prompt="BASE")
    assert result == f"BASE\n\n{instructions_for_mode('full')}"


async def test_deactivation_is_silent_while_already_off(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PONYTAIL_DEFAULT_MODE", "off")
    ui = RecordingUiBridge()
    runtime = load_runtime(tmp_path, setup, ui=ui)
    await runtime.emit_session_start("startup")

    await runtime.run_input_hooks("stop ponytail")

    assert ui.notifications == [("Ponytail loaded: off", "info")]


async def test_extension_sourced_input_does_not_deactivate(tmp_path) -> None:
    ui = RecordingUiBridge()
    runtime = load_runtime(tmp_path, setup, ui=ui)
    await runtime.emit_session_start("startup")

    outcome = await runtime.run_input_hooks("stop ponytail", source="extension")

    assert outcome.text == "stop ponytail"
    assert ui.notifications == [("Ponytail loaded: full", "info")]
    result = await runtime.run_before_agent_start_hooks(prompt="x", system_prompt="")
    assert result == instructions_for_mode("full")


def test_shortcut_request_builds_skill_messages() -> None:
    assert shortcut_request("review") == "/skill:ponytail-review"
    assert shortcut_request("debt", " the diff ") == "/skill:ponytail-debt the diff"


async def test_all_five_shortcuts_are_registered(tmp_path) -> None:
    runtime = load_runtime(tmp_path, setup)
    registry = runtime.build_command_registry()

    for skill in ("review", "audit", "debt", "gain", "help"):
        assert registry.get(f"ponytail-{skill}") is not None


async def _invoke(runtime, name: str, args: str = ""):
    registry = runtime.build_command_registry()
    command = registry.get(name)
    assert command is not None
    return await command.handler(
        CommandContext(
            session=None,
            registry=registry,
            text=f"/{name} {args}".rstrip(),
            name=name,
            args=args,
        )
    )


async def test_idle_shortcut_starts_a_turn(tmp_path) -> None:
    runtime = load_runtime(tmp_path, setup)
    session = RecordingSession(tmp_path, running=False)
    runtime.bind(session)
    turns: list[str] = []
    runtime.set_turn_requested_callback(lambda content, *_: turns.append(content))

    await _invoke(runtime, "ponytail-review")

    assert turns == ["/skill:ponytail-review"]
    assert session.followed_up == []


async def test_active_shortcut_queues_follow_up(tmp_path) -> None:
    ui = RecordingUiBridge()
    runtime = load_runtime(tmp_path, setup, ui=ui)
    session = RecordingSession(tmp_path, running=True)
    runtime.bind(session)

    result = await _invoke(runtime, "ponytail-audit", " my module ")

    assert session.followed_up == ["/skill:ponytail-audit my module"]
    assert result.message == "/skill:ponytail-audit my module queued as follow-up."


async def test_unavailable_skill_follows_tau_handling_without_crash(tmp_path) -> None:
    runtime = load_runtime(tmp_path, setup)
    session = RecordingSession(tmp_path, running=False)
    runtime.bind(session)

    result = await _invoke(runtime, "ponytail-help")

    assert result.message is None
    assert session.followed_up == ["/skill:ponytail-help"]
