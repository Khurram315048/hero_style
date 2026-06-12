from pydantic import BaseModel,field_validator,EmailStr
from typing import Optional
import re


class BaseValidator(BaseModel):
    
    model_config={
        "str_strip_whitespace":True,   
        "str_min_length":1,           
    }


class EmailValidator(BaseValidator):

    email:EmailStr

    @field_validator("email")
    @classmethod
    def email_lowercase(cls,v):
        return v.lower()


class PasswordValidator(BaseValidator):

    password:str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):

        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number.")
        
        return v


def extract_errors(exc) -> list[str]:

    messages=[]
    for err in exc.errors():
        field=" → ".join(str(loc) for loc in err["loc"])
        msg=err["msg"].replace("Value error, ", "")
        messages.append(f"{field}: {msg}")
        
    return messages