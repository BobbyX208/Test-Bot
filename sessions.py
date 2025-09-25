import time
from typing import Dict, Optional, Any
from dataclasses import dataclass
from config import config

@dataclass
class Session:
    """User session data"""
    user_id: int
    host: str
    username: str
    password: str
    port: int
    created_at: float
    last_used: float
    is_connected: bool = False
    winrm_client: Any = None

class SessionManager:
    """Manage user sessions with TTL"""
    
    def __init__(self):
        self.sessions: Dict[int, Session] = {}
    
    def create_session(self, user_id: int, host: str, username: str, password: str, port: int = None) -> Session:
        """Create a new session for user"""
        if port is None:
            if ':' in host:
                host, port_str = host.split(':', 1)
                port = int(port_str)
            else:
                port = config.WINRM_PORT
        
        session = Session(
            user_id=user_id,
            host=host,
            username=username,
            password=password,
            port=port,
            created_at=time.time(),
            last_used=time.time()
        )
        
        self.sessions[user_id] = session
        return session
    
    def get_session(self, user_id: int) -> Optional[Session]:
        """Get user session if valid"""
        session = self.sessions.get(user_id)
        
        if session:
            # Check TTL
            if time.time() - session.last_used > config.SESSION_TTL:
                self.delete_session(user_id)
                return None
            
            # Update last used time
            session.last_used = time.time()
            return session
        
        return None
    
    def delete_session(self, user_id: int) -> bool:
        """Delete user session"""
        if user_id in self.sessions:
            # Clean up WinRM client if exists
            session = self.sessions[user_id]
            if session.winrm_client:
                try:
                    # WinRM doesn't have explicit close, but we can clean up references
                    session.winrm_client = None
                except:
                    pass
            
            del self.sessions[user_id]
            return True
        return False
    
    def update_session_connection(self, user_id: int, is_connected: bool, winrm_client: Any = None) -> bool:
        """Update session connection status"""
        session = self.get_session(user_id)
        if session:
            session.is_connected = is_connected
            session.winrm_client = winrm_client
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count removed"""
        current_time = time.time()
        expired_users = [
            user_id for user_id, session in self.sessions.items()
            if current_time - session.last_used > config.SESSION_TTL
        ]
        
        for user_id in expired_users:
            self.delete_session(user_id)
        
        return len(expired_users)

# Global session manager
session_manager = SessionManager()