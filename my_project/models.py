from sqlalchemy import Column, Integer, String
from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)

# Simple models for reference, not directly used with Pydantic
class Message:
    def __init__(self, message_id: int, channel_name: str, message_text: str):
        self.message_id = message_id
        self.channel_name = channel_name
        self.message_text = message_text

class Detection:
    def __init__(self, message_id: int, detected_object_class: str, confidence_score: float):
        self.message_id = message_id
        self.detected_object_class = detected_object_class
        self.confidence_score = confidence_score