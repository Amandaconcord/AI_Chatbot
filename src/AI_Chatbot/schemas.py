from pydantic import BaseModel, Field, EmailStr, constr
from datetime import date
from typing import Literal

class Slots(BaseModel):
    """
    Represents the slots for a chatbot interaction.
    """
    full_name:  constr(pattern=r"^[A-Za-z ,.'-]{2,100}$") = Field(
        ...,
        description="Customer’s first and last name, plain ASCII letters only",
        example="Jane Doe"
    )
    dob:        date = Field(
        ...,
        description="Date of birth in ISO format (YYYY-MM-DD)",
        example="1990-04-23"
    )
    ssn_last4:  constr(pattern=r"^\d{4}$") = Field(
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

