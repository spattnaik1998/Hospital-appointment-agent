"""
Example: Register patients using Python code
"""
import requests
import json

def register_patient_via_python():
    """Method 2: Register patient using Python requests"""
    base_url = "http://127.0.0.1:8001"
    
    # Patient data
    patient_data = {
        "name": "Robert Chen",
        "age": 42,
        "condition": "Cardiac consultation"
    }
    
    try:
        # Make the API call
        response = requests.post(
            f"{base_url}/api/patients",
            json=patient_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Patient registered successfully!")
            print(f"   Patient ID: {result.get('patient_id')}")
            print(f"   Name: {patient_data['name']}")
            print(f"   Age: {patient_data['age']}")
            print(f"   Condition: {patient_data['condition']}")
            return result.get('patient_id')
        else:
            print(f"ERROR: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        return None

def register_via_appointment_booking():
    """Method 3: Register patient automatically through appointment booking"""
    base_url = "http://127.0.0.1:8001"
    
    message_data = {
        "message": "I want to book an appointment with Dr. Baker tomorrow at 11 AM for Jennifer Wilson",
        "session_id": "python_booking_demo"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json=message_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Patient registered via appointment booking!")
            print(f"   Message: {result.get('message', 'No message')}")
            print(f"   Success: {result.get('success')}")
            
            if result.get('booking_result'):
                booking = result['booking_result']
                print(f"   Patient: {booking.get('patient_name')}")
                print(f"   Doctor: {booking.get('doctor_name')}")
                print(f"   Appointment: {booking.get('formatted_date')} at {booking.get('formatted_time')}")
        else:
            print(f"ERROR: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")

def check_current_patients():
    """Check how many patients we have now"""
    base_url = "http://127.0.0.1:8001"
    
    try:
        response = requests.get(f"{base_url}/api/patients")
        if response.status_code == 200:
            patients = response.json().get('patients', [])
            print(f"\nCurrent patients in system: {len(patients)}")
            for patient in patients:
                print(f"   - {patient['name']} (ID: {patient['id']}) - {patient['condition']}")
        
        # Also check appointments
        response = requests.get(f"{base_url}/api/appointments")
        if response.status_code == 200:
            appointments = response.json().get('appointments', [])
            print(f"\nCurrent appointments: {len(appointments)}")
            for apt in appointments:
                print(f"   - {apt['patient_name']} with {apt['doctor_name']} on {apt['date']} at {apt['time']}")
                
    except Exception as e:
        print(f"Error checking patients: {e}")

if __name__ == "__main__":
    print("Patient Registration Methods Demo")
    print("=" * 40)
    
    print("\n1. Current patients:")
    check_current_patients()
    
    print("\n2. Registering patient via Python API call...")
    register_patient_via_python()
    
    print("\n3. Registering patient via appointment booking...")
    register_via_appointment_booking()
    
    print("\n4. Final patient count:")
    check_current_patients()
    
    print("\n" + "=" * 40)
    print("Demo completed!")