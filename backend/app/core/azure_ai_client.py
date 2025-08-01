from typing import Dict, Any, Optional
from app.models.schemas import ConversationStep
import json
import re

class AzureAIClient:
    def __init__(self):
        # For testing, we'll use a mock client instead of real Azure OpenAI
        self.client = None
        print("🤖 Using Mock AI Client for testing (no Azure OpenAI required)")
    
    async def extract_information(self, user_message: str, current_step: ConversationStep) -> Dict[str, Any]:
        """Enhanced extract structured information from user message with natural language understanding"""
        
        user_message = user_message.strip()
        user_lower = user_message.lower()
        extracted = {}
        
        if current_step == ConversationStep.ASK_NAME:
            # Enhanced name extraction - handles multiple formats
            name_patterns = [
                r"my name is (.+?)(?:\.|$|,|\sand\s)",
                r"i'm (.+?)(?:\.|$|,|\sand\s)", 
                r"i am (.+?)(?:\.|$|,|\sand\s)",
                r"call me (.+?)(?:\.|$|,|\sand\s)",
                r"this is (.+?)(?:\.|$|,|\sand\s)",
                r"^(.+?)(?:\.|$)"  # Fallback: treat whole message as name if it looks like one
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, user_lower, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    # Clean up the name
                    name = re.sub(r'\b(speaking|here|from|the|customer|client)\b', '', name, flags=re.IGNORECASE)
                    name = ' '.join(name.split())  # Remove extra spaces
                    
                    # Validate it looks like a name (has at least 2 words, mostly letters)
                    words = name.split()
                    if len(words) >= 2 and all(re.match(r"[a-zA-Z\-'\.]+", word) for word in words):
                        extracted['full_name'] = name.title()
                        break
                        
        elif current_step == ConversationStep.ASK_DOB:
            # Enhanced DOB extraction - handles natural language dates
            dob = self._extract_date_of_birth(user_message)
            if dob:
                extracted['dob'] = dob
        
        elif current_step == ConversationStep.ASK_EMAIL:
            # Enhanced email extraction with multiple patterns
            email_patterns = [
                r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',  # Standard email
                r'(?:email|address|update|new|change)\s+(?:is\s+|to\s+)?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'  # Simple fallback
            ]
            
            # Always try to extract email first, regardless of yes/no words
            for pattern in email_patterns:
                match = re.search(pattern, user_message, re.IGNORECASE)
                if match:
                    extracted['email'] = match.group(1).lower()
                    print(f"🔍 Extracted email: {extracted['email']}")  # Debug log
                    break
            
            # If no email found and it looks like they're trying to provide one, be more flexible
            if 'email' not in extracted and '@' in user_message:
                # Try to extract anything that looks like an email
                flexible_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+)', user_message)
                if flexible_match:
                    potential_email = flexible_match.group(1)
                    # Add common domain endings if missing
                    if not re.search(r'\.[a-zA-Z]{2,}$', potential_email):
                        if potential_email.endswith('@gmail'):
                            potential_email += '.com'
                        elif potential_email.endswith('@yahoo'):
                            potential_email += '.com'
                        # Add more common fixes as needed
                    
                    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', potential_email):
                        extracted['email'] = potential_email.lower()
                        print(f"🔍 Extracted email (flexible): {extracted['email']}")  # Debug log
                
        elif current_step == ConversationStep.ASK_SSN:
            # Enhanced SSN extraction
            ssn_patterns = [
                r"(?:last|final|end)\s*(?:four|4)\s*(?:digits?|numbers?)\s*(?:are|is)?\s*(\d{4})",
                r"(?:ssn|social)\s*(?:ends?|ending)\s*(?:in|with)?\s*(\d{4})",
                r"\b(\d{4})\b"  # Simple 4-digit fallback
            ]
            
            for pattern in ssn_patterns:
                match = re.search(pattern, user_lower)
                if match:
                    extracted['ssn_last4'] = match.group(1)
                    break
                    
        elif current_step == ConversationStep.VBT_CODE_INPUT:
            # Enhanced SMS code extraction
            code_patterns = [
                r"(?:code|verification)\s*(?:is|was)?\s*(\d{6})",
                r"(?:received|got)\s*(\d{6})",
                r"\b(\d{6})\b"  # Simple 6-digit fallback
            ]
            
            for pattern in code_patterns:
                match = re.search(pattern, user_message)
                if match:
                    extracted['sms_code'] = match.group(1)
                    break
                    
        elif current_step == ConversationStep.BANK_ACCOUNT_INFO or current_step == ConversationStep.BANK_ACCOUNT_CONFIRM:
            # Enhanced bank account extraction
            account_info = self._extract_bank_info(user_message)
            extracted.update(account_info)
            
        elif current_step == ConversationStep.DEBIT_CARD_COLLECTION or current_step == ConversationStep.DEBIT_CARD_CONFIRM:
            # Enhanced debit card extraction
            card_info = self._extract_card_info(user_message)
            extracted.update(card_info)
        
        return extracted

    def _extract_date_of_birth(self, text: str) -> Optional[str]:
        """Enhanced date extraction supporting multiple natural formats"""
        import datetime as dt
        
        date_patterns = [
            # Standard formats
            (r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', 'mdy'),  # MM/DD/YYYY or MM-DD-YYYY
            (r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})', 'ymd'),  # YYYY/MM/DD or YYYY-MM-DD
            (r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{2})', 'mdy2'), # MM/DD/YY or MM-DD-YY
            
            # Month name formats - FIXED: More flexible comma and space handling
            (r'(january|jan)\s*,?\s*(\d{1,2})\s*,?\s*(\d{4})', 'month_name'),
            (r'(february|feb)\s*,?\s*(\d{1,2})\s*,?\s*(\d{4})', 'month_name'),
            (r'(march|mar)\s*,?\s*(\d{1,2})\s*,?\s*(\d{4})', 'month_name'),
            (r'(april|apr)\s*,?\s*(\d{1,2})\s*,?\s*(\d{4})', 'month_name'),
            (r'(may)\s*,?\s*(\d{1,2})\s*,?\s*(\d{4})', 'month_name'),
            (r'(june|jun)\s*,?\s*(\d{1,2})\s*,?\s*(\d{4})', 'month_name'),
            (r'(july|jul)\s*,?\s*(\d{1,2})\s*,?\s*(\d{4})', 'month_name'),
            (r'(august|aug)\s*,?\s*(\d{1,2})\s*,?\s*(\d{4})', 'month_name'),
            (r'(september|sep|sept)\s*,?\s*(\d{1,2})\s*,?\s*(\d{4})', 'month_name'),
            (r'(october|oct)\s*,?\s*(\d{1,2})\s*,?\s*(\d{4})', 'month_name'),
            (r'(november|nov)\s*,?\s*(\d{1,2})\s*,?\s*(\d{4})', 'month_name'),
            (r'(december|dec)\s*,?\s*(\d{1,2})\s*,?\s*(\d{4})', 'month_name'),
            
            # Reverse month name formats (22 July 2000)
            (r'(\d{1,2})\s*,?\s*(january|jan)\s*,?\s*(\d{4})', 'day_month_name'),
            (r'(\d{1,2})\s*,?\s*(february|feb)\s*,?\s*(\d{4})', 'day_month_name'),
            (r'(\d{1,2})\s*,?\s*(march|mar)\s*,?\s*(\d{4})', 'day_month_name'),
            (r'(\d{1,2})\s*,?\s*(april|apr)\s*,?\s*(\d{4})', 'day_month_name'),
            (r'(\d{1,2})\s*,?\s*(may)\s*,?\s*(\d{4})', 'day_month_name'),
            (r'(\d{1,2})\s*,?\s*(june|jun)\s*,?\s*(\d{4})', 'day_month_name'),
            (r'(\d{1,2})\s*,?\s*(july|jul)\s*,?\s*(\d{4})', 'day_month_name'),
            (r'(\d{1,2})\s*,?\s*(august|aug)\s*,?\s*(\d{4})', 'day_month_name'),
            (r'(\d{1,2})\s*,?\s*(september|sep|sept)\s*,?\s*(\d{4})', 'day_month_name'),
            (r'(\d{1,2})\s*,?\s*(october|oct)\s*,?\s*(\d{4})', 'day_month_name'),
            (r'(\d{1,2})\s*,?\s*(november|nov)\s*,?\s*(\d{4})', 'day_month_name'),
            (r'(\d{1,2})\s*,?\s*(december|dec)\s*,?\s*(\d{4})', 'day_month_name'),
            
            # Natural language
            (r'born\s+(?:on\s+)?(.+)', 'natural'),
            (r'birthday\s+(?:is\s+)?(.+)', 'natural'),
            (r'date\s+of\s+birth\s+(?:is\s+)?(.+)', 'natural'),
        ]
        
        # Rest of the method stays the same...
        month_map = {
            'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
            'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6,
            'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12
        }
        
        text_lower = text.lower().strip()
        print(f"🔍 Trying to extract date from: '{text_lower}'")
        
        for pattern, format_type in date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                print(f"🔍 Pattern matched: {pattern} -> {match.groups()}")
                try:
                    if format_type == 'mdy':
                        month, day, year = match.groups()
                        date_obj = dt.date(int(year), int(month), int(day))
                        
                    elif format_type == 'ymd':
                        year, month, day = match.groups()
                        date_obj = dt.date(int(year), int(month), int(day))
                        
                    elif format_type == 'mdy2':
                        month, day, year = match.groups()
                        year = int(year)
                        if year < 50:
                            year += 2000
                        else:
                            year += 1900
                        date_obj = dt.date(year, int(month), int(day))
                        
                    elif format_type == 'month_name':
                        month_name, day, year = match.groups()
                        month_num = month_map[month_name.lower()]
                        date_obj = dt.date(int(year), month_num, int(day))
                        
                    elif format_type == 'day_month_name':
                        day, month_name, year = match.groups()
                        month_num = month_map[month_name.lower()]
                        date_obj = dt.date(int(year), month_num, int(day))
                    
                    result = date_obj.strftime('%Y-%m-%d')
                    print(f"✅ Successfully extracted date: {result}")
                    return result
                    
                except (ValueError, KeyError) as e:
                    print(f"❌ Error parsing date: {e}")
                    continue
        
        print(f"❌ No date pattern matched for: '{text_lower}'")
        return None

    def _extract_bank_info(self, text: str) -> Dict[str, Any]:
        """Extract bank account and routing information"""
        extracted = {}
        
        # Look for account number
        account_patterns = [
            r"account\s+(?:number\s+)?(?:is\s+)?(\d{8,12})",
            r"checking\s+(?:account\s+)?(?:is\s+)?(\d{8,12})",
            r"savings\s+(?:account\s+)?(?:is\s+)?(\d{8,12})",
            r"\b(\d{8,12})\b"  # Fallback: any 8-12 digit number
        ]
        
        # Look for routing number  
        routing_patterns = [
            r"routing\s+(?:number\s+)?(?:is\s+)?(\d{9})",
            r"transit\s+(?:number\s+)?(?:is\s+)?(\d{9})",
            r"\b(\d{9})\b"  # Fallback: any 9 digit number
        ]
        
        for pattern in account_patterns:
            match = re.search(pattern, text.lower())
            if match:
                extracted['bank_account'] = match.group(1)
                break
                
        for pattern in routing_patterns:
            match = re.search(pattern, text.lower())
            if match:
                extracted['bank_routing'] = match.group(1)
                break
        
        return extracted
    
    # Add this missing method at the end of your AzureAIClient class

    def _extract_card_info(self, text: str) -> Dict[str, Any]:
        """Extract debit card information"""
        extracted = {}
        
        # Look for card number (16 digits)
        card_match = re.search(r'\b(\d{16})\b', text)
        if card_match:
            extracted['card_number'] = card_match.group(1)
        
        # Look for CVV (3-4 digits, but not the card number)
        cvv_matches = re.findall(r'\b(\d{3,4})\b', text)
        for cvv in cvv_matches:
            if cvv != extracted.get('card_number', '')[:4]:  # Don't match first 4 of card
                extracted['card_cvv'] = cvv
                break
        
        # Look for expiry (MM/YY format)
        expiry_match = re.search(r'(\d{1,2})/(\d{2})', text)
        if expiry_match:
            month, year = expiry_match.groups()
            extracted['card_expiry'] = f"{month.zfill(2)}/{year}"
        
        # Look for name on card (uppercase words that look like names)
        words = text.upper().split()
        name_candidates = [word for word in words if word.isalpha() and len(word) > 1]
        if len(name_candidates) >= 2:
            extracted['card_name'] = ' '.join(name_candidates[:3])  # Take first 3 words as name
        
        return extracted
    
    async def analyze_yes_no_response(self, user_message: str) -> bool:
        """Analyze if user response is positive (yes) or negative (no)"""
        user_message = user_message.lower()
        positive_words = ['yes', 'yeah', 'yep', 'correct', 'right', 'that\'s right', 'affirmative', 'sure', 'okay', 'ok', 'true']
        negative_words = ['no', 'nope', 'incorrect', 'wrong', 'that\'s not right', 'negative', 'not correct', 'false']
        
        # Check for positive indicators
        if any(word in user_message for word in positive_words):
            return True
        
        # Check for negative indicators  
        if any(word in user_message for word in negative_words):
            return False
            
        # Default to False if unclear
        return False
    
    async def analyze_code_refusal(self, user_message: str) -> bool:
        """Analyze if user is refusing to provide SMS verification code"""
        user_message = user_message.lower()
        refusal_words = ['refuse', 'don\'t want', 'no thanks', 'not interested', 'don\'t send', 'no texts']
        return any(word in user_message for word in refusal_words)
    
    async def analyze_debit_card_refusal(self, user_message: str) -> bool:
        """Analyze if user is refusing to provide debit card information"""
        user_message = user_message.lower()
        refusal_words = ['refuse', 'don\'t want', 'not comfortable', 'won\'t provide', 'no thanks', 'don\'t give']
        return any(word in user_message for word in refusal_words)