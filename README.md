# FRITZ!Box Wake-on-LAN Tool

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

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
git clone https://github.com/Victini378/fritzbox-wol.git
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
  "host": "your_hostname_or_ip",
  "port": 443,
  "username": "your_fritzbox_username",
  "password": "your_fritzbox_password",
  "devices": {
    "default": "AA:BB:CC:DD:EE:FF",
    "desktop": "11:22:33:44:55:66",
    "server": "AA:11:BB:22:CC:33",
    "laptop": "DD:EE:FF:00:11:22",
    "nas": "99:88:77:66:55:44"
  }
}
```

### 🔑 Configuration Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `host` | string | ✅ Yes | FRITZ!Box hostname or IP address |
| `port` | integer | ✅ Yes | HTTPS port (usually 443) |
| `username` | string | ✅ Yes | FRITZ!Box admin username |
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
