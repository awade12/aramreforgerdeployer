# Troubleshooting

## “Config file not found”

Run:

```bash
reforger where
```

Reforger Deployer normally discovers its config automatically. If you manage more than one setup, choose the exact one:

```bash
reforger --config /path/to/deployer.json where
```

## SteamCMD Is Missing

Run:

```bash
reforger doctor
```

On Ubuntu/Debian, the usual fix is:

```bash
sudo apt update
sudo apt install steamcmd
```

If SteamCMD is installed somewhere unusual, set its full path in `deployer.json` with `reforger edit`.

## Players Cannot Connect

1. Confirm the address printed by `reforger testingserver invite` is your public VPS IP or domain.
2. Set the public address through `reforger testingserver edit` if needed.
3. Run `reforger ports`.
4. Open both UDP ports in the host firewall and your VPS provider firewall/security group.
5. Confirm the server is up with `reforger testingserver resources` or `reforger query testingserver`.

## Server Will Not Start

```bash
reforger testingserver health
reforger testingserver logs
reforger testingserver where
```

The health scorecard identifies missing SteamCMD, server files, port conflicts, low disk space, and config issues. Render after changing settings:

```bash
reforger render testingserver
```

## Logs Are Empty

Use `reforger testingserver where` to see the active profile/log path. A systemd server may write to the journal instead:

```bash
reforger logs testingserver --systemd --follow
```

## I Need to Undo a Change

```bash
reforger backup list
reforger backup restore
```

Restoration asks for confirmation. Restore into a test directory first when you are uncertain.

## Micro Is Missing

Run:

```bash
reforger testingserver edit --raw
```

The command offers an opt-in installation. You can also install it manually:

```bash
sudo apt install micro     # Debian/Ubuntu
brew install micro         # macOS
```

## Still Stuck?

Collect the output of these commands before asking for help:

```bash
reforger where
reforger testingserver health
reforger testingserver logs
reforger --help
```

Never post passwords, Discord bot tokens, or private IP/network details publicly.
