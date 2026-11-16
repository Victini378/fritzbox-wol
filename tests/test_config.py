import json

import pytest

from config import load_config, normalize_mac, validate_device


def test_normalize_mac_accepts_common_separators():
    assert normalize_mac("aa-bb-cc-dd-ee-ff") == "AA:BB:CC:DD:EE:FF"
    assert normalize_mac("aabbccddeeff") == "AA:BB:CC:DD:EE:FF"


@pytest.mark.parametrize("value", ["invalid", "AA:BB:CC", "GG:BB:CC:DD:EE:FF", ""])
def test_normalize_mac_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        normalize_mac(value)


def test_load_config_normalizes_device_macs(tmp_path):
    config_path = tmp_path / "wakeup.json"
    config_path.write_text(
        json.dumps({
            "host": "fritz.box",
            "username": "wol-user",
            "devices": {"desktop": "aa-bb-cc-dd-ee-ff"},
        }),
        encoding="utf-8",
    )

    config = load_config(str(config_path))

    assert config["devices"]["desktop"] == "AA:BB:CC:DD:EE:FF"
    assert validate_device(config, "desktop") == "AA:BB:CC:DD:EE:FF"


def test_load_config_requires_host_username_and_devices(tmp_path):
    config_path = tmp_path / "wakeup.json"
    config_path.write_text('{"host": "fritz.box", "devices": {}}', encoding="utf-8")

    with pytest.raises(ValueError, match="username"):
        load_config(str(config_path))


def test_load_config_rejects_invalid_port(tmp_path):
    config_path = tmp_path / "wakeup.json"
    config_path.write_text(
        json.dumps({
            "host": "fritz.box",
            "username": "wol-user",
            "port": 70000,
            "devices": {"desktop": "AA:BB:CC:DD:EE:FF"},
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="port"):
        load_config(str(config_path))


def test_validate_device_lists_available_names():
    config = {"devices": {"desktop": "AA:BB:CC:DD:EE:FF"}}
    with pytest.raises(ValueError, match="desktop"):
        validate_device(config, "server")
