from pydantic import BaseModel, Field, EmailStr, constr
from datetime import date, datetime  
from typing import Literal, Optional, Dict, Any, List
from enum import Enum

class Slots(BaseModel):
    """
    Represents the slots for a chatbot interaction.
    """
    full_name: constr(pattern=r"^[A-Za-z ,.'-]{2,100}$") = Field(
        ...,
        description="Customer’s first and last name, plain ASCII letters only",
        example="Jane Doe"
    )
    dob:        date = Field(
        ...,
        description="Date of birth in ISO format (YYYY-MM-DD)",
        example="1990-04-23"
    )
    ssn_last4: constr(pattern=r"^\d{4}$") = Field(
        ...,
        description="Last four digits of the Social Security Number",
        example="1234"
    )
    email:      EmailStr = Field(
        ...,
        description="Primary e-mail address on file",
        example="jane.doe@gmail.com"
    ),
    phone_number: constr(pattern=r"^\d{10}$") = Field(
        ...,
        description="Primary phone number on file, 10 digits without dashes or spaces",
        example="1234567890"
    ),
    # qualifting questions
    military_status: Literal["yes", "no"] = Field(
        ...,
        description="Military status of the customer or their spouse",
        example="yes"
    ),
    # bank information 
    bank_account: constr(pattern=r"^\d{8,12}$") = Field(
        ...,
        description="Bank account number, 8 to 12 digits",
        example="1234567890"
    ),
    bank_routing: constr(pattern=r"^\d{9}$") = Field(
        ...,
        description="Bank routing number, 9 digits",
        example="123456789"
    ),
    account_type: constr(pattern=r"^(checking|savings)$") = Field(
        ..., 
        description="Bank account type: checking or savings", 
        example="checking"
    ),
    receives_paycheck_in_account: bool = Field(
        ..., 
        description="Does the user receive their paycheck in this account?", 
        example=True
    ),
    paycheck_type: constr(pattern=r"^(direct deposit|paper check)$") = Field(
        ..., 
        description="How they receive their paycheck", 
        example="direct deposit"
    ),
    # Debit Card Information
    card_number: constr(pattern=r"\d{16}") = Field(
        ..., description="16-digit card number", example="4111111111111111"
    )
    card_name: constr(min_length=2, max_length=50) = Field(
        ..., description="Name on card", example="JANE A DOE"
    )
    card_expiry: constr(pattern=r"(0[1-9]|1[0-2])\/\d{2}") = Field(
        ..., description="Card expiration in MM/YY format", example="04/27"
    )
    card_cvv: constr(pattern=r"\d{3,4}") = Field(
        ..., description="Card security code (CVV)", example="123"
    ),
    debit_card_payment_consent: Literal["yes", "no"] = Field(
        ..., description="Did the customer give consent to use debit card for future payments?",
        example="yes"
    ),
    # employment information
    employment_status: Literal["Employed","Self-Employed","Unemployed","Social Security Income","Social Security Disability",
                               "Veteran's Disability","Pension","Seasonal"] = Field(
        ...,
        description="Employment status: self-employed or employed",
        example="employed"
    ),
    job_title: constr(min_length=2, max_length=100) = Field(
        ...,
        description="Job title of the customer",
        example="Software Engineer"
    ),
    work_phone: Optional[str] = Field(
        None,
        description="Work phone number of the customer, 10 digits without dashes or spaces",
        example="0987654321"
    )
    work_phone_confirmed: Optional[bool] = Field(
        None,
        description="Whether the work phone number has been confirmed by the customer",
        example=True
    ),
    alternative_work_phone: Optional[str] = Field(
        description="If the customer says the original work phone is not reachable, collect an alternative work number."
    ),
    pay_frequency: Optional[str] = Field(
        description="How often the customer is paid. Accept values: 'weekly', 'biweekly', 'semimonthly', 'monthly', etc.",
        example="biweekly"
    ),
    next_paycheck_date: Optional[date] = Field(
        description="The next expected paycheck date.",
        example="2025-08-01"
    ),
    early_payment_on_holidays: Optional[bool] = Field(
        description="Whether the customer is paid before holidays/weekends if the pay date falls on one.",
        example=True
    )


class ConversationStep(str, Enum):
    GREETING = "greeting"
    ASK_NAME = "ask_name"
    ASK_DOB = "ask_dob"
    ASK_SSN = "ask_ssn"
    ASK_EMAIL = "ask_email"
    EMAIL_USAGE_CHECK = "email_usage_check"
    CONTACT_INFO_CHECK = "contact_info_check"  # Home number verification
    VBT_INITIATE = "vbt_initiate"  # Send SMS
    VBT_CODE_CHECK = "vbt_code_check"  # Ask if received code
    VBT_CODE_INPUT = "vbt_code_input"  # Get the 6-digit code
    VBT_WAIT_RETRY = "vbt_wait_retry"  # Wait 5 seconds scenario
    VBT_REFUSE_CODE = "vbt_refuse_code"  # Customer refuses to provide code
    CODE_RECEIVED = "code_received"  # Code received successfully
    CODE_NOT_RECEIVED = "code_not_received"  # Code not received yet
    CONTINUE_AFTER_WAIT = "continue_after_wait"  # Continue after waiting for code
    QUALIFYING_INTRO = "qualifying_intro"  # Military member question
    MILITARY_QUESTION = "military_question"
    BANK_ACCOUNT_INFO = "bank_account_info"  # Bank account verification
    BANK_ACCOUNT_CONFIRM = "bank_account_confirm"  # Confirm account number
    ACCOUNT_TYPE_CHECK = "account_type_check"  # Checking or savings
    PAYCHECK_ACCOUNT_CHECK = "paycheck_account_check"  # Same account for paycheck
    PAYCHECK_TYPE_CHECK = "paycheck_type_check"  # Paper check or direct deposit
    DEBIT_CARD_COLLECTION = "debit_card_collection"  # Collect debit card info
    DEBIT_CARD_CONFIRM = "debit_card_confirm"  # Confirm debit card info
    DEBIT_CARD_REFUSAL = "debit_card_refusal"  # Customer refuses debit card
    EMPLOYMENT_INFO = "employment_info"
    FINAL_CONFIRMATION = "final_confirmation"
    LOAN_APPROVED = "loan_approved"
    LOAN_DECLINED = "loan_declined"
    ESCALATION = "escalation"
    COMPLETE = "complete"

class ConversationState(BaseModel):
    session_id: str
    current_step: ConversationStep
    customer_name: Optional[str] = None
    agent_name: str = "Virtual Assistant"
    company_name: str = "Dash Of Cash"
    slots_filled: Dict[str, Any] = {}
    verification_attempts: int = 0
    max_attempts: int = 3
    escalation_flags: List[str] = []
    script_context: Dict[str, Any] = {}
    
    # Identity verification status
    dob_verified: bool = False
    ssn_verified: bool = False
    email_verified: bool = False
    email_usage_confirmed: bool = False
    
    # Phone verification status
    home_number_confirmed: bool = False
    mobile_number_confirmed: bool = False
    sms_code_sent: bool = False
    sms_code_verified: bool = False
    sms_code_refused: bool = False
    sms_retry_count: int = 0
    max_sms_retries: int = 2
    has_time_to_continue: bool = True
    
    # Qualifying questions
    is_military_member: Optional[bool] = None
    
    # Banking information
    bank_account_verified: bool = False
    bank_account_confirmed: bool = False
    account_type_confirmed: bool = False
    paycheck_account_same: Optional[bool] = None
    paycheck_type_confirmed: bool = False
    
    # Debit card information
    debit_card_provided: bool = False
    debit_card_confirmed: bool = False
    debit_card_refused: bool = False
    
    # Final status
    loan_approved: bool = False
    loan_declined: bool = False
    
class VerificationResult(BaseModel):
    identity_verified: bool
    account_matched: bool
    email_confirmed: bool
    employment_verified: bool
    risk_score: float = 0.0
    verification_status: Literal["approved", "pending", "rejected", "escalate"]
    failure_reasons: List[str] = []
    next_action: str

class LoanDecision(BaseModel):
    approved: bool
    decline_reasons: List[str] = []

class ChatRequest(BaseModel):
    session_id: str
    message: str
    
class ChatResponse(BaseModel):
    response: str
    current_step: ConversationStep
    slots_needed: List[str] = []
    verification_status: Optional[str] = None
    escalate: bool = False
    auto_follow_up: bool = False
    follow_up_delay: float = 0.0