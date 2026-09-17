"""Focused tests for instruction composition (spec: Runtime modes, Run guidance)."""

from pathlib import Path

from tau_ponytail.instructions import filter_skill_body_for_mode, instructions_for_mode

MODES = ("lite", "full", "ultra")
SECTIONS = (
    "# Ponytail",
    "## Persistence",
    "## The ladder",
    "## Rules",
    "## Output",
    "## Intensity",
    "## When NOT to be lazy",
    "## Boundaries",
)


def test_header_names_the_active_level() -> None:
    for mode in MODES:
        assert instructions_for_mode(mode).startswith(f"PONYTAIL MODE ACTIVE — level: {mode}\n\n")


def test_common_body_complete_with_only_active_intensity_row_and_example() -> None:
    for mode in MODES:
        text = instructions_for_mode(mode)
        for section in SECTIONS:
            assert section in text
        assert "1. **Does this need to exist at all?**" in text
        assert "7. **Only then:**" in text
        assert "| Level | What change |" in text
        assert f"| **{mode}** |" in text
        assert f'- {mode}: "' in text
        for other in MODES:
            if other != mode:
                assert f"| **{other}** |" not in text
                assert f'- {other}: "' not in text


def test_instruction_contains_exactly_one_active_marker() -> None:
    text = instructions_for_mode("ultra")
    assert text.count("PONYTAIL MODE ACTIVE") == 1


def test_unsupported_mode_falls_back_to_full() -> None:
    assert instructions_for_mode("banana") == instructions_for_mode("full")


def test_filter_keeps_non_mode_labeled_lines_verbatim() -> None:
    body = 'plain rule\n- Ship it: "not a mode label"\n| **Level** | header-ish\n| **lite** | row'
    filtered = filter_skill_body_for_mode(body, "ultra")
    assert filtered == 'plain rule\n- Ship it: "not a mode label"\n| **Level** | header-ish'


def test_upstream_attribution_is_retained() -> None:
    import tau_ponytail.instructions as instructions_module

    doc = instructions_module.__doc__ or ""
    assert "DietrichGebert" in doc
    assert "4.10.0" in doc
    assert "MIT" in doc
    license_text = (Path(instructions_module.__file__ or ".").parents[2] / "LICENSE").read_text(
        encoding="utf-8"
    )
    assert "Copyright (c) 2026 DietrichGebert" in license_text
