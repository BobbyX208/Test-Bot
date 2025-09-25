import re
from typing import Dict, Optional, Tuple

class CredentialExtractor:
    """Extract credentials from messy text dumps"""
    
    def __init__(self):
        # Patterns for different credential formats
        self.patterns = [
            # IP: 192.168.1.1, User: admin, Pass: password
            self._pattern_ip_user_pass,
            # Host: 192.168.1.1:3389, Username: admin, Password: password
            self._pattern_host_user_pass,
            # Various separator patterns
            self._pattern_with_separators,
            # Simple space/tab separated
            self._pattern_simple,
        ]
    
    def extract(self, text: str) -> Optional[Dict[str, str]]:
        """Extract credentials from text"""
        text = self._preprocess_text(text)
        
        for pattern_func in self.patterns:
            result = pattern_func(text)
            if result and self._validate_credentials(result):
                return result
        
        return None
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better extraction"""
        # Remove extra whitespace but preserve structure
        text = re.sub(r'\s+', ' ', text)
        # Common replacements
        text = text.replace('：', ':')  # Chinese colon to English
        text = text.replace('–', '-')  # Different dash types
        text = text.replace('—', '-')
        return text.strip()
    
    def _pattern_ip_user_pass(self, text: str) -> Optional[Dict[str, str]]:
        """Pattern: IP: x.x.x.x, User: xxx, Pass: xxx"""
        patterns = [
            r'(?:IP|Host|Server|地址)[\s:：\-]*([\d\.]+(?::\d+)?)[\s,;\-]*(?:User|Username|用户|用户名)[\s:：\-]*([^\s,;]+)[\s,;\-]*(?:Pass|Password|密码)[\s:：\-]*([^\s,;]+)',
            r'(?:User|Username)[\s:：\-]*([^\s,;]+)[\s,;\-]*(?:Pass|Password)[\s:：\-]*([^\s,;]+)[\s,;\-]*(?:IP|Host)[\s:：\-]*([\d\.]+(?::\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'host': match.group(3) if 'User' in pattern else match.group(1),
                    'username': match.group(1) if 'User' in pattern else match.group(2),
                    'password': match.group(2) if 'User' in pattern else match.group(3)
                }
        return None
    
    def _pattern_host_user_pass(self, text: str) -> Optional[Dict[str, str]]:
        """Pattern with explicit labels"""
        pattern = r'(?:Host|Server)[\s:：\-]*([\d\.]+(?::\d+)?)[^a-zA-Z]*(?:User|Username)[\s:：\-]*([^\s,;]+)[^a-zA-Z]*(?:Pass|Password)[\s:：\-]*([^\s,;]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {
                'host': match.group(1),
                'username': match.group(2),
                'password': match.group(3)
            }
        return None
    
    def _pattern_with_separators(self, text: str) -> Optional[Dict[str, str]]:
        """Pattern with various separators like ➡️, →, etc."""
        # Remove emojis and special characters but preserve structure
        cleaned = re.sub(r'[➡️→▶️🔹•\-]+', ' ', text)
        parts = cleaned.split()
        
        if len(parts) >= 3:
            # Try to find IP pattern in parts
            ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?$'
            for i, part in enumerate(parts):
                if re.match(ip_pattern, part) and i + 2 < len(parts):
                    return {
                        'host': part,
                        'username': parts[i+1],
                        'password': parts[i+2]
                    }
        return None
    
    def _pattern_simple(self, text: str) -> Optional[Dict[str, str]]:
        """Simple space/tab separated pattern"""
        ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?\b'
        matches = list(re.finditer(ip_pattern, text))
        
        if matches:
            # Take the first IP match and try to extract credentials around it
            ip_match = matches[0]
            start = max(0, ip_match.start() - 50)
            end = min(len(text), ip_match.end() + 50)
            context = text[start:end]
            
            # Split context and look for username/password near IP
            parts = context.split()
            for i, part in enumerate(parts):
                if ip_match.group() in part:
                    if i > 0 and i + 1 < len(parts):
                        return {
                            'host': ip_match.group(),
                            'username': parts[i-1],
                            'password': parts[i+1]
                        }
        return None
    
    def _validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """Validate extracted credentials"""
        if not all(k in credentials for k in ['host', 'username', 'password']):
            return False
        
        # Basic validation
        host = credentials['host']
        username = credentials['username']
        password = credentials['password']
        
        # Validate host format
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?$', host):
            return False
        
        # Basic length checks
        if len(username) < 1 or len(password) < 1:
            return False
        
        return True

# Global instance
extractor = CredentialExtractor()