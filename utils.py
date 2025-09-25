import re
from typing import Optional

def truncate_text(text: str, max_length: int = 4000) -> str:
    """Truncate text to maximum length with ellipsis if needed"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def redact_password(text: str, password: str) -> str:
    """Redact password from text for logging"""
    if not password:
        return text
    return text.replace(password, "***REDACTED***")

def validate_host(host: str) -> Optional[str]:
    """Validate and normalize host address"""
    host = host.strip()
    
    # Check if it's an IP with port
    if ':' in host and not host.endswith(']'):
        parts = host.split(':')
        if len(parts) == 2:
            ip, port = parts
            # Validate IP
            ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
            if re.match(ip_pattern, ip) and port.isdigit():
                return f"{ip}:{port}"
    
    # Check if it's just an IP
    ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    if re.match(ip_pattern, host):
        return host
    
    return None

def format_command_output(stdout: str, stderr: str, exit_code: int) -> str:
    """Format command output for Telegram message"""
    output_parts = []
    
    if stdout:
        output_parts.append(f"📤 **Stdout:**\n```\n{stdout}\n```")
    
    if stderr:
        output_parts.append(f"📥 **Stderr:**\n```\n{stderr}\n```")
    
    output_parts.append(f"🔢 **Exit Code:** `{exit_code}`")
    
    return "\n\n".join(output_parts)