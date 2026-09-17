# Tau Ponytail

Tau Ponytail is a standalone Tau extension that applies Ponytail's minimal-code discipline without changing Tau core.

## Language

### Extension and guidance

**Tau extension**: The standalone integration that adds Ponytail behavior through Tau's public extension contract.
_Avoid_: Pi adapter, Tau-core plugin

**Ponytail instruction**: Behavioral guidance appended to one agent run's system prompt that tells the agent how strongly to prefer deletion, standard facilities, and the smallest safe change.
_Avoid_: user message, durable prompt message, policy text

**Shortcut command**: A direct command that queues one of Ponytail's companion capabilities, such as review, audit, debt, gain, or help.
_Avoid_: skill implementation, mode

### Modes and defaults

**Ponytail mode**: One of `off`, `lite`, `full`, or `ultra`, describing how strongly the extension applies minimal-code guidance.
_Avoid_: profile, setting

**Active mode**: The Ponytail mode currently governing requests in a running extension generation or session.
_Avoid_: configured default

**Configured default**: The mode selected for a new session after environment and configuration resolution.
_Avoid_: active mode

**Mode deactivation**: Turning Ponytail guidance off for the current runtime by selecting `off` or using an exact natural-language stop command.
_Avoid_: disabling the extension
