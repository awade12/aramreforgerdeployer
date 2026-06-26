# Project Structure

The code is split by job so no single file owns the whole deployer.

```text
reforger                Linux/macOS command launcher
reforger.py             Windows-friendly command launcher
ardr.py                 backward-compatible legacy launcher
deployer.json           global deployer settings
instances/              one editable config file per server
ardr/
  cli/
    __init__.py         main entrypoint
    parser.py           build_parser entrypoint
    subparsers.py       argparse subcommand definitions
  commands/
    __init__.py         command handler exports
    handlers.py         setup, status, platform command handlers
    lifecycle.py        start, stop, restart, pause, resume, logs
    helpers.py          shared instance/config helpers
    management.py       backup, firewall, mods, query, deploy, service
    registry.py         interactive menu dispatch table
  config/
    __init__.py         config load/save exports
    io.py               load and save deployer config
    instances.py        instance selection and per-file storage
    validation.py       port and schema validation
    sample.py           starter deployer.json content
    wizard.py           guided config prompts
    commands.py         init, configure, default, validate commands
    json_io.py          shared JSON write helper
  core/
    constants.py        app IDs and shared constants
    paths.py            deployment path helpers
    ports.py            automatic safe port assignment
    platforming.py      OS detection, quoting, command execution
    network.py          host IP detection and connect address helpers
    terminal.py         CLI formatting and tables
  server/
    processes.py        start, stop, pause, resume, PID tracking
    render.py           Reforger config and start-script rendering
    ops.py              install, update, restart, logs, ports
    status.py           runtime status rows
    info.py             one-view instance details
    mods.py             mod config helpers
    query.py            live A2S query
    battleye.py         BattlEye RCon append helper
  platform/
    services.py         systemd and Windows Scheduled Task helpers
    firewall.py         local firewall automation
    linux_setup.py      non-root Linux user setup
    linuxgsm.py         LinuxGSM helper generation
    doctor.py           preflight checks
  deploy/
    backup.py           backup and restore helpers
    workflow.py         first-deploy workflow
  web/
    __init__.py         dashboard server entrypoint
    auth.py             password/session helpers
    models.py           dashboard state summaries
    layout.py           shared HTML page shell
    views.py            HTMX/Tailwind dashboard views
    handler.py          HTTP request handler
    actions.py          dashboard action runners
    state.py            dashboard session state
  ui/
    menu.py             interactive management menu
scripts/
  install-linux.sh      Linux bootstrap
  install-windows.ps1   Windows bootstrap
docs/
  DEPLOYMENT.md         operator guide
  CONFIGURATION.md      deployer and instance config guide
  OPERATIONS.md         service, firewall, backup, and mod commands
  STRUCTURE.md          code layout
```

Generated server installs, configs, logs, profiles, SteamCMD tools, and PID files are ignored by Git.
