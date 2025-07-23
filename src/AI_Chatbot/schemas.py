from pydantic import BaseModel, Field, EmailStr, constr
from datetime import date


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
    )