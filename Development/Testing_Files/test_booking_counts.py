"""
Test script to verify patient/appointment counting is correct
"""
import requests
import json

def test_booking_counts():
    """Test that patient counts only increase when appointments are actually created"""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Patient/Appointment Counting")
    print("=" * 40)
    
    # Get initial counts
    stats_response = requests.get(f"{base_url}/api/stats")
    if stats_response.status_code == 200:
        initial_stats = stats_response.json()
        initial_patients = initial_stats.get("data_store", {}).get("statistics", {}).get("total_patients", 0)
        initial_appointments = initial_stats.get("data_store", {}).get("statistics", {}).get("active_appointments", 0)
        
        print(f"Initial - Patients: {initial_patients}, Appointments: {initial_appointments}")
    else:
        print("Could not get initial stats")
        return
    
    # Test Case 1: Successful booking (should increase both counts)
    print("\n--- Test 1: Successful Booking ---")
    session_id = "test_booking_success"
    
    messages = [
        "I want to book an appointment",
        "My name is Test Patient", 
        "I need to see Dr. Adams",
        "Tomorrow at 10 AM"
    ]
    
    for message in messages:
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
                print("✅ Booking successful!")
                break
        else:
            print(f"❌ Error: {response.status_code}")
    
    # Check counts after successful booking
    stats_response = requests.get(f"{base_url}/api/stats")
    if stats_response.status_code == 200:
        after_success_stats = stats_response.json()
        patients_after_success = after_success_stats.get("data_store", {}).get("statistics", {}).get("total_patients", 0)
        appointments_after_success = after_success_stats.get("data_store", {}).get("statistics", {}).get("active_appointments", 0)
        
        print(f"After Success - Patients: {patients_after_success}, Appointments: {appointments_after_success}")
        
        if patients_after_success == initial_patients + 1 and appointments_after_success == initial_appointments + 1:
            print("✅ Counts increased correctly for successful booking")
        else:
            print("❌ Counts did not increase correctly for successful booking")
    
    # Test Case 2: Failed booking with invalid time (should NOT increase counts)
    print("\n--- Test 2: Failed Booking (Invalid Time) ---")
    session_id = "test_booking_fail"
    
    messages = [
        "I want to book an appointment",
        "My name is Failed Test Patient", 
        "I need to see Dr. Baker",
        "Tomorrow at 99 PM"  # Invalid time
    ]
    
    for message in messages:
        response = requests.post(
            f"{base_url}/api/chat",
            json={"message": message, "session_id": session_id},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"User: {message}")
            print(f"Assistant: {result.get('message', 'No response')}")
            
            if not result.get('success') and "couldn't understand" in result.get('message', '').lower():
                print("✅ Booking failed as expected!")
                break
        else:
            print(f"❌ Error: {response.status_code}")
    
    # Check counts after failed booking
    stats_response = requests.get(f"{base_url}/api/stats")
    if stats_response.status_code == 200:
        final_stats = stats_response.json()
        final_patients = final_stats.get("data_store", {}).get("statistics", {}).get("total_patients", 0)
        final_appointments = final_stats.get("data_store", {}).get("statistics", {}).get("active_appointments", 0)
        
        print(f"After Failed - Patients: {final_patients}, Appointments: {final_appointments}")
        
        if final_patients == patients_after_success and final_appointments == appointments_after_success:
            print("✅ Counts remained unchanged for failed booking")
        else:
            print("❌ Counts incorrectly changed for failed booking")
    
    print("\n" + "=" * 40)
    print("Test completed!")

if __name__ == "__main__":
    test_booking_counts()