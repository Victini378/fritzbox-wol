"""FritzBox client for Wake-on-LAN operations."""

import getpass
import hashlib
from typing import Dict, Optional

import requests
from lxml import etree
from packaging import version
from requests.exceptions import SSLError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SID_NOAUTH = '0000000000000000'


class FritzBoxClient:
    """Client for interacting with FritzBox router."""

    def __init__(self, config: Dict):
        """
        Initialize FritzBox client.
        
        Args:
            config: Configuration dictionary containing host, port, username, etc.
        """
        self.config = config
        self.host = config['host']
        self.port = config['port']
        self.username = config['username']
        self.verify_ssl = config.get('verify_ssl', True)
        
        self.url_login = f"https://{self.host}:{self.port}/login_sid.lua"
        self.url_data = f"https://{self.host}:{self.port}/data.lua"

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with SSL error handling.
        
        Args:
            method: HTTP method (get/post)
            url: Request URL
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            ConnectionError: If SSL verification fails
        """
        try:
            if method.lower() == 'get':
                return requests.get(url, **kwargs)
            elif method.lower() == 'post':
                return requests.post(url, **kwargs)
        except SSLError:
            raise ConnectionError(
                "SSL certificate verification failed. "
                "Use --ssl-no-verify flag to bypass (not recommended)"
            )

    def _get_challenge(self) -> str:
        """
        Retrieve authentication challenge from FritzBox.
        
        Returns:
            Challenge string
        """
        response = self._make_request('get', self.url_login, verify=self.verify_ssl)
        tree = etree.XML(response.content)
        return tree.xpath('//Challenge/text()')[0]

    def _calculate_response(self, challenge: str, password: str) -> str:
        """
        Calculate challenge-response hash for authentication.
        
        Args:
            challenge: Challenge string from FritzBox
            password: Router password
            
        Returns:
            Response hash string
        """
        challenge_pwd = f"{challenge}-{password}"
        hash_value = hashlib.md5(challenge_pwd.encode('utf-16-le')).hexdigest()
        return f"{challenge}-{hash_value}"

    def authenticate(self, password: Optional[str] = None) -> str:
        """
        Authenticate with FritzBox and return session ID.
        
        Args:
            password: Router password. If None, prompts user.
            
        Returns:
            Session ID string
            
        Raises:
            PermissionError: If authentication fails
        """
        if password is None:
            password = self.config.get('password') or getpass.getpass("Password: ")

        challenge = self._get_challenge()
        response = self._calculate_response(challenge, password)
        
        auth_url = f"{self.url_login}?username={self.username}&response={response}"
        r = self._make_request('get', auth_url, verify=self.verify_ssl)
        
        tree = etree.XML(r.content)
        sid = tree.xpath('//SID/text()')[0]
        
        if sid == SID_NOAUTH:
            raise PermissionError(
                "Authentication failed. Please check username and password."
            )
        
        return sid

    def get_device_uid(self, sid: str, mac_address: str) -> str:
        """
        Get device UID by MAC address.
        
        Args:
            sid: Session ID
            mac_address: Device MAC address
            
        Returns:
            Device UID
            
        Raises:
            LookupError: If device with given MAC is not found
        """
        payload = {'sid': sid, 'page': 'netDev', 'xhrId': 'all'}
        response = self._make_request(
            'post', 
            self.url_data, 
            data=payload, 
            verify=self.verify_ssl
        )
        data = response.json()
        
        for device_list in [data['data']['passive'], data['data']['active']]:
            for device in device_list:
                if device['mac'] == mac_address:
                    return device['UID']
        
        raise LookupError(
            f"Device with MAC address {mac_address} not found in FritzBox"
        )

    def get_firmware_version(self, sid: str) -> str:
        """
        Get FritzBox firmware version.
        
        Args:
            sid: Session ID
            
        Returns:
            Firmware version string (e.g., '7.50')
        """
        try:
            payload = {'sid': sid, 'page': 'overview'}
            response = self._make_request(
                'post',
                self.url_data,
                data=payload,
                verify=self.verify_ssl
            )
            data = response.json()
            return data['data']['fritzos']['nspver'].split()[0]
        except (KeyError, IndexError):
            return '0.0'

    def send_wakeup(self, sid: str, uid: str) -> bool:
        """
        Send Wake-on-LAN packet to device.
        
        Args:
            sid: Session ID
            uid: Device UID
            
        Returns:
            True if successful
            
        Raises:
            RuntimeError: If wake-up fails
        """
        payload = {
            'sid': sid,
            'dev': uid,
            'oldpage': 'net/edit_device.lua',
            'page': 'edit_device',
            'btn_wake': ''
        }
        
        # Adjust page parameter for older firmware versions
        fw_version = self.get_firmware_version(sid)
        if version.parse(fw_version) <= version.parse('7.24'):
            payload['page'] += '2'
        
        response = self._make_request(
            'post',
            self.url_data,
            data=payload,
            verify=self.verify_ssl
        )
        
        content_type = response.headers.get("content-type", "")
        if content_type.startswith('application/json'):
            data = response.json()
            success = data.get('data', {}).get('btn_wake') == 'ok'
        else:
            success = '"pid":"netDev"' in response.text
        
        if not success:
            raise RuntimeError("Failed to send wake-up packet")
        
        return True