# Deployment

This guide covers turning a new configuration into a running dedicated server.

## Recommended Linux VPS Flow

1. Install Reforger Deployer with `scripts/install-linux.sh`.
2. Run `reforger setup`.
3. Check the generated paths with `reforger where`.
4. Preview the deployment:

   ```bash
   reforger launch testingserver
   ```

5. Apply it with the privileges required for systemd and firewall work:

   ```bash
   sudo reforger launch testingserver --apply
   ```

6. Confirm it is running:

   ```bash
   reforger testingserver
   reforger testingserver logs
   ```

`launch --apply` renders configuration, creates a backup, downloads server files through SteamCMD, prepares local firewall rules, installs/enables the systemd service, starts the server, and prints follow-up information.

## Before You Start

Run the readiness checks:

```bash
reforger testingserver health
reforger doctor
```

The doctor checks Python, SteamCMD, free disk, configuration, ports, local UDP binding, and server files. It ends with a scorecard and commands for anything that needs attention.

You must also open the game and query UDP ports in your VPS provider firewall/security group. `reforger ports` prints the exact ports and commands.

## Services on Linux

After a successful launch, daily commands use the generated systemd service automatically when available:

```bash
reforger testingserver on
reforger testingserver off
reforger testingserver logs
```

For direct systemd control:

```bash
sudo reforger systemd install --instance testingserver
sudo reforger service enable testingserver
sudo reforger service restart testingserver
reforger service logs testingserver --follow
```

## Non-Root Deployment User

For a long-lived VPS, run server files as a dedicated unprivileged user:

```bash
sudo reforger linux-user --user armar --target /opt/ardr
sudo reforger linux-user --user armar --target /opt/ardr --apply
sudo -iu armar
cd /opt/ardr
```

The first command is a dry run. The applied command creates the user if required and copies the project without generated server/profile data.

## Windows

1. Run `scripts/install-windows.ps1` from an elevated PowerShell.
2. Run `reforger setup`.
3. Install server files:

   ```powershell
   reforger install testingserver
   ```

4. Open the UDP ports shown by `reforger ports`.
5. Optional startup task:

   ```powershell
   reforger windows-task install --instance testingserver
   ```

## Stable and Experimental

Set the server `branch` to either:

```json
"stable"
```

or:

```json
"experimental"
```

Stable uses Steam app `1874900`; experimental uses `1890870`.

## LinuxGSM

LinuxGSM is optional. It can be useful when you prefer its established maintenance and monitoring workflow:

```bash
reforger linuxgsm
```

The command renders helper scripts in the generated server folder. Reforger Deployer’s native service workflow remains the simplest default.
