"""
Persistent data store for the appointment system with local file storage
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
from pathlib import Path
import random
import string

class DataStore:
    """Persistent data store for patients, doctors, and appointments with local file storage"""
    
    def __init__(self, data_file: str = "appointment_data.json"):
        self.data_file = data_file
        self.patients = {}  # alphanumeric_id -> patient data
        self.doctors = {}   # id -> doctor data  
        self.appointments = {}  # id -> appointment data
        self.next_appointment_id = 1
        self.used_patient_ids = set()  # Track used alphanumeric patient IDs
        
        # Load existing data or initialize with sample data
        self._load_data()
        
        print(f"SUCCESS: DataStore initialized with {len(self.patients)} patients and {len([a for a in self.appointments.values() if a['status'] == 'scheduled'])} active appointments")
    
    def _generate_unique_patient_id(self) -> str:
        """Generate a unique alphanumeric patient ID (format: P + 2 letters + 4 numbers)"""
        while True:
            # Generate format: P + 2 random letters + 4 random numbers
            letters = ''.join(random.choices(string.ascii_uppercase, k=2))
            numbers = ''.join(random.choices(string.digits, k=4))
            patient_id = f"P{letters}{numbers}"
            
            # Ensure uniqueness
            if patient_id not in self.used_patient_ids:
                self.used_patient_ids.add(patient_id)
                return patient_id
    
    def _load_data(self):
        """Load data from file or initialize with sample data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Load saved data
                loaded_patients = data.get('patients', {})
                self.doctors = {int(k): v for k, v in data.get('doctors', {}).items()}
                self.appointments = {int(k): v for k, v in data.get('appointments', {}).items()}
                self.next_appointment_id = data.get('next_appointment_id', 1)
                
                # Handle patient ID migration from integer to alphanumeric
                self.patients = {}
                self.used_patient_ids = set(data.get('used_patient_ids', []))
                
                for k, v in loaded_patients.items():
                    # Check if this is an old integer ID that needs migration
                    if k.isdigit():
                        # Generate new alphanumeric ID for existing patient
                        new_patient_id = self._generate_unique_patient_id()
                        v['id'] = new_patient_id
                        v['old_id'] = int(k)  # Keep reference to old ID for appointment updates
                        self.patients[new_patient_id] = v
                        print(f"MIGRATION: Patient '{v['name']}' migrated to new secure ID format")
                    else:
                        # Already alphanumeric ID
                        self.patients[k] = v
                        self.used_patient_ids.add(k)
                
                # If migration occurred, save the updated data immediately
                if any(k.isdigit() for k in loaded_patients.keys()):
                    print("MIGRATION: Saving migrated patient data...")
                    self._save_data()
                
                # Initialize doctors if none exist (first time setup)
                if not self.doctors:
                    self._init_sample_doctors()
                    
                print(f"SUCCESS: Loaded data from {self.data_file}")
            else:
                # First time - initialize with sample data
                self._init_sample_doctors()
                self._save_data()
                print(f"SUCCESS: Initialized new data file {self.data_file}")
                
        except Exception as e:
            print(f"ERROR: Could not load data file, starting fresh: {e}")
            self._init_sample_doctors()
    
    def _init_sample_doctors(self):
        """Initialize with sample doctors"""
        sample_doctors = [
            {"id": 1, "name": "Dr. Adams", "specialty": "General Medicine"},
            {"id": 2, "name": "Dr. Baker", "specialty": "Pediatrics"},
            {"id": 3, "name": "Dr. Clark", "specialty": "Dermatology"},
            {"id": 4, "name": "Dr. Davis", "specialty": "Endocrinology"}
        ]
        
        for doctor in sample_doctors:
            self.doctors[doctor['id']] = doctor
    
    def _save_data(self):
        """Save current data to file"""
        try:
            data = {
                'patients': self.patients,
                'doctors': self.doctors,
                'appointments': self.appointments,
                'next_appointment_id': self.next_appointment_id,
                'used_patient_ids': list(self.used_patient_ids),
                'last_saved': datetime.now().isoformat()
            }
            
            # Create backup of existing file
            if os.path.exists(self.data_file):
                backup_file = f"{self.data_file}.backup"
                os.replace(self.data_file, backup_file)
            
            # Save new data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"ERROR: Could not save data: {e}")
            # Restore backup if save failed
            backup_file = f"{self.data_file}.backup"
            if os.path.exists(backup_file) and not os.path.exists(self.data_file):
                os.replace(backup_file, self.data_file)
    
    # Patient methods
    def create_patient(self, name: str, age: int = 35, condition: str = "General consultation") -> str:
        """Create a new patient and return the alphanumeric ID"""
        patient_id = self._generate_unique_patient_id()
        self.patients[patient_id] = {
            "id": patient_id,
            "name": name,
            "age": age,
            "condition": condition,
            "created_at": datetime.now().isoformat()
        }
        self._save_data()  # Auto-save after creating patient
        return patient_id
    
    def find_patient_by_name(self, name: str) -> Optional[Dict]:
        """Find patient by name (case insensitive)"""
        name_lower = name.lower().strip()
        for patient in self.patients.values():
            if name_lower in patient['name'].lower():
                return patient
        return None
    
    def get_patient_by_id(self, patient_id) -> Optional[Dict]:
        """Get patient by ID (supports both old integer IDs and new alphanumeric IDs)"""
        # If it's a string (alphanumeric ID), use directly
        if isinstance(patient_id, str):
            return self.patients.get(patient_id)
        
        # If it's an integer (old ID), search by old_id field
        if isinstance(patient_id, int):
            for patient in self.patients.values():
                if patient.get('old_id') == patient_id:
                    return patient
            # Also check if it was passed as string version of integer
            return self.patients.get(str(patient_id))
        
        return None
    
    def get_all_patients(self) -> List[Dict]:
        """Get all patients"""
        return list(self.patients.values())
    
    # Doctor methods
    def get_all_doctors(self) -> List[Dict]:
        """Get all doctors"""
        return list(self.doctors.values())
    
    def get_doctor_by_id(self, doctor_id: int) -> Optional[Dict]:
        """Get doctor by ID"""
        return self.doctors.get(doctor_id)
    
    def find_doctor_by_name_or_specialty(self, query: str) -> Optional[Dict]:
        """Find doctor by name or specialty"""
        query_lower = query.lower().strip()
        
        # First try exact name match
        for doctor in self.doctors.values():
            if query_lower in doctor['name'].lower():
                return doctor
        
        # Then try specialty match
        specialty_mapping = {
            'dermatologist': 'dermatology',
            'pediatrician': 'pediatrics',
            'general': 'general medicine',
            'endocrinologist': 'endocrinology'
        }
        
        mapped_specialty = specialty_mapping.get(query_lower, query_lower)
        
        for doctor in self.doctors.values():
            if mapped_specialty in doctor['specialty'].lower():
                return doctor
        
        return None
    
    # Appointment methods
    def create_appointment(self, patient_id, doctor_id: int, date: str, time: str) -> int:
        """Create a new appointment and return the ID"""
        # Ensure we're using the correct patient ID format
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        # Use the current patient ID (alphanumeric) for new appointments
        current_patient_id = patient['id']
        
        appointment_id = self.next_appointment_id
        self.appointments[appointment_id] = {
            "id": appointment_id,
            "patient_id": current_patient_id,  # Always use alphanumeric ID
            "doctor_id": doctor_id,
            "date": date,  # YYYY-MM-DD format
            "time": time,  # HH:MM format
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        self.next_appointment_id += 1
        self._save_data()  # Auto-save after creating appointment
        return appointment_id
    
    def get_appointment_by_id(self, appointment_id: int) -> Optional[Dict]:
        """Get appointment by ID"""
        return self.appointments.get(appointment_id)
    
    def get_all_appointments(self, include_expired: bool = False) -> List[Dict]:
        """Get all appointments with patient and doctor info"""
        result = []
        now = datetime.now()
        
        for apt in self.appointments.values():
            # Skip cancelled appointments
            if apt['status'] == 'cancelled':
                continue
                
            # Check if appointment has expired (using full datetime comparison)
            try:
                apt_datetime_str = f"{apt['date']} {apt['time']}"
                apt_datetime = datetime.strptime(apt_datetime_str, '%Y-%m-%d %H:%M')
                is_expired = apt_datetime < now
                
                # Skip expired appointments unless specifically requested
                if is_expired and not include_expired:
                    continue
                    
            except (ValueError, TypeError):
                # If date parsing fails, include the appointment
                is_expired = False
            
            patient = self.get_patient_by_id(apt['patient_id'])
            doctor = self.get_doctor_by_id(apt['doctor_id'])
            
            apt_data = apt.copy()
            apt_data['patient_name'] = patient['name'] if patient else 'Unknown'
            apt_data['doctor_name'] = doctor['name'] if doctor else 'Unknown'
            apt_data['specialty'] = doctor['specialty'] if doctor else 'Unknown'
            apt_data['is_expired'] = is_expired if 'apt_date' in locals() else False
            
            result.append(apt_data)
        
        return result
    
    def get_patient_appointments(self, patient_id) -> List[Dict]:
        """Get all appointments for a specific patient"""
        # Get the patient to understand their current ID
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return []
        
        current_patient_id = patient['id']
        old_patient_id = patient.get('old_id')
        
        result = []
        for apt in self.appointments.values():
            # Match against current alphanumeric ID or old integer ID
            if ((apt['patient_id'] == current_patient_id or 
                 apt['patient_id'] == old_patient_id) and 
                apt['status'] != 'cancelled'):
                result.append(apt)
        return result
    
    def is_slot_available(self, doctor_id: int, date: str, time: str) -> bool:
        """Check if a time slot is available for a doctor"""
        for apt in self.appointments.values():
            if (apt['doctor_id'] == doctor_id and 
                apt['date'] == date and 
                apt['time'] == time and 
                apt['status'] == 'scheduled'):
                return False
        return True
    
    def update_appointment(self, appointment_id: int, new_date: str, new_time: str) -> bool:
        """Update an appointment's date and time"""
        if appointment_id in self.appointments:
            self.appointments[appointment_id]['date'] = new_date
            self.appointments[appointment_id]['time'] = new_time
            self.appointments[appointment_id]['updated_at'] = datetime.now().isoformat()
            self._save_data()  # Auto-save after updating appointment
            return True
        return False
    
    def delete_appointment(self, appointment_id: int) -> bool:
        """Cancel an appointment (mark as cancelled)"""
        if appointment_id in self.appointments:
            self.appointments[appointment_id]['status'] = 'cancelled'
            self.appointments[appointment_id]['cancelled_at'] = datetime.now().isoformat()
            self._save_data()  # Auto-save after cancelling appointment
            return True
        return False
    
    def delete_patient(self, patient_id: int) -> bool:
        """Delete a patient from the system"""
        if patient_id in self.patients:
            del self.patients[patient_id]
            self._save_data()  # Auto-save after deleting patient
            return True
        return False
    
    def backup_data(self, backup_filename: str = None) -> str:
        """Create a manual backup of the data"""
        if not backup_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"appointment_data_backup_{timestamp}.json"
        
        try:
            data = {
                'patients': self.patients,
                'doctors': self.doctors,
                'appointments': self.appointments,
                'next_appointment_id': self.next_appointment_id,
                'used_patient_ids': list(self.used_patient_ids),
                'backup_created': datetime.now().isoformat()
            }
            
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return backup_filename
        except Exception as e:
            print(f"ERROR: Could not create backup: {e}")
            return None
    
    def get_data_file_info(self) -> Dict[str, Any]:
        """Get information about the data file"""
        try:
            if os.path.exists(self.data_file):
                stat = os.stat(self.data_file)
                return {
                    "file_exists": True,
                    "file_path": os.path.abspath(self.data_file),
                    "file_size": stat.st_size,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            else:
                return {
                    "file_exists": False,
                    "file_path": os.path.abspath(self.data_file)
                }
        except Exception as e:
            return {
                "error": str(e)
            }
    
    # Statistics methods
    def get_stats(self) -> Dict[str, int]:
        """Get basic statistics"""
        today = datetime.now().date()
        active_appointments = []
        expired_appointments = []
        
        for apt in self.appointments.values():
            if apt['status'] == 'scheduled':
                try:
                    apt_date = datetime.strptime(apt['date'], '%Y-%m-%d').date()
                    if apt_date < today:
                        expired_appointments.append(apt)
                    else:
                        active_appointments.append(apt)
                except (ValueError, TypeError):
                    # If date parsing fails, count as active
                    active_appointments.append(apt)
        
        return {
            "total_patients": len(self.patients),
            "total_doctors": len(self.doctors),
            "active_appointments": len(active_appointments),
            "expired_appointments": len(expired_appointments),
            "completed_appointments": len([a for a in self.appointments.values() if a['status'] == 'completed']),
            "cancelled_appointments": len([a for a in self.appointments.values() if a['status'] == 'cancelled'])
        }
    
    def cleanup_expired_appointments(self) -> Dict[str, Any]:
        """COMPLETELY REMOVE expired appointments from storage and return cleanup summary"""
        now = datetime.now()
        expired_count = 0
        expired_appointments = []
        appointments_to_remove = []
        
        # First pass: identify ALL expired appointments (regardless of status)
        for apt_id, apt in self.appointments.items():
            try:
                # Parse date and time to create full datetime for comparison
                apt_datetime_str = f"{apt['date']} {apt['time']}"
                apt_datetime = datetime.strptime(apt_datetime_str, '%Y-%m-%d %H:%M')
                
                # Compare full datetime - if appointment time has passed, remove it
                if apt_datetime < now:
                    expired_count += 1
                    
                    # Get patient and doctor names for logging before removal
                    patient = self.get_patient_by_id(apt['patient_id'])
                    doctor = self.get_doctor_by_id(apt['doctor_id'])
                    
                    expired_appointments.append({
                        'appointment_id': apt['id'],
                        'patient_name': patient['name'] if patient else 'Unknown',
                        'doctor_name': doctor['name'] if doctor else 'Unknown',
                        'date': apt['date'],
                        'time': apt['time'],
                        'status': apt['status']
                    })
                    
                    appointments_to_remove.append(apt_id)
                    
            except (ValueError, TypeError):
                continue
        
        # Second pass: actually remove the expired appointments
        for apt_id in appointments_to_remove:
            del self.appointments[apt_id]
            print(f"REMOVED: Expired appointment ID {apt_id} deleted from storage")
        
        if expired_count > 0:
            self._save_data()  # Save changes to file
            print(f"SUCCESS: {expired_count} expired appointments completely removed from storage")
        
        return {
            'expired_count': expired_count,
            'expired_appointments': expired_appointments,
            'cleanup_date': datetime.now().isoformat(),
            'removed_appointment_ids': appointments_to_remove
        }