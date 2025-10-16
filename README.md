# FRITZ!Box Wake-on-LAN Tool

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> 🚀 Send Wake-on-LAN packets to your devices through your FRITZ!Box router with ease!

A Python tool to remotely wake up devices on your network using your AVM FRITZ!Box router's web interface.

## 🔧 Requirements

-  **Python 3.1+**
-  **AVM FRITZ!Box Router** (tested with FRITZ!OS 7.x and 8.x)
-  **Required Python packages:**
    - `requests` - HTTP library
    - `lxml` - XML processing
    - `packaging` - Version comparison

## 📥 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/fritzbox-wol.git
cd fritzbox-wol
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Create a `wakeup.json` configuration file in the project directory:

```json
{
  "host": "fritz.box",
  "port": 443,
  "username": "admin",
  "password": "your-password",
  "devices": {
    "desktop": "AA:BB:CC:DD:EE:FF",
    "laptop": "11:22:33:44:55:66",
    "server": "FF:EE:DD:CC:BB:AA"
  }
}
```

### 🔑 Configuration Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `host` | string | ✅ Yes | FritzBox hostname or IP address |
| `port` | integer | ✅ Yes | HTTPS port (usually 443) |
| `username` | string | ✅ Yes | FritzBox admin username |
| `password` | string | ❌ No | Password (will prompt if not provided) |
| `devices` | object | ✅ Yes | Device name to MAC address mapping |

> 💡 **Tip:** For security, omit the `password` field to be prompted at runtime!

## 🎮 Usage

### Basic Usage

```bash
# Wake up a device
python wakeup.py desktop
```

### 📋 Using Custom Config File

```bash
python wakeup.py laptop --config /path/to/custom.json
```

### 🔓 Skip SSL Verification (Testing Only)

```bash
python wakeup.py desktop --ssl-no-verify
```

> ⚠️ **Warning:** Only use `--ssl-no-verify` for testing! It's not secure for production.

## 🙏 Acknowledgments

This project was inspired by [n0rc](https://github.com/n0rc/fritzbox).

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
