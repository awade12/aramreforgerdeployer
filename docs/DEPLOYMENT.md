# Deployment Guide

## Recommended Layout

Keep the deployer repo separate from generated server files:

```text
aramreforgerdeployer/
  ardr.py
  deployer.json
  instances/
    reforger-1.json
  deployments/
    reforger-1/
      server/
      generated/
  profiles/
    reforger-1/
```

`server/` contains SteamCMD-installed Reforger files. `profiles/` contains logs, downloaded addons, and profile data.

## VPS Checklist

1. Pick a Linux VPS with enough CPU and memory for the player count and mod set.
2. Install the deployer with `scripts/install-linux.sh`.
3. Optionally move it to a non-root user with `sudo ./ardr.py linux-user --apply`.
4. Run `./ardr.py configure` or edit `instances/*.json`.
5. Run `./ardr.py doctor`.
6. Run `./ardr.py install`.
7. Open UDP ports from `./ardr.py ports`.
8. Install systemd services with `sudo ./ardr.py systemd install --instance <name>`.
9. Start with `sudo ./ardr.py service enable --instance <name>` and `sudo ./ardr.py service start --instance <name>`.
10. Watch logs with `./ardr.py service logs --instance <name> --follow`.

## Windows Checklist

1. Install Python 3.
2. Run PowerShell as Administrator.
3. Run `.\scripts\install-windows.ps1`.
4. Run `py .\ardr.py configure` or edit `instances\*.json`.
5. Run `py .\ardr.py install`.
6. Open UDP ports from `py .\ardr.py ports`.
7. Install startup tasks with `py .\ardr.py windows-task install`.

## Operator Menu

Run:

```bash
./ardr.py menu
```

The menu gives an easy way to run status, start, stop, restart, pause, resume, update, render, show/fix ports, doctor, LinuxGSM helper generation, and config wizard actions.

For a single summary view of a server:

```bash
./ardr.py info --instance reforger-1
```

## Preflight Doctor

Run:

```bash
./ardr.py doctor
```

It checks Python, SteamCMD availability, config validity, disk space, whether UDP ports can bind locally, expected server executables, local firewall hints, and reminds you that VPS provider firewall/security groups must also be opened.

## Non-Root Linux User

Do a dry run first:

```bash
./ardr.py linux-user --user armar --target /opt/ardr
```

Apply as root:

```bash
sudo ./ardr.py linux-user --user armar --target /opt/ardr --apply
sudo -iu armar
cd /opt/ardr
```

This creates the `armar` user if missing, copies the deployer to `/opt/ardr`, excludes generated server/profile data, and owns the target directory as `armar`.

## Lifecycle Commands

```bash
sudo ./ardr.py systemd install --instance reforger-1
sudo ./ardr.py service enable --instance reforger-1
sudo ./ardr.py service start --instance reforger-1
sudo ./ardr.py service restart --instance reforger-1
sudo ./ardr.py service stop --instance reforger-1
./ardr.py service logs --instance reforger-1 --follow
./ardr.py pause --instance reforger-1
./ardr.py resume --instance reforger-1
./ardr.py update
./ardr.py update --instance reforger-1 --no-restart
./ardr.py debug --instance reforger-1
```

Use `./ardr.py start --instance reforger-1` only as a quick manual smoke test on VPS hosts. The standard path is systemd.

`update` stops and restarts only servers that ARDR knows were already running. Add `--start-stopped` when you want updated stopped instances to start too.

Service controls, firewall apply, backups, and mods are covered in [OPERATIONS.md](/Users/awade/Documents/aramreforgerdeployer/docs/OPERATIONS.md).

## Adding Another Server

Run `./ardr.py configure`, or copy an existing `instances/*.json` file and change:

- `name`
- `port`
- `queryPort`
- `profileDir`
- `server.name`
- `server.adminPassword`

Then run:

```bash
./ardr.py validate
./ardr.py ports --fix
./ardr.py render
./ardr.py install --instance new-name
```

## Stable vs Experimental

Use:

```json
"branch": "stable"
```

or:

```json
"branch": "experimental"
```

Stable uses Steam app `1874900`. Experimental uses Steam app `1890870`.

## LinuxGSM Option

For Linux hosts, LinuxGSM is often the best operational wrapper if you want mature monitoring, console attach, backups, debug output, and cron-driven update checks.

Generate ARDR helper scripts:

```bash
./ardr.py linuxgsm
```

Then run the generated `linuxgsm-bootstrap.sh` inside the instance generated folder or copy its commands into a dedicated `armarserver` user account.

Useful LinuxGSM commands:

```bash
./armarserver start
./armarserver stop
./armarserver restart
./armarserver console
./armarserver update
./armarserver force-update
./armarserver validate
./armarserver monitor
./armarserver details
./armarserver debug
./armarserver backup
```

Recommended LinuxGSM cron:

```cron
*/5 * * * * /home/armarserver/armarserver monitor > /dev/null 2>&1
*/30 * * * * /home/armarserver/armarserver update > /dev/null 2>&1
0 0 * * 0 /home/armarserver/armarserver update-lgsm > /dev/null 2>&1
```

## BattlEye RCon

Append RCon settings:

```bash
./ardr.py battleye --instance reforger-1 --rcon-port 5678 --rcon-password "change-this"
```

Do not overwrite `BattlEye/BEServer_x64.cfg`; the game writes required values there.

## Docker Notes

The included manager targets direct Linux/Windows installs. If running inside Docker, make sure the container networking exposes UDP game and query ports. Depending on NAT, set values such as `publicAddress`, `gameHostRegisterBindAddress`, and `gameHostRegisterPort` in each instance server block.
