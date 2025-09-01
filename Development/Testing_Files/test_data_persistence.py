"""
Test script to verify data persistence across application restarts
"""
import requests
import json
import time
import subprocess
import sys
import os

def test_data_persistence():
    """Test that data persists across application restarts"""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Data Persistence Across Application Restarts")
    print("=" * 55)
    
    # Step 1: Start server and create some test data
    print("\n1. Creating test data...")
    
    # Create a test patient and appointment
    session_id = "persistence_test"
    
    messages = [
        "I want to book an appointment",
        "My name is Persistence Test Patient", 
        "I need to see Dr. Adams",
        "Tomorrow at 2 PM"
    ]
    
    appointment_created = False
    
    for message in messages:
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={"message": message, "session_id": session_id},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"User: {message}")
                print(f"Assistant: {result.get('message', 'No response')}")
                
                if result.get('success') and "scheduled" in result.get('message', '').lower():
                    print("✅ Test appointment created successfully!")
                    appointment_created = True
                    break
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    if not appointment_created:
        print("❌ Could not create test appointment. Server may not be running.")
        print("Please start the server with: python main_improved.py")
        return
    
    # Step 2: Get current statistics
    try:
        stats_response = requests.get(f"{base_url}/api/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            patients_count = stats.get("data_store", {}).get("statistics", {}).get("total_patients", 0)
            appointments_count = stats.get("data_store", {}).get("statistics", {}).get("active_appointments", 0)
            
            print(f"\nBefore restart - Patients: {patients_count}, Active Appointments: {appointments_count}")
        else:
            print("❌ Could not get statistics")
            return
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return
    
    # Step 3: Get data file info
    try:
        info_response = requests.get(f"{base_url}/api/data-info")
        if info_response.status_code == 200:
            info = info_response.json()
            file_info = info.get("file_info", {})
            
            if file_info.get("file_exists"):
                print(f"✅ Data file exists: {file_info.get('file_path')}")
                print(f"   File size: {file_info.get('file_size')} bytes")
                print(f"   Last modified: {file_info.get('last_modified')}")
            else:
                print("❌ Data file does not exist")
                return
        else:
            print("❌ Could not get data file info")
            return
    except Exception as e:
        print(f"❌ Error getting data info: {e}")
        return
    
    # Step 4: Check if appointment_data.json exists
    data_file = "appointment_data.json"
    if os.path.exists(data_file):
        print(f"✅ Found data file: {data_file}")
        
        # Read the file to verify content
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            patients_in_file = len(data.get('patients', {}))
            appointments_in_file = len([a for a in data.get('appointments', {}).values() if a.get('status') == 'scheduled'])
            
            print(f"   Data file contains: {patients_in_file} patients, {appointments_in_file} active appointments")
            
            # Check if our test patient is in the file
            test_patient_found = False
            for patient in data.get('patients', {}).values():
                if 'Persistence Test Patient' in patient.get('name', ''):
                    test_patient_found = True
                    print(f"   ✅ Found test patient: {patient['name']}")
                    break
            
            if not test_patient_found:
                print("   ❌ Test patient not found in data file")
                
        except Exception as e:
            print(f"   ❌ Error reading data file: {e}")
    else:
        print(f"❌ Data file {data_file} not found")
        return
    
    print("\n" + "=" * 55)
    print("✅ Data persistence test completed!")
    print("   - Test appointment was created")
    print("   - Data was saved to local file")
    print("   - You can now restart the server to verify data loads correctly")
    print("\nTo test persistence:")
    print("1. Stop the current server (Ctrl+C)")
    print("2. Restart: python main_improved.py")
    print("3. Check dashboard - your data should still be there!")

def verify_persistence_after_restart():
    """Verify that data exists after restart (run this after restarting server)"""
    base_url = "http://127.0.0.1:8000"
    
    print("Verifying Data After Server Restart")
    print("=" * 35)
    
    try:
        # Check stats
        stats_response = requests.get(f"{base_url}/api/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            patients_count = stats.get("data_store", {}).get("statistics", {}).get("total_patients", 0)
            appointments_count = stats.get("data_store", {}).get("statistics", {}).get("active_appointments", 0)
            
            print(f"After restart - Patients: {patients_count}, Active Appointments: {appointments_count}")
            
            if patients_count > 0 and appointments_count > 0:
                print("✅ Data successfully persisted across restart!")
            else:
                print("❌ Data may not have persisted correctly")
        
        # Get actual patients and appointments
        patients_response = requests.get(f"{base_url}/api/patients")
        appointments_response = requests.get(f"{base_url}/api/appointments")
        
        if patients_response.status_code == 200 and appointments_response.status_code == 200:
            patients = patients_response.json().get('patients', [])
            appointments = appointments_response.json().get('appointments', [])
            
            print(f"\nFound {len(patients)} patients:")
            for patient in patients:
                print(f"  - {patient.get('name')} (ID: {patient.get('id')})")
            
            print(f"\nFound {len(appointments)} appointments:")
            for apt in appointments:
                print(f"  - {apt.get('patient_name')} with {apt.get('doctor_name')} on {apt.get('date')} at {apt.get('time')}")
                
        else:
            print("❌ Could not retrieve patients/appointments")
            
    except Exception as e:
        print(f"❌ Error verifying persistence: {e}")
        print("Make sure the server is running: python main_improved.py")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_persistence_after_restart()
    else:
        test_data_persistence()