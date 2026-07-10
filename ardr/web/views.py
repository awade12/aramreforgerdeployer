from __future__ import annotations

import html
from typing import Any

from .layout import page


def login(error: str = "") -> str:
    err = f"<p class='rounded-lg border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-200'>{html.escape(error)}</p>" if error else ""
    return page("Sign in · Reforger", f"""<section class="card mx-auto mt-20 max-w-md rounded-3xl border border-white/10 bg-slate-900/85 p-7 backdrop-blur">
<div class="mb-8"><div class="mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-emerald-400 text-xl text-slate-950">R</div>
<h1 class="text-2xl font-bold tracking-tight">Welcome back</h1><p class="mt-2 text-sm leading-6 text-slate-400">Sign in to your calm, simple Reforger server room.</p></div>
<form method="post" action="/login" class="space-y-4">{err}
<label class="block text-sm font-medium text-slate-300">Dashboard password<input name="password" type="password" autofocus required class="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none transition focus:border-emerald-400" placeholder="Enter password"></label>
<button class="w-full rounded-xl bg-emerald-400 px-4 py-3 font-semibold text-slate-950 transition hover:bg-emerald-300">Open dashboard</button>
</form></section>""")


def dashboard(instances: list[dict[str, Any]], selected: str, csrf: str, panel: str) -> str:
    links = "".join(_instance_link(i, selected) for i in instances)
    count = len(instances)
    body = f"""<header class="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-5">
<a href="/" class="flex items-center gap-3"><span class="grid h-10 w-10 place-items-center rounded-xl bg-emerald-400 font-bold text-slate-950">R</span><span><strong class="block text-lg tracking-tight">Reforger Control Room</strong><span class="text-sm text-slate-400">Your servers, without the headache</span></span></a>
<div class="flex items-center gap-3"><span class="hidden rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300 sm:block">{count} server{'s' if count != 1 else ''}</span><a href="/logout" class="rounded-xl border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:bg-slate-800">Sign out</a></div>
</header>
<div class="mt-6 grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
<aside class="space-y-4"><nav class="card rounded-2xl border border-white/10 bg-slate-900/80 p-3"><p class="px-2 pb-2 text-xs font-semibold uppercase tracking-widest text-slate-500">Your servers</p><div class="space-y-1">{links}</div></nav>
<div class="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-4"><p class="font-semibold text-emerald-200">Need a hand?</p><p class="mt-1 text-sm leading-5 text-emerald-50/75">Start with <strong>Check readiness</strong>. It tells you exactly what needs attention.</p></div></aside>
<section id="panel" class="min-w-0">{panel}</section>
</div>"""
    return page("Reforger Control Room", body, csrf)


def instance_panel(instance: dict[str, Any], details: dict[str, Any], csrf: str, output: str = "", action: str = "") -> str:
    name = html.escape(instance["name"])
    server = instance.get("server", {})
    is_running = details["running"]
    ready = details["serverExeExists"]
    banner = _action_banner(action, output)
    return f"""<div id="panel" hx-get="/panel?instance={name}" hx-trigger="every 15s" hx-swap="outerHTML">
<div class="card overflow-hidden rounded-2xl border border-white/10 bg-slate-900/80">
  <div class="border-b border-white/10 p-5 sm:p-6"><div class="flex flex-wrap items-start justify-between gap-4"><div><p class="text-sm font-medium text-emerald-300">Server control</p><h1 class="mt-1 text-2xl font-bold tracking-tight">{html.escape(server.get('name', instance['name']))}</h1><p class="mt-1 text-sm text-slate-400">{name} · {html.escape(str(details['connectAddress']))}</p></div>{_status_badge(is_running, ready)}</div>
  <div class="mt-5 grid gap-3 sm:grid-cols-3">{_stat('Players', str(server.get('maxPlayers', 64)) + ' slots')}{_stat('Game port', str(instance['port']))}{_stat('Last checked', details['checkedAt'])}</div></div>
  <div class="p-5 sm:p-6">{banner}
    <section><div class="flex items-baseline justify-between gap-2"><div><h2 class="font-semibold">What do you want to do?</h2><p class="mt-1 text-sm text-slate-400">The everyday controls are right here.</p></div><span class="loading rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">Working…</span></div>
    <div class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">{_action_card(name, csrf, 'start', 'Start server', 'Bring it online', 'emerald', disabled=is_running)}{_action_card(name, csrf, 'restart', 'Restart', 'Apply a quick reset', 'amber')}{_action_card(name, csrf, 'stop', 'Stop server', 'Take it offline', 'rose', confirm='Stop this server? Players will be disconnected.')}{_action_card(name, csrf, 'logs', 'View latest logs', 'See what it is doing', 'slate')}</div></section>
    <section class="mt-8"><h2 class="font-semibold">Get ready to play</h2><p class="mt-1 text-sm text-slate-400">Run these in order if this is a new or changed server.</p>
    <div class="mt-4 grid gap-3 md:grid-cols-3">{_action_card(name, csrf, 'check', '1. Check readiness', 'Find setup problems first', 'sky')}{_action_card(name, csrf, 'install', '2. Install or update files', 'Download the server through SteamCMD', 'violet')}{_action_card(name, csrf, 'render', '3. Save server setup', 'Generate config and launch files', 'slate')}</div></section>
    <details class="mt-8 rounded-xl border border-slate-800 bg-slate-950/45"><summary class="cursor-pointer list-none p-4 font-semibold">More tools <span class="ml-2 text-sm font-normal text-slate-500">updates, backups, diagnostics, and live query</span></summary><div class="grid gap-2 border-t border-slate-800 p-4 sm:grid-cols-2 lg:grid-cols-3">{_small_button(name, csrf, 'update', 'Update server')}{_small_button(name, csrf, 'backup', 'Create backup')}{_small_button(name, csrf, 'query', 'Query live status')}{_small_button(name, csrf, 'status', 'Technical status')}{_small_button(name, csrf, 'doctor', 'Run diagnostics')}{_small_button(name, csrf, 'ports', 'Show port help')}{_small_button(name, csrf, 'pause', 'Pause process')}{_small_button(name, csrf, 'resume', 'Resume process')}</div></details>
    {_mods(instance, csrf)}
    {_settings(instance, csrf)}
    {_paths(details)}
    {_activity(output)}
  </div></div></div>"""


def _instance_link(instance: dict[str, Any], selected: str) -> str:
    name = html.escape(instance["name"])
    active = "bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-500/10" if instance["name"] == selected else "text-slate-300 hover:bg-slate-800"
    return f"<a class='flex items-center justify-between rounded-xl px-3 py-3 text-sm font-medium transition {active}' hx-get='/panel?instance={name}' hx-target='#panel' hx-push-url='true' href='/?instance={name}'><span>{name}</span><span class='text-xs opacity-70'>{instance.get('port', '')}</span></a>"


def _status_badge(running: bool, ready: bool) -> str:
    if running:
        return "<span class='rounded-full bg-emerald-400/15 px-3 py-1.5 text-sm font-semibold text-emerald-300'>● Online</span>"
    if ready:
        return "<span class='rounded-full bg-amber-400/15 px-3 py-1.5 text-sm font-semibold text-amber-200'>● Offline</span>"
    return "<span class='rounded-full bg-rose-400/15 px-3 py-1.5 text-sm font-semibold text-rose-200'>● Needs setup</span>"


def _stat(label: str, value: str) -> str:
    return f"<div class='rounded-xl bg-slate-950/65 p-3'><p class='text-xs font-medium uppercase tracking-wide text-slate-500'>{html.escape(label)}</p><p class='mt-1 truncate text-sm font-semibold text-slate-200'>{html.escape(value)}</p></div>"


def _action_card(instance: str, csrf: str, action: str, title: str, description: str, color: str, disabled: bool = False, confirm: str = "") -> str:
    shades = {'emerald': 'border-emerald-400/25 hover:border-emerald-400/60 hover:bg-emerald-400/10', 'amber': 'border-amber-400/25 hover:border-amber-400/60 hover:bg-amber-400/10', 'rose': 'border-rose-400/25 hover:border-rose-400/60 hover:bg-rose-400/10', 'sky': 'border-sky-400/25 hover:border-sky-400/60 hover:bg-sky-400/10', 'violet': 'border-violet-400/25 hover:border-violet-400/60 hover:bg-violet-400/10', 'slate': 'border-slate-700 hover:border-slate-500 hover:bg-slate-800'}[color]
    inactive = "opacity-45 cursor-not-allowed" if disabled else ""
    confirm_attr = f" onsubmit=\"return confirm('{html.escape(confirm, quote=True)}')\"" if confirm else ""
    disabled_attr = " disabled" if disabled else ""
    return f"<form hx-post='/action' hx-target='#panel' hx-indicator='.loading'{confirm_attr}><input type='hidden' name='csrf' value='{html.escape(csrf)}'><input type='hidden' name='instance' value='{instance}'><input type='hidden' name='action' value='{action}'><button{disabled_attr} class='h-full w-full rounded-xl border p-4 text-left transition {shades} {inactive}'><strong class='block text-sm'>{html.escape(title)}</strong><span class='mt-1 block text-xs leading-5 text-slate-400'>{html.escape(description)}</span></button></form>"


def _small_button(instance: str, csrf: str, action: str, label: str) -> str:
    return f"<form hx-post='/action' hx-target='#panel' hx-indicator='.loading'><input type='hidden' name='csrf' value='{html.escape(csrf)}'><input type='hidden' name='instance' value='{instance}'><input type='hidden' name='action' value='{action}'><button class='w-full rounded-lg border border-slate-700 px-3 py-2 text-left text-sm text-slate-300 transition hover:bg-slate-800'>{html.escape(label)}</button></form>"


def _mods(instance: dict[str, Any], csrf: str) -> str:
    name = html.escape(instance['name'])
    mods = instance.get('mods', [])
    listed = ''.join(f"<li class='flex items-center justify-between gap-3 rounded-lg bg-slate-950/65 px-3 py-2 text-sm'><span class='truncate'>{html.escape(str(mod.get('name') or mod.get('modId') or mod.get('id', 'Unnamed mod')))}</span><code class='text-xs text-slate-500'>{html.escape(str(mod.get('modId') or mod.get('id', '')))}</code></li>" for mod in mods)
    empty = "<p class='text-sm text-slate-500'>No mods yet. Add one below when you are ready.</p>" if not listed else f"<ul class='mt-3 space-y-2'>{listed}</ul>"
    return f"<section class='mt-8'><h2 class='font-semibold'>Mods <span class='text-sm font-normal text-slate-500'>({len(mods)})</span></h2>{empty}<form class='mt-3 grid gap-2 sm:grid-cols-[1fr_1fr_auto]' hx-post='/mods/add' hx-target='#panel'><input type='hidden' name='csrf' value='{html.escape(csrf)}'><input type='hidden' name='instance' value='{name}'><input required name='mod_id' class='rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-emerald-400' placeholder='Mod ID'><input name='mod_name' class='rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-emerald-400' placeholder='Friendly mod name (optional)'><button class='rounded-xl bg-sky-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-300'>Add mod</button></form></section>"


def _settings(instance: dict[str, Any], csrf: str) -> str:
    server = instance.get('server', {})
    name = html.escape(instance['name'])
    checked = ' checked' if server.get('visible', True) else ''
    return f"<details class='mt-8 rounded-xl border border-slate-800 bg-slate-950/45'><summary class='cursor-pointer list-none p-4 font-semibold'>Edit the basics <span class='ml-2 text-sm font-normal text-slate-500'>name, passwords, players, ports, and visibility</span></summary><form class='grid gap-3 border-t border-slate-800 p-4 sm:grid-cols-2' hx-post='/settings' hx-target='#panel'><input type='hidden' name='csrf' value='{html.escape(csrf)}'><input type='hidden' name='instance' value='{name}'>{_field('server_name', 'Server name', server.get('name', ''), True)}{_field('scenario_id', 'Scenario ID', server.get('scenarioId', ''), True)}{_field('max_players', 'Player slots', server.get('maxPlayers', 64), True, 'number')}{_field('port', 'Game port', instance.get('port', ''), True, 'number')}{_field('query_port', 'Query port', instance.get('queryPort', ''), True, 'number')}{_field('password', 'Join password (leave blank to keep)', '', False, 'password')}<label class='flex items-center gap-2 text-sm text-slate-300'><input name='visible' type='checkbox' value='yes'{checked} class='h-4 w-4 accent-emerald-400'> Show this server publicly</label><button class='rounded-xl bg-emerald-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-emerald-300'>Save changes</button></form></details>"


def _field(name: str, label: str, value: object, required: bool, input_type: str = 'text') -> str:
    req = ' required' if required else ''
    return f"<label class='block text-sm text-slate-300'>{html.escape(label)}<input name='{name}' type='{input_type}' value='{html.escape(str(value), quote=True)}'{req} class='mt-1.5 w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-emerald-400'></label>"


def _action_banner(action: str, output: str) -> str:
    if not action:
        return ''
    failed = 'ERROR:' in output or 'Unknown action:' in output
    tone = 'border-rose-400/35 bg-rose-400/10 text-rose-100' if failed else 'border-emerald-400/35 bg-emerald-400/10 text-emerald-100'
    title = 'That did not work' if failed else 'Done'
    return f"<div class='mb-6 rounded-xl border {tone} p-4 text-sm'><strong>{title}.</strong> {html.escape(action.title())} {('needs a look below.' if failed else 'finished successfully.')}</div>"


def _activity(output: str) -> str:
    if not output:
        return ''
    return f"<section class='mt-8'><h2 class='mb-2 font-semibold'>What happened</h2><pre class='max-h-80 overflow-auto rounded-xl bg-slate-950 p-4 text-xs leading-5 text-slate-300'>{html.escape(output)}</pre></section>"


def _paths(details: dict[str, Any]) -> str:
    rows = [('Install folder', details['installDir']), ('Profile & logs', details['profileDir']), ('Server config', details['configFile'])]
    values = ''.join(f"<div><dt class='text-slate-500'>{label}</dt><dd class='mt-1 break-all font-mono text-xs text-slate-300'>{html.escape(str(value))}</dd></div>" for label, value in rows)
    return f"<details class='mt-8 text-sm'><summary class='cursor-pointer text-slate-500 hover:text-slate-300'>Technical paths</summary><dl class='mt-3 grid gap-3 rounded-xl bg-slate-950/65 p-4 sm:grid-cols-3'>{values}</dl></details>"
