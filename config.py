# -*- coding: utf-8 -*-
"""
Configuration loader for Bitcoin-Cracker.
Manages proxy settings, scanner parameters, seed checker, and RPC endpoints.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent

_DEFAULTS = {
    "proxies": {
        "enabled": True,
        "rotation_mode": "round-robin",   # "round-robin" or "random"
        "proxy_list": [],
        "proxy_file": "proxies.txt",
        "validation_interval_sec": 300,
        "timeout_sec": 15,
        "max_retries": 3,
        "fallback_to_direct": False
    },
    "scanner": {
        "threads": 20,
        "request_timeout_sec": 30,
        "retry_on_fail": True,
        "max_retries": 3,
        "delay_between_requests_ms": 100
    },
    "seed_checker": {
        "seed_file": "seeds.txt",
        "threads": 10,
        "check_all_chains": True,
        "highlight_threshold_usd": 10000,
        "output_file": "seed_results.txt"
    },
    "rpc_endpoints": {
        "bitcoin": "https://blockstream.info/api"
    },
    "export": {
        "default_format": "txt",          # "txt", "csv", "json"
        "output_directory": "./results",
        "include_usd_value": True
    },
    "verbose_logging": False
}


def load_config() -> dict:
    """
    Load configuration from config.json with fallback to defaults.
    Creates config.json if missing.
    """
    config_path = BASE_DIR / "config.json"
    if not config_path.exists():
        save_config(_DEFAULTS)
        return dict(_DEFAULTS)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(_DEFAULTS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, IOError):
        return dict(_DEFAULTS)


def save_config(config: dict) -> None:
    """Save configuration to config.json with pretty formatting."""
    config_path = BASE_DIR / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def get_proxy_config(config: dict) -> dict:
    """Return proxy settings dict."""
    return config.get("proxies", _DEFAULTS["proxies"])


def get_scanner_config(config: dict) -> dict:
    """Return scanner settings dict."""
    return config.get("scanner", _DEFAULTS["scanner"])


def get_seed_checker_config(config: dict) -> dict:
    """Return seed checker settings dict."""
    return config.get("seed_checker", _DEFAULTS["seed_checker"])


def get_rpc_endpoints(config: dict) -> dict:
    """Return RPC endpoints dict."""
    return config.get("rpc_endpoints", _DEFAULTS["rpc_endpoints"])


def get_export_config(config: dict) -> dict:
    """Return export settings dict."""
    return config.get("export", _DEFAULTS["export"])


def set_proxy_enabled(config: dict, enabled: bool) -> dict:
    """Enable/disable proxy usage and save."""
    config.setdefault("proxies", {})["enabled"] = enabled
    save_config(config)
    return config


def add_proxy(config: dict, proxy_str: str) -> dict:
    """Add a proxy to the list (format: protocol://user:pass@host:port) and save."""
    proxies = config.setdefault("proxies", {})
    if "proxy_list" not in proxies:
        proxies["proxy_list"] = []
    proxies["proxy_list"].append(proxy_str.strip())
    save_config(config)
    return config


def remove_proxy(config: dict, index: int) -> dict:
    """Remove a proxy by index (0-based) and save."""
    proxies = config.get("proxies", {})
    if "proxy_list" in proxies and 0 <= index < len(proxies["proxy_list"]):
        del proxies["proxy_list"][index]
        save_config(config)
    return config


def set_threads(config: dict, threads: int) -> dict:
    """Set number of scanner threads and save."""
    config.setdefault("scanner", {})["threads"] = threads
    save_config(config)
    return config