# Security Policy

## Supported Versions

Security fixes are made against the current default branch.

## Reporting a Vulnerability

Do not publish vulnerabilities, credentials, server addresses, or exploit details in a public issue.

Instead, contact the repository owner privately with:

- A clear description of the issue
- Affected command or file
- Reproduction steps using redacted data
- Impact and any suggested mitigation

Allow time for acknowledgement and a fix before public disclosure.

## Sensitive Data

Treat these as secrets:

- Server admin and join passwords
- Discord bot tokens and channel IDs where privacy matters
- BattlEye RCon passwords
- Private hostnames, private IP addresses, and VPN details
- Backup archives and profile data

Reforger Deployer avoids printing passwords in guided-editor previews. Contributors must preserve that behavior and avoid logging secrets in errors, tests, or documentation.

## Operational Guidance

- Run game services under a dedicated non-root account on Linux.
- Bind the optional web dashboard to localhost unless it is behind HTTPS and an access-controlled reverse proxy.
- Use strong dashboard, admin, and RCon passwords.
- Keep operating system packages, SteamCMD, and server files updated.
- Check backups and restore procedures before relying on them during an incident.
- Review `reforger where` output before handling or sharing files from a server.
