import json
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config.json"
NODE_DIR = ROOT_DIR / "node"
STATE_DIR = ROOT_DIR / ".servergo"
PID_FILE = STATE_DIR / "server.pid"

DEFAULT_CONFIG: dict[str, Any] = {
    "projectName": "ServerGo Platform",
    "defaultPort": 3000,
    "autoOpenBrowser": True,
    "ui": {
        "clearScreenOnMenu": True,
        "pauseAfterAction": True,
    },
    "scaffold": {
        "defaultOutputDir": "generated-projects",
        "createPublicDir": True,
        "createLogsDir": True,
        "createScriptsDir": True,
    },
    "apiManager": {
        "servicesDir": "services",
        "defaultRuntime": "node",
    },
    "future": {
        "backupsDir": "backups",
        "autoRoadmap": True,
    },
    "plugins": {
        "enabled": [],
        "defaultTimeoutSec": 120,
    },
    "https": {
        "enabled": False,
        "autoGenerateCert": True,
        "keyPath": "certs/server.key",
        "certPath": "certs/server.crt",
        "redirectHttp": True,
        "httpPort": 8080,
    },
    "automation": {
        "startAllApisWithMainServer": False,
        "runEnabledPluginsOnStart": False,
    },
    "support": {
        "repoUrl": "https://github.com/owner/servergo",
    },
    "python": {
        "bannerDelayMs": 25
    }
}


def load_config() -> dict[str, Any]:
    data: dict[str, Any] = {}
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
    return _merge_dict(DEFAULT_CONFIG, data)


def save_config(config: dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=2, ensure_ascii=True)
        file.write("\n")


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def _merge_dict(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in base.items():
        if isinstance(value, dict):
            provided = override.get(key, {})
            if isinstance(provided, dict):
                result[key] = _merge_dict(value, provided)
            else:
                result[key] = value
        else:
            result[key] = override.get(key, value)

    for key, value in override.items():
        if key not in result:
            result[key] = value

    return result
