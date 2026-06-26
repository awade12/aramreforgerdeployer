from __future__ import annotations

import os
import shutil
import sys
from collections.abc import Iterable


def use_color() -> bool:
    return sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def color(text: str, code: str) -> str:
    if not use_color():
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(text: str) -> str:
    return color(text, "1")


def dim(text: str) -> str:
    return color(text, "2")


def good(text: str) -> str:
    return color(text, "32")


def warn(text: str) -> str:
    return color(text, "33")


def bad(text: str) -> str:
    return color(text, "31")


def cyan(text: str) -> str:
    return color(text, "36")


def width(default: int = 88) -> int:
    return max(72, min(shutil.get_terminal_size((default, 24)).columns, 120))


def rule(title: str = "") -> None:
    if title:
        label = f" {title} "
        fill = max(0, width() - len(label))
        print(bold(label + "-" * fill))
    else:
        print(dim("-" * width()))


def heading(title: str, subtitle: str = "") -> None:
    print(bold(title))
    if subtitle:
        print(dim(subtitle))
    print(dim("-" * min(width(), max(28, len(title), len(subtitle)))))


def section(title: str) -> None:
    print()
    print(bold(title))


def kv(rows: Iterable[tuple[str, object]]) -> None:
    materialized = [(label, "" if value is None else str(value)) for label, value in rows]
    if not materialized:
        return
    label_width = max(len(label) for label, _ in materialized)
    for label, value in materialized:
        print(f"  {dim(label.ljust(label_width))}  {value}")


def commands(items: Iterable[tuple[str, str]]) -> None:
    materialized = list(items)
    if not materialized:
        return
    command_width = max(len(command) for command, _ in materialized)
    for command, description in materialized:
        print(f"  {cyan(command.ljust(command_width))}  {dim(description)}")


def table(headers: list[str], rows: list[list[object]]) -> None:
    if not rows:
        print("  " + dim("No rows."))
        return
    text_rows = [[str(cell) for cell in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in text_rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    header = "  " + "  ".join(bold(headers[index].ljust(widths[index])) for index in range(len(headers)))
    print(header)
    print("  " + "  ".join(dim("-" * item_width) for item_width in widths))
    for row in text_rows:
        print("  " + "  ".join(row[index].ljust(widths[index]) for index in range(len(headers))))


def status_label(state: str) -> str:
    normalized = state.lower()
    if normalized in {"ok", "ready", "running", "active", "enabled"}:
        return good(state)
    if normalized in {"warn", "warning", "stopped", "inactive", "unknown"}:
        return warn(state)
    if normalized in {"fail", "failed", "error"}:
        return bad(state)
    return state


def check_line(ok: bool, label: str, detail: str = "") -> None:
    mark = good("OK") if ok else bad("FAIL")
    suffix = f" {dim(detail)}" if detail else ""
    print(f"  [{mark}] {label}{suffix}")


def note(text: str) -> None:
    print(f"  {dim(text)}")
