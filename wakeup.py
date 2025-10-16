#!/usr/bin/env python3
"""
FRITZ!Box Wake-on-LAN Tool
Send WOL packets to devices through FritzBox router.
"""

import argparse
import sys

from client import FritzBoxClient
from config import load_config, validate_device

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Send Wake-on-LAN packets through FRITZ!Box router',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
            %(prog)s mypc                    Wake up device 'mypc'
            %(prog)s server -c custom.json   Use custom config file
            %(prog)s laptop -k               Skip SSL verification
        """
    )
    
    parser.add_argument(
        'device',
        nargs='?',
        default='default',
        help='Device name from config file (default: default)'
    )
    parser.add_argument(
        '--config', '-c',
        default='wakeup.json',
        metavar='FILE',
        help='Configuration file path (default: wakeup.json)'
    )
    parser.add_argument(
        '--ssl-no-verify', '-k',
        action='store_true',
        help='Disable SSL certificate verification (not recommended)'
    )
    
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        config = load_config(args.config)
        config['verify_ssl'] = not args.ssl_no_verify
        
        target_mac = validate_device(config, args.device)
        
        print(f"onnecting to FritzBox at {config['host']}...")
        client = FritzBoxClient(config)
        sid = client.authenticate()
        
        print(f"🔍 Looking up device {args.device} ({target_mac})...")
        uid = client.get_device_uid(sid, target_mac)
        
        print(f"📡 Sending wake-up packet...")
        client.send_wakeup(sid, uid)
        
        print(f"✅ Wake-up packet sent successfully to {args.device} ({target_mac})")
        return 0
    
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Config Error: {e}", file=sys.stderr)
        return 1
    
    except PermissionError as e:
        print(f"❌ Authentication Error: {e}", file=sys.stderr)
        return 1
    
    except ConnectionError as e:
        print(f"❌ Connection Error: {e}", file=sys.stderr)
        return 1
    
    except LookupError as e:
        print(f"❌ Device Error: {e}", file=sys.stderr)
        return 1
    
    except RuntimeError as e:
        print(f"❌ Operation Error: {e}", file=sys.stderr)
        return 1
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user", file=sys.stderr)
        return 130
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1
    
if __name__ == '__main__':

    sys.exit(main())
