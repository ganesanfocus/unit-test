from pydantic import BaseModel, EmailStr

class EmployeeCreate(BaseModel):
    fullname: str
    email: EmailStr
    mobile: str
    department: str
    designation: str
    city: str

class EmployeeUpdate(BaseModel):
    fullname: str
    email: EmailStr
    mobile: str
    department: str
    designation: str
    city: str

class EmployeeResponse(BaseModel):
    emp_id: int
    fullname: str
    email: str
    mobile: str
    department: str
    designation: str
    city: str
    created_at: str
    updated_at: str
