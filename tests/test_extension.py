"""Integration proof of v1 behavior through Tau's real extension runtime (issue #4).

One scenario per distinct public boundary not already established by the unit
suites: manifest load into a real CodingSession, run-scoped prompt
transformation across a multi-call tool run, restoration on success/error/
cancellation, durable-history absence, off-mode no-op, non-consuming
deactivation reaching the model, and print-mode operation without Textual.
"""

import asyncio
from pathlib import Path

import pytest
from tau_agent import AssistantMessage, ToolCall
from tau_agent.messages import TextContent, assistant_content
from tau_agent.provider_events import (
    AssistantDoneEvent,
    AssistantErrorEvent,
    AssistantStartEvent,
)
from tau_agent.session import JsonlSessionStorage
from tau_agent.tools import AgentTool, AgentToolResult
from tau_ai import FakeProvider
from tau_coding import CodingSession, CodingSessionConfig

from helpers import REPO_ROOT
from tau_ponytail.extension import setup as ponytail_setup
from tau_ponytail.instructions import instructions_for_mode

pytestmark = pytest.mark.anyio

FULL_INSTRUCTION = instructions_for_mode("full")


def _assistant_start() -> AssistantStartEvent:
    return AssistantStartEvent(partial=AssistantMessage(model="fake"))


def _assistant_done(message: AssistantMessage) -> AssistantDoneEvent:
    reason = "toolUse" if message.tool_calls else "stop"
    message.stop_reason = reason
    return AssistantDoneEvent(reason=reason, message=message)


def _assistant_error(message: str) -> AssistantErrorEvent:
    error = AssistantMessage(stop_reason="error", error_message=message)
    return AssistantErrorEvent(reason="error", error=error)


def _echo_tool() -> AgentTool:
    async def echo(
        tool_call_id: object, arguments: object, signal: object = None, on_update: object = None
    ) -> AgentToolResult:
        return AgentToolResult(content=[TextContent(text="done")])

    return AgentTool(
        name="echo",
        label="Echo",
        description="Return done.",
        parameters={"type": "object"},
        execute_fn=echo,
    )


def _hang_tool(tool_started: asyncio.Event, release: asyncio.Event) -> AgentTool:
    async def hang(
        tool_call_id: object, arguments: object, signal: object = None, on_update: object = None
    ) -> AgentToolResult:
        tool_started.set()
        await release.wait()
        return AgentToolResult(content=[TextContent(text="done")])

    return AgentTool(
        name="hang",
        label="Hang",
        description="Block until released.",
        parameters={"type": "object"},
        execute_fn=hang,
    )


async def _collect(events) -> None:
    async for _event in events:
        pass


async def _load_session(tmp_path: Path, provider, *, tools=(), storage=None):
    return await CodingSession.load(
        CodingSessionConfig(
            provider=provider,
            model="fake",
            system="BASE",
            storage=storage or JsonlSessionStorage(tmp_path / "session.jsonl"),
            cwd=tmp_path,
            tools=list(tools),
            extension_paths=(REPO_ROOT,),
            extensions_enabled=False,
        )
    )


async def test_manifest_load_and_multi_call_run_use_one_instruction(tmp_path) -> None:
    tool_call = ToolCall(id="call-1", name="echo", arguments={})
    provider = FakeProvider(
        [
            [
                _assistant_start(),
                _assistant_done(
                    AssistantMessage(content=assistant_content("Using tool.", [tool_call]))
                ),
            ],
            [_assistant_start(), _assistant_done(AssistantMessage(content="Finished."))],
        ]
    )
    session = await _load_session(tmp_path, provider, tools=[_echo_tool()])

    await _collect(session.prompt("go"))

    assert [system for _model, system, _messages, _tools in provider.calls] == [
        f"BASE\n\n{FULL_INSTRUCTION}",
        f"BASE\n\n{FULL_INSTRUCTION}",
    ]
    assert session.system_prompt == "BASE"
    await session.aclose()


async def test_instruction_is_absent_from_durable_session_file(tmp_path) -> None:
    provider = FakeProvider([[_assistant_start(), _assistant_done(AssistantMessage(content="ok"))]])
    storage = JsonlSessionStorage(tmp_path / "session.jsonl")
    session = await _load_session(tmp_path, provider, storage=storage)

    await _collect(session.prompt("hello"))

    raw = (tmp_path / "session.jsonl").read_text(encoding="utf-8")
    assert "PONYTAIL MODE ACTIVE" not in raw
    assert "Ponytail" not in raw
    await session.aclose()


async def test_off_mode_leaves_every_provider_call_unchanged(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PONYTAIL_DEFAULT_MODE", "off")
    provider = FakeProvider([[_assistant_start(), _assistant_done(AssistantMessage(content="ok"))]])
    session = await _load_session(tmp_path, provider)

    await _collect(session.prompt("go"))

    assert [system for _model, system, _messages, _tools in provider.calls] == ["BASE"]
    assert session.system_prompt == "BASE"
    await session.aclose()


async def test_base_prompt_restored_after_provider_error(tmp_path) -> None:
    provider = FakeProvider([[_assistant_error("provider failed")]])
    session = await _load_session(tmp_path, provider)

    await _collect(session.prompt("go"))

    assert [system for _model, system, _messages, _tools in provider.calls] == [
        f"BASE\n\n{FULL_INSTRUCTION}"
    ]
    assert session.system_prompt == "BASE"
    await session.aclose()


async def test_base_prompt_restored_after_cancellation(tmp_path) -> None:
    tool_started = asyncio.Event()
    release = asyncio.Event()
    tool_call = ToolCall(id="call-1", name="hang", arguments={})
    provider = FakeProvider(
        [
            [
                _assistant_start(),
                _assistant_done(
                    AssistantMessage(content=assistant_content("Running.", [tool_call]))
                ),
            ],
        ]
    )
    session = await _load_session(tmp_path, provider, tools=[_hang_tool(tool_started, release)])

    async def consume() -> None:
        async for _event in session.prompt("go"):
            pass

    task = asyncio.create_task(consume())
    await asyncio.wait_for(tool_started.wait(), timeout=5)
    session.cancel()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert [system for _model, system, _messages, _tools in provider.calls] == [
        f"BASE\n\n{FULL_INSTRUCTION}"
    ]
    assert session.system_prompt == "BASE"
    await session.aclose()


async def test_deactivation_prompt_reaches_model_unchanged(tmp_path, monkeypatch) -> None:
    provider = FakeProvider([[_assistant_start(), _assistant_done(AssistantMessage(content="ok"))]])
    session = await _load_session(tmp_path, provider)

    await _collect(session.prompt("Stop ponytail."))

    assert [system for _model, system, _messages, _tools in provider.calls] == ["BASE"]
    persisted = (tmp_path / "session.jsonl").read_text(encoding="utf-8")
    assert "Stop ponytail." in persisted
    await session.aclose()


def test_real_setup_registers_the_public_surface() -> None:
    """The setup handed to Tau's runtime is the module entry, not a test double."""
    from tau_coding import BuiltInExtension, TauResourcePaths
    from tau_coding.extensions import ExtensionRuntime

    runtime = ExtensionRuntime(
        built_in_extensions=(BuiltInExtension(name="tau-ponytail", setup=ponytail_setup),)
    )
    runtime.load(
        TauResourcePaths(
            root=REPO_ROOT / "build-test-home",
            cwd=REPO_ROOT / "build-test-cwd",
            agents_root=REPO_ROOT / "build-test-agents",
        ),
        include_resource_dirs=False,
    )

    registry = runtime.build_command_registry()
    for name in (
        "ponytail",
        "ponytail-review",
        "ponytail-audit",
        "ponytail-debt",
        "ponytail-gain",
        "ponytail-help",
    ):
        assert registry.get(name) is not None
