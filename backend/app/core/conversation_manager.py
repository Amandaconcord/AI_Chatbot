import asyncio
from typing import Optional, Dict, Any
from app.models.schemas import *
from app.core.script_manager import ScriptManager
from app.core.verification_engine import VerificationEngine
from app.core.azure_ai_client import AzureAIClient

class ConversationManager:
    def __init__(self):
        self.script_manager = ScriptManager()
        self.verification_engine = VerificationEngine()
        self.ai_client = AzureAIClient()
        self.active_conversations: Dict[str, ConversationState] = {}
    
    async def start_conversation(self, session_id: str) -> str:
        """Initialize a new conversation"""
        state = ConversationState(
            session_id=session_id,
            current_step=ConversationStep.GREETING
        )
        
        self.active_conversations[session_id] = state
        
        return self.script_manager.get_script_response(ConversationStep.GREETING)
    
    async def process_message(self, session_id: str, user_message: str) -> ChatResponse:
        """Process user message and return appropriate response"""
    
        # Debug shortcuts for testing
        if user_message.lower().strip() == "skip to vbt":
            return await self._debug_skip_to_vbt(session_id)
        elif user_message.lower().strip() == "skip to bank":
            return await self._debug_skip_to_bank(session_id)
        
        # Continue with normal processing...
        if session_id not in self.active_conversations:
            return ChatResponse(
                response="Session not found. Please start a new conversation.",
                current_step=ConversationStep.GREETING
            )
        
        state = self.active_conversations[session_id]
        
        # Extract information using Azure AI
        extracted_info = await self.ai_client.extract_information(
            user_message, state.current_step
        )
        
        # Update conversation state with extracted information
        self._update_state_with_extracted_info(state, extracted_info)
        
        # Determine next step and response
        next_response = await self._determine_next_response(state, user_message)
        
        return next_response
    
    async def _debug_skip_to_vbt(self, session_id: str) -> ChatResponse:
        """Debug method to skip directly to VBT"""
        if session_id not in self.active_conversations:
            return ChatResponse(response="Session not found", current_step=ConversationStep.GREETING)
        
        state = self.active_conversations[session_id]
        state.current_step = ConversationStep.VBT_CODE_CHECK
        state.customer_name = state.customer_name or "John Smith"
        state.dob_verified = True
        state.ssn_verified = True
        state.email_verified = True
        state.sms_code_sent = True
        
        mobile_number = await self.verification_engine.get_customer_mobile_number(state.customer_name)
        
        mobile_confirmation = f"I see your mobile number is {mobile_number}. "
        vbt_initiate_response = self.script_manager.get_script_response("vbt_initiate")
        vbt_code_check_response = self.script_manager.get_script_response("vbt_code_check")
        
        full_response = f"{mobile_confirmation}{vbt_initiate_response}\n\n{vbt_code_check_response}"
        
        return ChatResponse(
            response=full_response,
            current_step=state.current_step
        )

    def _update_state_with_extracted_info(self, state: ConversationState, extracted_info: Dict[str, Any]):
        """Update conversation state with extracted information"""
        for key, value in extracted_info.items():
            if value is not None:
                state.slots_filled[key] = value
        
        # Update customer name if extracted
        if 'full_name' in extracted_info and extracted_info['full_name']:
            state.customer_name = extracted_info['full_name']
    
    async def _determine_next_response(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Determine the next response based on current state and user input"""
        
        if state.current_step == ConversationStep.GREETING:
            return await self._handle_greeting(state, user_message)
        
        elif state.current_step == ConversationStep.ASK_NAME:
            return await self._handle_name_response(state, user_message)
        
        elif state.current_step == ConversationStep.ASK_DOB:
            return await self._handle_dob_response(state, user_message)
        
        elif state.current_step == ConversationStep.ASK_SSN:
            return await self._handle_ssn_response(state, user_message)
        
        elif state.current_step == ConversationStep.ASK_EMAIL:
            return await self._handle_email_confirmation(state, user_message)
        
        elif state.current_step == ConversationStep.EMAIL_USAGE_CHECK:
            return await self._handle_email_usage_response(state, user_message)
        
        elif state.current_step == ConversationStep.CONTACT_INFO_CHECK:
            return await self._handle_contact_info_check(state, user_message)
        
        elif state.current_step == ConversationStep.VBT_INITIATE:
            return await self._handle_vbt_initiate(state, user_message)
        
        elif state.current_step == ConversationStep.VBT_CODE_CHECK:
            return await self._handle_vbt_code_check(state, user_message)
        
        elif state.current_step == ConversationStep.VBT_CODE_INPUT:
            return await self._handle_vbt_code_input(state, user_message)
        
        elif state.current_step == ConversationStep.VBT_WAIT_RETRY:
            return await self._handle_vbt_wait_retry(state, user_message)
        
        elif state.current_step == ConversationStep.VBT_REFUSE_CODE:
            return await self._handle_vbt_refuse_code(state, user_message)
        
        elif state.current_step == ConversationStep.QUALIFYING_QUESTIONS:
            return await self._handle_qualifying_questions(state, user_message)
        
        elif state.current_step == ConversationStep.BANK_ACCOUNT_INFO:
            return await self._handle_bank_account_info(state, user_message)
        
        elif state.current_step == ConversationStep.BANK_ACCOUNT_CONFIRM:
            return await self._handle_bank_account_confirm(state, user_message)
        
        elif state.current_step == ConversationStep.ACCOUNT_TYPE_CHECK:
            return await self._handle_account_type_check(state, user_message)
        
        elif state.current_step == ConversationStep.PAYCHECK_ACCOUNT_CHECK:
            return await self._handle_paycheck_account_check(state, user_message)
        
        elif state.current_step == ConversationStep.PAYCHECK_TYPE_CHECK:
            return await self._handle_paycheck_type_check(state, user_message)
        
        elif state.current_step == ConversationStep.DEBIT_CARD_COLLECTION:
            return await self._handle_debit_card_collection(state, user_message)
        
        elif state.current_step == ConversationStep.DEBIT_CARD_CONFIRM:
            return await self._handle_debit_card_confirm(state, user_message)
        
        elif state.current_step == ConversationStep.DEBIT_CARD_REFUSAL:
            return await self._handle_debit_card_refusal(state, user_message)
        
        return ChatResponse(
            response="I'm not sure how to help with that. Let me connect you with a specialist.",
            current_step=ConversationStep.ESCALATION,
            escalate=True
        )
    
    async def _handle_greeting(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle greeting phase - check if customer has time"""
        has_time = await self.ai_client.analyze_yes_no_response(user_message)
        
        if has_time:
            state.has_time_to_continue = True
            state.current_step = ConversationStep.ASK_NAME
            
            response = self.script_manager.get_script_response(state.current_step)
            
            return ChatResponse(
                response=response,
                current_step=state.current_step,
                slots_needed=["full_name"]
            )
        else:
            state.has_time_to_continue = False
            response = self.script_manager.get_script_response(ConversationStep.GREETING, {"key": "no_time_callback"})
            
            return ChatResponse(
                response="That's okay! We can always come back to this later. Just let me know when you're ready.",
                current_step=state.current_step
            )
    
    async def _handle_name_response(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle customer name input"""
        extracted_info = await self.ai_client.extract_information(user_message, state.current_step)
        
        if 'full_name' in extracted_info:
            state.customer_name = extracted_info['full_name']
            state.slots_filled['full_name'] = extracted_info['full_name']
            
            # Move to DOB verification
            state.current_step = ConversationStep.ASK_DOB
            response = self.script_manager.get_script_response(state.current_step)
            
            return ChatResponse(
                response=response,
                current_step=state.current_step,
                slots_needed=["dob"]
            )
        else:
            return ChatResponse(
                response="I didn't catch your full name clearly. Could you please tell me your first and last name?",
                current_step=state.current_step,
                slots_needed=["full_name"]
            )
    
    async def _handle_dob_response(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle date of birth response"""
        extracted_info = await self.ai_client.extract_information(user_message, state.current_step)
        
        if 'dob' in extracted_info:
            state.slots_filled['dob'] = extracted_info['dob']
            
            # Verify DOB against database
            dob_valid = await self.verification_engine.verify_dob(
                state.customer_name, extracted_info['dob']
            )
            
            if dob_valid:
                state.dob_verified = True
                state.current_step = ConversationStep.ASK_SSN
                
                response = self.script_manager.get_script_response("ask_ssn")
                
                return ChatResponse(
                    response=response,
                    current_step=state.current_step,
                    slots_needed=["ssn_last4"]
                )
            else:
                state.verification_attempts += 1
                if state.verification_attempts >= state.max_attempts:
                    return await self._handle_max_attempts_reached(state)
                
                return ChatResponse(
                    response="I'm sorry, but the date of birth doesn't match our records. Could you please try again?",
                    current_step=state.current_step
                )
        else:
            # Better error message with examples
            return ChatResponse(
                response="I didn't understand the date format. You can provide your date of birth in any of these formats: July 22, 2000 or 07/22/2000 or 22 July 2000.",
                current_step=state.current_step,
                slots_needed=["dob"]
            )
    
    async def _handle_ssn_response(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle SSN last 4 digits response"""
        extracted_info = await self.ai_client.extract_information(user_message, state.current_step)
        
        if 'ssn_last4' in extracted_info:
            state.slots_filled['ssn_last4'] = extracted_info['ssn_last4']
            
            # Verify SSN against database
            ssn_valid = await self.verification_engine.verify_ssn(
                state.customer_name, extracted_info['ssn_last4']
            )
            
            if ssn_valid:
                state.ssn_verified = True
                state.current_step = ConversationStep.ASK_EMAIL
                
                # Get customer's email from database to confirm
                customer_email = await self.verification_engine.get_customer_email(state.customer_name)
                
                context = {"email": customer_email}
                response = self.script_manager.get_script_response(state.current_step, context)
                
                return ChatResponse(
                    response=response,
                    current_step=state.current_step,
                    slots_needed=["email_confirmation"]
                )
            else:
                state.verification_attempts += 1
                if state.verification_attempts >= state.max_attempts:
                    return await self._handle_max_attempts_reached(state)
                
                return ChatResponse(
                    response="The last 4 digits of the SSN don't match our records. Please try again with just the 4 digits (for example: 1234).",
                    current_step=state.current_step
                )
        else:
            return ChatResponse(
                response="Please provide only the last 4 digits of your Social Security Number (for example: 1234).",
                current_step=state.current_step,
                slots_needed=["ssn_last4"]
            )
    
    async def _handle_email_confirmation(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle email address confirmation"""
        
        # First, check if user provided a new email address directly
        extracted_info = await self.ai_client.extract_information(user_message, ConversationStep.ASK_EMAIL)
        
        if 'email' in extracted_info:
            # User provided a new email address
            state.slots_filled['email'] = extracted_info['email']
            state.email_verified = True
            state.current_step = ConversationStep.EMAIL_USAGE_CHECK
            
            response = self.script_manager.get_script_response(ConversationStep.EMAIL_USAGE_CHECK)
            
            return ChatResponse(
                response=response,
                current_step=state.current_step
            )
        
        # If no email provided, check if they confirmed the existing email (yes/no response)
        confirmation = await self.ai_client.analyze_yes_no_response(user_message)
        
        if confirmation:
            state.email_verified = True
            state.current_step = ConversationStep.EMAIL_USAGE_CHECK
            
            response = self.script_manager.get_script_response(ConversationStep.EMAIL_USAGE_CHECK)
            
            return ChatResponse(
                response=response,
                current_step=state.current_step
            )
        else:
            # User said email is wrong, ask for correct email and stay in same step
            return ChatResponse(
                response="Could you please provide your correct email address?",
                current_step=state.current_step,  # Stay in ASK_EMAIL step
                slots_needed=["email"]
            )
    
    async def _handle_email_usage_response(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle email usage check response"""
        
        # First, check if user provided a new email address
        extracted_info = await self.ai_client.extract_information(user_message, ConversationStep.ASK_EMAIL)
        
        if 'email' in extracted_info:
            # User provided a new email address
            state.slots_filled['email'] = extracted_info['email']
            state.email_verified = True
            state.email_usage_confirmed = True
            
            # Move to contact info check
            if state.dob_verified and state.ssn_verified and state.email_verified:
                response = self.script_manager.get_script_response(ConversationStep.GREETING) + "\n\n"
                state.current_step = ConversationStep.CONTACT_INFO_CHECK
                
                # Get home number from database
                home_number = await self.verification_engine.get_customer_home_number(state.customer_name)
                
                if home_number:
                    context = {"home_number": home_number}
                    next_response = f"Your account shows you home number as {home_number}, is that a number we would be able to contact you on?"
                else:
                    next_response = "Unfortunately, we do not have a home number on file, is there another number you would like to add to your account?"
                
                full_response = f"Thank you for updating your email address.\n\n{next_response}"
                
                return ChatResponse(
                    response=full_response,
                    current_step=state.current_step,
                    verification_status="identity_verified"
                )
        
        # If no email provided, check yes/no response
        uses_email_regularly = await self.ai_client.analyze_yes_no_response(user_message)
        
        if uses_email_regularly:
            state.email_usage_confirmed = True
            
            # All identity verification complete, move to contact info check
            if state.dob_verified and state.ssn_verified and state.email_verified:
                response = "Perfect, we can now go ahead with the process which is a quick review of the loan information and verification of your information. Once completed we can send the loan off right to your account on file.\n\n"
                state.current_step = ConversationStep.CONTACT_INFO_CHECK
                
                # Check if customer has home number on file
                home_number = await self.verification_engine.get_customer_home_number(state.customer_name)
                
                if home_number:
                    next_response = f"Your account shows you home number as {home_number}, is that a number we would be able to contact you on?"
                else:
                    next_response = "Unfortunately, we do not have a home number on file, is there another number you would like to add to your account?"
                
                full_response = f"{response}{next_response}"
                
                return ChatResponse(
                    response=full_response,
                    current_step=state.current_step,
                    verification_status="identity_verified"
                )
        else:
            # User doesn't check email regularly, ask for updated email
            if not extracted_info.get('email'):  # Only ask if they haven't provided one yet
                response = "I'd recommend updating your email address to one you check regularly. This helps us keep you informed about your loan status. Could you please provide an updated email address?"
                
                return ChatResponse(
                    response=response,
                    current_step=state.current_step  # Stay in same step to collect new email
                )
    
    async def _handle_contact_info_check(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle home number confirmation and initiate VBT"""
        confirmed = await self.ai_client.analyze_yes_no_response(user_message)
        
        if confirmed:
            state.home_number_confirmed = True
        
        # Move directly to VBT_CODE_CHECK (skip VBT_INITIATE since we're combining messages)
        state.current_step = ConversationStep.VBT_CODE_CHECK
        state.sms_code_sent = True  # Mark as sent since we're simulating sending it
        
        # Get mobile number from database
        mobile_number = await self.verification_engine.get_customer_mobile_number(state.customer_name)
        
        if mobile_number:
            # Build the complete VBT response with all parts
            mobile_confirmation = f"I see your mobile number is {mobile_number}. "
            vbt_initiate_response = self.script_manager.get_script_response("vbt_initiate")
            vbt_code_check_response = self.script_manager.get_script_response("vbt_code_check")
            
            # Combine all three parts
            full_response = f"{mobile_confirmation}{vbt_initiate_response}\n\n{vbt_code_check_response}"
            
            return ChatResponse(
                response=full_response,
                current_step=state.current_step
            )
        else:
            # If no mobile number, ask for it first
            response = "Could you please provide your mobile number for verification?"
            state.current_step = ConversationStep.CONTACT_INFO_CHECK  # Stay here to collect mobile number
            
            return ChatResponse(
                response=response,
                current_step=state.current_step
            )
    
    ## new version 

    async def _handle_vbt_initiate(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle VBT initiation - send SMS code and ask if received"""
        # Here you would integrate with SMS service to send verification code
        # For demo purposes, we'll simulate sending the code
        
        state.sms_code_sent = True
        state.current_step = ConversationStep.VBT_CODE_CHECK
        
        # Get both messages from script manager
        vbt_initiate_response = self.script_manager.get_script_response("vbt_initiate")
        vbt_code_check_response = self.script_manager.get_script_response("vbt_code_check")
        
        # Combine both messages with a line break
        full_response = f"{vbt_initiate_response}\n\n{vbt_code_check_response}"

        return ChatResponse(
            response=full_response,
            current_step=state.current_step
        )

    async def _handle_vbt_code_check(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle checking if customer received SMS code"""
        refuses_code = await self.ai_client.analyze_code_refusal(user_message)
        
        if refuses_code:
            state.sms_code_refused = True
            state.current_step = ConversationStep.QUALIFYING_QUESTIONS
            
            # Get the actual script text
            refusal_response = self.script_manager.get_script_response("code_refusal")
            qualifying_intro = self.script_manager.get_script_response("qualifying_intro")
            military_question = self.script_manager.get_script_response("military_question")
            
            full_response = f"{refusal_response}\n\n{qualifying_intro}\n\n{military_question}"
            
            return ChatResponse(
                response=full_response,
                current_step=state.current_step
            )
        
        # Check if they received the code
        received_code = await self.ai_client.analyze_yes_no_response(user_message)
        
        if received_code:
            state.current_step = ConversationStep.VBT_CODE_INPUT
            response = self.script_manager.get_script_response("code_received")
            
            return ChatResponse(
                response=response,
                current_step=state.current_step,
                slots_needed=["sms_code"]
            )
        else:
            # Customer hasn't received code
            state.sms_retry_count += 1
            state.current_step = ConversationStep.VBT_WAIT_RETRY
            
            response = self.script_manager.get_script_response("code_not_received")
            
            return ChatResponse(
                response=response,
                current_step=state.current_step
            )

    async def _handle_vbt_wait_retry(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle the wait and retry scenario when code not received"""
        # Give them a moment and then continue
        wait_response = self.script_manager.get_script_response("wait_5_seconds")
        
        # Check if they now say they have the code
        received_code = await self.ai_client.analyze_yes_no_response(user_message)
        
        if received_code:
            state.current_step = ConversationStep.VBT_CODE_INPUT
            response = self.script_manager.get_script_response("code_received")
            
            return ChatResponse(
                response=response,
                current_step=state.current_step,
                slots_needed=["sms_code"]
            )
        else:
            # Still no code, continue without it but offer to continue process
            state.current_step = ConversationStep.QUALIFYING_QUESTIONS
            
            continue_response = self.script_manager.get_script_response("still_no_code")
            qualifying_intro = self.script_manager.get_script_response("qualifying_intro")
            military_question = self.script_manager.get_script_response("military_question")
            
            full_response = f"{continue_response}\n\n{qualifying_intro}\n\n{military_question}"
            
            return ChatResponse(
                response=full_response,
                current_step=state.current_step
            )

        
    
    async def _handle_vbt_code_input(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle SMS code input and verification"""
        extracted_info = await self.ai_client.extract_information(user_message, state.current_step)
        
        if 'sms_code' in extracted_info:
            # Verify the SMS code (in real implementation, check against sent code)
            code_valid = await self.verification_engine.verify_sms_code(
                state.customer_name, extracted_info['sms_code']
            )
            
            if code_valid:
                state.sms_code_verified = True
                state.mobile_number_confirmed = True
                state.current_step = ConversationStep.QUALIFYING_QUESTIONS  
                
                response = self.script_manager.get_script_response(ConversationStep.CONTINUE_AFTER_WAIT, {"key": "continue_after_wait"})
                next_response = self.script_manager.get_script_response(ConversationStep.QUALIFYING_QUESTIONS, {"key": "military_question"})
                
                return ChatResponse(
                    response=f"{response}\n\n{next_response}",
                    current_step=state.current_step,
                    verification_status="phone_verified"
                )
            else:
                return ChatResponse(
                    response="The code you provided doesn't match. Could you please check and try again?",
                    current_step=state.current_step
                )
        else:
            return ChatResponse(
                response="I need the 6-digit code from your text message. Could you please provide it?",
                current_step=state.current_step,
                slots_needed=["sms_code"]
            )
    
    async def _handle_vbt_wait_retry(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle the 5-second wait scenario when code not received"""
        import asyncio
        
        # Simulate waiting 5 seconds
        await asyncio.sleep(5)
        
        # Ask again if they received the code
        still_no_code = not await self.ai_client.analyze_yes_no_response(user_message)
    
    async def _hangle_qualifying_questions(self, state: ConversationState, user_message: str) -> ChatResponse:
        if not state.slots_filled.get('military_status'):
            # Extract military status
            is_military = await self.ai_client.analyze_yes_no_response(user_message)
            state.slots_filled['military_status'] = is_military
            
            # Move to bank account information
            state.current_step = ConversationStep.BANK_ACCOUNT_INFO
            
            # Get account ending from database
            account_ending = await self.verification_engine.get_customer_account_ending(state.customer_name)
            
            qualifying_complete = self.script_manager.get_script_response("qualifying_complete")
            bank_account_intro = self.script_manager.get_script_response("bank_account_intro", {"account_ending": account_ending})
            
            full_response = f"{qualifying_complete}\n\n{bank_account_intro}"
            
            return ChatResponse(
                response=full_response,
                current_step=state.current_step,
                slots_needed=["bank_account", "bank_routing"]
            )
        
        # If we get here, something went wrong
        return ChatResponse(
            response="Let me connect you with a specialist to help you further.",
            current_step=ConversationStep.ESCALATION,
            escalate=True
        )
    
    # bank account

    async def _handle_paycheck_account_check(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle checking if this is the same account where they receive paycheck"""
        same_account = await self.ai_client.analyze_yes_no_response(user_message)
        
        state.paycheck_account_same = same_account
        state.slots_filled['receives_paycheck_in_account'] = same_account
        
        if same_account:
            # Same account, move to paycheck type question
            state.current_step = ConversationStep.PAYCHECK_TYPE_CHECK
            response = self.script_manager.get_script_response(ConversationStep.GREETING, {"key": "paycheck_type_question"})
            
            return ChatResponse(
                response=response,
                current_step=state.current_step,
                slots_needed=["paycheck_type"]
            )
        else:
            # Different account, need to update
            response = self.script_manager.get_script_response(ConversationStep.GREETING, {"key": "paycheck_no_update"})
            # Stay in same step to collect the paycheck account info
            
            return ChatResponse(
                response=response,
                current_step=ConversationStep.BANK_ACCOUNT_INFO  # Go back to collect paycheck account
            )
    
    async def _handle_paycheck_type_check(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle paycheck type (paper check or direct deposit)"""
        extracted_info = await self.ai_client.extract_information(user_message, state.current_step)
        
        paycheck_type = None
        user_message_lower = user_message.lower()
        
        if 'direct deposit' in user_message_lower or 'direct' in user_message_lower:
            paycheck_type = "direct deposit"
        elif 'paper check' in user_message_lower or 'paper' in user_message_lower or 'check' in user_message_lower:
            paycheck_type = "paper check"
        elif 'paycheck_type' in extracted_info:
            paycheck_type = extracted_info['paycheck_type']
        
        if paycheck_type:
            state.slots_filled['paycheck_type'] = paycheck_type
            state.paycheck_type_confirmed = True
            
            # Evaluate loan eligibility based on all responses
            loan_decision = await self.verification_engine.evaluate_loan_eligibility(state.slots_filled)
            
            if loan_decision.approved:
                state.loan_approved = True
                state.current_step = ConversationStep.DEBIT_CARD_COLLECTION
                
                response = self.script_manager.get_script_response(ConversationStep.GREETING, {"key": "debit_card_intro"})
                next_response = self.script_manager.get_script_response(ConversationStep.GREETING, {"key": "debit_card_request"})
                
                return ChatResponse(
                    response=f"{response}\n\n{next_response}",
                    current_step=state.current_step,
                    verification_status="loan_approved",
                    slots_needed=["card_number", "card_name", "card_expiry", "card_cvv"]
                )
            else:
                state.loan_declined = True
                state.current_step = ConversationStep.LOAN_DECLINED
                
                response = self.script_manager.get_script_response(ConversationStep.GREETING, {"key": "loan_declined"})
                
                return ChatResponse(
                    response=response,
                    current_step=state.current_step,
                    verification_status="loan_declined"
                )
        else:
            return ChatResponse(
                response="Are you paid via paper check or direct deposit?",
                current_step=state.current_step,
                slots_needed=["paycheck_type"]
            )
    
    async def _handle_debit_card_collection(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle debit card information collection"""
        # Check if customer is refusing to provide debit card
        refuses_card = await self.ai_client.analyze_debit_card_refusal(user_message)
        
        if refuses_card:
            state.debit_card_refused = True
            state.current_step = ConversationStep.DEBIT_CARD_REFUSAL
            
            response = self.script_manager.get_script_response(ConversationStep.GREETING, {"key": "debit_card_refusal"})
            
            return ChatResponse(
                response=response,
                current_step=state.current_step,
                escalate=True
            )
        
        extracted_info = await self.ai_client.extract_information(user_message, state.current_step)
        
        required_fields = ["card_number", "card_name", "card_expiry", "card_cvv"]
        has_all_fields = all(field in extracted_info for field in required_fields)
        
        if has_all_fields:
            # Validate card number
            card_valid = await self.verification_engine.validate_debit_card(extracted_info['card_number'])
            
            if card_valid:
                for field in required_fields:
                    state.slots_filled[field] = extracted_info[field]
                
                state.debit_card_provided = True
                state.current_step = ConversationStep.DEBIT_CARD_CONFIRM
                
                response = self.script_manager.get_script_response(ConversationStep.GREETING, {"key": "debit_card_confirm"})
                
                return ChatResponse(
                    response=response,
                    current_step=state.current_step
                )
            else:
                response = self.script_manager.get_script_response(ConversationStep.GREETING, {"key": "debit_card_invalid"})
                
                return ChatResponse(
                    response=response,
                    current_step=state.current_step
                )
        else:
            missing_fields = [field for field in required_fields if field not in extracted_info]
            
            return ChatResponse(
                response="I need the full 16-digit card number, the full customer name (initial if needed) as it appears on the card, the expiration date, and security code (CVV). Could you please provide all this information?",
                current_step=state.current_step,
                slots_needed=missing_fields
            )
    
    async def _handle_debit_card_confirm(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle debit card information confirmation"""
        # Customer should repeat the debit card information
        extracted_info = await self.ai_client.extract_information(user_message, state.current_step)
        
        required_fields = ["card_number", "card_name", "card_expiry", "card_cvv"]
        has_all_fields = all(field in extracted_info for field in required_fields)
        
        if has_all_fields:
            # Verify the repeated information matches
            matches = all(
                extracted_info[field] == state.slots_filled.get(field)
                for field in required_fields
            )
            
            if matches:
                state.debit_card_confirmed = True
                state.current_step = ConversationStep.COMPLETE
                
                # Set debit card payment consent
                state.slots_filled['debit_card_payment_consent'] = "yes"
                
                response = "Perfect! I have successfully collected and verified all your information. Your loan application is now complete and will be processed shortly. You should receive confirmation within 24 hours. Thank you for choosing Dash Of Cash!"
                
                return ChatResponse(
                    response=response,
                    current_step=state.current_step,
                    verification_status="complete"
                )
            else:
                return ChatResponse(
                    response="The information doesn't match what you provided earlier. Please provide the debit card information again.",
                    current_step=ConversationStep.DEBIT_CARD_COLLECTION
                )
        else:
            return ChatResponse(
                response="Please repeat all the debit card information: card number, name on card, expiration date, and CVV.",
                current_step=state.current_step
            )
    
    async def _handle_debit_card_refusal(self, state: ConversationState, user_message: str) -> ChatResponse:
        """Handle when customer refuses to provide debit card"""
        # This leads to loan withdrawal
        state.current_step = ConversationStep.COMPLETE
        
        response = "I understand. Unfortunately, without the debit card information, we cannot proceed with your loan application at this time. Thank you for your time today."
        
        return ChatResponse(
            response=response,
            current_step=state.current_step,
            verification_status="withdrawn",
            escalate=True
        )
    
    async def _handle_max_attempts_reached(self, state: ConversationState) -> ChatResponse:
        """Handle when maximum verification attempts are reached"""
        state.current_step = ConversationStep.ESCALATION
        
        response = self.script_manager.get_script_response(ConversationStep.GREETING)  # This should map to "max_attempts_reached"
        
        return ChatResponse(
            response="I'm having trouble verifying your information after multiple attempts. Let me connect you with one of our specialists who can help you further.",
            current_step=state.current_step,
            escalate=True
        )
    
    def _get_field_prompt(self, field_name: str) -> str:
        """Get prompt for specific field"""
        prompts = {
            "full_name": "Could you please confirm your full name?",
            "dob": "May I have your date of birth?",
            "ssn_last4": "What are the last 4 digits of your social security number?",
            "email": "Could you confirm the email address we have on file?"
        }
        return prompts.get(field_name, f"Could you provide your {field_name}?")