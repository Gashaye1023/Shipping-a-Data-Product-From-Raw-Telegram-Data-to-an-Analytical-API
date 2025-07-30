from pydantic import BaseModel
from typing import List, Optional

# Base model for Item
class ItemBase(BaseModel):
    name: str
    description: str

# Model for creating a new Item
class ItemCreate(ItemBase):
    pass

# Model representing an Item with an ID
class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True

# Model for product mentions in messages
class ProductMention(BaseModel):
    detected_object_class: str
    count: int

# Model for channel activity
class ChannelActivity(BaseModel):
    date: str
    message_count: int

# Model for search results of messages
class MessageSearchResult(BaseModel):
    message_id: int
    channel_name: str
    message_text: str
    detection: Optional[str] = None

# Response model for report containing top products
class ReportResponse(BaseModel):
    top_products: List[ProductMention]

# Response model for channel activity
class ChannelActivityResponse(BaseModel):
    channel_name: str
    activity: List[ChannelActivity]

# Response model for search results
class SearchResponse(BaseModel):
    messages: List[MessageSearchResult]