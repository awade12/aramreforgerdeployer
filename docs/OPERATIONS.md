# Operations

## The Server Control Room

```bash
reforger testingserver
```

The server-first command opens the interactive control room. It provides Start, Stop, Logs, Update, Mods, Backup, Health, Details, Resources, Invite, and Edit settings in one place.

The control room and main menu also open the Reforger Help Desk. You can launch it directly or jump to a known runbook:

```bash
reforger helpdesk
reforger helpdesk mod-update --instance testingserver
```

You can use direct commands instead:

```bash
reforger testingserver on
reforger testingserver off
reforger testingserver restart
reforger testingserver logs
reforger testingserver resources --watch 2
```

Use `Ctrl+C` to stop a watched resource dashboard or live log stream.

## Logs and Live Status

```bash
reforger testingserver logs
reforger testingserver tail
reforger query testingserver
```

The regular log view highlights errors and warnings. `tail` follows the current log. With systemd, use:

```bash
reforger logs testingserver --systemd --follow
```

`query` uses the A2S query port and reports live server data such as player count, map, version, and ping when the server responds.

## Resources

```bash
reforger testingserver resources
reforger testingserver resources --watch 2
```

The resource view reports process CPU/RAM, deployment disk usage, player count, ping, and process runtime when available. Reforger does not expose a tick/FPS value through the query protocol, so the dashboard labels that honestly rather than inventing a value.

## Updates and Backups

```bash
reforger testingserver update
reforger backup list
reforger backup create testingserver
reforger backup restore
```

Updates create a safety backup by default and ask before potentially restarting a running server. `backup restore` lists available archives when no `--archive` is supplied and asks before writing files.

Useful flags:

```bash
reforger update testingserver --no-restart --yes
reforger update testingserver --no-backup --yes
reforger backup create testingserver --include-downloads
reforger backup restore --archive /path/to/backup.tar.gz --target ./restore-test --yes
```

## Editing and Admins

```bash
reforger testingserver edit
```

Use the guided editor for names, passwords, player limits, admin Steam IDs, scenario settings, network settings, and mods. Admin IDs are managed one at a time—add, remove, or deliberately replace the full list. Changes are previewed before saving.

Use raw JSON only for settings not represented in the guided editor:

```bash
reforger testingserver edit --raw
```

## Player Invite

```bash
reforger testingserver invite
```

This prints a clean message containing the server name, direct address, password status, and player limit. Set `server.publicAddress` through the guided editor if the address is wrong.

## Firewall

```bash
reforger ports
reforger firewall apply --dry-run
sudo reforger firewall apply
```

Firewall application asks before changing local rules. It only handles a local firewall such as UFW; you must still permit the same UDP ports in your VPS provider control panel.

## Mods and Workshop

```bash
reforger testingserver mod list
reforger testingserver mod add <workshop-url>
reforger mods remove testingserver --id MOD_ID
```

Workshop application previews the selected scenario and dependencies, then creates a safety backup before it changes the server definition.

## Export and Import

```bash
reforger testingserver export testingserver.json
reforger import testingserver.json --as eventserver
```

Exported files contain a portable server definition, not installed game files or secrets outside the server definition. Inspect an imported server with `reforger eventserver` before using it.

## Web Dashboard

The web dashboard is optional; the CLI is the primary interface.

```bash
reforger web --host 127.0.0.1 --port 8080
```

Bind to localhost and use SSH tunneling for remote access:

```bash
ssh -L 8080:127.0.0.1:8080 ubuntu@YOUR_VPS_IP
```

Then browse to `http://127.0.0.1:8080` locally. If you expose the dashboard through a reverse proxy, use HTTPS and a strong password.

## Discord

```bash
reforger discord configure
reforger discord post
reforger discord sync
reforger discord start
```

Discord updates a single status embed rather than posting a new message each interval. Keep the bot token private and prefer `DISCORD_BOT_TOKEN` for unattended service or cron use.
