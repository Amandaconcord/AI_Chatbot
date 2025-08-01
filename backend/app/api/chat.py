from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.core.conversation_manager import ConversationManager, ConversationStep
import uuid

router = APIRouter()
conversation_manager = ConversationManager()

@router.post("/chat/start")
async def start_conversation():
    """Start a new conversation"""
    session_id = str(uuid.uuid4())
    
    try:
        initial_response = await conversation_manager.start_conversation(session_id=session_id)
        
        return {
            "session_id": session_id,
            "response": initial_response
        }
    except Exception as e:
        print(f"Error in start_conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/message")
async def send_message(message: ChatRequest):
    """Send a message and get response"""
    try:
        response = await conversation_manager.process_message(
            session_id=message.session_id,
            user_message=message.message
        )
        
        return {
            "response": response.response,
            "current_step": response.current_step.value,
            "slots_needed": response.slots_needed or [],
            "verification_status": response.verification_status,
            "escalate": response.escalate or False
        }
        
    except Exception as e:
        print(f"Error in send_message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get current session status"""
    try: 
        if session_id in conversation_manager.active_conversations:
            state = conversation_manager.active_conversations[session_id]
            return {
                "session_id": session_id,
                "current_step": state.current_step.value,
                "customer_name": state.customer_name,
                "slots_filled": list(state.slots_filled.keys()),
                "verification_attempts": state.verification_attempts,
                "has_time_to_continue": state.has_time_to_continue,
                "dob_verified": state.dob_verified,
                "ssn_verified": state.ssn_verified,
                "email_verified": state.email_verified,
                "sms_code_sent": state.sms_code_sent,
                "sms_code_verified": state.sms_code_verified
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        print(f"Error in get_session_status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/session/{session_id}")
async def end_conversation(session_id: str):
    """End a conversation and clean up session"""
    try:
        if session_id in conversation_manager.active_conversations:
            del conversation_manager.active_conversations[session_id]
            return {"message": "Session ended successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        print(f"Error in end_conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Add this to your chat.py router
@router.post("/chat/debug/skip-to-vbt")
async def skip_to_vbt(session_id: str):
    """Debug endpoint - skip directly to VBT for testing"""
    try:
        if session_id not in conversation_manager.active_conversations:
            # Create a mock conversation state
            from app.models.schemas import ConversationState, ConversationStep
            state = ConversationState(
                session_id=session_id,
                current_step=ConversationStep.VBT_CODE_CHECK
            )
            # Pre-fill required data for testing
            state.customer_name = "John Smith"
            state.dob_verified = True
            state.ssn_verified = True
            state.email_verified = True
            state.home_number_confirmed = True
            state.sms_code_sent = True
            
            conversation_manager.active_conversations[session_id] = state
        else:
            # Update existing conversation
            state = conversation_manager.active_conversations[session_id]
            state.current_step = ConversationStep.VBT_CODE_CHECK
            state.customer_name = state.customer_name or "John Smith"
            state.dob_verified = True
            state.ssn_verified = True
            state.email_verified = True
            state.home_number_confirmed = True
            state.sms_code_sent = True
        
        # Get mobile number and send VBT message
        mobile_number = await conversation_manager.verification_engine.get_customer_mobile_number(state.customer_name)
        
        mobile_confirmation = f"I see your mobile number is {mobile_number}. "
        vbt_initiate_response = conversation_manager.script_manager.get_script_response("vbt_initiate")
        vbt_code_check_response = conversation_manager.script_manager.get_script_response("vbt_code_check")
        
        full_response = f"{mobile_confirmation}{vbt_initiate_response}\n\n{vbt_code_check_response}"
        
        return {
            "session_id": session_id,
            "response": full_response,
            "current_step": state.current_step.value,
            "message": "Skipped to VBT for testing"
        }
        
    except Exception as e:
        print(f"Error in skip_to_vbt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Alternative: Add keyword shortcuts in your main flow
# In conversation_manager.py, add this to the beginning of process_message:



