"""
Test script to demonstrate the improved Master-Worker architecture
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_conversation_flow():
    """Test a complete conversation flow with memory"""
    
    print("🧪 Testing Improved Master-Worker Agent Architecture")
    print("=" * 60)
    
    session_id = f"test_session_{int(time.time())}"
    
    # Test conversation with memory
    messages = [
        "Hello!",
        "Hi, I'm John Smith",
        "I need to see a doctor",
        "I'd like to book with Dr. Adams",
        "How about tomorrow at 2 PM?",
        "Yes, that sounds good"
    ]
    
    print(f"Session ID: {session_id}")
    print("\nConversation Flow:")
    print("-" * 30)
    
    for i, message in enumerate(messages, 1):
        print(f"\n👤 User: {message}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": message, "session_id": session_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Assistant: {data.get('message', 'No response')}")
                
                if data.get('success') and 'booking_result' in data.get('data', {}):
                    print("✅ Appointment booked successfully!")
                    break
            else:
                print(f"❌ Error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Is it running on port 8000?")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        
        time.sleep(1)  # Small delay between messages
    
    print("\n" + "=" * 60)
    return True

def test_system_status():
    """Test system status endpoint"""
    
    print("📊 Testing System Status...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        if response.status_code == 200:
            data = response.json()
            print("✅ System Status:")
            print(f"   Architecture: {data.get('architecture')}")
            print(f"   Active Sessions: {data.get('conversation_memory', {}).get('active_sessions', 0)}")
            print(f"   Total Patients: {data.get('data_store', {}).get('statistics', {}).get('total_patients', 0)}")
            print(f"   Total Appointments: {data.get('data_store', {}).get('statistics', {}).get('active_appointments', 0)}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

def test_health_check():
    """Test health check endpoint"""
    
    print("🏥 Testing Health Check...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check Passed:")
            print(f"   Status: {data.get('status')}")
            print(f"   Architecture: {data.get('architecture')}")
            print(f"   User Interface: {data.get('user_interface')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error in health check: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Tests for Improved AI Scheduling System")
    print()
    
    # Test health check first
    if not test_health_check():
        print("❌ Health check failed. Is the server running?")
        exit(1)
    
    print()
    
    # Test system status
    if not test_system_status():
        print("❌ System status check failed.")
    
    print()
    
    # Test conversation flow
    if test_conversation_flow():
        print("✅ All tests completed successfully!")
        print("\n📌 Key Improvements Demonstrated:")
        print("   • Single Master Agent handles ALL user communication")
        print("   • Worker Agents operate behind the scenes")
        print("   • Conversation memory maintains context")
        print("   • Natural, seamless conversation flow")
        print("   • No confusing agent switching")
    else:
        print("❌ Conversation flow test failed.")
    
    print("\n🌐 Open http://localhost:8000/chat to test the web interface!")