# Project Structure

The code is split by job so no single file owns the whole deployer.

```text
ardr.py                 tiny command launcher
deployer.json           global deployer settings
instances/              one editable config file per server
ardr/
  cli.py                argparse command wiring
  commands.py           command handlers
  config.py             config load, sample config, validation
  doctor.py             preflight checks
  linux_setup.py        non-root Linux user setup
  ports.py              automatic safe port assignment
  wizard.py             guided config prompts
  render.py             Reforger config and start-script rendering
  processes.py          start, stop, pause, resume, PID tracking
  ops.py                install, update, restart, logs, ports
  services.py           systemd and Windows Scheduled Task helpers
  linuxgsm.py           LinuxGSM helper generation
  battleye.py           BattlEye RCon append helper
  backup.py             backup and restore helpers
  firewall.py           local firewall automation
  mods.py               mod config helpers
  paths.py              deployment path helpers
  platforming.py        OS detection, quoting, command execution
  constants.py          app IDs and shared constants
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
