"""
Test script for the improved conversation system
"""
import requests
import json

def test_conversation():
    """Test the improved conversational flow"""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Improved Conversation System")
    print("=" * 50)
    
    # Test scenarios for natural conversation
    test_cases = [
        {
            "name": "Natural Greeting",
            "messages": ["Hello there!"]
        },
        {
            "name": "Unclear Request", 
            "messages": ["I need some help"]
        },
        {
            "name": "Booking Flow",
            "messages": [
                "I want to book an appointment",
                "My name is Sarah Johnson", 
                "I need to see Dr. Adams",
                "How about tomorrow afternoon?"
            ]
        },
        {
            "name": "Query Availability",
            "messages": ["What times are available with Dr. Clark next week?"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print("-" * 30)
        
        session_id = f"test_{test_case['name'].lower().replace(' ', '_')}"
        
        for i, message in enumerate(test_case['messages']):
            print(f"\nUser: {message}")
            
            try:
                response = requests.post(
                    f"{base_url}/api/chat",
                    json={
                        "message": message,
                        "session_id": session_id
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Assistant: {result.get('message', 'No response')}")
                    
                    # Show intent detection
                    intent = result.get('intent', 'unknown')
                    print(f"   Intent: {intent}")
                    
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Conversation testing complete!")

if __name__ == "__main__":
    test_conversation()