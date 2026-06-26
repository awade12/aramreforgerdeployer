# Arma Reforger Server Deployer

A small, dependency-free deployment toolkit for running one or many Arma Reforger dedicated servers on Linux VPS hosts, bare-metal Linux machines, or Windows servers.

It uses the official dedicated-server Steam app IDs:

- Stable server: `1874900` ([SteamDB](https://steamdb.info/app/1874900/))
- Experimental server: `1890870` ([SteamDB](https://steamdb.info/app/1890870/))

Useful official/community references:

- Arma Reforger server hosting wiki: <https://community.bistudio.com/wiki/Arma_Reforger:Server_Hosting>
- Arma Reforger server config wiki: <https://community.bistudio.com/wiki/Arma_Reforger:Server_Config>
- SteamCMD documentation: <https://developer.valvesoftware.com/wiki/SteamCMD>
- LinuxGSM Arma Reforger server: <https://linuxgsm.com/servers/armarserver/>

## What This Gives You

- One global config plus one editable `instances/*.json` file per server.
- Automatic safe port assignment for new or repaired instances.
- Preflight `doctor` checks for Python, SteamCMD, disk, ports, firewall notes, config, and server files.
- Non-root Linux user setup for safer VPS hosting.
- Guided config wizard for adding/editing servers.
- Interactive operator menu for common actions.
- SteamCMD install/update for stable or experimental dedicated servers.
- Per-instance server config and start-script generation.
- Simple lifecycle commands: start, stop, restart, pause, resume, update, logs, debug.
- Optional Linux `systemd` service files for auto-start and crash restart.
- Service controls, firewall automation, backups, and mod helpers.
- Optional Windows startup Scheduled Tasks.
- LinuxGSM helper scripts and guidance for Linux admins who want its console, monitor, cron, backup, and debug workflows.
- Firewall command suggestions for required UDP ports.
- BattlEye RCon helper that appends settings without overwriting existing BattlEye config.

## Quick Start: Linux VPS

```bash
cd aramreforgerdeployer
chmod +x scripts/install-linux.sh
./scripts/install-linux.sh
```

Then run:

```bash
./ardr.py configure
./ardr.py doctor
./ardr.py install
./ardr.py start --instance reforger-1
```

```bash
./ardr.py menu
```

```bash
sudo ./ardr.py systemd install
sudo systemctl enable --now ardr-reforger-1.service
```

## Quick Start: Windows

Open PowerShell as Administrator:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install-windows.ps1
```

Then run:

```powershell
py .\ardr.py configure
py .\ardr.py install
py .\ardr.py start --instance reforger-1
```

```powershell
py .\ardr.py windows-task install
```

## Configure Many Servers

Run this once to create a starter config:

```bash
./ardr.py init
```

Add or edit servers with prompts:

```bash
./ardr.py configure
./ardr.py configure --instance reforger-1
```

Each server is saved as its own file in `instances/`. ARDR can assign safe ports automatically.

Detailed config examples are in [docs/CONFIGURATION.md](/Users/awade/Documents/aramreforgerdeployer/docs/CONFIGURATION.md).

## Ports

```bash
./ardr.py ports
./ardr.py ports --fix
```

## Common Commands

```bash
./ardr.py init                         # create starter deployer.json
./ardr.py configure                    # guided add/edit wizard
./ardr.py menu                         # interactive operator menu
./ardr.py validate                     # check config and port collisions
./ardr.py ports --fix                  # auto-assign safe ports and save instance files
./ardr.py doctor                       # preflight host/config checks
./ardr.py linux-user                   # dry-run non-root Linux setup
./ardr.py firewall apply --dry-run
sudo ./ardr.py firewall apply
./ardr.py render                       # generate server JSON and start scripts
./ardr.py install                      # install/update all instances with SteamCMD
./ardr.py install --instance reforger-1
./ardr.py update                       # update and restart servers that were running
./ardr.py update --instance reforger-1 --no-restart
./ardr.py start --instance reforger-1
./ardr.py stop --instance reforger-1
./ardr.py restart --instance reforger-1
./ardr.py pause --instance reforger-1
./ardr.py resume --instance reforger-1
./ardr.py status
./ardr.py logs --instance reforger-1 --follow
./ardr.py debug --instance reforger-1
./ardr.py service restart --instance reforger-1
./ardr.py service logs --instance reforger-1 --follow
./ardr.py mods add --instance reforger-1 --id MOD_ID --name "Mod Name"
./ardr.py mods list --instance reforger-1
./ardr.py backup create --instance reforger-1
./ardr.py ports
./ardr.py linuxgsm
./ardr.py battleye --instance reforger-1 --rcon-port 5678 --rcon-password "change-me"
```

`debug` runs the server in the foreground so you can see output directly. Use `logs --systemd --follow` when the instance is running under a generated Linux service.
More operation commands are in [docs/OPERATIONS.md](/Users/awade/Documents/aramreforgerdeployer/docs/OPERATIONS.md).

## Linux Service Workflow

For safer VPS hosting, prepare a non-root server user after cloning the repo:

```bash
sudo ./ardr.py linux-user --user armar --target /opt/ardr --apply
sudo -iu armar
cd /opt/ardr
```

The default `linux-user` command is a dry run unless `--apply` is passed.

Install and manage services:

```bash
sudo ./ardr.py systemd install
sudo systemctl enable --now ardr-reforger-1.service
sudo ./ardr.py service restart --instance reforger-1
./ardr.py service logs --instance reforger-1 --follow
```

## LinuxGSM Workflow

LinuxGSM is a strong option on Linux when you want a battle-tested wrapper with monitor, console, backup, debug, update, and cron support.

```bash
./ardr.py linuxgsm
```

More detail is in [docs/DEPLOYMENT.md](/Users/awade/Documents/aramreforgerdeployer/docs/DEPLOYMENT.md).

## Windows Startup Workflow

Install startup tasks:

```powershell
py .\ardr.py windows-task install
```

Manage in Task Scheduler, or use `schtasks`:

```powershell
schtasks /Run /TN "ARDR reforger-1"
schtasks /End /TN "ARDR reforger-1"
```

## Notes

- `-maxFPS` defaults to `60`; Reforger servers can consume excessive CPU without it.
- The deployer uses `-config` and `-profile` for each instance.
- BattlEye RCon settings are appended to `BattlEye/BEServer_x64.cfg`; do not erase the existing generated content in that file.
- `pause` and `resume` suspend the tracked process. Prefer `stop` or `restart` for normal maintenance.
