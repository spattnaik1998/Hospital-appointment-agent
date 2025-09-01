"""
Improved FastAPI Application with Master-Worker Agent Architecture
Single Master Agent handles ALL user communication
Worker Agents operate behind the scenes
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import asyncio
import threading
import time
from datetime import datetime
from dotenv import load_dotenv

from data_store import DataStore
from improved_orchestrator import ImprovedOrchestrator

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Improved AI Appointment Scheduling System",
    description="Master-Worker architecture with conversation memory and seamless user experience",
    version="3.0.0"
)

# Initialize data store first
data_store = DataStore()

# PRIORITY: Run cleanup agent first at startup to remove all past appointments
print("PRIORITY: Running initial cleanup to remove all expired appointments...")
try:
    initial_cleanup = data_store.cleanup_expired_appointments()
    if initial_cleanup['expired_count'] > 0:
        print(f"SUCCESS: Startup cleanup completely removed {initial_cleanup['expired_count']} expired appointments from storage")
        for apt in initial_cleanup['expired_appointments']:
            print(f"  - DELETED: {apt['patient_name']} with {apt['doctor_name']} on {apt['date']} at {apt['time']} (was {apt['status']})")
    else:
        print("SUCCESS: No expired appointments found during startup")
except Exception as e:
    print(f"ERROR: Initial cleanup failed: {e}")
    # Don't continue if cleanup fails - this could indicate data issues
    raise

# Initialize orchestrator after cleanup
orchestrator = ImprovedOrchestrator(data_store)

# Cleanup control flag
cleanup_running = True

# Automatic cleanup system
def periodic_cleanup():
    """Background task to periodically clean up expired appointments"""
    global cleanup_running
    # Sleep in small intervals to allow quick shutdown response
    cleanup_interval = 21600  # 6 hours total
    sleep_chunk = 30  # Sleep 30 seconds at a time
    
    while cleanup_running:
        try:
            # Sleep in small chunks to allow responsive shutdown
            for i in range(0, cleanup_interval, sleep_chunk):
                if not cleanup_running:
                    print("CLEANUP: Background cleanup thread stopping...")
                    return
                time.sleep(sleep_chunk)
            
            # Only run cleanup if still supposed to be running
            if not cleanup_running:
                print("CLEANUP: Background cleanup thread stopping...")
                return
                
            cleanup_result = data_store.cleanup_expired_appointments()
            if cleanup_result['expired_count'] > 0:
                print(f"CLEANUP: Automatically removed {cleanup_result['expired_count']} expired appointments from storage at {datetime.now().isoformat()}")
                for apt in cleanup_result['expired_appointments']:
                    print(f"  - DELETED: {apt['patient_name']} with {apt['doctor_name']} on {apt['date']} at {apt['time']} (was {apt['status']})")
            
        except Exception as e:
            print(f"ERROR: Automatic cleanup failed: {e}")
            if not cleanup_running:
                break
    
    print("CLEANUP: Background cleanup thread exited")

# Start background cleanup thread (daemon so it stops with main program)
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()

# Templates
templates = Jinja2Templates(directory="templates")

# Pydantic models for API
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class PatientCreate(BaseModel):
    name: str
    age: int = 35
    condition: str = "General consultation"

# Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse) 
async def chat_page(request: Request):
    """Chat interface page - now with improved Master Agent"""
    return templates.TemplateResponse("chat_simple.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Patient registration page"""
    return templates.TemplateResponse("register.html", {"request": request})

# API Endpoints
@app.post("/api/chat")
async def chat_endpoint(message: ChatMessage):
    """
    Main chat endpoint - now routes to Master Agent only
    Master Agent coordinates with Worker Agents behind the scenes
    """
    try:
        result = orchestrator.process_message(message.message, message.session_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/api/doctors")
async def get_doctors():
    """Get all available doctors"""
    return {"doctors": data_store.get_all_doctors()}

@app.get("/api/patients")
async def get_patients():
    """Get all patients"""
    return {"patients": data_store.get_all_patients()}

@app.post("/api/patients")
async def create_patient(patient: PatientCreate):
    """Create a new patient"""
    try:
        patient_id = data_store.create_patient(patient.name, patient.age, patient.condition)
        return {"success": True, "patient_id": patient_id, "message": "Patient created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/appointments")
async def get_appointments():
    """Get all appointments with details"""
    return {"appointments": data_store.get_all_appointments()}

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics including conversation memory"""
    return orchestrator.get_system_status()

@app.post("/api/cleanup")
async def cleanup_sessions():
    """Clean up old conversation sessions"""
    try:
        result = orchestrator.cleanup_old_sessions()
        return {"success": True, "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "Improved AI Appointment System with Master-Worker architecture is running",
        "architecture": "master_worker_pattern",
        "user_interface": "single_master_agent"
    }

@app.get("/api/data-info")
async def get_data_info():
    """Get information about the persistent data storage"""
    return {
        "data_storage": "persistent_local_file",
        "file_info": data_store.get_data_file_info(),
        "statistics": data_store.get_stats()
    }

@app.post("/api/backup")
async def create_backup():
    """Create a manual backup of the data"""
    try:
        backup_filename = data_store.backup_data()
        if backup_filename:
            return {
                "success": True,
                "message": f"Backup created successfully",
                "backup_file": backup_filename
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create backup")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating backup: {str(e)}")

@app.post("/api/cleanup-expired")
async def cleanup_expired_appointments():
    """Manually cleanup expired appointments"""
    try:
        result = data_store.cleanup_expired_appointments()
        return {
            "success": True,
            "message": f"Cleaned up {result['expired_count']} expired appointments",
            "cleanup_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up appointments: {str(e)}")

@app.get("/api/appointments/expired")
async def get_expired_appointments():
    """Get appointments that have expired but are still marked as scheduled"""
    try:
        # Get all appointments including expired ones
        all_appointments = data_store.get_all_appointments(include_expired=True)
        expired_appointments = [apt for apt in all_appointments if apt.get('is_expired', False)]
        
        return {
            "expired_appointments": expired_appointments,
            "count": len(expired_appointments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting expired appointments: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import signal
    import sys
    import atexit
    
    def shutdown_cleanup():
        """Ensure cleanup thread stops on shutdown"""
        global cleanup_running
        if cleanup_running:
            print("\nSHUTDOWN: Stopping cleanup agent...")
            cleanup_running = False
            # Give thread a moment to exit gracefully
            if cleanup_thread.is_alive():
                cleanup_thread.join(timeout=1)
            print("SHUTDOWN: Cleanup agent stopped")
    
    def signal_handler(sig, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {sig}, shutting down...")
        shutdown_cleanup()
        sys.exit(0)
    
    # Register cleanup to run at exit
    atexit.register(shutdown_cleanup)
    
    # Register signal handlers (Windows supports SIGINT, limited SIGTERM)
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)  # Termination signal (Unix)
    
    try:
        print("SUCCESS: Starting Improved AI Appointment Scheduling System")
        print("SUCCESS: Master-Worker architecture initialized")
        print("SUCCESS: Single Master Agent handles all user communication")
        print("SUCCESS: Worker Agents operate behind the scenes")
        print("SUCCESS: Conversation memory and context management active")
        print("SUCCESS: Cleanup agent running in background (responsive shutdown)")
        print("SUCCESS: System ready at http://localhost:8000")
        print("INFO: Press Ctrl+C to stop the server")
        
        uvicorn.run(app, host="127.0.0.1", port=8000)
        
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received...")
        shutdown_cleanup()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        shutdown_cleanup()
    finally:
        # Final cleanup
        cleanup_running = False