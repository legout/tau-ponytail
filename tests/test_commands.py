"""Focused tests for /ponytail commands and default persistence (spec criteria 2-4, 9)."""

import json
from pathlib import Path

import pytest
from tau_coding.commands import CommandContext

from helpers import load_runtime
from tau_ponytail.config import config_path
from tau_ponytail.extension import setup
from tau_ponytail.instructions import instructions_for_mode

pytestmark = pytest.mark.anyio


def make_invoker(runtime):
    """Return an async invoker for the runtime's /ponytail command."""
    registry = runtime.build_command_registry()
    command = registry.get("ponytail")
    assert command is not None

    async def invoke(args: str) -> str:
        result = await command.handler(
            CommandContext(
                session=None,
                registry=registry,
                text=f"/ponytail {args}",
                name="ponytail",
                args=args,
            )
        )
        assert result.handled is True
        return result.message

    return invoke


@pytest.mark.anyio
async def test_bare_command_enables_resolved_default(tmp_path) -> None:
    runtime = load_runtime(tmp_path, setup)
    invoke = make_invoker(runtime)
    await runtime.emit_session_start("startup")

    assert await invoke("") == "Ponytail mode set to full."

    result = await runtime.run_before_agent_start_hooks(prompt="x", system_prompt="")
    assert result == instructions_for_mode("full")


@pytest.mark.anyio
async def test_bare_command_with_off_default_enables_full(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PONYTAIL_DEFAULT_MODE", "off")
    runtime = load_runtime(tmp_path, setup)
    invoke = make_invoker(runtime)
    await runtime.emit_session_start("startup")

    assert await invoke("") == "Ponytail mode set to full."


@pytest.mark.parametrize("args", ["lite", "full", "ultra", "off"])
@pytest.mark.anyio
async def test_explicit_mode_commands(tmp_path, args) -> None:
    runtime = load_runtime(tmp_path, setup)
    invoke = make_invoker(runtime)

    assert await invoke(args) == f"Ponytail mode set to {args}."


@pytest.mark.anyio
async def test_status_reports_active_and_default(tmp_path) -> None:
    runtime = load_runtime(tmp_path, setup)
    invoke = make_invoker(runtime)
    await runtime.emit_session_start("startup")

    await invoke("lite")

    assert await invoke("status") == "Ponytail: current lite • default full"


@pytest.mark.anyio
async def test_default_persists_atomically_preserving_keys(tmp_path) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"quietStartup": True, "defaultMode": "lite"}), encoding="utf-8")
    runtime = load_runtime(tmp_path, setup)
    invoke = make_invoker(runtime)

    message = await invoke("default ultra")

    assert message == "Default Ponytail mode set to ultra."
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "quietStartup": True,
        "defaultMode": "ultra",
    }


@pytest.mark.anyio
async def test_persisted_default_honors_env_precedence_message(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PONYTAIL_DEFAULT_MODE", "off")
    runtime = load_runtime(tmp_path, setup)
    invoke = make_invoker(runtime)

    message = await invoke("default lite")

    assert message == "Saved default lite, but env override keeps default at off."
    assert json.loads(config_path().read_text(encoding="utf-8")) == {"defaultMode": "lite"}


@pytest.mark.parametrize("args", ["banana", "default", "default review"])
@pytest.mark.anyio
async def test_invalid_input_leaves_state_and_config_unchanged(tmp_path, args) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"defaultMode": "lite", "keep": 1}), encoding="utf-8")
    runtime = load_runtime(tmp_path, setup)
    invoke = make_invoker(runtime)
    await runtime.emit_session_start("startup")

    message = await invoke(args)

    assert message.startswith("Unknown or unsupported /ponytail mode.")
    assert json.loads(path.read_text(encoding="utf-8")) == {"defaultMode": "lite", "keep": 1}


@pytest.mark.anyio
async def test_invalid_mode_command_keeps_active_mode(tmp_path) -> None:
    runtime = load_runtime(tmp_path, setup)
    invoke = make_invoker(runtime)
    await runtime.emit_session_start("startup")

    await invoke("ultra")
    await invoke("banana")

    result = await runtime.run_before_agent_start_hooks(prompt="x", system_prompt="")
    assert result == instructions_for_mode("ultra")


@pytest.mark.anyio
async def test_write_failure_is_contained_without_changing_state(tmp_path, monkeypatch) -> None:
    from tau_ponytail import extension as extension_module

    runtime = load_runtime(tmp_path, setup)
    invoke = make_invoker(runtime)
    await runtime.emit_session_start("startup")
    await invoke("lite")

    def broken_write(mode: object) -> Path:
        raise OSError("disk on fire")

    monkeypatch.setattr(extension_module, "write_default_mode", broken_write)

    message = await invoke("default ultra")

    assert message == "Failed to save default mode: disk on fire"
    result = await runtime.run_before_agent_start_hooks(prompt="x", system_prompt="")
    assert result == instructions_for_mode("lite")
