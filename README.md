# Arma Reforger Server Deployer

A small, dependency-free deployment toolkit for running one or many Arma Reforger dedicated servers on Linux VPS hosts, bare-metal Linux machines, or Windows servers.

It uses the official dedicated-server Steam app IDs:

- Stable server: `1874900` ([SteamDB](https://steamdb.info/app/1874900/))
- Arma Reforger server config wiki: <https://community.bistudio.com/wiki/Arma_Reforger:Server_Config>
- SteamCMD documentation: <https://developer.valvesoftware.com/wiki/SteamCMD>

## What This Gives You

- One global config plus one editable `instances/*.json` file per server.
- Automatic safe port assignment for new or repaired instances.
- Preflight `doctor` checks for Python, SteamCMD, disk, ports, firewall notes, config, and server files.
- Non-root Linux user setup for safer VPS hosting.
- Guided config wizard for adding/editing servers.
- Interactive operator menu for common actions.
- SteamCMD install/update for stable or experimental dedicated servers.
- Per-instance server config and start-script generation.
- Lifecycle commands: start, stop, restart, pause, resume, update, logs, debug.
- Optional Linux `systemd` service files for auto-start and crash restart.
- Service controls, firewall automation, backups, and mod helpers.
- Authenticated HTMX/Tailwind web dashboard.
- Discord status embed that updates one message in a channel.
- Optional Windows startup Scheduled Tasks.
- LinuxGSM helper scripts and guidance.
- Firewall command suggestions for required UDP ports.
- BattlEye RCon helper that appends settings without overwriting existing BattlEye config.

## Quick Start: Linux VPS

```bash
cd aramreforgerdeployer
chmod +x scripts/install-linux.sh
./scripts/install-linux.sh
```

The installer adds a `reforger` command to your PATH.

Then run:

```bash
reforger setup
reforger launch reforger-1
sudo reforger launch reforger-1 --apply
reforger tail reforger-1
```

```bash
reforger menu
```

After the service is installed, `reforger start`, `reforger stop`, `reforger restart`, and `reforger tail` automatically use systemd when available.

## Quick Start: Windows

Open PowerShell as Administrator:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install-windows.ps1
```

The installer adds a `reforger` command to your user PATH. Open a new terminal if PowerShell does not find it immediately.

Then run:

```powershell
reforger setup
reforger install
reforger start reforger-1
```

```powershell
reforger windows-task install
```

## Configure Many Servers

Run this once to create a starter config:

```bash
reforger init
```

Add or edit servers with prompts:

```bash
reforger configure
reforger configure reforger-1
```

Each server is saved as its own file in `instances/`. Reforger can assign safe ports automatically.

Detailed config examples are in [docs/CONFIGURATION.md](/Users/awade/Documents/aramreforgerdeployer/docs/CONFIGURATION.md).

## Ports

```bash
reforger ports
reforger ports --fix
```

## Common Commands

The easiest way to work is server-first: put the server name first, then say what you want.

You can run `reforger` from any directory. It automatically finds the deployer config beside the installed command (or use `--config /path/to/deployer.json` when managing a different server).

Run `reforger where` at any time to see the exact config, project, install, log, generated-file, and backup locations in use. Use `reforger testingserver where` for one server.

```bash
reforger testingserver              # show a friendly summary and the next best step
reforger testingserver on           # start it (also: start)
reforger testingserver off          # stop it (also: stop)
reforger testingserver logs         # show logs
reforger testingserver health       # run readiness checks
reforger testingserver backup       # create a backup
reforger testingserver mod add <workshop-url>  # add a Workshop scenario and its dependencies
reforger testingserver resources    # CPU, RAM, disk, and player dashboard
reforger testingserver invite       # print a shareable player invite
reforger testingserver export server.json  # save a portable server config
reforger import server.json --as another-server  # load it on another host
```

The original command-first style continues to work too:

```bash
reforger setup                       # guided first-time setup, safe ports, checks
reforger launch reforger-1           # preview first deploy
sudo reforger launch reforger-1 --apply
reforger default reforger-1          # make instance optional for daily commands
reforger status
reforger info
reforger query
reforger start
reforger stop
reforger restart
reforger tail
reforger update
reforger backup create
reforger mods list
reforger check                       # validate, ports, doctor
reforger fix                         # fix safe ports, validate, doctor
reforger open --host 127.0.0.1 --port 8080
reforger discord configure
reforger discord start

# Advanced commands are still available:
reforger init
reforger configure
reforger menu
reforger validate
reforger ports --fix
reforger doctor
reforger linux-user
reforger firewall apply --dry-run
sudo reforger firewall apply
reforger render
reforger install
reforger install reforger-1
sudo reforger systemd install --instance reforger-1
sudo reforger service enable --instance reforger-1
sudo reforger service start --instance reforger-1
reforger deploy reforger-1
reforger update reforger-1 --no-restart
reforger pause reforger-1
reforger resume reforger-1
reforger logs reforger-1 --follow
reforger debug reforger-1
reforger service restart --instance reforger-1
reforger service logs --instance reforger-1 --follow
reforger mods add reforger-1 --id MOD_ID --name "Mod Name"
reforger mods list reforger-1
reforger backup create reforger-1
reforger ports
reforger linuxgsm
reforger battleye --instance reforger-1 --rcon-port 5678 --rcon-password "change-me"
```

## Quality-of-Life Features

`reforger testingserver` opens a small interactive control room for that server. Updates create a backup before making changes, and stopping, restarting, updating, restoring, or applying firewall rules asks for confirmation. Use `--yes` only when you intentionally need to automate one of those actions.

The latest log view highlights errors and warnings. Run `reforger doctor` or `reforger testingserver health` for a readiness scorecard with copy-paste fixes.

`reforger testingserver resources --watch 2` refreshes the terminal dashboard every two seconds. It shows CPU, RAM, disk use, player count, ping, and uptime when available. Tick/FPS is shown honestly as unavailable until Reforger exposes it through its server query.

When using `reforger configure`, every pending setting is shown in a clear **Config preview** before anything is saved. Choose `n` to discard it.

### Tab Completion

Enable completion once in your current shell:

```bash
eval "$(reforger completion bash)"  # Bash
eval "$(reforger completion zsh)"   # Zsh
```

Add the matching line to `~/.bashrc` or `~/.zshrc` to keep it enabled. Completion includes server names and common server-first actions.

`debug` runs the server in the foreground so you can see output directly. Use `logs --systemd --follow` when the instance is running under a generated Linux service.
For VPS hosting, install the service with `launch --apply`; daily `start`, `stop`, `restart`, and `tail` will use it automatically.
More operation commands are in [docs/OPERATIONS.md](/Users/awade/Documents/aramreforgerdeployer/docs/OPERATIONS.md).

## Linux Service Workflow

For safer VPS hosting, prepare a non-root server user after cloning the repo:

```bash
sudo reforger linux-user --user armar --target /opt/ardr --apply
sudo -iu armar
cd /opt/ardr
```

The default `linux-user` command is a dry run unless `--apply` is passed.

Install and manage services:

```bash
sudo reforger systemd install
sudo systemctl enable --now ardr-reforger-1.service
sudo reforger service restart --instance reforger-1
reforger service logs --instance reforger-1 --follow
```

## LinuxGSM Workflow

LinuxGSM is a strong option on Linux when you want a battle-tested wrapper with monitor, console, backup, debug, update, and cron support.

```bash
reforger linuxgsm
```

More detail is in [docs/DEPLOYMENT.md](/Users/awade/Documents/aramreforgerdeployer/docs/DEPLOYMENT.md).

## Windows Startup Workflow

Install startup tasks:

```powershell
reforger windows-task install
```

Manage in Task Scheduler, or use `schtasks`:

```powershell
schtasks /Run /TN "Reforger reforger-1"
schtasks /End /TN "Reforger reforger-1"
```

## Notes

- `-maxFPS` defaults to `60`; Reforger servers can consume excessive CPU without it.
- The deployer uses `-config` and `-profile` for each instance.
- BattlEye RCon settings are appended to `BattlEye/BEServer_x64.cfg`; do not erase the existing generated content in that file.
- `pause` and `resume` suspend the tracked process. Prefer `stop` or `restart` for normal maintenance.
