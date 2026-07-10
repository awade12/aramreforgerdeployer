# Configuration

Reforger Deployer keeps global settings in `deployer.json` and one server per file under `instances/`.

```text
deployer.json
instances/
  testingserver.json
  eventserver.json
```

Start with the guided setup:

```bash
reforger setup
```

For an existing server, use the guided editor rather than editing JSON directly:

```bash
reforger testingserver edit
```

It previews every save. Raw JSON remains available through `reforger testingserver edit --raw`.

## Global Settings

```json
{
  "baseDir": "./deployments",
  "steamcmd": "steamcmd",
  "instanceDir": "instances",
  "defaultInstance": "testingserver"
}
```

| Setting | Purpose |
| --- | --- |
| `baseDir` | Location for installed server files, generated files, and backups. |
| `steamcmd` | `steamcmd` command or absolute SteamCMD path. |
| `instanceDir` | Folder containing per-server JSON files. |
| `defaultInstance` | Optional server used by short command forms such as `reforger start`. |

## Server Settings

Save a server as `instances/<server-name>.json`.

```json
{
  "name": "testingserver",
  "branch": "stable",
  "port": 2001,
  "queryPort": 17777,
  "maxFPS": 60,
  "profileDir": "./profiles/testingserver",
  "server": {
    "name": "My Reforger Server",
    "password": "",
    "adminPassword": "change-this-admin-password",
    "admins": ["76561198000000000"],
    "scenarioId": "{ECC61978EDCC2B5A}Missions/23_Campaign.conf",
    "maxPlayers": 64,
    "visible": true,
    "publicAddress": ""
  },
  "mods": []
}
```

### Important Fields

| Field | Meaning |
| --- | --- |
| `name` | Local server name used in commands. Keep it short and unique. |
| `branch` | `stable`, `experimental`, or a numeric Steam app ID. |
| `port` / `queryPort` | Unique UDP game and A2S query ports. |
| `maxFPS` | Server FPS cap; `60` is a sensible default. |
| `profileDir` | Profile data, logs, and downloaded addons. |
| `server.name` | Name shown to players. |
| `server.password` | Optional join password; empty means public. |
| `server.adminPassword` | Administrative password. Do not share it. |
| `server.admins` | Optional Steam IDs with admin access. Use the guided add/remove list manager. |
| `server.scenarioId` | Scenario config path. |
| `server.maxPlayers` | Maximum player slots. |
| `server.publicAddress` | Public VPS IP or domain for direct-connect and invite output. |
| `mods` | Configured Workshop mods. |

## Ports and Multiple Servers

Every server needs unique game and query ports. The default sequence is:

- Game: `2001`, `2003`, `2005`, …
- Query: `17777`, `17779`, `17781`, …

Repair missing or conflicting ports with:

```bash
reforger ports --fix
```

Review the required provider and host firewall ports with:

```bash
reforger ports
```

## Default Server

Set a default once to keep command lines short:

```bash
reforger default testingserver
reforger start
reforger tail
```

The server-first form is always clear and does not require a default:

```bash
reforger testingserver on
reforger testingserver logs
```

## Mods and Workshop URLs

Use a Workshop URL to apply a scenario and its dependencies:

```bash
reforger testingserver mod add <workshop-url>
```

This previews the result, creates a safety backup before saving, and merges mods. To manage a mod ID directly:

```bash
reforger mods add testingserver --id MOD_ID --name "Mod Name"
reforger mods list testingserver
reforger mods remove testingserver --id MOD_ID
```

## Export and Import

Move a server definition between hosts without copying the entire project:

```bash
reforger testingserver export testingserver.json
reforger import testingserver.json --as testingserver-copy
```

Imports preserve the definition but assign safe ports if a collision would occur. Review an imported server before starting it:

```bash
reforger testingserver-copy
```

## Discord Status

Discord secrets are deliberately separate from server configuration.

```bash
reforger discord configure
reforger discord status
reforger discord post
reforger discord sync
reforger discord start
```

The local `.ardr-discord.ini` stores the bot configuration with restrictive permissions. Use `DISCORD_BOT_TOKEN` in automation when you do not want the token in that file.
