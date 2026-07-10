# Project Structure

Reforger Deployer is intentionally dependency-light. The command-line application, configuration handling, deployment code, and optional integrations are separated by responsibility.

```text
reforger                         Linux/macOS launcher
reforger.py                      Windows launcher
ardr.py                          Backward-compatible launcher
deployer.json                    Global settings (created at setup)
instances/                       One JSON file per server
ardr/
  cli/                           Argument parsing, shortcuts, completion
  commands/                      Command handlers and dispatch registry
  config/                        Config loading, discovery, validation, import/export
  core/                          Paths, ports, terminal output, platform helpers
  deploy/                        Backup and first-deploy workflow
  integrations/discord/          Discord status integration
  platform/                      Services, firewall, Linux setup, doctor, LinuxGSM
  server/                        Rendering, processes, query, status, resources, mods
  ui/                            Home screen, menus, hub, prompts, guided editor
  web/                           Optional authenticated dashboard
scripts/                         Linux and Windows bootstrap scripts
docs/                            User, operator, and development documentation
tests/                           Automated tests
```

## Main Areas

| Area | Owns |
| --- | --- |
| `ardr/cli` | Command parsing, server-first shortcuts, shell completion. |
| `ardr/config` | Configuration discovery, JSON persistence, port normalization, import/export. |
| `ardr/server` | Reforger render files, SteamCMD operations, process lifecycle, logs, query, resource display. |
| `ardr/ui` | Beginner-first terminal workflows and guided editing. |
| `ardr/platform` | Linux systemd, Windows tasks, local firewall, host diagnostics. |
| `ardr/deploy` | Backups and the first-launch orchestration. |
| `ardr/web` | Optional authenticated HTMX dashboard. |

## Generated Data

Generated server installs, profiles, logs, backups, SteamCMD data, PID files, auth files, and secrets should not be committed. Run `reforger where` to see the exact active locations on a machine.

## Command Design

The public command surface supports both forms:

```bash
reforger start testingserver
reforger testingserver on
```

The server-first form is intended for everyday use. New commands should preserve the traditional form when practical and provide a clear, non-destructive default.
