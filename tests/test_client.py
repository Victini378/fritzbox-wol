import pytest

import client as client_module
from client import FritzBoxClient
from fritzconnection.core.exceptions import FritzAuthorizationError


class FakeConnection:
    def __init__(self):
        self.actions = []

    def call_action(self, service, action, **kwargs):
        self.actions.append((service, action, kwargs))
        return {}


class FakeHosts:
    def __init__(self, connection):
        self.connection = connection

    @property
    def host_numbers(self):
        return 2

    def get_hosts_info(self):
        return [
            {"name": "desktop", "mac": "AA:BB:CC:DD:EE:FF", "status": False},
        ]


def make_config(**overrides):
    config = {
        "host": "fritz.box",
        "username": "wol-user",
        "password": "secret",
        "devices": {"desktop": "AA:BB:CC:DD:EE:FF"},
    }
    config.update(overrides)
    return config


def test_authenticate_falls_back_from_legacy_port(monkeypatch):
    calls = []
    fake_connection = FakeConnection()

    def fake_fritz_connection(**kwargs):
        calls.append(kwargs["port"])
        if kwargs["port"] == 443:
            raise ValueError("not a TR-064 endpoint")
        return fake_connection

    monkeypatch.setattr(client_module, "FritzConnection", fake_fritz_connection)
    monkeypatch.setattr(client_module, "FritzHosts", FakeHosts)

    client = FritzBoxClient(make_config(port=443))
    client.authenticate()

    assert calls == [443, 49443]
    assert client.connection is fake_connection
    assert client.port == 49443


def test_explicit_tr064_port_disables_fallback(monkeypatch):
    calls = []

    def fake_fritz_connection(**kwargs):
        calls.append(kwargs["port"])
        raise ValueError("unavailable")

    monkeypatch.setattr(client_module, "FritzConnection", fake_fritz_connection)

    client = FritzBoxClient(make_config(port=443, tr064_port=12345))
    with pytest.raises(ConnectionError):
        client.authenticate()

    assert calls == [12345]


def test_send_wakeup_calls_tr064_action(monkeypatch):
    fake_connection = FakeConnection()
    monkeypatch.setattr(client_module, "FritzConnection", lambda **kwargs: fake_connection)
    monkeypatch.setattr(client_module, "FritzHosts", FakeHosts)

    client = FritzBoxClient(make_config())
    client.authenticate()

    assert client.send_wakeup("AA:BB:CC:DD:EE:FF") is True
    assert fake_connection.actions == [
        (
            "Hosts1",
            "X_AVM-DE_WakeOnLANByMACAddress",
            {"NewMACAddress": "AA:BB:CC:DD:EE:FF"},
        )
    ]


def test_authentication_errors_are_reported(monkeypatch):
    fake_connection = FakeConnection()

    def denied_action(*args, **kwargs):
        raise FritzAuthorizationError("denied")

    fake_connection.call_action = denied_action
    monkeypatch.setattr(client_module, "FritzConnection", lambda **kwargs: fake_connection)
    monkeypatch.setattr(client_module, "FritzHosts", FakeHosts)

    client = FritzBoxClient(make_config())
    client.authenticate()

    with pytest.raises(PermissionError, match="authorization"):
        client.send_wakeup("AA:BB:CC:DD:EE:FF")


def test_get_devices_uses_fritz_hosts(monkeypatch):
    fake_connection = FakeConnection()
    monkeypatch.setattr(client_module, "FritzConnection", lambda **kwargs: fake_connection)
    monkeypatch.setattr(client_module, "FritzHosts", FakeHosts)

    client = FritzBoxClient(make_config())
    client.authenticate()

    assert client.get_devices()[0]["name"] == "desktop"
