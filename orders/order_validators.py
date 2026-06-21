from pydantic import BaseModel,field_validator
from typing import Optional
from utils.validators import BaseValidator


class CheckoutValidator(BaseValidator):

    first_name:str
    last_name:str
    city:str
    shipping_address:str
    payment_method:str
    postal_code:Optional[str]=""
    email:Optional[str] = None
    promo_code:Optional[str] = None


    @field_validator("first_name","last_name")
    @classmethod
    def name_alpha(cls, v: str) -> str:
        if not v.replace(" ","").isalpha():
            raise ValueError("Must contain letters only.")
        
        if len(v) < 2:
            raise ValueError("Must be at least 2 characters.")
        
        return v.title()


    @field_validator("shipping_address")
    @classmethod
    def address_length(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Please enter a more complete address (min 10 chars).")
        
        return v


    @field_validator("payment_method")
    @classmethod
    def valid_payment(cls, v: str) -> str:
        allowed={"COD","JazzCash","EasyPaisa","bank_transfer","card"}

        if v not in allowed:
            raise ValueError(f"Invalid payment method.")
        
        return v


    @field_validator("email",mode="before")
    @classmethod
    def email_optional(cls,v):
        if v=="" or v is None:
            return None
        
        return v.lower().strip()

    @field_validator("promo_code",mode="before")
    @classmethod
    def promo_upper(cls,v):
        if v=="" or v is None:
            return None
        
        return v.upper().strip()



class CartItemValidator(BaseValidator):

    product_id:int
    quantity:int

    @field_validator("product_id",mode="before")
    @classmethod
    def valid_product_id(cls, v):
        try:
            v=int(v)
        except (ValueError,TypeError):
            raise ValueError("Invalid product ID.")
        if v <= 0:
            raise ValueError("Invalid product ID.")
        return v

    @field_validator("quantity",mode="before")
    @classmethod
    def valid_quantity(cls, v):
        try:
            v=int(v)
        except (ValueError,TypeError):
            raise ValueError("Invalid quantity.")
        if v < 1:
            raise ValueError("Quantity must be at least 1.")
        if v > 100:
            raise ValueError("Quantity cannot exceed 100.")
        return v