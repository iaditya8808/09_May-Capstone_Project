from pydantic import BaseModel, EmailStr

class Book(BaseModel):
    title: str
    author: str
    isbn: str
    category: str
    total_copies: int
    available_copies: int

class Member(BaseModel):
    name: str
    email: EmailStr
    course: str

class Borrow(BaseModel):
    member_name: str
    book_title: str

class User(BaseModel):
    username: str
    password: str