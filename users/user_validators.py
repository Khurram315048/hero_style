from pydantic import BaseModel,field_validator,EmailStr,model_validator
from typing import Optional
from utils.validators import BaseValidator,PasswordValidator



class UserSignupValidator(PasswordValidator):
    first_name:str
    last_name:str
    email:EmailStr

    @field_validator("first_name","last_name")
    @classmethod
    def names_alpha(cls, v: str) -> str:

        if not v.replace(" ", "").isalpha():
            raise ValueError("Must contain letters only.")
        
        if len(v) < 2:
            raise ValueError("Must be at least 2 characters.")
        
        return v.title()          

    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.lower()




class UserLoginValidator(BaseValidator):

    email:EmailStr
    password:str

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if len(v) < 1:
            raise ValueError("Password cannot be empty.")

        return v




class UserProfileValidator(BaseValidator):

    first_name:str
    last_name:str
    email:EmailStr

    @field_validator("first_name","last_name")
    @classmethod
    def names_alpha(cls, v: str) -> str:
        if not v.replace(" ","").isalpha():
            raise ValueError("Must contain letters only.")
        
        return v.title()




class OTPEmailValidator(BaseValidator):

    email:EmailStr

    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.lower()


class OTPVerifyValidator(BaseValidator):
    otp:str

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, v: str) -> str:
        v=v.strip()
        if not v.isdigit():
            raise ValueError("OTP must contain digits only.")
        
        if len(v) != 6:
            raise ValueError("OTP must be exactly 6 digits.")
        
        return v


class NewPasswordValidator(BaseValidator):

    new_password:str
    confirm_password:str

    @field_validator("new_password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain an uppercase letter.")
        
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a number.")
        
        return v

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self



class ReviewValidator(BaseValidator):

    rating:int
    comment:str

    @field_validator("rating",mode="before")
    @classmethod
    def validate_rating(cls, v):
        try:
            v=int(v)
        except (ValueError,TypeError):
            raise ValueError("Rating must be a number.")
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5.")
        return v

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Comment must be at least 3 characters.")
        if len(v) > 1000:
            raise ValueError("Comment cannot exceed 1000 characters.")
        return v.strip()



class ReturnReasonValidator(BaseValidator):

    reason:str

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        if len(v) < 5:
            raise ValueError("Please provide a more detailed reason (min 5 characters).")
        if len(v) > 500:
            raise ValueError("Reason cannot exceed 500 characters.")
        return v.strip()