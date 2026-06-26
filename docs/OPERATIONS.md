# Operations

## One-View Info

```bash
./ardr.py info --instance reforger-1
```

This prints service state, connection hint, ports, important file paths, useful commands, and the rendered launch command.

## Service Controls

After `sudo ./ardr.py systemd install`, use:

```bash
sudo ./ardr.py service start --instance reforger-1
sudo ./ardr.py service stop --instance reforger-1
sudo ./ardr.py service restart --instance reforger-1
./ardr.py service status --instance reforger-1
./ardr.py service logs --instance reforger-1 --follow
```

## Firewall Apply

```bash
./ardr.py firewall apply --dry-run
sudo ./ardr.py firewall apply
```

This applies local `ufw` rules when available. You still need to open the same UDP ports in your VPS provider firewall/security group.

## Backups

```bash
./ardr.py backup create
./ardr.py backup create --instance reforger-1
./ardr.py backup create --instance reforger-1 --include-downloads
./ardr.py backup list
./ardr.py backup restore --archive deployments/backups/FILE.tar.gz --target ./restore-test
```

Backups include `deployer.json`, `instances/*.json`, profiles, and BattlEye config. `--include-downloads` also includes the installed server directory for the selected instance.

## Mods

```bash
./ardr.py mods add --instance reforger-1 --id MOD_ID --name "Mod Name"
./ardr.py mods list --instance reforger-1
./ardr.py mods remove --instance reforger-1 --id MOD_ID
./ardr.py render --instance reforger-1
```
