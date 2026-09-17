"""Deterministic fakes for driving Tau's real extension runtime."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from tau_coding import BuiltInExtension, TauResourcePaths
from tau_coding.extensions import ExtensionAPI, ExtensionRuntime

if TYPE_CHECKING:
    from tau_coding.extensions import UiBridge

EXTENSION_NAME = "tau-ponytail"
REPO_ROOT = Path(__file__).resolve().parent.parent


class RecordingUiBridge:
    """Records notifications; satisfies the UiBridge surface this suite touches."""

    def __init__(self) -> None:
        self.has_ui = True
        self.notifications: list[tuple[str, str]] = []

    def notify(self, message: str, level: str = "info") -> None:
        self.notifications.append((message, level))


class RecordingSession:
    """Minimal deterministic BoundSession fake for the real runtime."""

    def __init__(self, tmp_path: Path, *, running: bool = False) -> None:
        self.cwd = tmp_path
        self.model = "fake"
        self.provider_name = "fake"
        self.inference_provider: str | None = None
        self.inference_provider_mode = "automatic"
        self.session_id = "session-1"
        self.session_name: str | None = "Test session"
        self.thinking_level = "medium"
        self.system_prompt = "You are Tau."
        self.is_running = running
        self.messages: tuple[object, ...] = ()
        self.steered: list[str] = []
        self.followed_up: list[str] = []
        self.custom_entries: list[tuple[str, dict[str, object]]] = []
        self.turn_requests: list[str] = []

    def queue_steering_message(self, content: str, **_kwargs: object) -> None:
        self.steered.append(content)

    def queue_follow_up_message(self, content: str, **_kwargs: object) -> None:
        self.followed_up.append(content)

    async def append_custom_entry(self, namespace: str, data: dict[str, object]) -> None:
        self.custom_entries.append((namespace, data))

    async def set_label(self, target_id: str, label: str | None) -> object:
        return (target_id, label)

    def set_inference_provider(self, route: str | None) -> str:
        self.inference_provider = route
        return route or "automatic"


def load_runtime(
    tmp_path: Path,
    setup: Callable[[ExtensionAPI], None],
    *,
    ui: RecordingUiBridge | None = None,
) -> ExtensionRuntime:
    """Load ``setup`` into a real ExtensionRuntime generation."""
    from typing import cast

    runtime = ExtensionRuntime(
        # The minimal fake intentionally implements only the notify seam.
        ui=cast("UiBridge | None", ui),
        built_in_extensions=(BuiltInExtension(name=EXTENSION_NAME, setup=setup),),
    )
    runtime.load(
        TauResourcePaths(
            root=tmp_path / "tau-home",
            cwd=tmp_path / "project",
            agents_root=tmp_path / "agents",
        ),
        include_resource_dirs=False,
    )
    return runtime
