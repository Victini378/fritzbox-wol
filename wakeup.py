#!/usr/bin/env python3
"""Send Wake-on-LAN requests through a FRITZ!Box using TR-064."""

import argparse
import sys
import warnings

from client import FritzBoxClient
from config import load_config, validate_device


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send Wake-on-LAN packets through a FRITZ!Box router",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s desktop
  %(prog)s laptop --config /path/to/custom.json
  %(prog)s --list
  %(prog)s server --tr064-port 49443
""",
    )
    parser.add_argument(
        "device",
        nargs="?",
        default="default",
        help="Device name from the config file (default: default)",
    )
    parser.add_argument(
        "--config", "-c",
        default="wakeup.json",
        metavar="FILE",
        help="Configuration file path (default: wakeup.json)",
    )
    parser.add_argument(
        "--tr064-port",
        type=int,
        metavar="PORT",
        help="Explicit TR-064 port (overrides ports in the config file)",
    )
    parser.add_argument(
        "--no-tls",
        action="store_true",
        help="Use unencrypted TR-064 on the local network (port 49000 by default)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List devices known to the FRITZ!Box without waking one",
    )
    parser.add_argument(
        "--ssl-no-verify", "-k",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser


def print_devices(devices: list[dict]) -> None:
    if not devices:
        print("No devices found.")
        return

    print(f"{'#':>3}  {'STATUS':<8} {'NAME':<28} {'IP':<16} MAC")
    print("-" * 78)
    devices.sort(
        key=lambda item: (
            bool(item.get("status")),
            (item.get("name") or "").casefold(),
        )
    )
    for index, device in enumerate(devices, start=1):
        status = "online" if device.get("status") else "offline"
        name = device.get("name") or "<unknown>"
        print(
            f"{index:>3}  {status:<8} {name[:28]:<28} "
            f"{device.get('ip') or '':<16} {device.get('mac') or ''}"
        )


def main(argv: list[str] | None = None) -> int:
    args = create_parser().parse_args(argv)

    try:
        config = load_config(args.config)
        if args.tr064_port is not None:
            config["tr064_port"] = args.tr064_port
        if args.no_tls:
            config["use_tls"] = False
        if args.ssl_no_verify:
            warnings.warn(
                "--ssl-no-verify is obsolete: fritzconnection accepts the "
                "FRITZ!Box self-signed certificate without certificate verification.",
                DeprecationWarning,
                stacklevel=2,
            )

        target_mac = None if args.list else validate_device(config, args.device)

        print(f"Connecting to FRITZ!Box at {config['host']}...")
        client = FritzBoxClient(config)
        client.authenticate()
        print(f"Connected through TR-064 on port {client.port}.")

        if args.list:
            print_devices(client.get_devices())
            return 0

        print(f"Sending Wake-on-LAN request to {args.device} ({target_mac})...")
        client.send_wakeup(target_mac)
        print(
            f"Wake-on-LAN request accepted by the FRITZ!Box for "
            f"{args.device} ({target_mac})."
        )
        return 0

    except (FileNotFoundError, ValueError) as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 1
    except PermissionError as exc:
        print(f"Authentication error: {exc}", file=sys.stderr)
        return 1
    except ConnectionError as exc:
        print(f"Connection error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"Operation error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
