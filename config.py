"""Configuration loading and validation for the FRITZ!Box WOL tool."""

import json
import re
from pathlib import Path
from typing import Any

_MAC_HEX_RE = re.compile(r"^[0-9a-fA-F]{12}$")


def normalize_mac(mac_address: str) -> str:
    """Validate a MAC address and return its canonical colon-separated form."""
    if not isinstance(mac_address, str):
        raise ValueError("MAC address must be a string")

    compact = mac_address.replace(":", "").replace("-", "").strip()
    if not _MAC_HEX_RE.fullmatch(compact):
        raise ValueError(f"Invalid MAC address: {mac_address!r}")

    compact = compact.upper()
    return ":".join(compact[index:index + 2] for index in range(0, 12, 2))


def load_config(config_path: str) -> dict[str, Any]:
    """Load and validate a JSON configuration file."""
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with path.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in config file: {exc}") from exc

    if not isinstance(config, dict):
        raise ValueError("Configuration root must be a JSON object")

    required_fields = ("host", "username", "devices")
    missing_fields = [field for field in required_fields if not config.get(field)]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    if not isinstance(config["host"], str):
        raise ValueError("'host' must be a string")
    if not isinstance(config["username"], str):
        raise ValueError("'username' must be a string")
    if not isinstance(config["devices"], dict) or not config["devices"]:
        raise ValueError("'devices' must be a non-empty object mapping names to MAC addresses")

    for port_key in ("port", "tr064_port"):
        port = config.get(port_key)
        if port is not None and (
            isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535
        ):
            raise ValueError(f"'{port_key}' must be an integer between 1 and 65535")

    if "use_tls" in config and not isinstance(config["use_tls"], bool):
        raise ValueError("'use_tls' must be true or false")

    for device_name, mac_address in config["devices"].items():
        if not isinstance(device_name, str) or not device_name.strip():
            raise ValueError("Device names must be non-empty strings")
        try:
            config["devices"][device_name] = normalize_mac(mac_address)
        except ValueError as exc:
            raise ValueError(f"Invalid MAC for device {device_name!r}: {exc}") from exc

    return config


def validate_device(config: dict[str, Any], device_name: str) -> str:
    """Return the normalized MAC address for a configured device."""
    devices = config["devices"]
    if device_name not in devices:
        available = ", ".join(sorted(devices))
        raise ValueError(
            f"Unknown device: {device_name}\nAvailable devices: {available}"
        )
    return normalize_mac(devices[device_name])
