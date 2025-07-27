from pydantic import BaseModel, EmailStr

class RegisterUser(BaseModel):
    email: EmailStr
    password: str
    company_name: str
    contact_number: str
    location: str

class LoginUser(BaseModel):
    email: EmailStr
    password: str
