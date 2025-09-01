"""
Query Worker Agent - Internal only, no user communication
Handles availability queries behind the scenes for the Master Agent
"""
from typing import Dict, Any, List
from datetime import datetime, date, timedelta

class QueryWorker:
    """Worker agent that handles availability queries"""
    
    def __init__(self, data_store):
        self.data_store = data_store
        print("SUCCESS: Query Worker Agent initialized")
    
    def get_availability(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get available appointment slots based on query parameters
        This method is called by the Master Agent only
        """
        try:
            doctor_name = query_params.get("doctor_name")
            specialty = query_params.get("specialty") 
            date_preference = query_params.get("date_preference")
            
            # Get available slots
            slots = self._find_available_slots(doctor_name, specialty, date_preference)
            
            if not slots:
                message = self._create_no_availability_message(doctor_name, specialty)
                return {
                    "success": True,
                    "message": message,
                    "slots": [],
                    "total_available": 0
                }
            
            # Format the response message
            message = self._format_availability_message(slots, doctor_name, specialty)
            
            return {
                "success": True,
                "message": message,
                "slots": slots[:10],  # Limit to first 10 slots
                "total_available": len(slots)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"I had trouble checking availability: {str(e)}",
                "slots": []
            }
    
    def _find_available_slots(self, doctor_name: str = None, specialty: str = None, date_preference: str = None) -> List[Dict]:
        """Find available appointment slots"""
        slots = []
        today = date.today()
        
        # Determine date range
        if date_preference:
            start_date = self._parse_date_preference(date_preference)
            if start_date:
                days_to_check = 3  # Check 3 days from specified date
            else:
                start_date = today + timedelta(days=1)  # Tomorrow
                days_to_check = 7
        else:
            start_date = today + timedelta(days=1)  # Tomorrow
            days_to_check = 7
        
        # Get doctors to check
        if doctor_name:
            doctor = self.data_store.find_doctor_by_name_or_specialty(doctor_name)
            doctors = [doctor] if doctor else []
        elif specialty:
            doctor = self.data_store.find_doctor_by_name_or_specialty(specialty)
            doctors = [doctor] if doctor else []
        else:
            doctors = self.data_store.get_all_doctors()
        
        # Find available slots
        for i in range(days_to_check):
            check_date = start_date + timedelta(days=i)
            
            # Skip weekends
            if check_date.weekday() >= 5:
                continue
                
            date_str = check_date.strftime('%Y-%m-%d')
            
            # Standard appointment times
            times = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00']
            
            for doctor in doctors:
                for time_slot in times:
                    if self.data_store.is_slot_available(doctor['id'], date_str, time_slot):
                        slots.append({
                            "doctor_id": doctor['id'],
                            "doctor_name": doctor['name'],
                            "specialty": doctor['specialty'],
                            "date": date_str,
                            "time": time_slot,
                            "day_name": check_date.strftime('%A'),
                            "formatted_date": check_date.strftime('%B %d'),
                            "formatted_time": self._format_time(time_slot)
                        })
        
        return slots
    
    def _parse_date_preference(self, date_pref: str) -> date:
        """Parse date preference"""
        if not date_pref:
            return None
        
        today = date.today()
        date_lower = date_pref.lower().strip()
        
        try:
            if date_lower == 'today':
                return today
            elif date_lower == 'tomorrow':
                return today + timedelta(days=1)
            elif 'next week' in date_lower:
                return today + timedelta(days=7)
            elif 'this week' in date_lower:
                return today
            elif 'next' in date_lower:
                # Handle "next Monday", "next Friday", etc.
                weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for i, day in enumerate(weekdays):
                    if day in date_lower:
                        days_ahead = i - today.weekday()
                        if days_ahead <= 0:
                            days_ahead += 7
                        return today + timedelta(days=days_ahead)
        except:
            pass
        
        return None
    
    def _format_time(self, time_str: str) -> str:
        """Format time for display"""
        try:
            time_obj = datetime.strptime(time_str, '%H:%M').time()
            return time_obj.strftime('%I:%M %p')
        except:
            return time_str
    
    def _create_no_availability_message(self, doctor_name: str = None, specialty: str = None) -> str:
        """Create message when no availability found"""
        if doctor_name:
            return f"I don't see any available slots with {doctor_name} in the next week. Would you like me to check with other doctors or look further ahead?"
        elif specialty:
            return f"I don't see any available slots for {specialty} in the next week. Would you like me to check further ahead or with other specialties?"
        else:
            return "I don't see any available slots in the next week. Would you like me to check further ahead?"
    
    def _format_availability_message(self, slots: List[Dict], doctor_name: str = None, specialty: str = None) -> str:
        """Format the availability message"""
        
        if doctor_name or specialty:
            filter_text = f" with {doctor_name or specialty}"
        else:
            filter_text = ""
        
        message = f"Here are some available appointment slots{filter_text}:\n\n"
        
        # Group by date
        slots_by_date = {}
        for slot in slots[:10]:  # Show first 10 slots
            date_key = f"{slot['day_name']}, {slot['formatted_date']}"
            if date_key not in slots_by_date:
                slots_by_date[date_key] = []
            slots_by_date[date_key].append(slot)
        
        # Format message
        for date_key, date_slots in slots_by_date.items():
            message += f"**{date_key}:**\n"
            for slot in date_slots:
                message += f"• {slot['formatted_time']} - {slot['doctor_name']} ({slot['specialty']})\n"
            message += "\n"
        
        if len(slots) > 10:
            message += f"... and {len(slots) - 10} more slots available."
        
        message += "\nWould you like to book any of these times?"
        
        return message