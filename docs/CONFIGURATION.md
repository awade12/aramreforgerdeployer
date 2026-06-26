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
  "instanceDir": "instances"
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
- `server.adminPassword`: Admin password.
- `server.scenarioId`: Scenario config path.
- `mods`: Workshop mods passed into the generated server config.

Every instance needs unique `port` and `queryPort` values.

## Automatic Ports

New instances get safe ports automatically. Reforger starts at:

- Game ports: `2001`, `2003`, `2005`, ...
- Query ports: `17777`, `17779`, `17781`, ...

If you manually edit files and accidentally collide ports, run:

```bash
reforger ports --fix
```

That rewrites `instances/*.json` with safe ports before rendering or starting servers.
