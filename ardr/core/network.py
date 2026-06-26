from __future__ import annotations

import ipaddress
import socket
from typing import Any


def connect_address(instance: dict[str, Any]) -> tuple[str, str]:
    server = instance.get("server", {})
    configured = str(server.get("publicAddress", "")).strip()
    if configured:
        return configured, "configured publicAddress"
    detected = detect_host_ip()
    if detected:
        return detected, "detected host IP"
    return "<set publicAddress>", "unknown"


def detect_host_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("1.1.1.1", 80))
            return str(sock.getsockname()[0])
    except OSError:
        pass
    for candidate in _host_addresses():
        if _usable_host_ip(candidate):
            return candidate
    return ""


def _host_addresses() -> list[str]:
    addresses: list[str] = []
    try:
        addresses.extend(socket.gethostbyname_ex(socket.gethostname())[2])
    except OSError:
        pass
    try:
        for result in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            addresses.append(str(result[4][0]))
    except OSError:
        pass
    return addresses


def _usable_host_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    return not (ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified)


def address_note(host: str, source: str) -> str:
    if source == "configured publicAddress":
        return "Using server.publicAddress from the instance config."
    if source == "unknown":
        return "Set server.publicAddress in the instance config to show the real direct-connect address."
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return "Detected from this host's outbound network interface."
    if ip.is_private or ip.is_loopback or ip.is_link_local:
        return "Detected a private/local address. If players connect from the internet, set server.publicAddress to the VPS public IP."
    return "Detected from this host's outbound network interface."
