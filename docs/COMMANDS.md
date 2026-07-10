# Command Reference

Use `reforger --help` for the authoritative list on the installed version. The commands below are the everyday interface.

## Getting Started

```bash
reforger                         # home screen
reforger setup                   # first server wizard
reforger quickstart              # alias for setup
reforger menu                    # guided multi-server menu
reforger where                   # show every active path
```

## Server-First Shortcuts

```bash
reforger <server>                # interactive server hub
reforger <server> on|off
reforger <server> restart
reforger <server> logs|tail
reforger <server> health
reforger <server> resources [--watch SECONDS]
reforger <server> invite
reforger <server> edit
reforger <server> where
reforger <server> backup
reforger <server> update --yes
```

## Configuration

```bash
reforger configure [server]
reforger <server> edit
reforger <server> edit --raw
reforger default [server]
reforger validate
reforger ports [--fix]
reforger <server> export FILE.json
reforger import FILE.json [--as new-server]
```

## Lifecycle

```bash
reforger start|stop|restart <server>
reforger logs <server> [-f|--follow] [--systemd]
reforger tail <server> [--systemd]
reforger pause|resume <server>
reforger debug <server>
reforger update <server> [--no-restart] [--no-backup] [--yes]
```

## Deployment and Checks

```bash
reforger check [server]
reforger fix [server]
reforger doctor
reforger render [server]
reforger install [server]
reforger launch <server> [--apply]
```

## Backups, Mods, and Query

```bash
reforger backup create [server] [--include-downloads]
reforger backup list
reforger backup restore [--archive FILE] [--target DIRECTORY] [--yes]
reforger <server> mod add <workshop-url>
reforger mods add|list|remove <server> [--id MOD_ID]
reforger query <server> [--host HOST]
```

## Platform and Integrations

```bash
reforger systemd render|install [--instance server]
reforger service start|stop|restart|status|enable|disable|logs [server]
reforger firewall apply [--dry-run] [--yes]
reforger windows-task install|remove [--instance server]
reforger battleye --instance server --rcon-port PORT --rcon-password PASSWORD
reforger discord configure|status|post|sync|start
reforger web [--host HOST] [--port PORT]
```

## Completion

```bash
eval "$(reforger completion bash)"
eval "$(reforger completion zsh)"
```

Add the matching line to your shell profile to keep completion enabled.
