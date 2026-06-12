from pydantic import field_validator,EmailStr
from typing import Optional
import re
from utils.validators import BaseValidator


ALLOWED_CATEGORIES={"order","return","warranty","product","payment","other"}


class SupportFormValidator(BaseValidator):

    fullName:str
    email:EmailStr
    phone:Optional[str]=None
    category:str
    subject:str
    message:str
    orderId:Optional[str]=None
    rating:Optional[int]=None

    @field_validator("fullName")
    @classmethod
    def name_valid(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("Full name must be at least 2 characters.")
        
        if len(v) > 100:
            raise ValueError("Full name cannot exceed 100 characters.")
        
        if not v.replace(" ", "").replace("-", "").replace("'", "").isalpha():
            raise ValueError("Name must contain letters only.")
        
        return v.strip()


    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.lower().strip()

    @field_validator("phone",mode="before")
    @classmethod
    def phone_optional(cls, v):
        if v=="" or v is None:
            return None
        
        v=re.sub(r"[\s\-\(\)\+]","",v)   
        if not v.isdigit():
            raise ValueError("Phone number must contain digits only.")
        
        if len(v) < 7 or len(v) > 15:
            raise ValueError("Phone number must be 7–15 digits.")
        
        return v


    @field_validator("category")
    @classmethod
    def category_whitelist(cls, v: str) -> str:
        if v.lower() not in ALLOWED_CATEGORIES:
            raise ValueError(f"Invalid category.Choose from:{', '.join(ALLOWED_CATEGORIES)}")
        
        return v.lower()


    @field_validator("subject")
    @classmethod
    def subject_length(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Subject must be at least 3 characters.")
        
        if len(v) > 255:
            raise ValueError("Subject cannot exceed 255 characters.")
        
        return v.strip()


    @field_validator("message")
    @classmethod
    def message_length(cls, v: str) -> str:
        if len(v) < 20:
            raise ValueError("Message must be at least 20 characters.")
        
        if len(v) > 2000:
            raise ValueError("Message cannot exceed 2000 characters.")
        
        return v.strip()


    @field_validator("orderId",mode="before")
    @classmethod
    def order_id_optional(cls, v):
        if v=="" or v is None:
            return None
        
        v=v.strip()
        if not v.isdigit():
            return None    
        
        return v


    @field_validator("rating",mode="before")
    @classmethod
    def rating_optional(cls, v):
        if v=="" or v is None:
            return None
        
        try:
            v=int(v)
        except (ValueError,TypeError):
            return None
        
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5.")
        
        return v