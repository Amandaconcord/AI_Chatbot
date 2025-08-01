from typing import Dict, Any
from app.models.schemas import ConversationState, ConversationStep

class ScriptManager:
    def __init__(self):
        self.scripts = self._load_scripts()
    
    def _load_scripts(self) -> Dict[str, str]:
        return {
            # Initial greeting and time check
            "greeting": "Hello! I'm your virtual assistant from {company_name}. I'm here to help you complete your loan verification process. Is now a good time to complete the process?",
            "no_time_callback": "That's okay! We can always come back to this later. Just let me know when you're ready.",
            "ask_name": "Great! To get started, could you please tell me your full name?",
            
            # Identity verification steps
            "ask_dob": "To protect your privacy and security, Can you confirm the following information before we can continue. May I have your date of birth?",
            "ask_ssn": "Thank you. Now, could you please provide the last 4 digits of your social security number?",
            "ask_email": "Great! Lastly, I would need you to confirm the email address we have on file. Is your email address {email}?",
            "email_usage_check": "Is this an email account you check regularly?",
            "email_update_request": "I'd recommend updating your email address to one you check regularly. This helps us keep you informed about your loan status. Would you like to provide an updated email address?",
            
            # Identity verification success
            "identity_success": "Perfect, we can now go ahead with the process which is a quick review of the loan information and verification of your information. Once completed we can send the loan off right to your account on file.",
            
            # Contact information verification
            "unique_account": "Your account shows you home number as {home_number}, is that a number we would be able to contact you on?",
            "no_entry": "Unfortunately, we do not have a home number on file, is there another number you would like to add to your account?",
            
            # VBT (Verification by Text) flow
            "vbt_initiate": "Thank you for confirming. To complete the mobile number verification, I have initiated a text message to your mobile phone, you should be receiving it shortly.",
            "vbt_code_check": "After opening the text, you will see an approval code which will help us verify your phone. This action will enable you to receive reminders about upcoming payments, as well as future promotional offers. Have you received the code?",
            "code_received": "Great. Can you please provide me with the 6-digit code in the message?",
            "code_not_received": "Not a problem. Let's give it a moment to see if it comes in.",
            "wait_5_seconds": "Let's wait 5 seconds to see if the code arrives.",
            "still_no_code": "Since you haven't received the code by now, let's continue with the process. If at any time during our conversation you receive the text, please let me know.",
            "continue_after_wait": "I appreciate that information, let's continue with your application.",
            "code_refusal": "Not a problem, we can continue without the code, however this verification will ensure you receive important payment reminder during your loan. If you do receive the code, please let me know.",
            
            # Qualifying Questions
            "qualifying_intro": "We have some general questions regarding your account, I appreciate your assistance as we ensure the accuracy for quality purposes.",
            "military_question": "Are you or your spouse, if married, an active member of the military?",
            "qualifying_complete": "Thank you for confirming that information, next we will review your financial information.",
            
            # Bank Account Information
            "bank_account_intro": "I see on file we have a bank account ending with {account_ending}. Can you please confirm the full account and routing number for that bank account to ensure we can provide the proper account with the funds? The information is in the middle of the loan agreement and we need to make sure its accurate before you sign.",
            "bank_account_confirm": "And to ensure accuracy, can please confirm the account number one more time?",
            "account_type_question": "And is the account you provided a checking or savings account?",
            "paycheck_account_question": "Is this the same account where you receive your paycheck?",
            "paycheck_no_update": "Unfortunately, in order to verify the information submitted within this application and to ensure successful payment to your account, we do require the primary bank account to be the one in which you receive your paycheck. I would be happy to update this for you now.",
            "paycheck_type_question": "Lastly, are you paid via paper check or direct deposit?",
            
            # Debit Card Collection
            "debit_card_intro": "We will now discuss your payment options, to ensure on-time payments, Dash Of Cash requires collecting the debit card associated with the bank account on file. This will help ensure on-time payments. We reserve the right to debit your account using either an electronically or via your Debit Card.",
            "debit_card_request": "Can you provide me with the debit card information associated with the bank account on file?",
            "debit_card_confirm": "Thank you for the information. To ensure we have accurate information can you please repeat the information one more time.",
            "debit_card_refusal": "Unfortunately, a debit card is required. Without the associated debit card, I am afraid we cannot continue the loan process.",
            "debit_card_invalid": "This Card number is not valid. Please update the card number or switch AutoPay to ACH",
            
            # Loan Status
            "loan_approved": "Continue to Collect Debit Card Info",
            "loan_declined": "Based upon the information you provided I am sorry to let you know that we cannot offer you a loan.",
            "loan_decline_rebuttal": "When inputting the information into my system it appears that one or more of your responses triggered your application to decline, I do apologize but unfortunately, we cannot continue at this time.",
            
            # Error messages
            "verification_failed": "I'm sorry, but the information provided doesn't match our records. Let's try again. You have {attempts_remaining} attempts remaining.",
            "max_attempts_reached": "I'm having trouble verifying your information after multiple attempts. Let me connect you with one of our specialists who can help you further.",
        }
    
    def get_script_response(self, script_key: str, context: Dict[str, Any] = None) -> str:
        """Get the appropriate script response based on script key"""
        
        # Convert ConversationStep enum to string if needed
        if hasattr(script_key, 'value'):
            script_key = script_key.value
        
        script_template = self.scripts.get(script_key, f"Script not found for key: {script_key}")
        
        if context and script_template:
            try:
                return script_template.format(**context)
            except KeyError as e:
                print(f"Missing context key: {e}")
                return script_template
        
        return script_template