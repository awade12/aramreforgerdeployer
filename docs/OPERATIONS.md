# Operations

## Web Dashboard

```bash
./ardr.py web --host 127.0.0.1 --port 8080
./ardr.py web --host 0.0.0.0 --port 8080
./ardr.py web --host 0.0.0.0 --port 8080 --password "change-this"
```

The first run generates a password and stores only a local hash in `.ardr-web-auth.json`. The dashboard uses HTMX and Tailwind, requires login, signs session cookies, and uses CSRF tokens on actions. For public use, put HTTPS in front of it with Caddy or another reverse proxy.

## One-View Info

```bash
./ardr.py info --instance reforger-1
```

This prints service state, connection hint, ports, important file paths, useful commands, and the rendered launch command.

## Live Query

```bash
./ardr.py query --instance reforger-1
./ardr.py query --instance reforger-1 --host 203.0.113.10
```

This queries the instance A2S port and prints live server name, map, player count, version, and ping when the server responds.

## First Deploy

Preview:

```bash
./ardr.py deploy --instance reforger-1
```

Apply:

```bash
sudo ./ardr.py deploy --instance reforger-1 --apply
```

Deploy renders configs, creates a backup, installs/updates server files, applies local firewall rules, installs systemd, enables the service, starts it, and prints `info`.

## Service Controls

After `sudo ./ardr.py systemd install`, use:

```bash
sudo ./ardr.py service start --instance reforger-1
sudo ./ardr.py service stop --instance reforger-1
sudo ./ardr.py service restart --instance reforger-1
./ardr.py service status --instance reforger-1
./ardr.py service logs --instance reforger-1 --follow
```

## Firewall Apply

```bash
./ardr.py firewall apply --dry-run
sudo ./ardr.py firewall apply
```

This applies local `ufw` rules when available. You still need to open the same UDP ports in your VPS provider firewall/security group.

## Backups

```bash
./ardr.py backup create
./ardr.py backup create --instance reforger-1
./ardr.py backup create --instance reforger-1 --include-downloads
./ardr.py backup list
./ardr.py backup restore --archive deployments/backups/FILE.tar.gz --target ./restore-test
```

Backups include `deployer.json`, `instances/*.json`, profiles, and BattlEye config. `--include-downloads` also includes the installed server directory for the selected instance.

## Mods

```bash
./ardr.py mods add --instance reforger-1 --id MOD_ID --name "Mod Name"
./ardr.py mods list --instance reforger-1
./ardr.py mods remove --instance reforger-1 --id MOD_ID
./ardr.py render --instance reforger-1
```
