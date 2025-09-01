"""
Management Worker Agent - Internal only, no user communication  
Handles appointment rescheduling and cancellation behind the scenes for the Master Agent
"""
from typing import Dict, Any
from datetime import datetime, date, timedelta

class ManagementWorker:
    """Worker agent that handles appointment management (reschedule/cancel)"""
    
    def __init__(self, data_store):
        self.data_store = data_store
        print("SUCCESS: Management Worker Agent initialized")
    
    def reschedule_appointment(self, reschedule_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reschedule an appointment based on provided information
        This method is called by the Master Agent only
        """
        try:
            patient_id = reschedule_info.get("patient_id")
            current_date = reschedule_info.get("current_date")
            new_date = reschedule_info.get("date") or reschedule_info.get("new_date")
            new_time = reschedule_info.get("time") or reschedule_info.get("new_time")
            
            if not patient_id:
                return {
                    "success": False,
                    "message": "I need your patient ID to reschedule your appointment. Please provide your 7-character patient ID."
                }
            
            # Find patient
            patient = self.data_store.get_patient_by_id(patient_id)
            if not patient:
                return {
                    "success": False,
                    "message": f"Patient ID '{patient_id}' not found in our system. Please check your patient ID."
                }
            
            # Find the appointment to reschedule
            appointments = self.data_store.get_patient_appointments(patient_id)
            target_appointment = None
            
            if current_date:
                # Find by specific date
                parsed_current_date = self._parse_date(current_date)
                if parsed_current_date:
                    for apt in appointments:
                        if apt['date'] == parsed_current_date:
                            target_appointment = apt
                            break
            
            if not target_appointment:
                # Find the next upcoming appointment
                today = date.today().strftime('%Y-%m-%d')
                future_appointments = [a for a in appointments if a['date'] >= today]
                if future_appointments:
                    target_appointment = sorted(future_appointments, key=lambda x: x['date'])[0]
            
            if not target_appointment:
                return {
                    "success": False,
                    "message": f"I couldn't find any upcoming appointments for {patient['name']} to reschedule."
                }
            
            # If no new date/time provided, ask for it
            if not new_date or not new_time:
                doctor = self.data_store.get_doctor_by_id(target_appointment['doctor_id'])
                current_formatted_date = self._format_date(target_appointment['date'])
                current_formatted_time = self._format_time(target_appointment['time'])
                
                return {
                    "success": False,
                    "message": f"I found your appointment with {doctor['name']} on {current_formatted_date} at {current_formatted_time}. What new date and time would you like?"
                }
            
            # Parse new date and time
            parsed_new_date = self._parse_date(new_date)
            parsed_new_time = self._parse_time(new_time)
            
            if not parsed_new_date:
                return {
                    "success": False,
                    "message": f"I couldn't understand the date '{new_date}'. Please try something like 'tomorrow', 'next Monday', or '2024-08-30'."
                }
            
            if not parsed_new_time:
                return {
                    "success": False,
                    "message": f"I couldn't understand the time '{new_time}'. Please try something like '2 PM', '14:30', or 'morning'."
                }
            
            # Check if new slot is available
            doctor_id = target_appointment['doctor_id']
            if not self.data_store.is_slot_available(doctor_id, parsed_new_date, parsed_new_time):
                doctor = self.data_store.get_doctor_by_id(doctor_id)
                formatted_new_date = self._format_date(parsed_new_date)
                formatted_new_time = self._format_time(parsed_new_time)
                
                return {
                    "success": False,
                    "message": f"{doctor['name']} is not available on {formatted_new_date} at {formatted_new_time}. Would you like to see other available times?"
                }
            
            # Update the appointment
            success = self.data_store.update_appointment(
                target_appointment['id'],
                parsed_new_date,
                parsed_new_time
            )
            
            if success:
                doctor = self.data_store.get_doctor_by_id(doctor_id)
                old_formatted_date = self._format_date(target_appointment['date'])
                old_formatted_time = self._format_time(target_appointment['time'])
                new_formatted_date = self._format_date(parsed_new_date)
                new_formatted_time = self._format_time(parsed_new_time)
                
                return {
                    "success": True,
                    "message": f"Perfect! I've rescheduled {patient['name']}'s appointment with {doctor['name']} from {old_formatted_date} at {old_formatted_time} to {new_formatted_date} at {new_formatted_time}.",
                    "old_date": target_appointment['date'],
                    "old_time": target_appointment['time'],
                    "new_date": parsed_new_date,
                    "new_time": parsed_new_time,
                    "doctor_name": doctor['name']
                }
            else:
                return {
                    "success": False,
                    "message": "I encountered an error while rescheduling your appointment. Please try again."
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"I encountered an error while rescheduling: {str(e)}"
            }
    
    def cancel_appointment(self, cancel_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cancel an appointment based on provided information
        This method is called by the Master Agent only
        """
        try:
            patient_id = cancel_info.get("patient_id")
            appointment_date = cancel_info.get("date") or cancel_info.get("appointment_date")
            
            if not patient_id:
                return {
                    "success": False,
                    "message": "I need your patient ID to cancel your appointment. Please provide your 7-character patient ID."
                }
            
            # Find patient
            patient = self.data_store.get_patient_by_id(patient_id)
            if not patient:
                return {
                    "success": False,
                    "message": f"Patient ID '{patient_id}' not found in our system. Please check your patient ID."
                }
            
            # Find the appointment to cancel
            appointments = self.data_store.get_patient_appointments(patient_id)
            target_appointment = None
            
            if appointment_date:
                # Find by specific date
                parsed_date = self._parse_date(appointment_date)
                if parsed_date:
                    for apt in appointments:
                        if apt['date'] == parsed_date:
                            target_appointment = apt
                            break
            
            if not target_appointment:
                # Find the next upcoming appointment
                today = date.today().strftime('%Y-%m-%d')
                future_appointments = [a for a in appointments if a['date'] >= today]
                if future_appointments:
                    target_appointment = sorted(future_appointments, key=lambda x: x['date'])[0]
            
            if not target_appointment:
                return {
                    "success": False,
                    "message": f"I couldn't find any upcoming appointments for {patient['name']} to cancel."
                }
            
            # If no specific date provided, confirm which appointment
            if not appointment_date and len([a for a in appointments if a['date'] >= today]) > 1:
                doctor = self.data_store.get_doctor_by_id(target_appointment['doctor_id'])
                formatted_date = self._format_date(target_appointment['date'])
                formatted_time = self._format_time(target_appointment['time'])
                
                return {
                    "success": False,
                    "message": f"I found your appointment with {doctor['name']} on {formatted_date} at {formatted_time}. Is this the appointment you want to cancel?"
                }
            
            # Cancel the appointment
            success = self.data_store.delete_appointment(target_appointment['id'])
            
            if success:
                doctor = self.data_store.get_doctor_by_id(target_appointment['doctor_id'])
                formatted_date = self._format_date(target_appointment['date'])
                formatted_time = self._format_time(target_appointment['time'])
                
                message = f"I've successfully cancelled {patient['name']}'s appointment with {doctor['name']} on {formatted_date} at {formatted_time}."
                
                # Check if patient has any other active appointments
                remaining_appointments = self.data_store.get_patient_appointments(patient_id)
                patient_removed = False
                
                if not remaining_appointments:
                    # Only remove patient if they have no other appointments
                    patient_removed = self.data_store.delete_patient(patient_id)
                    if patient_removed:
                        message += f" {patient['name']} has also been removed from the patient database."
                
                return {
                    "success": True,
                    "message": message,
                    "cancelled_date": target_appointment['date'],
                    "cancelled_time": target_appointment['time'],
                    "doctor_name": doctor['name'],
                    "patient_removed": patient_removed
                }
            else:
                return {
                    "success": False,
                    "message": "I encountered an error while cancelling your appointment. Please try again."
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"I encountered an error while cancelling: {str(e)}"
            }
    
    def _parse_date(self, date_str: str) -> str:
        """Convert natural language date to YYYY-MM-DD format"""
        if not date_str:
            return None
            
        # Check if already in correct format
        if len(date_str) == 10 and date_str.count('-') == 2:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except:
                pass
        
        today = date.today()
        date_str_lower = date_str.lower().strip()
        
        try:
            if date_str_lower == 'today':
                return today.strftime('%Y-%m-%d')
            elif date_str_lower == 'tomorrow':
                return (today + timedelta(days=1)).strftime('%Y-%m-%d')
            elif 'next' in date_str_lower:
                weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for i, day in enumerate(weekdays):
                    if day in date_str_lower:
                        days_ahead = i - today.weekday()
                        if days_ahead <= 0:
                            days_ahead += 7
                        target_date = today + timedelta(days=days_ahead)
                        return target_date.strftime('%Y-%m-%d')
        except:
            pass
        
        return None
    
    def _parse_time(self, time_str: str) -> str:
        """Convert natural language time to HH:MM format"""
        if not time_str:
            return None
        
        time_str_lower = time_str.lower().strip()
        
        try:
            if 'morning' in time_str_lower:
                return '09:00'
            elif 'afternoon' in time_str_lower:
                return '14:00'
            elif 'evening' in time_str_lower:
                return '17:00'
            else:
                import re
                time_patterns = [
                    r'(\d{1,2}):(\d{2})\s*(am|pm)',
                    r'(\d{1,2})\s*(am|pm)',
                    r'(\d{1,2}):(\d{2})',
                ]
                
                for pattern in time_patterns:
                    match = re.search(pattern, time_str_lower)
                    if match:
                        groups = match.groups()
                        
                        if len(groups) == 3:
                            hour, minute, period = groups
                            hour, minute = int(hour), int(minute)
                            if period == 'pm' and hour != 12:
                                hour += 12
                            elif period == 'am' and hour == 12:
                                hour = 0
                            if 0 <= hour <= 23 and 0 <= minute <= 59:
                                return f"{hour:02d}:{minute:02d}"
                        
                        elif len(groups) == 2 and groups[1] in ['am', 'pm']:
                            hour, period = groups
                            hour = int(hour)
                            if period == 'pm' and hour != 12:
                                hour += 12
                            elif period == 'am' and hour == 12:
                                hour = 0
                            if 0 <= hour <= 23:
                                return f"{hour:02d}:00"
                        
                        elif len(groups) == 2:
                            hour, minute = groups
                            hour, minute = int(hour), int(minute)
                            if 0 <= hour <= 23 and 0 <= minute <= 59:
                                return f"{hour:02d}:{minute:02d}"
        except:
            pass
        
        return None
    
    def _format_date(self, date_str: str) -> str:
        """Format date for display"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            return date_obj.strftime('%A, %B %d, %Y')
        except:
            return date_str
    
    def _format_time(self, time_str: str) -> str:
        """Format time for display"""
        try:
            time_obj = datetime.strptime(time_str, '%H:%M').time()
            return time_obj.strftime('%I:%M %p')
        except:
            return time_str