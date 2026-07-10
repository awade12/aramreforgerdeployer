# Reforger Deployer

Reforger Deployer is a beginner-friendly command-line manager for one or more **Arma Reforger dedicated servers**. It installs, configures, starts, updates, monitors, backs up, and shares servers from Linux or Windows without requiring you to remember a pile of file paths.

The normal command is `reforger`.

## Start Here

### Linux / VPS

```bash
# From a clone or downloaded copy of this repository:
cd /path/to/aramreforgerdeployer
chmod +x scripts/install-linux.sh
./scripts/install-linux.sh
```

The installer creates the `reforger` command and creates a starter configuration when needed.

Then run:

```bash
reforger setup
reforger reforger-1
```

`reforger setup` asks only the important first-time questions. `reforger reforger-1` opens that server’s interactive control room.

### Windows

Open PowerShell as Administrator in the project folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install-windows.ps1
```

Then use the same `reforger setup` and `reforger <server>` workflow.

## Daily Use

Put the server name first and say what you want to do:

```bash
reforger testingserver             # interactive server control room
reforger testingserver on          # start
reforger testingserver off         # stop safely
reforger testingserver logs        # latest logs
reforger testingserver health      # readiness checks and fixes
reforger testingserver resources   # CPU, RAM, disk, players, ping
reforger testingserver invite      # print a shareable player invite
reforger testingserver backup      # create a backup
```

The traditional command-first form also works:

```bash
reforger start testingserver
reforger logs testingserver
reforger update testingserver --yes
```

Run `reforger` with no command for a quick home screen, or `reforger menu` for a guided multi-server menu.

## No More Folder Hunting

You can run `reforger` from any SSH directory. It automatically finds `deployer.json` beside the installed command, in the current directory or a parent directory, and in `~/aramreforgerdeployer`.

```bash
reforger where
reforger testingserver where
```

`where` shows the exact config, project, install, profile/log, generated-file, and backup paths currently in use. To manage a separate setup explicitly, use:

```bash
reforger --config /path/to/deployer.json testingserver
```

## Edit Settings Without Raw JSON

```bash
reforger testingserver edit
```

The guided editor separates settings into small menus:

- Server name and browser visibility
- Player slots, join password, admin password, and admin Steam IDs
- Scenario, FPS limit, third-person, and BattlEye
- Public address and game/query ports
- Mods

Admin IDs have their own add/remove/replace list manager. Every change is previewed before it is saved. For advanced editing only:

```bash
reforger testingserver edit --raw
```

This opens the instance JSON in [Micro](https://micro-editor.github.io/). If Micro is missing, Reforger Deployer explains the install options and asks before invoking a package manager.

## First Deployment

Preview the work first:

```bash
reforger launch testingserver
```

On Linux, apply the complete first deployment with the required privileges:

```bash
sudo reforger launch testingserver --apply
```

The workflow renders config files, creates a backup, installs or updates the server through SteamCMD, prepares firewall commands, installs/enables a systemd service, starts it, and prints the next best step.

See [Deployment](docs/DEPLOYMENT.md) for Linux, Windows, services, and VPS guidance.

## Safety Built In

- Updates and Workshop changes create a backup automatically.
- Stop, restart, update, restore, and firewall-apply commands ask before changing anything.
- Use `--yes` only in intentional automation.
- `reforger doctor` ends with a readiness scorecard and copy-paste fixes.
- `reforger check` validates configuration, ports, disk, SteamCMD, server files, and local bind availability.

## Useful Commands

```bash
reforger where                       # resolve every path in use
reforger testingserver edit          # guided settings editor
reforger testingserver resources --watch 2
reforger testingserver mod add <workshop-url>
reforger testingserver export server.json
reforger import server.json --as copied-server
reforger backup list
reforger backup restore              # choose a backup interactively
reforger completion bash             # print Bash completion setup
reforger completion zsh              # print Zsh completion setup
```

For the complete command reference, see [Commands](docs/COMMANDS.md). For day-to-day tasks, see [Operations](docs/OPERATIONS.md).

## Documentation

- [Deployment guide](docs/DEPLOYMENT.md)
- [Configuration guide](docs/CONFIGURATION.md)
- [Operations guide](docs/OPERATIONS.md)
- [Command reference](docs/COMMANDS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Project structure](docs/STRUCTURE.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## Official References

- Arma Reforger dedicated server: [Bohemia Interactive community wiki](https://community.bistudio.com/wiki/Arma_Reforger:Server_Config)
- Stable dedicated server app: [SteamDB app 1874900](https://steamdb.info/app/1874900/)
- SteamCMD: [Valve Developer Community](https://developer.valvesoftware.com/wiki/SteamCMD)

## License

Add a project license before distributing modified copies. Until then, treat the repository as source available only to its owner and collaborators.
