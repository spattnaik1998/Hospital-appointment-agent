"""
Test script for expired appointment cleanup functionality
"""
import requests
import json
from datetime import datetime, timedelta

def test_expired_appointments():
    """Test the expired appointment cleanup functionality"""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Expired Appointment Cleanup")
    print("=" * 40)
    
    # Get initial stats
    try:
        response = requests.get(f"{base_url}/api/stats")
        if response.status_code == 200:
            initial_stats = response.json()['data_store']['statistics']
            print(f"Initial Stats:")
            print(f"  Active appointments: {initial_stats['active_appointments']}")
            print(f"  Expired appointments: {initial_stats.get('expired_appointments', 0)}")
            print(f"  Completed appointments: {initial_stats.get('completed_appointments', 0)}")
        else:
            print("ERROR: Could not get initial stats")
            return
    except Exception as e:
        print(f"ERROR: {e}")
        return
    
    # Create a test appointment with yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"\n1. Creating test appointment for yesterday ({yesterday})...")
    
    try:
        # Create appointment via chat (should create patient + appointment)
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": f"Book appointment for Test Patient with Dr. Adams on {yesterday} at 10 AM",
                "session_id": "expired_test"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("SUCCESS: Test appointment created")
            else:
                print(f"FAILED: {result.get('message')}")
        else:
            print(f"ERROR: {response.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Check stats after creating expired appointment
    print(f"\n2. Checking stats after creating yesterday's appointment...")
    try:
        response = requests.get(f"{base_url}/api/stats")
        if response.status_code == 200:
            stats = response.json()['data_store']['statistics']
            print(f"  Active appointments: {stats['active_appointments']}")
            print(f"  Expired appointments: {stats.get('expired_appointments', 0)}")
            print(f"  Completed appointments: {stats.get('completed_appointments', 0)}")
        else:
            print("ERROR: Could not get stats")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Get expired appointments
    print(f"\n3. Getting list of expired appointments...")
    try:
        response = requests.get(f"{base_url}/api/appointments/expired")
        if response.status_code == 200:
            expired_data = response.json()
            print(f"Found {expired_data['count']} expired appointments:")
            for apt in expired_data['expired_appointments']:
                print(f"  - {apt['patient_name']} with {apt['doctor_name']} on {apt['date']} at {apt['time']}")
        else:
            print(f"ERROR: {response.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Manual cleanup
    print(f"\n4. Running manual cleanup...")
    try:
        response = requests.post(f"{base_url}/api/cleanup-expired")
        if response.status_code == 200:
            result = response.json()
            cleanup_data = result['cleanup_result']
            print(f"SUCCESS: {result['message']}")
            
            if cleanup_data['expired_count'] > 0:
                print("Cleaned up appointments:")
                for apt in cleanup_data['expired_appointments']:
                    print(f"  - {apt['patient_name']} with {apt['doctor_name']} on {apt['date']} at {apt['time']}")
        else:
            print(f"ERROR: {response.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Check final stats
    print(f"\n5. Final stats after cleanup...")
    try:
        response = requests.get(f"{base_url}/api/stats")
        if response.status_code == 200:
            final_stats = response.json()['data_store']['statistics']
            print(f"  Active appointments: {final_stats['active_appointments']}")
            print(f"  Expired appointments: {final_stats.get('expired_appointments', 0)}")
            print(f"  Completed appointments: {final_stats.get('completed_appointments', 0)}")
            print(f"  Cancelled appointments: {final_stats.get('cancelled_appointments', 0)}")
        else:
            print("ERROR: Could not get final stats")
    except Exception as e:
        print(f"ERROR: {e}")
    
    print(f"\n" + "=" * 40)
    print("Test completed!")
    print("\nNOTE: The system also runs automatic cleanup:")
    print("- On startup: Cleans existing expired appointments")
    print("- Every 6 hours: Background cleanup of expired appointments")

if __name__ == "__main__":
    test_expired_appointments()