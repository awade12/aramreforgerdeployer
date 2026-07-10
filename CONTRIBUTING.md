# Contributing to Reforger Deployer

Thanks for helping make Reforger Deployer easier to run, safer to operate, and clearer for beginners.

## Ground Rules

- Keep the CLI dependency-light and cross-platform where practical.
- Preserve existing command forms when adding friendlier shortcuts.
- Prefer safe defaults: preview, confirm, back up, then change.
- Never print passwords, Discord bot tokens, or other secrets in normal output.
- Write copy-pasteable messages. Operators often use the tool over SSH under pressure.

## Local Setup

Use Python 3.10 or newer.

```bash
git clone <your-fork-or-repository-url>
cd aramreforgerdeployer
python3 -m unittest discover -s tests -v
```

You can inspect the current CLI locally without installing it:

```bash
python3 ardr.py --help
python3 ardr.py --config /path/to/deployer.json where
```

## Before You Change Code

1. Read the relevant user documentation in `README.md` and `docs/`.
2. Keep beginner workflows small and discoverable from `reforger`, `reforger <server>`, `where`, and `edit`.
3. Consider both direct commands and the interactive hub/menu.
4. Do not assume a working directory. Commands should respect automatic config discovery and `--config`.

## Testing

Run the complete suite before opening a pull request:

```bash
python3 -m compileall -q ardr tests
python3 -m unittest discover -s tests -v
```

For CLI changes, also manually check the help and a disposable configuration:

```bash
python3 ardr.py --help
python3 ardr.py --config /tmp/deployer.json
```

Do not run install, firewall-apply, service-install, or destructive restore commands against a real server while testing a change unless you explicitly intend to operate that server.

## Pull Requests

Keep each pull request focused. Include:

- What changed and why
- Commands or tests you ran
- Documentation updates for user-visible behavior
- Migration or compatibility notes, if relevant

For terminal UI changes, include a short before/after transcript when it helps reviewers understand the flow.

## Documentation Standard

Documentation is part of the feature. Update the relevant files when you change:

| Change | Update |
| --- | --- |
| First-run or daily workflow | `README.md` |
| CLI flags or commands | `docs/COMMANDS.md` |
| Config fields or guided editor behavior | `docs/CONFIGURATION.md` |
| Deployment/service behavior | `docs/DEPLOYMENT.md` |
| Backups, logs, mods, or integrations | `docs/OPERATIONS.md` |
| Common failure mode | `docs/TROUBLESHOOTING.md` |

## Security

Follow [SECURITY.md](SECURITY.md). Do not include real credentials, public server admin passwords, IP addresses, or backup archives in commits, issues, screenshots, or test fixtures.
