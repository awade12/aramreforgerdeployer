from __future__ import annotations

import html
from typing import Any


def page(title: str, body: str, csrf: str = "") -> str:
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/htmx.org@2.0.4"></script>
</head><body class="bg-slate-950 text-slate-100 min-h-screen">
<main class="mx-auto max-w-7xl p-6" data-csrf="{html.escape(csrf)}">{body}</main>
</body></html>"""


def login(error: str = "") -> str:
    err = f"<p class='text-sm text-red-300'>{html.escape(error)}</p>" if error else ""
    return page(
        "ARDR Login",
        f"""<section class="mx-auto mt-24 max-w-sm rounded-lg border border-slate-800 bg-slate-900 p-6">
<h1 class="text-xl font-semibold">ARDR Dashboard</h1>
<p class="mt-1 text-sm text-slate-400">Sign in to manage your Reforger servers.</p>
<form method="post" action="/login" class="mt-6 space-y-4">
{err}
<input name="password" type="password" autofocus class="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2" placeholder="Password">
<button class="w-full rounded bg-emerald-500 px-3 py-2 font-medium text-slate-950">Sign in</button>
</form></section>""",
    )


def dashboard(instances: list[dict[str, Any]], selected: str, csrf: str, panel: str) -> str:
    links = "".join(_instance_link(i, selected) for i in instances)
    body = f"""<div class="flex items-center justify-between gap-4">
<div><h1 class="text-2xl font-semibold">ARDR Dashboard</h1><p class="text-sm text-slate-400">Arma Reforger server control panel</p></div>
<a href="/logout" class="rounded border border-slate-700 px-3 py-2 text-sm">Logout</a></div>
<div class="mt-6 grid gap-6 lg:grid-cols-[260px_1fr]">
<aside class="rounded-lg border border-slate-800 bg-slate-900 p-3"><div class="space-y-2">{links}</div></aside>
<section id="panel" class="rounded-lg border border-slate-800 bg-slate-900 p-4">{panel}</section>
</div>"""
    return page("ARDR Dashboard", body, csrf)


def instance_panel(instance: dict[str, Any], status: str, service: str, csrf: str, output: str = "") -> str:
    name = html.escape(instance["name"])
    server = instance.get("server", {})
    out = f"<pre class='mt-4 max-h-72 overflow-auto rounded bg-slate-950 p-3 text-xs'>{html.escape(output)}</pre>" if output else ""
    return f"""<div class="flex flex-wrap items-start justify-between gap-4">
<div><h2 class="text-xl font-semibold">{name}</h2><p class="text-sm text-slate-400">{html.escape(server.get('name', instance['name']))}</p></div>
<span class="rounded bg-slate-800 px-3 py-1 text-sm">{html.escape(status)}</span></div>
<div class="mt-4 grid gap-3 md:grid-cols-4">
{_metric('Game UDP', instance['port'])}{_metric('Query UDP', instance['queryPort'])}{_metric('Service', service or 'unknown')}{_metric('Players', server.get('maxPlayers', 64))}
</div>
<div class="mt-5 flex flex-wrap gap-2">{_button(name, 'start', csrf)}{_button(name, 'stop', csrf)}{_button(name, 'restart', csrf)}{_button(name, 'backup', csrf)}{_button(name, 'render', csrf)}{_button(name, 'query', csrf)}</div>
<form class="mt-5 flex flex-wrap gap-2" hx-post="/mods/add" hx-target="#panel">
<input type="hidden" name="csrf" value="{html.escape(csrf)}">
<input type="hidden" name="instance" value="{name}">
<input name="mod_id" class="min-w-48 rounded border border-slate-700 bg-slate-950 px-3 py-2" placeholder="Mod ID">
<input name="mod_name" class="min-w-48 rounded border border-slate-700 bg-slate-950 px-3 py-2" placeholder="Mod name">
<button class="rounded bg-sky-500 px-3 py-2 font-medium text-slate-950">Add mod</button></form>
<div class="mt-5 text-sm text-slate-300"><p>Connect: <code>&lt;VPS_PUBLIC_IP&gt;:{instance['port']}</code></p>
<p>Config: <code>instances/{name}.json</code></p></div>{out}"""


def _instance_link(instance: dict[str, Any], selected: str) -> str:
    name = html.escape(instance["name"])
    active = "bg-emerald-500 text-slate-950" if instance["name"] == selected else "bg-slate-800"
    return f"<a class='block rounded px-3 py-2 {active}' hx-get='/panel?instance={name}' hx-target='#panel' href='/?instance={name}'>{name}</a>"


def _metric(label: str, value: object) -> str:
    return f"<div class='rounded bg-slate-950 p-3'><div class='text-xs text-slate-500'>{html.escape(label)}</div><div class='mt-1 font-medium'>{html.escape(str(value))}</div></div>"


def _button(instance: str, action: str, csrf: str) -> str:
    label = action.title()
    return f"<form hx-post='/action' hx-target='#panel'><input type='hidden' name='csrf' value='{html.escape(csrf)}'><input type='hidden' name='instance' value='{instance}'><input type='hidden' name='action' value='{action}'><button class='rounded bg-slate-100 px-3 py-2 text-sm font-medium text-slate-950'>{label}</button></form>"
