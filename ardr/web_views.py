from __future__ import annotations

import html
from typing import Any


def page(title: str, body: str, csrf: str = "") -> str:
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/htmx.org@2.0.4"></script>
</head><body class="min-h-screen bg-zinc-950 text-zinc-100">
<main class="mx-auto max-w-7xl p-6" data-csrf="{html.escape(csrf)}">{body}</main>
</body></html>"""


def login(error: str = "") -> str:
    err = f"<p class='text-sm text-red-300'>{html.escape(error)}</p>" if error else ""
    return page(
        "ARDR Login",
        f"""<section class="mx-auto mt-24 max-w-sm rounded-lg border border-zinc-800 bg-zinc-900 p-6">
<h1 class="text-xl font-semibold">ARDR Dashboard</h1>
<p class="mt-1 text-sm text-zinc-400">Sign in to manage your Reforger servers.</p>
<form method="post" action="/login" class="mt-6 space-y-4">
{err}
<input name="password" type="password" autofocus class="w-full rounded border border-zinc-700 bg-zinc-950 px-3 py-2" placeholder="Password">
<button class="w-full rounded bg-emerald-500 px-3 py-2 font-medium text-zinc-950">Sign in</button>
</form></section>""",
    )


def dashboard(instances: list[dict[str, Any]], selected: str, csrf: str, panel: str) -> str:
    links = "".join(_instance_link(i, selected) for i in instances)
    body = f"""<div class="flex items-center justify-between gap-4">
<div><h1 class="text-2xl font-semibold">ARDR Dashboard</h1><p class="text-sm text-zinc-400">Arma Reforger server control panel</p></div>
<a href="/logout" class="rounded border border-zinc-700 px-3 py-2 text-sm">Logout</a></div>
<div class="mt-6 grid gap-6 lg:grid-cols-[260px_1fr]">
<aside class="rounded-lg border border-zinc-800 bg-zinc-900 p-3"><div class="space-y-2">{links}</div></aside>
<section id="panel" class="rounded-lg border border-zinc-800 bg-zinc-900 p-4">{panel}</section>
</div>"""
    return page("ARDR Dashboard", body, csrf)


def instance_panel(
    instance: dict[str, Any],
    details: dict[str, Any],
    csrf: str,
    output: str = "",
    action: str = "",
) -> str:
    name = html.escape(instance["name"])
    server = instance.get("server", {})
    banner = _action_banner(action, output)
    out = _activity(output)
    running = "online" if details["running"] else "offline"
    return f"""<div hx-get="/panel?instance={name}" hx-trigger="every 10s" hx-swap="outerHTML">
<div class="flex flex-wrap items-start justify-between gap-4">
<div><h2 class="text-xl font-semibold">{name}</h2><p class="text-sm text-zinc-400">{html.escape(server.get('name', instance['name']))}</p></div>
<div class="flex flex-wrap gap-2">{_badge(running, details['running'])}{_badge('systemd ' + details['service'], details['service'] == 'active')}</div></div>
{banner}
<div class="mt-4 grid gap-3 md:grid-cols-4">
{_metric('Runtime', details['runtime'])}{_metric('PID', details.get('pid') or 'none')}{_metric('Game UDP', instance['port'])}{_metric('Query UDP', instance['queryPort'])}
{_metric('Players', server.get('maxPlayers', 64))}{_metric('Scenario', server.get('scenarioId', ''))}{_metric('Executable', 'found' if details['serverExeExists'] else 'missing')}{_metric('Checked', details['checkedAt'])}
</div>
<div class="mt-5 flex flex-wrap gap-2">{_button(name, 'start', csrf, 'bg-emerald-500')}{_button(name, 'stop', csrf, 'bg-red-400')}{_button(name, 'restart', csrf, 'bg-amber-400')}{_button(name, 'status', csrf)}{_button(name, 'logs', csrf)}{_button(name, 'backup', csrf)}{_button(name, 'render', csrf)}{_button(name, 'query', csrf)}</div>
<form class="mt-5 flex flex-wrap gap-2" hx-post="/mods/add" hx-target="#panel">
<input type="hidden" name="csrf" value="{html.escape(csrf)}">
<input type="hidden" name="instance" value="{name}">
<input name="mod_id" class="min-w-48 rounded border border-zinc-700 bg-zinc-950 px-3 py-2" placeholder="Mod ID">
<input name="mod_name" class="min-w-48 rounded border border-zinc-700 bg-zinc-950 px-3 py-2" placeholder="Mod name">
<button class="rounded bg-sky-400 px-3 py-2 font-medium text-zinc-950">Add mod</button></form>
{_paths(instance, details)}
{out}</div>"""


def _instance_link(instance: dict[str, Any], selected: str) -> str:
    name = html.escape(instance["name"])
    active = "bg-emerald-500 text-zinc-950" if instance["name"] == selected else "bg-zinc-800"
    return f"<a class='block rounded px-3 py-2 {active}' hx-get='/panel?instance={name}' hx-target='#panel' href='/?instance={name}'>{name}</a>"


def _metric(label: str, value: object) -> str:
    return f"<div class='rounded bg-zinc-950 p-3'><div class='text-xs text-zinc-500'>{html.escape(label)}</div><div class='mt-1 break-words text-sm font-medium'>{html.escape(str(value))}</div></div>"


def _button(instance: str, action: str, csrf: str, color: str = "bg-zinc-100") -> str:
    label = action.title()
    return f"<form hx-post='/action' hx-target='#panel'><input type='hidden' name='csrf' value='{html.escape(csrf)}'><input type='hidden' name='instance' value='{instance}'><input type='hidden' name='action' value='{action}'><button class='rounded {color} px-3 py-2 text-sm font-medium text-zinc-950'>{label}</button></form>"


def _badge(label: str, good: bool) -> str:
    color = "bg-emerald-500 text-zinc-950" if good else "bg-zinc-800 text-zinc-200"
    return f"<span class='rounded px-3 py-1 text-sm font-medium {color}'>{html.escape(label)}</span>"


def _action_banner(action: str, output: str) -> str:
    if not action:
        return ""
    failed = "ERROR:" in output or "Unknown action:" in output
    color = "border-red-500 bg-red-950 text-red-100" if failed else "border-emerald-500 bg-emerald-950 text-emerald-100"
    title = "Action failed" if failed else "Action complete"
    return f"<div class='mt-4 rounded border {color} p-3 text-sm'><strong>{title}:</strong> {html.escape(action.title())}</div>"


def _activity(output: str) -> str:
    if not output:
        return "<div class='mt-5 rounded bg-zinc-950 p-3 text-sm text-zinc-400'>No action output yet.</div>"
    return f"<div class='mt-5'><div class='mb-2 text-sm font-medium text-zinc-300'>Activity</div><pre class='max-h-80 overflow-auto rounded bg-zinc-950 p-3 text-xs'>{html.escape(output)}</pre></div>"


def _paths(instance: dict[str, Any], details: dict[str, Any]) -> str:
    connect = f"&lt;VPS_PUBLIC_IP&gt;:{instance['port']}"
    rows = [
        ("Connect", connect),
        ("Config", details["configFile"]),
        ("Install", details["installDir"]),
        ("Profile/logs", details["profileDir"]),
        ("Generated", details["generatedDir"]),
        ("PID file", details["pidFile"]),
    ]
    items = "".join(f"<div><dt class='text-zinc-500'>{k}</dt><dd class='break-all'><code>{html.escape(str(v))}</code></dd></div>" for k, v in rows)
    return f"<dl class='mt-5 grid gap-3 rounded bg-zinc-950 p-3 text-sm md:grid-cols-2'>{items}</dl>"
