from __future__ import annotations

import html


def page(title: str, body: str, csrf: str = "") -> str:
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/htmx.org@2.0.4"></script>
</head><body class="min-h-screen bg-zinc-950 text-zinc-100">
<main class="mx-auto max-w-7xl p-6" data-csrf="{html.escape(csrf)}">{body}</main>
</body></html>"""
