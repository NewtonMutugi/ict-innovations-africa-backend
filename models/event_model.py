from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# EventImages model
class EventImageBase(BaseModel):
    imageUrl: str
    imageDescription: str
    imageTitle: str


class EventImageCreate(EventImageBase):
    pass


class EventImageResponse(EventImageBase):
    id: int
    event_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Tag Model
class TagBase(BaseModel):
    tagName: str


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int

    class Config:
        orm_mode = True


# Event Model
class EventBase(BaseModel):
    title: str
    paragraph: str
    image: str
    venue: str
    type: str
    eventDate: str
    description: str
    registrationLink: str


class EventCreate(EventBase):
    tags: List[TagCreate]
    eventImages: Optional[List[EventImageCreate]] = None


class EventResponse(BaseModel):
    id: int
    title: str
    paragraph: str
    image: str
    venue: str
    type: str
    eventDate: str
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse]
    eventImages: List[EventImageResponse]

    class Config:
        orm_mode = True


# Pydantic schema for partial updates
class EventUpdateRequest(BaseModel):
    title: Optional[str] = None
    paragraph: Optional[str] = None
    image: Optional[str] = None
    venue: Optional[str] = None
    type: Optional[str] = None
    eventDate: Optional[str] = None
    description: Optional[str] = None
    registrationLink: Optional[str] = None
