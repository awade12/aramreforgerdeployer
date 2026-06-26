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
reforger configure
reforger doctor
reforger install
sudo reforger systemd install --instance reforger-1
sudo reforger service enable --instance reforger-1
sudo reforger service start --instance reforger-1
reforger service logs --instance reforger-1 --follow
```

```bash
reforger menu
```

Use `reforger start --instance reforger-1` only for a quick manual smoke test before installing the service.

## Quick Start: Windows

Open PowerShell as Administrator:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install-windows.ps1
```

The installer adds a `reforger` command to your user PATH. Open a new terminal if PowerShell does not find it immediately.

Then run:

```powershell
reforger configure
reforger install
reforger start --instance reforger-1
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
reforger configure --instance reforger-1
```

Each server is saved as its own file in `instances/`. Reforger can assign safe ports automatically.

Detailed config examples are in [docs/CONFIGURATION.md](/Users/awade/Documents/aramreforgerdeployer/docs/CONFIGURATION.md).

## Ports

```bash
reforger ports
reforger ports --fix
```

## Common Commands

```bash
reforger init                         # create starter deployer.json
reforger configure                    # guided add/edit wizard
reforger menu                         # interactive operator menu
reforger web --host 127.0.0.1 --port 8080
reforger info --instance reforger-1   # one-view instance details
reforger query --instance reforger-1  # live server query
reforger validate                     # check config and port collisions
reforger ports --fix                  # auto-assign safe ports and save instance files
reforger doctor                       # preflight host/config checks
reforger linux-user                   # dry-run non-root Linux setup
reforger firewall apply --dry-run
sudo reforger firewall apply
reforger render                       # generate server JSON and start scripts
reforger install                      # install/update all instances with SteamCMD
reforger install --instance reforger-1
sudo reforger systemd install --instance reforger-1
sudo reforger service enable --instance reforger-1
sudo reforger service start --instance reforger-1
reforger deploy --instance reforger-1 # dry-run first deploy
reforger update                       # update and restart servers that were running
reforger update --instance reforger-1 --no-restart
reforger start --instance reforger-1  # manual smoke test only on VPS
reforger stop --instance reforger-1
reforger restart --instance reforger-1
reforger pause --instance reforger-1
reforger resume --instance reforger-1
reforger status
reforger logs --instance reforger-1 --follow
reforger debug --instance reforger-1
reforger service restart --instance reforger-1
reforger service logs --instance reforger-1 --follow
reforger mods add --instance reforger-1 --id MOD_ID --name "Mod Name"
reforger mods list --instance reforger-1
reforger backup create --instance reforger-1
reforger ports
reforger linuxgsm
reforger battleye --instance reforger-1 --rcon-port 5678 --rcon-password "change-me"
```

`debug` runs the server in the foreground so you can see output directly. Use `logs --systemd --follow` when the instance is running under a generated Linux service.
For VPS hosting, prefer `systemd install` plus `service start` over direct `start`.
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
