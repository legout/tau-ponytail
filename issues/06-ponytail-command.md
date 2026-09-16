# Issue 06: `/ponytail` command

**Plan phase:** 3 — Tau extension behavior (design decision 4)
**Depends on:** #05 extension core
**Size:** M

## Context

`/ponytail` is a thin adapter over the mode model and config layer. Tau
commands are registered via the public API and run synchronously; UI feedback
goes through `tau.notify` (works in TUI and print mode — no Textual coupling,
per design decision 6). Because Tau may handle slash commands before the
normal prompt path, mode changes happen here, not in the `input` hook (#07).

Behavior (`arg` is the raw remainder after the command name):

| input                  | effect                                                     |
|------------------------|------------------------------------------------------------|
| *(none)*               | set active mode to the resolved default; if the default is `off`, enable `full` instead (matches upstream) |
| `lite` / `full` / `ultra` / `off` | set the active mode                          |
| `status`               | report current active mode and configured default          |
| `default <mode>`       | persist `<mode>` as the config default (#03 write)         |
| anything else          | short usage/error message; **no state change**             |

## Tasks

- Implement the command handler in `src/tau_ponytail/commands.py`, receiving
  the per-generation state object from #05.
- Register the command in `setup(tau)` as `/ponytail`.
- Use `parse_mode` (#02) for argument parsing; never hand-roll string checks.
- Notifications: mode changes notify the new active mode; `status` reports
  current + configured default; invalid input returns a concise usage line.
- `default <mode>`:
  - `default` alone or with an invalid mode → usage message, no write;
  - success → write via `config.write_default_mode`, notify, and do not
    change the active mode (default applies on next reset/startup — verify
    against upstream behavior and record the choice);
  - write failure (permissions, disk) → warning notification with the path;
    never raise into Tau's command loop.
- Keep the handler pure with respect to inputs: no reading of prompt text.

## Acceptance criteria

- [ ] All five rows of the table above behave as specified, including the
      `off`-default → `full` special case for bare `/ponytail`.
- [ ] `status` output names both the active mode and the configured default.
- [ ] `default lite` persists only `defaultMode`, preserving unrelated keys;
      `PONYTAIL_DEFAULT_MODE=ultra` still wins on the next resolution.
- [ ] Invalid input (`/ponytail banana`, `/ponytail default`) leaves both
      active mode and config untouched and returns a usage message.
- [ ] A simulated write failure surfaces as a warning, not an exception.

## Out of scope

- Skill shortcuts (`/ponytail-review` etc.) — #09.
- Natural-language deactivation — #07.
