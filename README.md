# FRITZ!Box Wake-on-LAN Tool

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A small Python CLI to wake devices on your network through an AVM FRITZ!Box.
It uses the router's **TR-064 interface** and the dedicated
`X_AVM-DE_WakeOnLANByMACAddress` action instead of depending on the private
web-interface endpoints `data.lua` and `edit_device`.

## Requirements

- Python 3.10 or newer.
- A FRITZ!Box with TR-064 enabled (Home Network → Network → Network Settings → Allow access for applications).
- A FRITZ!Box user with the permissions needed to access the router and use TR-064.
- The target device must support Wake-on-LAN and have it enabled in its network adapter and BIOS/UEFI.

## Installation

```bash
git clone https://github.com/Victini378/fritzbox-wol.git
cd fritzbox-wol
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp wakeup.example.json wakeup.json
```

On Windows, activate the virtual environment with `.venv\\Scripts\\activate`.

## Configuration

Edit `wakeup.json`:

```json
{
  "host": "fritz.box",
  "tr064_port": 49443,
  "use_tls": true,
  "username": "your_fritzbox_username",
  "devices": {
    "default": "AA:BB:CC:DD:EE:FF",
    "desktop": "11:22:33:44:55:66",
    "server": "AA:11:BB:22:CC:33",
    "laptop": "DD:EE:FF:00:11:22",
    "nas": "99:88:77:66:55:44"
  }
}
```

| Option | Required | Description |
| --- | --- | --- |
| `host` | Yes | FRITZ!Box hostname or IP address |
| `username` | Yes | FRITZ!Box user name |
| `password` | No | Password; prompted securely when omitted |
| `devices` | Yes | Mapping from device names to MAC addresses |
| `tr064_port` | No | Explicit TR-064 port; defaults to 49443 with TLS or 49000 without TLS |
| `use_tls` | No | Use HTTPS for TR-064; defaults to `true` |
| `port` | No | Legacy setting: tried first for compatibility, followed by the standard TR-064 port |

The old `port` setting is retained as a compatibility hint. Existing
configurations using `"port": 443` will try that port first (useful for a
MyFRITZ! remote port-forward) and then fall back to the standard local TR-064
port. For clarity, new configurations should use `tr064_port`.

For local TLS access, use port `49443`. For local unencrypted access, set
`"use_tls": false` (port `49000`). For MyFRITZ! remote access, use TLS and set
`tr064_port` to the HTTPS port configured under Internet → Permit Access →
FRITZ!Box Services (often `443` or a custom port).

The `fritzconnection` library currently disables certificate verification
because FRITZ!Box devices commonly use self-signed certificates. TLS still
encrypts the connection, but it does not authenticate the router certificate.
Use a trusted VPN for remote administration where possible.

Keep `wakeup.json` private. It is ignored by Git; use
`wakeup.example.json` as the template.

## Usage

Wake a configured device (the positional command is unchanged):

```bash
python wakeup.py desktop
python wakeup.py laptop --config /path/to/custom.json
```

List devices known to the FRITZ!Box:

```bash
python wakeup.py --list
```

Override the TR-064 port or disable TLS for local access:

```bash
python wakeup.py desktop --tr064-port 49443
python wakeup.py desktop --no-tls
```

The tool reports when the FRITZ!Box accepts the TR-064 request. This confirms
that the router accepted the Wake-on-LAN action; it does not prove that the
target computer has finished booting.

## Development and tests

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest
```

The tests mock the router API and do not require a physical FRITZ!Box.

## Acknowledgments

Inspired by [n0rc/fritzbox](https://github.com/n0rc/fritzbox).
Uses [fritzconnection](https://github.com/kbr/fritzconnection), an independent
Python library for the FRITZ!Box TR-064 interface.

## License

MIT. See [LICENSE](LICENSE).
