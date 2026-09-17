"""Focused tests for mode normalization (spec: Runtime modes)."""

import pytest

from tau_ponytail.modes import DEFAULT_MODE, RUNTIME_MODES, normalize_mode


def test_runtime_modes_are_exactly_the_four_levels() -> None:
    assert RUNTIME_MODES == ("off", "lite", "full", "ultra")
    assert DEFAULT_MODE == "full"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("full", "full"),
        (" LITE ", "lite"),
        ("Ultra", "ultra"),
        ("OFF", "off"),
        ("review", None),
        ("banana", None),
        ("", None),
        ("   ", None),
        (None, None),
        (1, None),
    ],
)
def test_normalize_mode_truth_table(value: object, expected: str | None) -> None:
    assert normalize_mode(value) == expected
