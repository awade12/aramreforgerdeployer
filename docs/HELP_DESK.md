# Reforger Help Desk

The built-in help desk turns common server questions into short, ordered runbooks:

```bash
reforger helpdesk
reforger helpdesk mod-update --instance testingserver
reforger helpdesk players-cannot-connect --instance testingserver
```

It is also available from the main `reforger menu` and from every server control room. The interactive view groups questions by everyday operation, updates and mods, configuration, connection problems, troubleshooting, safety and recovery, performance, services, and getting started. Press `S` to search all questions.

## When a Mod Updates

The dedicated-server update and a Workshop update are different jobs. To refresh a mod or scenario pack, re-apply its Workshop URL so the current version and dependency versions are saved, then render and restart:

```bash
reforger testingserver mod add <workshop-url>
reforger render testingserver
reforger restart testingserver
reforger testingserver tail
reforger query testingserver
```

The Workshop operation shows a preview and creates a safety backup. At startup, the server downloads or loads the versions named in the generated config.

To update the dedicated-server program itself instead:

```bash
reforger testingserver update
```

That path creates a backup, updates and validates files through SteamCMD, and restarts a server that was already running.

## Direct Topic Names

Use any of these with `reforger helpdesk TOPIC --instance SERVER`:

- `daily-check`
- `server-update`
- `mod-update`
- `add-mod`
- `remove-mod`
- `change-settings`
- `players-cannot-connect`
- `server-wont-start`
- `version-mismatch`
- `logs`
- `backup-restore`
- `performance`
- `disk-space`
- `ports-firewall`
- `admins-passwords`
- `startup-service`
- `move-server`
- `first-deploy`
- `get-support`

The command output is the authoritative version because its examples can include the selected server name.
