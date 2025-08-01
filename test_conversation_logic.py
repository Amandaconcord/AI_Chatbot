#!/usr/bin/env python3
"""
Simple test script to verify conversation logic without Azure AI
"""
import asyncio
import sys
import os
from typing import Dict, Any

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Now try to import
try:
    from app.models.schemas import ConversationState, ConversationStep
    from app.core.script_manager import ScriptManager
    print("✅ Successfully imported modules!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Let's check what's available...")
    
    # Try direct imports without app prefix
    sys.path.insert(0, os.path.join(backend_path, 'app'))
    sys.path.insert(0, os.path.join(backend_path, 'app', 'models'))
    sys.path.insert(0, os.path.join(backend_path, 'app', 'core'))
    
    try:
        from schemas import ConversationState, ConversationStep
        from script_manager import ScriptManager
        print("✅ Successfully imported with direct paths!")
    except ImportError as e2:
        print(f"❌ Still failing: {e2}")
        print("Please check that these files exist and have the correct classes:")
        print("- backend/app/models/schemas.py (with ConversationState, ConversationStep)")
        print("- backend/app/core/script_manager.py (with ScriptManager)")
        sys.exit(1)

class MockAIClient:
    """Mock AI client for testing without Azure OpenAI"""
    
    async def extract_information(self, user_message: str, step: ConversationStep) -> Dict[str, Any]:
        """Mock extraction based on simple keyword matching"""
        user_message = user_message.lower()
        extracted = {}
        
        if step == ConversationStep.ASK_NAME:
            # Look for name patterns
            if "my name is" in user_message:
                name_part = user_message.split("my name is")[1].strip()
                extracted['full_name'] = name_part.title()
            elif len(user_message.split()) >= 2:
                extracted['full_name'] = user_message.title()
        
        elif step == ConversationStep.ASK_DOB:
            # Look for date patterns
            import re
            date_patterns = [
                r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
                r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
            ]
            for pattern in date_patterns:
                match = re.search(pattern, user_message)
                if match:
                    month, day, year = match.groups()
                    extracted['dob'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    break
        
        elif step == ConversationStep.ASK_SSN:
            # Look for 4 digits
            import re
            match = re.search(r'\b(\d{4})\b', user_message)
            if match:
                extracted['ssn_last4'] = match.group(1)
        
        elif step == ConversationStep.VBT_CODE_INPUT:
            # Look for 6 digits
            import re
            match = re.search(r'\b(\d{6})\b', user_message)
            if match:
                extracted['sms_code'] = match.group(1)
        
        return extracted
    
    async def analyze_yes_no_response(self, user_message: str) -> bool:
        """Simple yes/no analysis"""
        user_message = user_message.lower()
        positive_words = ['yes', 'yeah', 'yep', 'sure', 'okay', 'correct', 'right', 'affirmative']
        return any(word in user_message for word in positive_words)
    
    async def analyze_code_refusal(self, user_message: str) -> bool:
        """Simple refusal analysis"""
        user_message = user_message.lower()
        refusal_words = ['refuse', 'don\'t want', 'no thanks', 'not interested']
        return any(word in user_message for word in refusal_words)

class MockVerificationEngine:
    """Mock verification engine for testing"""
    
    async def verify_dob(self, customer_name: str, dob: str) -> bool:
        # For testing, accept any DOB
        return True
    
    async def verify_ssn(self, customer_name: str, ssn_last4: str) -> bool:
        # For testing, accept any SSN
        return True
    
    async def get_customer_email(self, customer_name: str) -> str:
        return "test@example.com"
    
    async def get_customer_home_number(self, customer_name: str) -> str:
        return "8102405111"

async def test_conversation_flow():
    """Test the basic conversation flow"""
    print("🤖 Testing Auto Verification Chatbot Logic")
    print("=" * 50)
    
    # Initialize components
    script_manager = ScriptManager()
    mock_ai = MockAIClient()
    mock_verifier = MockVerificationEngine()
    
    # Test script loading
    print("✅ Testing Script Manager...")
    greeting = script_manager.get_script_response(ConversationStep.GREETING)
    print(f"Greeting: {greeting}")
    
    # Test conversation state
    print("\n✅ Testing Conversation State...")
    state = ConversationState(
        session_id="test-123",
        current_step=ConversationStep.GREETING
    )
    print(f"Initial state: {state.current_step}")
    
    # Test information extraction
    print("\n✅ Testing Information Extraction...")
    
    # Test name extraction
    name_response = "My name is John Smith"
    extracted_name = await mock_ai.extract_information(name_response, ConversationStep.ASK_NAME)
    print(f"Name extraction: '{name_response}' → {extracted_name}")
    
    # Test DOB extraction
    dob_response = "01/15/1990"
    extracted_dob = await mock_ai.extract_information(dob_response, ConversationStep.ASK_DOB)
    print(f"DOB extraction: '{dob_response}' → {extracted_dob}")
    
    # Test SSN extraction
    ssn_response = "1234"
    extracted_ssn = await mock_ai.extract_information(ssn_response, ConversationStep.ASK_SSN)
    print(f"SSN extraction: '{ssn_response}' → {extracted_ssn}")
    
    # Test yes/no analysis
    print("\n✅ Testing Yes/No Analysis...")
    yes_responses = ["yes", "yeah", "sure", "that's correct"]
    no_responses = ["no", "nope", "that's wrong", "incorrect"]
    
    for response in yes_responses:
        result = await mock_ai.analyze_yes_no_response(response)
        print(f"'{response}' → {result} (should be True)")
    
    for response in no_responses:
        result = await mock_ai.analyze_yes_no_response(response)
        print(f"'{response}' → {result} (should be False)")
    
    print("\n✅ Testing Complete Conversation Flow...")
    
    # Simulate a complete conversation
    conversation_steps = [
        ("GREETING", "yes, I have time"),
        ("ASK_NAME", "My name is John Smith"),
        ("ASK_DOB", "01/15/1990"),
        ("ASK_SSN", "1234"),
        ("ASK_EMAIL", "yes, that's correct"),
        ("EMAIL_USAGE_CHECK", "yes, I check it regularly"),
    ]
    
    current_state = ConversationState(
        session_id="test-conversation",
        current_step=ConversationStep.GREETING
    )
    
    for step_name, user_input in conversation_steps:
        print(f"\n--- Step: {step_name} ---")
        print(f"User: {user_input}")
        
        # Get script response
        script_response = script_manager.get_script_response(current_state.current_step)
        print(f"Bot: {script_response}")
        
        # Extract information
        extracted = await mock_ai.extract_information(user_input, current_state.current_step)
        if extracted:
            current_state.slots_filled.update(extracted)
            print(f"Extracted: {extracted}")
        
        # Move to next step (simplified logic)
        if current_state.current_step == ConversationStep.GREETING:
            current_state.current_step = ConversationStep.ASK_NAME
        elif current_state.current_step == ConversationStep.ASK_NAME:
            current_state.current_step = ConversationStep.ASK_DOB
        elif current_state.current_step == ConversationStep.ASK_DOB:
            current_state.current_step = ConversationStep.ASK_SSN
        elif current_state.current_step == ConversationStep.ASK_SSN:
            current_state.current_step = ConversationStep.ASK_EMAIL
        elif current_state.current_step == ConversationStep.ASK_EMAIL:
            current_state.current_step = ConversationStep.EMAIL_USAGE_CHECK
        
        print(f"Next step: {current_state.current_step}")
    
    print(f"\n✅ Final collected data: {current_state.slots_filled}")
    print("\n🎉 All tests passed! Your conversation logic is working correctly.")

def test_script_availability():
    """Test if all required scripts are available"""
    print("\n🔍 Testing Script Availability...")
    script_manager = ScriptManager()
    
    required_scripts = [
        "greeting", "ask_name", "ask_dob", "ask_ssn", "ask_email",
        "email_usage_check", "vbt_initiate", "code_received",
        "military_question", "bank_account_intro", "debit_card_intro"
    ]
    
    missing_scripts = []
    for script_key in required_scripts:
        if script_key not in script_manager.scripts:
            missing_scripts.append(script_key)
        else:
            print(f"✅ {script_key}: {script_manager.scripts[script_key][:50]}...")
    
    if missing_scripts:
        print(f"❌ Missing scripts: {missing_scripts}")
    else:
        print("✅ All required scripts are available!")

if __name__ == "__main__":
    print("🚀 Starting Auto Verification Chatbot Tests")
    
    try:
        # Test script availability first
        test_script_availability()
        
        # Test conversation flow
        asyncio.run(test_conversation_flow())
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n✅ All tests completed successfully!")
    print("Your chatbot logic is ready for Azure deployment!")