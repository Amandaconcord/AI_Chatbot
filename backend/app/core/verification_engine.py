from typing import Dict, Any, Optional
from app.models.schemas import VerificationResult, LoanDecision
import asyncio

class VerificationEngine:
    def __init__(self):
        # Mock database for testing
        self.mock_customers = {
            "john smith": {
                'full_name': 'John Smith',
                'dob': '1990-01-15',
                'ssn_last4': '1234',
                'email': 'john.smith@example.com',
                'phone_number': '1234567890',
                'home_number': '8102405111',
                'bank_account': '1234567890',
                'bank_routing': '123456789'
            }
        }
        print("🗄️ Using Mock Database for testing")
    
    async def verify_dob(self, customer_name: str, dob: str) -> bool:
        """Verify date of birth against customer database"""
        customer_record = self.mock_customers.get(customer_name.lower())
        if customer_record:
            return customer_record.get('dob') == dob
        return True  # For testing, accept any DOB for unknown customers
    
    async def verify_ssn(self, customer_name: str, ssn_last4: str) -> bool:
        """Verify last 4 digits of SSN against customer database"""
        customer_record = self.mock_customers.get(customer_name.lower())
        if customer_record:
            return customer_record.get('ssn_last4') == ssn_last4
        return True  # For testing, accept any SSN for unknown customers
    
    async def get_customer_email(self, customer_name: str) -> Optional[str]:
        """Get customer's email from database"""
        customer_record = self.mock_customers.get(customer_name.lower())
        return customer_record.get('email', 'test@example.com') if customer_record else 'test@example.com'
    
    async def get_customer_home_number(self, customer_name: str) -> Optional[str]:
        """Get customer's home phone number from database"""
        customer_record = self.mock_customers.get(customer_name.lower())
        return customer_record.get('home_number', '8102405111') if customer_record else '8102405111'
    
    async def get_customer_mobile_number(self, customer_name: str) -> Optional[str]:
        """Get customer's mobile phone number from database"""
        customer_record = self.mock_customers.get(customer_name.lower())
        return customer_record.get('phone_number', '1234567890') if customer_record else '1234567890'
    
    async def get_customer_account_ending(self, customer_name: str) -> Optional[str]:
        """Get last 4 digits of customer's bank account from database"""
        customer_record = self.mock_customers.get(customer_name.lower())
        account = customer_record.get('bank_account', '1234567890') if customer_record else '1234567890'
        return account[-4:] if account and len(account) >= 4 else '7890'
    
    async def verify_sms_code(self, customer_name: str, sms_code: str) -> bool:
        """Verify SMS verification code"""
        # For testing, accept any 6-digit code
        return len(sms_code) == 6 and sms_code.isdigit()
    
    async def verify_bank_account(self, customer_name: str, account_number: str, routing_number: str) -> bool:
        """Verify bank account and routing number against customer database"""
        customer_record = self.mock_customers.get(customer_name.lower())
        if customer_record:
            return (customer_record.get('bank_account') == account_number and 
                   customer_record.get('bank_routing') == routing_number)
        return True  # For testing, accept any account for unknown customers
    
    async def validate_debit_card(self, card_number: str) -> bool:
        """Validate debit card number format"""
        # Basic validation - check if it's 16 digits
        if not card_number.isdigit() or len(card_number) != 16:
            return False
        
        # Simple Luhn algorithm check
        def luhn_check(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10 == 0
        
        return luhn_check(card_number)
    
    async def evaluate_loan_eligibility(self, customer_data: Dict[str, Any]) -> 'LoanDecision':
        """Evaluate loan eligibility based on collected information"""
        # Simple mock eligibility - approve most applications for testing
        approved = True
        decline_reasons = []
        
        # Check if required info is present
        if not customer_data.get('bank_account') or not customer_data.get('bank_routing'):
            approved = False
            decline_reasons.append("Missing bank account information")
        
        return LoanDecision(
            approved=approved,
            decline_reasons=decline_reasons
        )