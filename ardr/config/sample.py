from __future__ import annotations

from typing import Any


def sample_config() -> dict[str, Any]:
    return {
        "baseDir": "./deployments",
        "steamcmd": "steamcmd",
        "instanceDir": "instances",
        "defaultInstance": "reforger-1",
        "instances": [
            _sample_instance("reforger-1", 2001, 17777),
            _sample_instance("reforger-2", 2003, 17779),
        ],
    }


def _sample_instance(name: str, port: int, query_port: int) -> dict[str, Any]:
    return {
        "name": name,
        "branch": "stable",
        "port": port,
        "queryPort": query_port,
        "maxFPS": 60,
        "profileDir": f"./profiles/{name}",
        "server": {
            "name": f"My Reforger Server {name.rsplit('-', 1)[-1]}",
            "password": "",
            "adminPassword": "change-this-admin-password",
            "scenarioId": "{ECC61978EDCC2B5A}Missions/23_Campaign.conf",
            "maxPlayers": 64,
            "visible": True,
            "gameHostRegisterBindAddress": "",
            "gameHostRegisterPort": 0,
            "publicAddress": "",
        },
        "mods": [],
    }
