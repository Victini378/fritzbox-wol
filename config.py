"""Configuration management for FritzBox WOL tool."""

import json
from pathlib import Path
from typing import Dict


def load_config(config_path: str) -> Dict:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file is not found
        ValueError: If config is invalid
    """
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    try:
        with path.open('r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")
    
    # Validate required fields
    required_fields = ['host', 'port', 'username', 'devices']
    missing_fields = [field for field in required_fields if field not in config]
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    return config


def validate_device(config: Dict, device_name: str) -> str:
    """
    Validate device exists in config and return MAC address.
    
    Args:
        config: Configuration dictionary
        device_name: Name of the device to validate
        
    Returns:
        MAC address of the device
        
    Raises:
        ValueError: If device is not found in config
    """
    if device_name not in config['devices']:
        available = ', '.join(config['devices'].keys())
        raise ValueError(
            f"Unknown device: {device_name}\n"
            f"Available devices: {available}"
        )
    
    return config['devices'][device_name]