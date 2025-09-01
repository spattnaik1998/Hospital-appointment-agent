"""
Master Agent - The ONLY agent that communicates with users
Coordinates with worker agents behind the scenes
"""
from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from .conversation_memory import ConversationMemory
from datetime import datetime

class MasterAgent(BaseAgent):
    """
    Master Agent that handles ALL user communication.
    Coordinates with worker agents internally but never lets them talk to the user.
    """
    
    def __init__(self, worker_agents: Dict[str, Any]):
        super().__init__()
        self.memory = ConversationMemory()
        self.worker_agents = worker_agents
        
        print("SUCCESS: Master Agent initialized with conversation memory")
    
    def process_request(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main method: Process user request and return response
        This is the ONLY place where user communication happens
        """
        session_id = context.get('session_id', 'default') if context else 'default'
        
        # Add user message to memory
        self.memory.add_message(session_id, 'user', request)
        
        try:
            # Step 1: Understand what the user wants
            intent_analysis = self._analyze_user_intent(request, session_id)
            intent = intent_analysis.get('intent', 'unclear')
            
            # Step 2: Update conversation context (but preserve booking intent during info gathering)
            current_last_intent = self.memory.get_last_intent(session_id)
            if intent == "provide_info" and current_last_intent in ["book", "reschedule", "cancel"]:
                # Don't override the last intent during information gathering
                pass
            else:
                self.memory.set_last_intent(session_id, intent)
            
            self._update_context_from_message(request, session_id)
            
            # Step 3: Determine what action to take
            response = self._handle_user_request(intent, request, session_id)
            
            # Step 4: Add assistant response to memory
            self.memory.add_message(session_id, 'assistant', response['message'])
            
            return response
            
        except Exception as e:
            error_response = "I apologize, I'm having some technical difficulties. Let me help you in a different way. What would you like to do with your appointment?"
            self.memory.add_message(session_id, 'assistant', error_response)
            
            return {
                "success": False,
                "message": error_response,
                "error": str(e),
                "session_id": session_id
            }
    
    def _analyze_user_intent(self, request: str, session_id: str) -> Dict[str, Any]:
        """Analyze user intent with conversation context"""
        
        # Get conversation context
        recent_messages = self.memory.get_recent_messages(session_id, 4)
        user_context = self.memory.get_user_context(session_id)
        partial_booking = self.memory.get_partial_booking(session_id)
        last_intent = self.memory.get_last_intent(session_id)
        
        # Build context for LLM
        context_info = ""
        if user_context.get("patient_id"):
            context_info += f"Patient ID: {user_context['patient_id']}\n"
        
        if partial_booking:
            context_info += "Current booking in progress:\n"
            for key, value in partial_booking.items():
                context_info += f"  {key}: {value}\n"
        
        if last_intent:
            context_info += f"Last intent: {last_intent}\n"
        
        conversation_context = ""
        if recent_messages:
            conversation_context = "Recent conversation:\n"
            for msg in recent_messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_context += f"{role}: {msg['content']}\n"
        
        messages = [
            {
                "role": "system",
                "content": f"""You are analyzing user intent for an appointment scheduling system.

Current context:
{context_info}

{conversation_context}

Analyze the user's message and determine their intent:
- book: Schedule a new appointment
- reschedule: Change existing appointment 
- cancel: Cancel an appointment
- query: Ask about availability or information
- provide_info: User is providing requested information (name, date, etc.)
- greeting: General greeting or conversation
- unclear: Cannot determine intent

IMPORTANT: If the user is answering a question or providing information in response to your previous request, the intent is likely "provide_info".

Respond with ONLY a JSON object:
{{"intent": "book|reschedule|cancel|query|provide_info|greeting|unclear", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""
            },
            {
                "role": "user",
                "content": request
            }
        ]
        
        try:
            response = self.call_llm(messages, temperature=0.1)
            
            # Try to parse JSON response
            import json
            result = json.loads(response.strip())
            return result
            
        except Exception as e:
            # Fallback intent detection
            request_lower = request.lower()
            if any(word in request_lower for word in ['book', 'schedule', 'appointment', 'see doctor']):
                return {"intent": "book", "confidence": 0.7, "reasoning": "keyword match"}
            elif any(word in request_lower for word in ['available', 'when', 'slots', 'times']):
                return {"intent": "query", "confidence": 0.7, "reasoning": "keyword match"}
            elif any(word in request_lower for word in ['hello', 'hi', 'hey', 'good morning']):
                return {"intent": "greeting", "confidence": 0.8, "reasoning": "keyword match"}
            else:
                return {"intent": "provide_info", "confidence": 0.5, "reasoning": "default fallback"}
    
    def _update_context_from_message(self, request: str, session_id: str):
        """Extract and update context information from user message"""
        
        # Extract patient name if mentioned
        messages = [
            {
                "role": "system",
                "content": """Extract information from the user's message. Return JSON with extracted info:
{
    "patient_id": "patient ID if mentioned (format: P + 2 letters + 4 numbers, e.g., PVY3830), or null",
    "doctor_name": "doctor name if mentioned, or null",
    "date": "date if mentioned, or null", 
    "time": "time if mentioned, or null",
    "specialty": "medical specialty if mentioned, or null"
}"""
            },
            {
                "role": "user",
                "content": request
            }
        ]
        
        try:
            response = self.call_llm(messages, temperature=0.1)
            import json
            extracted = json.loads(response.strip())
            
            # Update user context with extracted info
            if extracted.get("patient_id"):
                self.memory.update_user_context(session_id, patient_id=extracted["patient_id"])
            
            # Update partial booking with extracted info
            partial_update = {}
            for key in ["doctor_name", "date", "time", "specialty"]:
                if extracted.get(key):
                    partial_update[key] = extracted[key]
            
            if partial_update:
                self.memory.update_partial_booking(session_id, **partial_update)
                
        except Exception as e:
            # Silent fail - context extraction is optional
            pass
    
    def _handle_user_request(self, intent: str, request: str, session_id: str) -> Dict[str, Any]:
        """Handle user request based on intent"""
        
        if intent == "greeting":
            return self._handle_greeting(session_id)
        
        elif intent == "book":
            return self._handle_booking(request, session_id)
        
        elif intent == "provide_info":
            # Check if we're in the middle of a booking process
            last_intent = self.memory.get_last_intent(session_id)
            if last_intent == "book":
                return self._handle_booking(request, session_id)
            elif last_intent == "reschedule":
                return self._handle_reschedule(request, session_id)
            elif last_intent == "cancel":
                return self._handle_cancellation(request, session_id)
            else:
                return self._handle_info_provision(request, session_id)
        
        elif intent == "query":
            return self._handle_query(request, session_id)
        
        elif intent == "reschedule":
            return self._handle_reschedule(request, session_id)
        
        elif intent == "cancel":
            return self._handle_cancellation(request, session_id)
        
        
        else:
            return self._handle_unclear(request, session_id)
    
    def _handle_greeting(self, session_id: str) -> Dict[str, Any]:
        """Handle greeting messages"""
        user_context = self.memory.get_user_context(session_id)
        
        if user_context.get("patient_id"):
            # Get patient name from ID for greeting
            patient = self.worker_agents["scheduling"].data_store.get_patient_by_id(user_context["patient_id"])
            patient_name = patient['name'] if patient else "valued patient"
            message = f"Hello {patient_name}! How can I help you with your appointment today?"
        else:
            message = "Hello! I'm your appointment scheduling assistant. I can help you book appointments, check availability, reschedule, or cancel appointments. What would you like to do?"
        
        return {
            "success": True,
            "message": message,
            "intent": "greeting",
            "session_id": session_id
        }
    
    def _handle_booking(self, request: str, session_id: str) -> Dict[str, Any]:
        """Handle appointment booking with the scheduling worker agent"""
        
        partial_booking = self.memory.get_partial_booking(session_id)
        user_context = self.memory.get_user_context(session_id)
        
        # Check what information we have
        required_fields = ["patient_id", "doctor_name", "date", "time"]
        missing_fields = []
        
        current_info = {**user_context, **partial_booking}
        
        for field in required_fields:
            if not current_info.get(field):
                missing_fields.append(field)
        
        # If we have all info, try to book
        if not missing_fields:
            # Call worker agent to perform booking
            booking_result = self.worker_agents["scheduling"].execute_booking(current_info)
            
            if booking_result["success"]:
                # Clear partial booking on success
                self.memory.clear_partial_booking(session_id)
                
                message = f"Perfect! I've successfully booked your appointment. {booking_result['message']}"
                
                return {
                    "success": True,
                    "message": message,
                    "intent": "book",
                    "booking_result": booking_result,
                    "session_id": session_id
                }
            else:
                message = f"I wasn't able to complete your booking. {booking_result['message']} Would you like to try a different time or date?"
                
                return {
                    "success": False,
                    "message": message,
                    "intent": "book", 
                    "session_id": session_id
                }
        else:
            # Ask for missing information
            return self._ask_for_missing_info(missing_fields, current_info, session_id)
    
    def _handle_query(self, request: str, session_id: str) -> Dict[str, Any]:
        """Handle availability queries with dynamic, conversational responses"""
        
        # Extract query parameters
        partial_booking = self.memory.get_partial_booking(session_id)
        user_context = self.memory.get_user_context(session_id)
        recent_messages = self.memory.get_recent_messages(session_id, 3)
        
        query_params = {
            "doctor_name": partial_booking.get("doctor_name"),
            "specialty": partial_booking.get("specialty"),
            "date_preference": partial_booking.get("date")
        }
        
        # Call worker agent to get availability
        query_result = self.worker_agents["query"].get_availability(query_params)
        
        # Generate dynamic response based on query result
        conversation_context = ""
        if recent_messages:
            conversation_context = "Recent conversation:\n"
            for msg in recent_messages[-2:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_context += f"{role}: {msg['content']}\n"
        
        patient_id = user_context.get('patient_id', '')
        # Get patient name for display
        patient_name = ''
        if patient_id:
            patient = self.worker_agents["scheduling"].data_store.get_patient_by_id(patient_id)
            patient_name = patient['name'] if patient else 'Patient'
        
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful medical appointment scheduling assistant. Generate a response about appointment availability.
                
                Patient name: {patient_name}
                Query result: {query_result['message']}
                
                {conversation_context}
                
                User's request: "{request}"
                
                Generate a conversational response that:
                - Addresses their availability question naturally
                - Presents the information in a helpful way
                - Sounds friendly and professional, not robotic
                - Offers to help book an appointment if appropriate
                - Uses the patient's name naturally if you know it
                
                Keep it conversational and helpful (2-3 sentences max)."""
            },
            {
                "role": "user",
                "content": request
            }
        ]
        
        try:
            message = self.call_llm(messages, temperature=0.7)
        except:
            # Fallback to worker agent message
            message = query_result["message"]
        
        return {
            "success": True,
            "message": message,
            "intent": "query",
            "availability_data": query_result,
            "session_id": session_id
        }
    
    def _handle_reschedule(self, request: str, session_id: str) -> Dict[str, Any]:
        """Handle rescheduling with dynamic, empathetic responses"""
        
        partial_booking = self.memory.get_partial_booking(session_id)
        user_context = self.memory.get_user_context(session_id)
        recent_messages = self.memory.get_recent_messages(session_id, 3)
        
        reschedule_info = {**user_context, **partial_booking}
        
        # Call worker agent to reschedule
        reschedule_result = self.worker_agents["management"].reschedule_appointment(reschedule_info)
        
        # Generate dynamic response based on reschedule result
        conversation_context = ""
        if recent_messages:
            conversation_context = "Recent conversation:\n"
            for msg in recent_messages[-2:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_context += f"{role}: {msg['content']}\n"
        
        patient_id = user_context.get('patient_id', '')
        # Get patient name for display
        patient_name = ''
        if patient_id:
            patient = self.worker_agents["scheduling"].data_store.get_patient_by_id(patient_id)
            patient_name = patient['name'] if patient else 'Patient'
        
        messages = [
            {
                "role": "system",
                "content": f"""You are a compassionate medical appointment scheduling assistant. Generate a response about appointment rescheduling.
                
                Patient name: {patient_name}
                Reschedule was successful: {reschedule_result['success']}
                Reschedule result: {reschedule_result['message']}
                
                {conversation_context}
                
                User's request: "{request}"
                
                Generate a response that:
                - Acknowledges their rescheduling need with empathy
                - Clearly communicates the result (success or failure)
                - Sounds understanding and helpful, not robotic
                - Offers additional assistance if needed
                - Uses natural, conversational language
                
                Keep it professional but warm (2-3 sentences max)."""
            },
            {
                "role": "user",
                "content": request
            }
        ]
        
        try:
            message = self.call_llm(messages, temperature=0.7)
        except:
            # Fallback message based on result
            if reschedule_result["success"]:
                message = f"I've successfully rescheduled your appointment. {reschedule_result['message']}"
            else:
                message = f"I wasn't able to reschedule your appointment. {reschedule_result['message']}"
        
        if reschedule_result["success"]:
            self.memory.clear_partial_booking(session_id)
        
        return {
            "success": reschedule_result["success"],
            "message": message,
            "intent": "reschedule",
            "reschedule_result": reschedule_result,
            "session_id": session_id
        }
    
    def _handle_cancellation(self, request: str, session_id: str) -> Dict[str, Any]:
        """Handle cancellation with empathetic, understanding responses"""
        
        user_context = self.memory.get_user_context(session_id)
        partial_booking = self.memory.get_partial_booking(session_id)
        recent_messages = self.memory.get_recent_messages(session_id, 3)
        
        cancel_info = {**user_context, **partial_booking}
        
        # Call worker agent to cancel
        cancel_result = self.worker_agents["management"].cancel_appointment(cancel_info)
        
        # Generate dynamic, empathetic response
        conversation_context = ""
        if recent_messages:
            conversation_context = "Recent conversation:\n"
            for msg in recent_messages[-2:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_context += f"{role}: {msg['content']}\n"
        
        patient_id = user_context.get('patient_id', '')
        # Get patient name for display
        patient_name = ''
        if patient_id:
            patient = self.worker_agents["scheduling"].data_store.get_patient_by_id(patient_id)
            patient_name = patient['name'] if patient else 'Patient'
        
        messages = [
            {
                "role": "system",
                "content": f"""You are a understanding medical appointment scheduling assistant. Generate a response about appointment cancellation.
                
                Patient name: {patient_name}
                Cancellation was successful: {cancel_result['success']}
                Cancellation result: {cancel_result['message']}
                
                {conversation_context}
                
                User's request: "{request}"
                
                Generate a response that:
                - Shows understanding for their need to cancel
                - Clearly confirms the cancellation status
                - Sounds empathetic and professional, not robotic
                - Offers to help with future appointments naturally
                - Uses warm, caring language appropriate for healthcare
                
                Keep it brief but compassionate (2-3 sentences max)."""
            },
            {
                "role": "user",
                "content": request
            }
        ]
        
        try:
            message = self.call_llm(messages, temperature=0.7)
        except:
            # Fallback message based on result
            if cancel_result["success"]:
                message = f"I understand, and I've cancelled your appointment. {cancel_result['message']}"
            else:
                message = f"I wasn't able to cancel your appointment. {cancel_result['message']}"
        
        return {
            "success": cancel_result["success"],
            "message": message,
            "intent": "cancel",
            "cancel_result": cancel_result,
            "session_id": session_id
        }
    
    def _handle_info_provision(self, request: str, session_id: str) -> Dict[str, Any]:
        """Handle when user is providing requested information"""
        
        last_intent = self.memory.get_last_intent(session_id)
        
        if last_intent == "book":
            return self._handle_booking(request, session_id)
        elif last_intent == "reschedule": 
            return self._handle_reschedule(request, session_id)
        elif last_intent == "cancel":
            return self._handle_cancellation(request, session_id)
        else:
            return {
                "success": True,
                "message": "Thank you for the information! How can I help you with your appointment?",
                "intent": "provide_info",
                "session_id": session_id
            }
    
    def _handle_unclear(self, request: str, session_id: str) -> Dict[str, Any]:
        """Handle unclear requests"""
        
        user_context = self.memory.get_user_context(session_id)
        
        if user_context.get("patient_id"):
            # Get patient name from ID
            patient = self.worker_agents["scheduling"].data_store.get_patient_by_id(user_context["patient_id"])
            patient_name = patient['name'] if patient else "valued patient"
            message = f"I want to make sure I help you correctly, {patient_name}. Are you looking to book a new appointment, reschedule an existing one, cancel an appointment, or check available times?"
        else:
            message = "I'd be happy to help you with your appointment. Are you looking to book a new appointment, reschedule an existing one, cancel an appointment, or check available times?"
        
        return {
            "success": True,
            "message": message,
            "intent": "unclear",
            "session_id": session_id
        }
    
    def _ask_for_missing_info(self, missing_fields: list, current_info: dict, session_id: str) -> Dict[str, Any]:
        """Ask for missing information in a natural way"""
        
        field_questions = {
            "patient_id": "I need your patient ID to schedule your appointment. Your patient ID is a 7-character code that starts with 'P' followed by letters and numbers (like PVY3830). What's your patient ID?",
            "doctor_name": "Which doctor would you like to see? We have Dr. Adams (General Medicine), Dr. Baker (Pediatrics), Dr. Clark (Dermatology), and Dr. Davis (Endocrinology).",
            "date": "What date works for you? You can say something like 'tomorrow', 'next Monday', or a specific date.",
            "time": "What time would you prefer? You can say 'morning', 'afternoon', or a specific time like '2 PM'."
        }
        
        if current_info:
            summary = "Let me confirm what I have so far: "
            confirmed_items = []
            if current_info.get("patient_id"):
                # Get patient name from ID for display
                patient = self.worker_agents["scheduling"].data_store.get_patient_by_id(current_info["patient_id"])
                patient_name = patient['name'] if patient else current_info["patient_id"]
                confirmed_items.append(f"Patient: {patient_name}")
            if current_info.get("doctor_name"):
                confirmed_items.append(f"Doctor: {current_info['doctor_name']}")
            if current_info.get("date"):
                confirmed_items.append(f"Date: {current_info['date']}")
            if current_info.get("time"):
                confirmed_items.append(f"Time: {current_info['time']}")
            
            if confirmed_items:
                summary += ", ".join(confirmed_items) + ". "
            else:
                summary = ""
        else:
            summary = ""
        
        # Ask for the first missing field
        first_missing = missing_fields[0]
        question = field_questions[first_missing]
        
        message = summary + question
        
        return {
            "success": False,
            "message": message,
            "intent": "book",
            "missing_fields": missing_fields,
            "current_info": current_info,
            "session_id": session_id
        }