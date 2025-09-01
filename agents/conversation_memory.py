"""
Conversation Memory System for the Master Agent
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class ConversationMemory:
    """Manages conversation history, context, and user state"""
    
    def __init__(self):
        self.sessions = {}  # session_id -> SessionData
        self.cleanup_threshold = timedelta(hours=2)  # Clean up sessions older than 2 hours
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get or create session data"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [],
                "user_context": {},
                "partial_booking": {},
                "last_intent": None,
                "created_at": datetime.now(),
                "last_activity": datetime.now()
            }
        
        # Update last activity
        self.sessions[session_id]["last_activity"] = datetime.now()
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None):
        """Add a message to conversation history"""
        session = self.get_session(session_id)
        message = {
            "role": role,  # 'user' or 'assistant'
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        session["messages"].append(message)
        
        # Keep only last 20 messages to prevent memory bloat
        if len(session["messages"]) > 20:
            session["messages"] = session["messages"][-20:]
    
    def get_recent_messages(self, session_id: str, count: int = 6) -> List[Dict]:
        """Get recent messages for context"""
        session = self.get_session(session_id)
        return session["messages"][-count:] if session["messages"] else []
    
    def update_user_context(self, session_id: str, **kwargs):
        """Update user context information"""
        session = self.get_session(session_id)
        session["user_context"].update(kwargs)
    
    def get_user_context(self, session_id: str) -> Dict[str, Any]:
        """Get current user context"""
        session = self.get_session(session_id)
        return session["user_context"]
    
    def update_partial_booking(self, session_id: str, **kwargs):
        """Update partial booking information"""
        session = self.get_session(session_id)
        session["partial_booking"].update(kwargs)
    
    def get_partial_booking(self, session_id: str) -> Dict[str, Any]:
        """Get current partial booking data"""
        session = self.get_session(session_id)
        return session["partial_booking"]
    
    def clear_partial_booking(self, session_id: str):
        """Clear partial booking after completion"""
        session = self.get_session(session_id)
        session["partial_booking"] = {}
    
    def set_last_intent(self, session_id: str, intent: str):
        """Set the last detected intent"""
        session = self.get_session(session_id)
        session["last_intent"] = intent
    
    def get_last_intent(self, session_id: str) -> Optional[str]:
        """Get the last detected intent"""
        session = self.get_session(session_id)
        return session.get("last_intent")
    
    def get_conversation_summary(self, session_id: str) -> str:
        """Get a summary of the current conversation state"""
        session = self.get_session(session_id)
        user_context = session["user_context"]
        partial_booking = session["partial_booking"]
        recent_messages = self.get_recent_messages(session_id, 4)
        
        summary = ""
        
        if user_context.get("patient_name"):
            summary += f"Patient: {user_context['patient_name']}\n"
        
        if partial_booking:
            summary += "Current booking in progress:\n"
            for key, value in partial_booking.items():
                summary += f"  {key}: {value}\n"
        
        if recent_messages:
            summary += "Recent conversation:\n"
            for msg in recent_messages[-2:]:  # Last 2 messages
                role = "User" if msg["role"] == "user" else "Assistant"
                summary += f"  {role}: {msg['content'][:100]}...\n"
        
        return summary.strip()
    
    def cleanup_old_sessions(self):
        """Clean up sessions older than threshold"""
        cutoff_time = datetime.now() - self.cleanup_threshold
        to_remove = []
        
        for session_id, session_data in self.sessions.items():
            if session_data["last_activity"] < cutoff_time:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.sessions[session_id]
        
        return len(to_remove)