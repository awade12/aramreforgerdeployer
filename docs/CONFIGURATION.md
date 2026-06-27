# Configuration

Run the wizard first:

```bash
reforger configure
```

You can also edit files directly. Global settings live in `deployer.json`; each server lives in its own file under `instances/`.

```text
deployer.json
instances/
  reforger-1.json
  reforger-2.json
```

## Global Example

```json
{
  "baseDir": "./deployments",
  "steamcmd": "steamcmd",
  "instanceDir": "instances",
  "defaultInstance": "reforger-1"
}
```

## Instance Example

Save each server as `instances/<name>.json`.

```json
{
  "name": "reforger-1",
  "branch": "stable",
  "port": 2001,
  "queryPort": 17777,
  "maxFPS": 60,
  "profileDir": "./profiles/reforger-1",
  "server": {
    "name": "My Reforger Server 1",
    "password": "",
    "adminPassword": "change-this-admin-password",
    "scenarioId": "{ECC61978EDCC2B5A}Missions/23_Campaign.conf",
    "maxPlayers": 64,
    "visible": true
  },
  "mods": []
}
```

## Important Fields

- `name`: Local instance name used by Reforger commands.
- `branch`: `stable`, `experimental`, or a numeric Steam app ID.
- `port`: UDP game traffic port.
- `queryPort`: UDP A2S/query port.
- `maxFPS`: Server FPS cap. Keep this set, usually `60`.
- `profileDir`: Logs, downloaded addons, and profile data.
- `server.name`: Public browser name.
- `server.publicAddress`: Public VPS IP or DNS name shown by `reforger info` for direct connect.
- `server.adminPassword`: Admin password.
- `server.scenarioId`: Scenario config path.
- `mods`: Workshop mods passed into the generated server config.

Every instance needs unique `port` and `queryPort` values.

## Default Server

Set a default server to make daily commands shorter:

```bash
reforger default reforger-1
reforger status
reforger restart
reforger tail
```

Without a default, commands such as `restart` and `tail` will ask you to name a server when multiple instances are configured.

## Automatic Ports

New instances get safe ports automatically. Reforger starts at:

- Game ports: `2001`, `2003`, `2005`, ...
- Query ports: `17777`, `17779`, `17781`, ...

If you manually edit files and accidentally collide ports, run:

```bash
reforger ports --fix
```

That rewrites `instances/*.json` with safe ports before rendering or starting servers.

## Discord Status Embed

Post a live server status embed to a Discord channel. The deployer edits one message instead of sending a new one every update.

Secrets stay out of `deployer.json`. Reforger stores Discord settings in a local `.ardr-discord.ini` file with mode `600`, similar to the web dashboard auth file.

```bash
reforger discord configure
reforger discord status
reforger discord post
reforger discord start
```

Example local file:

```ini
[discord]
bot_token = your-bot-token-here
channel_id = 1234567890123456789
poll_interval_seconds = 30
query_live = true
title = Arma Reforger Server Status

[state]
channel_id = 1234567890123456789
message_id =
```

Create a Discord bot in the [Discord Developer Portal](https://discord.com/developers/applications), invite it to your server with `Send Messages` and `Embed Links`, then run `reforger discord configure`.

Commands:

- `reforger discord configure` — create or update `.ardr-discord.ini`
- `reforger discord status` — show saved settings without printing the token
- `reforger discord post` — create the first embed and save its message ID
- `reforger discord sync` — update the saved embed once
- `reforger discord start` — keep updating the same embed on an interval

For systemd or cron, you can override the token with an environment variable instead of storing it in the ini file:

```bash
export DISCORD_BOT_TOKEN="your-bot-token"
reforger discord sync --ini /etc/ardr/discord.ini
```

If the saved message was deleted, the next sync automatically posts a new one and updates the saved message ID in the ini file.
