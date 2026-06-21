from pydantic import BaseModel,field_validator,EmailStr,model_validator
from typing import Optional
from decimal import Decimal
from utils.validators import BaseValidator,PasswordValidator
 



class AdminSignupValidator(PasswordValidator):

    first_name:str
    last_name:str
    username:str
    email:EmailStr

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters.")
        
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters,numbers, _ and -")
        
        return v.lower()


    @field_validator("first_name","last_name")
    @classmethod
    def names_valid(cls, v: str) -> str:
        if not v.replace(" ","").isalpha():
            raise ValueError("Must contain letters only.")
        
        return v.title()


class AdminLoginValidator(BaseValidator):

    email:EmailStr
    password:str




class ProductValidator(BaseValidator):
    title:str
    product_no:str
    category_id:int
    base_price:Decimal
    sale_price:Optional[Decimal]=None
    stock:int=0
    status:str="active"
    short_description:Optional[str]=None
    long_description:Optional[str]=None
    display_type:Optional[str]=None
    battery_life:Optional[str]=None
    connectivity:Optional[str]=None
    strap_material:Optional[str]=None
    case_material:Optional[str]=None
    water_resistance:Optional[str]=None
    weight:Optional[str]=None
    warranty_month:int=12
    always_display:int=0
    brightness_nits:Optional[int]=None


    @field_validator("title")
    @classmethod
    def title_length(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("Title must be at least 2 characters.")
        
        if len(v) > 255:
            raise ValueError("Title cannot exceed 255 characters.")
        
        return v


    @field_validator("product_no")
    @classmethod
    def product_no_format(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("Product number too short.")
        
        return v.upper()


    @field_validator("base_price","sale_price")
    @classmethod
    def price_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError("Price cannot be negative.")
        
        return v


    @field_validator("sale_price",mode="before")
    @classmethod
    def sale_price_optional(cls, v):
        if v=="" or v is None:
            return None

        return v


    @field_validator("stock")
    @classmethod
    def stock_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Stock cannot be negative.")
        
        return v


    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        allowed={"active","draft","archived"}
        if v not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        
        return v


    @field_validator("category_id")
    @classmethod
    def category_positive(cls,v: int) -> int:
        if v <= 0:
            raise ValueError("Invalid category selected.")
        
        return v




class CategoryValidator(BaseValidator):
    name:str
    description:Optional[str]=None
    is_active:int=1


    @field_validator("name")
    @classmethod
    def name_length(cls,v: str) -> str:
        if len(v) < 2:
            raise ValueError("Category name must be at least 2 characters.")

        if len(v) > 100:
            raise ValueError("Category name cannot exceed 100 characters.")

        return v


    @field_validator("is_active")
    @classmethod
    def valid_active(cls, v) -> int:
        return int(v)




class OrderStatusValidator(BaseValidator):
    status:str

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        allowed={"pending","confirmed","shipped","delivered"}
        if v not in allowed:
            raise ValueError(f"Invalid order status: {v}")
        
        return v



class AdminProfileValidator(BaseValidator):

    first_name:str
    last_name:str
    username:str
    email:EmailStr

    @field_validator("first_name","last_name")
    @classmethod
    def names_alpha(cls, v: str) -> str:
        if not v.replace(" ","").isalpha():
            raise ValueError("Must contain letters only.")
        return v.title()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if not v.replace("_","").replace("-","").isalnum():
            raise ValueError("Username can only contain letters, numbers, _ and -")
        return v.lower()



class AdminResetEmailValidator(BaseValidator):

    email:EmailStr

    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.lower()



class AdminOTPVerifyValidator(BaseValidator):

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



class AdminNewPasswordValidator(BaseValidator):

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



class ReviewStatusValidator(BaseValidator):

    status:str

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        allowed={"approved","hidden","pending"}
        if v not in allowed:
            raise ValueError(f"Invalid review status. Must be one of: {', '.join(allowed)}")
        return v