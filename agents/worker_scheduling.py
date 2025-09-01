"""
Scheduling Worker Agent - Internal only, no user communication
Handles booking logic behind the scenes for the Master Agent
"""
from typing import Dict, Any
from datetime import datetime, date, timedelta

class SchedulingWorker:
    """Worker agent that handles appointment booking logic"""
    
    def __init__(self, data_store):
        self.data_store = data_store
        print("SUCCESS: Scheduling Worker Agent initialized")
    
    def execute_booking(self, booking_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute appointment booking based on provided information
        This method is called by the Master Agent only
        """
        try:
            # Extract information
            patient_id = booking_info.get("patient_id")
            doctor_name = booking_info.get("doctor_name") or booking_info.get("specialty")
            date_str = booking_info.get("date")
            time_str = booking_info.get("time")
            
            # Validate patient ID is provided and exists
            if not patient_id:
                return {
                    "success": False,
                    "message": "Patient ID is required for appointment booking. Please provide your 7-character patient ID (format: P + 2 letters + 4 numbers)."
                }
                
            patient = self.data_store.get_patient_by_id(patient_id)
            if not patient:
                return {
                    "success": False,
                    "message": f"Patient ID '{patient_id}' not found in our system. Please check your patient ID or contact reception for assistance."
                }
            
            # Find doctor first (don't create patient yet)
            doctor = self.data_store.find_doctor_by_name_or_specialty(doctor_name)
            if not doctor:
                return {
                    "success": False,
                    "message": f"I couldn't find a doctor matching '{doctor_name}'. Our available doctors are: {', '.join([d['name'] + ' (' + d['specialty'] + ')' for d in self.data_store.get_all_doctors()])}"
                }
            
            # Parse date and time before creating patient
            parsed_date = self._parse_date(date_str)
            parsed_time = self._parse_time(time_str)
            
            if not parsed_date:
                return {
                    "success": False,
                    "message": f"I couldn't understand the date '{date_str}'. Please try something like 'tomorrow', 'next Monday', or '2024-08-30'."
                }
            
            if not parsed_time:
                return {
                    "success": False,
                    "message": f"I couldn't understand the time '{time_str}'. Please try something like '2 PM', '14:30', or 'morning'."
                }
            
            # Check availability before creating patient
            if not self.data_store.is_slot_available(doctor['id'], parsed_date, parsed_time):
                return {
                    "success": False,
                    "message": f"{doctor['name']} is not available on {self._format_date(parsed_date)} at {self._format_time(parsed_time)}. Would you like to see other available times?"
                }
            
            # Patient already validated above, use the existing patient_id
            
            # Create appointment
            appointment_id = self.data_store.create_appointment(
                patient_id=patient_id,
                doctor_id=doctor['id'],
                date=parsed_date,
                time=parsed_time
            )
            
            formatted_date = self._format_date(parsed_date)
            formatted_time = self._format_time(parsed_time)
            
            return {
                "success": True,
                "message": f"{patient['name']} is scheduled with {doctor['name']} on {formatted_date} at {formatted_time}.",
                "appointment_id": appointment_id,
                "patient_name": patient['name'],
                "patient_id": patient_id,
                "doctor_name": doctor['name'],
                "doctor_specialty": doctor['specialty'],
                "date": parsed_date,
                "time": parsed_time,
                "formatted_date": formatted_date,
                "formatted_time": formatted_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"I encountered an error while booking the appointment: {str(e)}"
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
                # Handle "next Monday", "next Friday", etc.
                weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for i, day in enumerate(weekdays):
                    if day in date_str_lower:
                        days_ahead = i - today.weekday()
                        if days_ahead <= 0:
                            days_ahead += 7
                        target_date = today + timedelta(days=days_ahead)
                        return target_date.strftime('%Y-%m-%d')
            elif 'this' in date_str_lower:
                # Handle "this Monday", "this Friday", etc.
                weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for i, day in enumerate(weekdays):
                    if day in date_str_lower:
                        days_ahead = i - today.weekday()
                        if days_ahead < 0:
                            days_ahead += 7
                        target_date = today + timedelta(days=days_ahead)
                        return target_date.strftime('%Y-%m-%d')
            else:
                # Try to parse various date formats
                formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y', '%b %d, %Y']
                for fmt in formats:
                    try:
                        parsed = datetime.strptime(date_str, fmt)
                        return parsed.strftime('%Y-%m-%d')
                    except:
                        continue
        except:
            pass
        
        return None
    
    def _parse_time(self, time_str: str) -> str:
        """Convert natural language time to HH:MM format"""
        if not time_str:
            return None
        
        time_str_lower = time_str.lower().strip()
        
        try:
            # Handle natural time references
            if 'morning' in time_str_lower:
                return '09:00'
            elif 'afternoon' in time_str_lower:
                return '14:00'
            elif 'evening' in time_str_lower:
                return '17:00'
            elif 'noon' in time_str_lower or time_str_lower == '12pm':
                return '12:00'
            else:
                # Try to parse specific times
                import re
                
                # Pattern for time like "2 PM", "3:30 PM", "14:30"
                time_patterns = [
                    r'(\d{1,2}):(\d{2})\s*(am|pm)',  # 3:30 PM
                    r'(\d{1,2})\s*(am|pm)',         # 3 PM
                    r'(\d{1,2}):(\d{2})',           # 14:30
                ]
                
                for pattern in time_patterns:
                    match = re.search(pattern, time_str_lower)
                    if match:
                        groups = match.groups()
                        
                        if len(groups) == 3:  # Hour:Minute AM/PM
                            hour, minute, period = groups
                            hour, minute = int(hour), int(minute)
                            
                            if period == 'pm' and hour != 12:
                                hour += 12
                            elif period == 'am' and hour == 12:
                                hour = 0
                                
                            if 0 <= hour <= 23 and 0 <= minute <= 59:
                                return f"{hour:02d}:{minute:02d}"
                        
                        elif len(groups) == 2 and groups[1] in ['am', 'pm']:  # Hour AM/PM
                            hour, period = groups
                            hour = int(hour)
                            
                            if period == 'pm' and hour != 12:
                                hour += 12
                            elif period == 'am' and hour == 12:
                                hour = 0
                                
                            if 0 <= hour <= 23:
                                return f"{hour:02d}:00"
                        
                        elif len(groups) == 2:  # Hour:Minute 24hr
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