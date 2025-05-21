from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class LostPetReport(BaseModel):
    pet_id: int
    location: str
    last_seen: datetime
    description: str
class FoundPetReport(BaseModel):
    pet_id: int
    found_location: str
    found_date: datetime
    description: str
