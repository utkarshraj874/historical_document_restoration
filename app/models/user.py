from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base

class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(primary_key=True, index = True)
    email:Mapped[str] = mapped_column(String, unique = True , nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False) 




