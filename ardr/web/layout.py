from __future__ import annotations

import html


def page(title: str, body: str, csrf: str = "") -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/htmx.org@2.0.4"></script>
<style>
  ::selection {{ background: #34d399; color: #052e26; }}
  .grid-glow {{ background-image: radial-gradient(circle at 10% 0%, rgba(16,185,129,.16), transparent 30rem), radial-gradient(circle at 90% 20%, rgba(56,189,248,.10), transparent 26rem); }}
  .card {{ box-shadow: 0 18px 60px rgba(0,0,0,.18); }}
  .htmx-request .loading {{ display: inline-flex; }}
  .loading {{ display: none; }}
</style>
</head><body class="min-h-screen bg-slate-950 text-slate-100 antialiased">
<main class="grid-glow mx-auto min-h-screen max-w-7xl p-4 sm:p-6" data-csrf="{html.escape(csrf)}">{body}</main>
</body></html>"""
