"""
Improved Agent Orchestrator with Master-Worker Architecture
Only the Master Agent communicates with users
"""
from typing import Dict, Any
from agents.master_agent import MasterAgent
from agents.worker_scheduling import SchedulingWorker
from agents.worker_query import QueryWorker
from agents.worker_management import ManagementWorker

class ImprovedOrchestrator:
    """
    Improved orchestrator with Master-Worker pattern
    - Master Agent: Handles ALL user communication
    - Worker Agents: Internal processing only
    """
    
    def __init__(self, data_store):
        self.data_store = data_store
        
        # Initialize worker agents (internal only)
        self.worker_agents = {
            "scheduling": SchedulingWorker(data_store),
            "query": QueryWorker(data_store), 
            "management": ManagementWorker(data_store)
        }
        
        # Initialize master agent with references to worker agents
        self.master_agent = MasterAgent(self.worker_agents)
        
        print("SUCCESS: Improved Orchestrator initialized")
        print("SUCCESS: Master-Worker architecture ready")
        print("SUCCESS: Only Master Agent will communicate with users")
    
    def process_message(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Process user message through Master Agent only
        Worker agents operate behind the scenes
        """
        try:
            # All user communication goes through Master Agent
            result = self.master_agent.process_request(
                message, 
                context={"session_id": session_id}
            )
            
            # Add orchestrator metadata
            result["orchestrator"] = "master_worker_pattern"
            result["architecture"] = "single_user_interface"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": "I'm experiencing technical difficulties. Please try again or contact our office directly.",
                "error": str(e),
                "session_id": session_id,
                "orchestrator": "error_handler"
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of the Master-Worker system"""
        stats = self.data_store.get_stats()
        
        # Get conversation memory stats
        memory_stats = {
            "active_sessions": len(self.master_agent.memory.sessions),
            "total_messages": sum(len(session.get("messages", [])) for session in self.master_agent.memory.sessions.values())
        }
        
        return {
            "architecture": "master_worker_pattern",
            "agents": {
                "master_agent": "active - handles all user communication",
                "scheduling_worker": "active - internal booking processing",
                "query_worker": "active - internal availability checking", 
                "management_worker": "active - internal reschedule/cancel processing"
            },
            "data_store": {
                "status": "active",
                "statistics": stats
            },
            "conversation_memory": memory_stats,
            "system_status": "healthy - single user interface active"
        }
    
    def cleanup_old_sessions(self):
        """Clean up old conversation sessions"""
        cleaned = self.master_agent.memory.cleanup_old_sessions()
        return f"Cleaned up {cleaned} old sessions"