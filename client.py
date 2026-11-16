"""FRITZ!Box client using the stable TR-064 interface."""

from __future__ import annotations

import getpass
import xml.etree.ElementTree as ET
from typing import Any

from fritzconnection import FritzConnection
from fritzconnection.core.exceptions import (
    FritzAuthorizationError,
    FritzConnectionException,
)
from fritzconnection.lib.fritzhosts import FritzHosts
from requests.exceptions import RequestException


class FritzBoxClient:
    """Small TR-064 client for device discovery and Wake-on-LAN."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.host = config["host"]
        self.username = config["username"]
        self.password = config.get("password") or getpass.getpass("FRITZ!Box password: ")
        self.use_tls = config.get("use_tls", True)
        self.timeout = config.get("timeout", 10)
        self.connection: FritzConnection | None = None
        self.port: int | None = None

    def _port_candidates(self) -> list[int]:
        """Prefer an explicit TR-064 port, then try legacy and standard ports."""
        explicit_port = self.config.get("tr064_port")
        if explicit_port is not None:
            return [explicit_port]

        standard_port = 49443 if self.use_tls else 49000
        legacy_port = self.config.get("port")

        if legacy_port is None or legacy_port == standard_port:
            return [standard_port]

        # Older wakeup.json files used "port" for the web interface (often 443).
        # It may also be a MyFRITZ! externally forwarded TR-064 port.
        return [legacy_port, standard_port]

    def authenticate(self) -> None:
        """Create and validate a TR-064 connection.

        fritzconnection performs digest authentication for TR-064 calls. The
        legacy method name is retained so the CLI flow remains familiar.
        """
        errors: list[tuple[int, Exception]] = []

        for port in self._port_candidates():
            try:
                connection = FritzConnection(
                    address=self.host,
                    port=port,
                    user=self.username,
                    password=self.password,
                    timeout=self.timeout,
                    use_tls=self.use_tls,
                    use_cache=True,
                )
                # Force a real Hosts-service request now, so invalid endpoints
                # and authentication failures are reported before sending WOL.
                FritzHosts(connection).host_numbers
                self.connection = connection
                self.port = port
                return
            except FritzAuthorizationError as exc:
                raise PermissionError(
                    "FRITZ!Box authorization failed. Check the username, password "
                    "and the user's application permissions."
                ) from exc
            except (
                FritzConnectionException,
                RequestException,
                ET.ParseError,
                OSError,
                ValueError,
            ) as exc:
                errors.append((port, exc))

        attempted = ", ".join(str(port) for port, _ in errors)
        last_error = errors[-1][1] if errors else RuntimeError("No TR-064 port configured")
        raise ConnectionError(
            f"Could not connect to the FRITZ!Box TR-064 interface at "
            f"{self.host}. Tried port(s): {attempted}. "
            f"Check that access for applications is enabled and that the "
            f"TR-064 port/TLS settings are correct. Last error: {last_error}"
        ) from last_error

    def _require_connection(self) -> FritzConnection:
        if self.connection is None:
            self.authenticate()
        assert self.connection is not None
        return self.connection

    def get_devices(self) -> list[dict[str, Any]]:
        """Return devices known to the FRITZ!Box."""
        connection = self._require_connection()
        try:
            return FritzHosts(connection).get_hosts_info()
        except FritzAuthorizationError as exc:
            raise PermissionError("FRITZ!Box authorization failed.") from exc
        except (FritzConnectionException, RequestException) as exc:
            raise ConnectionError(f"Could not retrieve the FRITZ!Box host list: {exc}") from exc

    def send_wakeup(self, mac_address: str) -> bool:
        """Ask the FRITZ!Box to send a WOL packet to a MAC address.

        Returns True when the router accepts the TR-064 action. This does not
        guarantee that the target computer has completed its boot process.
        """
        connection = self._require_connection()
        try:
            connection.call_action(
                "Hosts1",
                "X_AVM-DE_WakeOnLANByMACAddress",
                NewMACAddress=mac_address,
            )
        except FritzAuthorizationError as exc:
            raise PermissionError(
                "FRITZ!Box authorization failed. Check the account permissions."
            ) from exc
        except (FritzConnectionException, RequestException) as exc:
            raise RuntimeError(f"FRITZ!Box rejected the Wake-on-LAN request: {exc}") from exc
        return True
