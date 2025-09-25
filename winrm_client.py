import winrm
from typing import Tuple, Optional
from config import config

class WinRMClient:
    """Wrapper for WinRM operations"""
    
    def __init__(self, host: str, username: str, password: str, port: int = None):
        self.host = host
        self.username = username
        self.password = password
        self.port = port or config.WINRM_PORT
        self.session = None
        self.is_connected = False
    
    def connect(self) -> Tuple[bool, str]:
        """Connect to Windows server via WinRM"""
        try:
            # Create WinRM session
            self.session = winrm.Session(
                f"{self.host}:{self.port}",
                auth=(self.username, self.password),
                transport='ntlm',
                server_cert_validation='ignore'  # For self-signed certs
            )
            
            # Test connection with whoami
            result = self.run_cmd("whoami")
            if result[2] == 0:  # Exit code 0 means success
                self.is_connected = True
                return True, "Connection successful"
            else:
                return False, f"Connection test failed: {result[1]}"
                
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def run_cmd(self, command: str) -> Tuple[str, str, int]:
        """Execute command via CMD"""
        try:
            result = self.session.run_cmd(command)
            return (
                result.std_out.decode('utf-8', errors='ignore') if result.std_out else "",
                result.std_err.decode('utf-8', errors='ignore') if result.std_err else "",
                result.status_code
            )
        except Exception as e:
            return "", f"Command execution error: {str(e)}", 1
    
    def run_ps(self, command: str) -> Tuple[str, str, int]:
        """Execute PowerShell command"""
        try:
            result = self.session.run_ps(command)
            return (
                result.std_out.decode('utf-8', errors='ignore') if result.std_out else "",
                result.std_err.decode('utf-8', errors='ignore') if result.std_err else "",
                result.status_code
            )
        except Exception as e:
            return "", f"PowerShell execution error: {str(e)}", 1

def test_connection(host: str, username: str, password: str, port: int = None) -> Tuple[bool, str]:
    """Test WinRM connection"""
    client = WinRMClient(host, username, password, port)
    return client.connect()