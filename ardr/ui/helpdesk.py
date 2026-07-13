from __future__ import annotations

from dataclasses import dataclass

from ..core.terminal import commands, heading, note, section


@dataclass(frozen=True)
class HelpTopic:
    slug: str
    category: str
    question: str
    answer: str
    steps: tuple[str, ...]
    commands: tuple[tuple[str, str], ...] = ()
    caution: str = ""


def _topics(server: str) -> tuple[HelpTopic, ...]:
    s = server or "<server>"
    return (
        HelpTopic(
            "daily-check",
            "Everyday operation",
            "What should I check each day?",
            "Use the status and query views first; only investigate further when they disagree or report a problem.",
            ("Check the tracked process state.", "Query the live game server.", "Open recent logs if either check looks wrong."),
            (("reforger status", "all configured servers"), (f"reforger query {s}", "players, map, version, and ping"), (f"reforger {s} logs", "recent server messages")),
        ),
        HelpTopic(
            "server-update",
            "Updates and mods",
            "How do I update the Reforger dedicated server?",
            "The update command makes a safety backup, stops the server if it is running, validates the latest files through SteamCMD, and starts it again.",
            ("Warn connected players and choose a quiet time.", "Run the update and approve the prompt.", "Check live status and logs after it restarts."),
            ((f"reforger {s} update", "safe update with backup and restart"), (f"reforger query {s}", "confirm it answers"), (f"reforger {s} logs", "look for startup errors")),
            "Use --no-restart only when you intentionally want the updated files to wait until a later restart.",
        ),
        HelpTopic(
            "mod-update",
            "Updates and mods",
            "A mod updated. How do I get the new version onto the server?",
            "Re-apply the mod's Workshop page. Reforger Deployer fetches its current version and dependencies, saves a backup, then the server downloads the configured versions when it starts.",
            ("Copy the same Workshop URL used for the mod or scenario.", "Apply it to the server; the preview shows the versions that will be saved.", "Render the changed server config.", "Restart and watch the logs while Workshop content downloads.", "Query the server before inviting players back."),
            ((f"reforger {s} mod add <workshop-url>", "refresh that mod and merge its dependencies"), (f"reforger render {s}", "write the new versions to the launch config"), (f"reforger restart {s}", "download/load them"), (f"reforger {s} tail", "watch download and load messages")),
            "Do not use `reforger update` for this job; that updates dedicated-server files, not the Workshop version stored in your server definition.",
        ),
        HelpTopic(
            "add-mod",
            "Updates and mods",
            "How do I add a mod, scenario, or dependency pack?",
            "Use the Workshop URL rather than manually copying files. The tool resolves the selected scenario and dependency tree for you.",
            ("Copy the Workshop page URL.", "Run the add command and review its scenario/mod preview.", "Render and restart.", "Check logs for a missing or incompatible dependency."),
            ((f"reforger {s} mod add <workshop-url>", "add it without removing existing mods"), (f"reforger render {s}", "save generated config"), (f"reforger restart {s}", "load the new setup"), (f"reforger {s} mod list", "review configured versions")),
        ),
        HelpTopic(
            "remove-mod",
            "Updates and mods",
            "How do I remove a mod safely?",
            "Remove it from the server definition, regenerate the config, and restart. Downloaded cache files may remain on disk but will no longer be loaded.",
            ("List mods and copy the exact mod ID.", "Create a backup.", "Remove the ID.", "Render, restart, and inspect logs."),
            ((f"reforger {s} mod list", "find the ID"), (f"reforger {s} backup", "safety copy"), (f"reforger mods remove {s} --id MOD_ID", "remove from config"), (f"reforger render {s}", "regenerate"), (f"reforger restart {s}", "apply")),
            "A scenario can depend on the mod you are removing. Change the scenario first if necessary.",
        ),
        HelpTopic(
            "change-settings",
            "Configuration",
            "I changed a name, password, map, port, or player limit. What next?",
            "Saved settings do not affect a running process until the generated server config is rendered and the server is restarted.",
            ("Open the guided editor and save the change.", "Render the selected server.", "Restart it.", "Use Details or Query to verify the result."),
            ((f"reforger {s} edit", "guided settings"), (f"reforger render {s}", "regenerate config"), (f"reforger restart {s}", "apply it"), (f"reforger info {s}", "verify configuration")),
        ),
        HelpTopic(
            "players-cannot-connect",
            "Connection problems",
            "Players cannot find or connect to the server. What do I check?",
            "Most connection failures are a stopped process, wrong public address, or a UDP rule missing from either the host firewall or provider firewall.",
            ("Confirm the process is running and the live query answers.", "Check the public address shown in the invite.", "Show the game and query UDP ports.", "Open both ports in the OS firewall and the VPS/cloud firewall.", "Retest from outside the server's own network."),
            ((f"reforger status {s}", "tracked process"), (f"reforger query {s}", "live response"), (f"reforger {s} invite", "public address"), (f"reforger ports {s}", "required UDP ports")),
            "TCP-only rules are not enough; both listed ports are UDP.",
        ),
        HelpTopic(
            "server-wont-start",
            "Troubleshooting",
            "The server will not start or stops immediately. What now?",
            "Run the readiness checks, then read the newest startup log. They cover missing files, bad config, port collisions, disk space, and host dependencies.",
            ("Run Health and fix the first failing item.", "Render again to catch invalid configuration.", "Start once, then inspect regular and systemd logs.", "Use Debug when the normal log does not show the cause."),
            ((f"reforger check {s}", "readiness scorecard"), (f"reforger render {s}", "validate and regenerate"), (f"reforger {s} logs", "profile log"), (f"reforger logs {s} --systemd", "service journal"), (f"reforger debug {s}", "foreground diagnosis")),
        ),
        HelpTopic(
            "version-mismatch",
            "Troubleshooting",
            "Players see a version mismatch or required-mod error. How do I fix it?",
            "Bring the dedicated server and Workshop definitions current, then restart so the generated config and downloaded content agree.",
            ("Update the dedicated-server files.", "Re-apply each recently changed Workshop URL.", "Render and restart.", "Have players update the same mods and reconnect.", "Read logs for the exact mod ID if the error remains."),
            ((f"reforger {s} update", "game/server version"), (f"reforger {s} mod add <workshop-url>", "Workshop version and dependencies"), (f"reforger render {s}", "write versions"), (f"reforger restart {s}", "reload everything")),
        ),
        HelpTopic(
            "logs",
            "Troubleshooting",
            "Where are the logs, and which log view should I use?",
            "The standard view reads the latest profile log. A systemd-managed server can also report service or launch failures in the journal.",
            ("Use Where to see the exact profile path.", "Read the latest normal log.", "Follow it live while reproducing the issue.", "Check the systemd journal when the process never gets far enough to create a profile log."),
            ((f"reforger {s} where", "all resolved paths"), (f"reforger {s} logs", "latest profile log"), (f"reforger {s} tail", "live profile log"), (f"reforger logs {s} --systemd --follow", "live service journal")),
        ),
        HelpTopic(
            "backup-restore",
            "Safety and recovery",
            "How do I back up, restore, or undo a bad change?",
            "Create backups before maintenance. Restore into a separate directory first when you want to inspect contents without overwriting the active setup.",
            ("Create a named server backup.", "List available archives.", "For a cautious test, restore an archive to a new directory.", "Stop the server before an intentional in-place recovery and confirm the restore prompt.", "Render and start after recovery."),
            ((f"reforger {s} backup", "create backup"), ("reforger backup list", "available archives"), ("reforger backup restore --target ./restore-test", "safe inspection copy"), ("reforger backup restore", "interactive restore")),
            "A normal backup excludes downloaded server/mod files; add --include-downloads only when you need a much larger archive.",
        ),
        HelpTopic(
            "performance",
            "Performance and capacity",
            "The server is lagging. What should I check?",
            "Measure CPU, RAM, disk usage, players, ping, and uptime before changing limits. Correlate spikes with the logs and recently added mods.",
            ("Watch resources during the problem.", "Check logs for script, network, and Workshop errors.", "Compare player load and recently changed mods.", "Verify free disk space and host health.", "Remove or roll back one recent change at a time."),
            ((f"reforger {s} resources --watch 2", "live resource view"), (f"reforger {s} tail", "correlate messages"), (f"reforger check {s}", "disk and host checks"), (f"reforger {s} mod list", "review the mod set")),
            "The query protocol does not expose server tick/FPS, so use process resources, player experience, and logs together.",
        ),
        HelpTopic(
            "disk-space",
            "Performance and capacity",
            "Disk space is low. What can I inspect safely?",
            "Use the resource and path views to identify where installs, profiles, downloads, and backups live before deleting anything.",
            ("Check deployment disk usage.", "Print all active paths.", "List backups and retain only the archives your policy requires.", "Inspect old logs and unused server deployments manually.", "Run Health again after cleanup."),
            ((f"reforger {s} resources", "deployment usage"), (f"reforger {s} where", "exact directories"), ("reforger backup list", "backup inventory"), (f"reforger check {s}", "verify free space")),
            "Do not delete the active config, profile, generated config, or current install based only on a folder name.",
        ),
        HelpTopic(
            "ports-firewall",
            "Connection problems",
            "How do ports and firewalls work for multiple servers?",
            "Every instance needs distinct game and query UDP ports. Those ports must be allowed both on the host and in the VPS/cloud provider security rules.",
            ("Print the assigned ports and look for collisions.", "Let the fixer assign safe missing/colliding ports when needed.", "Preview local firewall changes.", "Apply the host rules with privileges.", "Mirror the same UDP rules at the hosting provider."),
            (("reforger ports", "all assignments and copyable rules"), ("reforger ports --fix", "save safe unique ports"), ("reforger firewall apply --dry-run", "preview"), ("sudo reforger firewall apply", "apply locally")),
        ),
        HelpTopic(
            "admins-passwords",
            "Configuration",
            "How do I change passwords or server admins?",
            "Use the guided editor so admin Steam IDs are added or removed deliberately and secrets are not exposed in command history.",
            ("Open the server editor.", "Choose Players, passwords, and admins.", "Make and preview the changes, then save.", "Render and restart.", "Share player passwords privately; never post admin passwords in support output."),
            ((f"reforger {s} edit", "guided editor"), (f"reforger render {s}", "regenerate"), (f"reforger restart {s}", "apply")),
        ),
        HelpTopic(
            "startup-service",
            "Services and automation",
            "How do I make the server start after a reboot?",
            "On Linux, install and enable the generated systemd service. On Windows, install the generated Scheduled Task.",
            ("Render the current configuration.", "Install the platform service with administrator privileges.", "Enable/start it on Linux, or verify the Windows task.", "Reboot only after checking service status and logs."),
            ((f"sudo reforger systemd install --instance {s}", "Linux service file"), (f"sudo reforger service enable {s}", "Linux auto-start"), (f"sudo reforger service start {s}", "Linux start now"), (f"reforger windows-task install --instance {s}", "Windows auto-start (Admin PowerShell)")),
        ),
        HelpTopic(
            "move-server",
            "Safety and recovery",
            "How do I copy or move a server definition?",
            "Export/import moves the portable server definition. It does not copy installed game files or unrelated secrets.",
            ("Export the source server to JSON.", "Copy that file to the destination host.", "Set up Reforger Deployer there and import under a unique name.", "Review addresses, ports, paths, and passwords.", "Run the first-deploy preview, then apply it."),
            ((f"reforger {s} export server.json", "portable definition"), ("reforger import server.json --as new-server", "destination import"), ("reforger new-server edit", "review host-specific settings"), ("reforger launch new-server", "preview deployment"), ("sudo reforger launch new-server --apply", "deploy on Linux")),
        ),
        HelpTopic(
            "first-deploy",
            "Getting started",
            "What are the steps for a brand-new server?",
            "The guided setup creates the definition; Launch then renders, backs up, installs files, prepares firewall/service integration, starts, and shows connection details.",
            ("Run the setup wizard.", "Open the new server's control room and review Details.", "Preview Launch.", "Apply Launch with the required privileges.", "Open provider UDP rules if the host is a VPS.", "Query it and create a player invite."),
            (("reforger setup", "create definition"), (f"reforger {s}", "control room"), (f"reforger launch {s}", "preview"), (f"sudo reforger launch {s} --apply", "apply on Linux"), (f"reforger {s} invite", "share connection info")),
        ),
        HelpTopic(
            "get-support",
            "Troubleshooting",
            "What information should I collect before asking for help?",
            "Collect paths, readiness checks, status, and the relevant log excerpt. Redact secrets and private network details before sharing.",
            ("Run the path and health views.", "Capture tracked and live status.", "Copy only the log section around the failure.", "Describe what changed, the exact command used, and the expected result.", "Remove passwords, tokens, and sensitive addresses."),
            ((f"reforger {s} where", "resolved paths"), (f"reforger check {s}", "readiness"), (f"reforger status {s}", "process status"), (f"reforger query {s}", "live status"), (f"reforger {s} logs", "recent errors")),
            "Never share server/admin passwords, Discord bot tokens, private keys, or full unredacted config files.",
        ),
    )


def show_helpdesk(topic: str | None = None, server: str | None = None) -> None:
    """Show a single runbook or open the interactive Reforger help desk."""
    topics = _topics(server or "<server>")
    if topic:
        match = _find_topic(topics, topic)
        if not match:
            available = ", ".join(item.slug for item in topics)
            raise SystemExit(f"Unknown help topic: {topic}\nAvailable topics: {available}")
        _print_topic(match)
        return
    _interactive(topics, server)


def _interactive(topics: tuple[HelpTopic, ...], server: str | None) -> None:
    while True:
        heading("Reforger Help Desk", f"Step-by-step answers{f' for {server}' if server else ''}")
        categories = list(dict.fromkeys(item.category for item in topics))
        for index, category in enumerate(categories, start=1):
            count = sum(item.category == category for item in topics)
            print(f"  {index}. {category} ({count})")
        print("  S. Search questions")
        print("  0. Back\n")
        choice = input("Choose a category or search: ").strip().lower()
        if choice in {"0", "back", "quit", "exit"}:
            return
        if choice in {"s", "search", "/"}:
            query = input("Search words: ").strip()
            matches = _search(topics, query)
            if not matches:
                note("No matching questions. Try fewer or different words.")
                continue
            _topic_menu(matches, f"Search: {query}")
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(categories):
            category = categories[int(choice) - 1]
            _topic_menu(tuple(item for item in topics if item.category == category), category)
            continue
        note("Choose one of the numbers shown, or S to search.")


def _topic_menu(topics: tuple[HelpTopic, ...], title: str) -> None:
    while True:
        heading(title, "Choose a question")
        for index, topic in enumerate(topics, start=1):
            print(f"  {index}. {topic.question}")
        print("  0. Back\n")
        choice = input("Question number: ").strip().lower()
        if choice in {"0", "back", "quit", "exit"}:
            return
        if choice.isdigit() and 1 <= int(choice) <= len(topics):
            _print_topic(topics[int(choice) - 1])
            input("\nPress Enter to return to the questions...")
        else:
            note("Choose one of the question numbers shown.")


def _print_topic(topic: HelpTopic) -> None:
    heading(topic.question, topic.category)
    print(f"\n{topic.answer}")
    section("Steps")
    for index, step in enumerate(topic.steps, start=1):
        print(f"  {index}. {step}")
    if topic.commands:
        section("Commands")
        commands(topic.commands)
    if topic.caution:
        section("Important")
        note(topic.caution)


def _find_topic(topics: tuple[HelpTopic, ...], value: str) -> HelpTopic | None:
    normalized = value.strip().lower().replace("_", "-").replace(" ", "-")
    exact = next((item for item in topics if item.slug == normalized), None)
    if exact:
        return exact
    matches = _search(topics, value)
    return matches[0] if len(matches) == 1 else None


def _search(topics: tuple[HelpTopic, ...], query: str) -> tuple[HelpTopic, ...]:
    words = [word.lower() for word in query.replace("-", " ").split() if word]
    if not words:
        return ()
    return tuple(
        item
        for item in topics
        if all(word in f"{item.slug} {item.category} {item.question} {item.answer}".lower() for word in words)
    )
