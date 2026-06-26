# Deployment Guide

## Recommended Layout

Keep the deployer repo separate from generated server files:

```text
aramreforgerdeployer/
  reforger
  reforger.py
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
3. Use the installed `reforger` command for deployment and operations.
4. Optionally move it to a non-root user with `sudo reforger linux-user --apply`.
5. Run `reforger setup`, or edit `instances/*.json`.
6. Preview deploy with `reforger launch <name>`.
7. Apply deploy with `sudo reforger launch <name> --apply`.
8. Set a default with `reforger default <name>`.
9. Watch logs with `reforger tail`.

## Windows Checklist

1. Install Python 3.
2. Run PowerShell as Administrator.
3. Run `.\scripts\install-windows.ps1`.
4. Open a new terminal if PowerShell does not find `reforger` immediately.
5. Run `reforger setup` or edit `instances\*.json`.
6. Run `reforger install`.
7. Open UDP ports from `reforger ports`.
8. Install startup tasks with `reforger windows-task install`.

## Operator Menu

Run:

```bash
reforger menu
```

The menu gives an easy way to run status, start, stop, restart, pause, resume, update, render, show/fix ports, doctor, LinuxGSM helper generation, and config wizard actions.

For a single summary view of a server:

```bash
reforger info reforger-1
reforger query reforger-1
```

## Preflight Doctor

Run:

```bash
reforger check
reforger fix
```

`check` validates config, prints port guidance, checks Python, SteamCMD availability, disk space, whether UDP ports can bind locally, expected server executables, local firewall hints, and reminds you that VPS provider firewall/security groups must also be opened. `fix` also repairs safe port assignments before checking.

## Non-Root Linux User

Do a dry run first:

```bash
reforger linux-user --user armar --target /opt/ardr
```

Apply as root:

```bash
sudo reforger linux-user --user armar --target /opt/ardr --apply
sudo -iu armar
cd /opt/ardr
```

This creates the `armar` user if missing, copies the deployer to `/opt/ardr`, excludes generated server/profile data, and owns the target directory as `armar`.

## Lifecycle Commands

```bash
reforger default reforger-1
reforger status
reforger start
reforger stop
reforger restart
reforger tail
reforger pause
reforger resume
reforger update
reforger update reforger-1 --no-restart
reforger debug reforger-1
```

After a service is installed, `start`, `stop`, `restart`, and `tail` automatically use systemd when available. Without a service, they use direct process mode for local smoke tests.

`update` stops and restarts only servers that Reforger knows were already running. Add `--start-stopped` when you want updated stopped instances to start too.

Service controls, firewall apply, backups, and mods are covered in [OPERATIONS.md](/Users/awade/Documents/aramreforgerdeployer/docs/OPERATIONS.md).

## Adding Another Server

Run `reforger configure new-name`, or copy an existing `instances/*.json` file and change:

- `name`
- `port`
- `queryPort`
- `profileDir`
- `server.name`
- `server.adminPassword`

Then run:

```bash
reforger validate
reforger ports --fix
reforger render
reforger install new-name
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

Generate Reforger helper scripts:

```bash
reforger linuxgsm
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
reforger battleye --instance reforger-1 --rcon-port 5678 --rcon-password "change-this"
```

Do not overwrite `BattlEye/BEServer_x64.cfg`; the game writes required values there.

## Docker Notes

The included manager targets direct Linux/Windows installs. If running inside Docker, make sure the container networking exposes UDP game and query ports. Depending on NAT, set values such as `publicAddress`, `gameHostRegisterBindAddress`, and `gameHostRegisterPort` in each instance server block.
