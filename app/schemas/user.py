from pydantic import BaseModel, constr

class Usercreate(BaseModel):
    email:str
    password:str

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True