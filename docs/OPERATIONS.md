# Operations

## Web Dashboard

```bash
reforger web --host 127.0.0.1 --port 8080
reforger open --host 127.0.0.1 --port 8080
reforger web --host 0.0.0.0 --port 8080
reforger web --host 0.0.0.0 --port 8080 --password "change-this"
```

The first run generates a password and stores only a local hash in `.ardr-web-auth.json`. The dashboard uses HTMX and Tailwind, requires login, signs session cookies, and uses CSRF tokens on actions. For public use, put HTTPS in front of it with Caddy or another reverse proxy.

The instance panel shows runtime state, PID, systemd state, ports, scenario, executable presence, important paths, and a last-checked timestamp. Start, stop, restart, status, logs, backup, render, query, and mod-add actions all return a visible result banner plus an activity block with command output or errors.

For safer remote access, bind to localhost and tunnel it:

```bash
ssh -L 8080:127.0.0.1:8080 ubuntu@YOUR_VPS_IP
```

Then open `http://127.0.0.1:8080` on your computer.

## One-View Info

```bash
reforger info reforger-1
reforger default reforger-1
reforger info
```

This prints service state, connection hint, ports, important file paths, useful commands, and the rendered launch command.

## Live Query

```bash
reforger query reforger-1
reforger query reforger-1 --host 203.0.113.10
```

This queries the instance A2S port and prints live server name, map, player count, version, and ping when the server responds.

## First Deploy

Preview:

```bash
reforger launch reforger-1
```

Apply:

```bash
sudo reforger launch reforger-1 --apply
```

Launch/deploy renders configs, creates a backup, installs/updates server files, applies local firewall rules, installs systemd, enables the service, starts it, and prints `info`.

## Daily Controls

After the service is installed, the simple lifecycle commands automatically use systemd when available:

```bash
reforger start reforger-1
reforger stop reforger-1
reforger restart reforger-1
reforger status reforger-1
reforger tail reforger-1
reforger logs reforger-1 -f
```

The advanced `service` command remains available when you need direct systemd control.

## Firewall Apply

```bash
reforger firewall apply --dry-run
sudo reforger firewall apply
```

This applies local `ufw` rules when available. You still need to open the same UDP ports in your VPS provider firewall/security group.

## Backups

```bash
reforger backup create
reforger backup create reforger-1
reforger backup create reforger-1 --include-downloads
reforger backup list
reforger backup restore --archive deployments/backups/FILE.tar.gz --target ./restore-test
```

Backups include `deployer.json`, `instances/*.json`, profiles, and BattlEye config. `--include-downloads` also includes the installed server directory for the selected instance.

## Mods

```bash
reforger mods add reforger-1 --id MOD_ID --name "Mod Name"
reforger mods list reforger-1
reforger mods remove reforger-1 --id MOD_ID
reforger render reforger-1
```
