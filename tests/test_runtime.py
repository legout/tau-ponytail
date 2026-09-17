"""Lifecycle and run-guidance behavior through Tau's real extension runtime."""

import pytest

from helpers import REPO_ROOT, RecordingUiBridge, load_runtime
from tau_ponytail.extension import setup
from tau_ponytail.instructions import instructions_for_mode

pytestmark = pytest.mark.anyio


async def test_session_start_reports_loaded_default_mode(tmp_path) -> None:
    ui = RecordingUiBridge()
    runtime = load_runtime(tmp_path, setup, ui=ui)

    await runtime.emit_session_start("startup")

    assert ui.notifications == [("Ponytail loaded: full", "info")]


async def test_quiet_startup_env_suppresses_only_the_notification(tmp_path, monkeypatch) -> None:
    ui = RecordingUiBridge()
    runtime = load_runtime(tmp_path, setup, ui=ui)
    monkeypatch.setenv("PONYTAIL_QUIET_STARTUP", "1")

    await runtime.emit_session_start("startup")

    assert ui.notifications == []


async def test_quiet_startup_config_suppresses_the_notification(tmp_path, monkeypatch) -> None:
    import json

    from tau_ponytail.config import config_path

    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"quietStartup": True}), encoding="utf-8")
    ui = RecordingUiBridge()
    runtime = load_runtime(tmp_path, setup, ui=ui)

    await runtime.emit_session_start("startup")

    assert ui.notifications == []


async def test_session_start_resets_active_mode_to_resolved_default(tmp_path, monkeypatch) -> None:
    ui = RecordingUiBridge()
    runtime = load_runtime(tmp_path, setup, ui=ui)

    monkeypatch.setenv("PONYTAIL_DEFAULT_MODE", "lite")
    await runtime.emit_session_start("startup")
    assert ui.notifications == [("Ponytail loaded: lite", "info")]

    monkeypatch.setenv("PONYTAIL_DEFAULT_MODE", "ultra")
    await runtime.emit_session_start("new")
    assert ui.notifications[-1] == ("Ponytail loaded: ultra", "info")


async def test_invalid_config_warns_but_does_not_crash(tmp_path) -> None:
    from tau_ponytail.config import config_path

    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{broken", encoding="utf-8")
    ui = RecordingUiBridge()
    runtime = load_runtime(tmp_path, setup, ui=ui)

    await runtime.emit_session_start("startup")

    assert len(ui.notifications) == 2
    assert "Could not parse" in ui.notifications[0][0]
    assert ui.notifications[0][1] == "warning"
    assert ui.notifications[1] == ("Ponytail loaded: full", "info")

    result = await runtime.run_before_agent_start_hooks(prompt="go", system_prompt="BASE")
    assert result == f"BASE\n\n{instructions_for_mode('full')}"


async def test_before_agent_start_appends_exactly_one_instruction(tmp_path) -> None:
    runtime = load_runtime(tmp_path, setup)
    await runtime.emit_session_start("startup")

    result = await runtime.run_before_agent_start_hooks(prompt="hi", system_prompt="You are Tau.")

    instruction = instructions_for_mode("full")
    assert result == f"You are Tau.\n\n{instruction}"
    assert result.count("PONYTAIL MODE ACTIVE") == 1


async def test_before_agent_start_handles_empty_base_prompt(tmp_path) -> None:
    runtime = load_runtime(tmp_path, setup)
    await runtime.emit_session_start("startup")

    result = await runtime.run_before_agent_start_hooks(prompt="hi", system_prompt="")

    assert result == instructions_for_mode("full")


async def test_off_mode_returns_no_replacement(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PONYTAIL_DEFAULT_MODE", "off")
    runtime = load_runtime(tmp_path, setup)
    await runtime.emit_session_start("startup")

    result = await runtime.run_before_agent_start_hooks(prompt="hi", system_prompt="You are Tau.")

    assert result == "You are Tau."


async def test_active_state_is_generation_local(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PONYTAIL_DEFAULT_MODE", "lite")
    runtime_a = load_runtime(tmp_path, setup)
    await runtime_a.emit_session_start("startup")

    monkeypatch.setenv("PONYTAIL_DEFAULT_MODE", "ultra")
    runtime_b = load_runtime(tmp_path, setup)
    await runtime_b.emit_session_start("startup")

    result_a = await runtime_a.run_before_agent_start_hooks(prompt="x", system_prompt="")
    result_b = await runtime_b.run_before_agent_start_hooks(prompt="x", system_prompt="")
    assert result_a == instructions_for_mode("lite")
    assert result_b == instructions_for_mode("ultra")


def test_manifest_discovery_loads_clean_checkout(tmp_path) -> None:
    from tau_coding import TauResourcePaths
    from tau_coding.extensions import ExtensionRuntime

    runtime = ExtensionRuntime()
    runtime.load(
        TauResourcePaths(
            root=tmp_path / "tau-home",
            cwd=tmp_path / "project",
            agents_root=tmp_path / "agents",
        ),
        extra_paths=(REPO_ROOT,),
        include_resource_dirs=False,
    )

    assert runtime.extension_names == ("tau_ponytail",)
    assert not [d for d in runtime.diagnostics if d.severity == "error"]
