from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.schema import Event, EventImages, Tag
from database.database import SessionLocal
from models.event_model import EventCreate, EventImageResponse, EventResponse, EventUpdateRequest, TagResponse


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.post("/event", response_model=EventResponse)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """ Create event """
    db_event = Event(title=event.title, paragraph=event.paragraph, type=event.type,
                     image=event.image, venue=event.venue, eventDate=event.eventDate, description=event.description, registrationLink=event.registrationLink)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Create Tags
    for tag in event.tags:
        db_tag = db.query(Tag).filter(Tag.tagName == tag.tagName).first()
        if not db_tag:
            db_tag = Tag(tagName=tag.tagName)
            db.add(db_tag)
        db_event.tags.append(db_tag)

    # Create Event Images
    for image in event.eventImages:
        db_image = EventImages(imageUrl=image.imageUrl,
                               imageDescription=image.imageDescription, imageTitle=image.imageTitle, event=db_event)
        db.add(db_image)

    db.commit()
    db.refresh(db_event)
    return db_event


@router.get("/events", response_model=List[EventResponse])
def get_all_events(db: Session = Depends(get_db)):
    """ Get all events"""
    events = db.query(Event).all()
    return events


@router.get("/event/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """ Get single event """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/event/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event: EventCreate, db: Session = Depends(get_db)):
    """ Update event """
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Update event details
    db_event.title = event.title
    db_event.paragraph = event.paragraph
    db_event.image = event.image
    db_event.venue = event.venue
    db_event.type = event.type
    db_event.eventDate = event.eventDate
    db_event.description = event.description
    db_event.registrationLink = event.registrationLink

    # Update Tags
    db_event.tags = []
    for tag in event.tags:
        db_tag = db.query(Tag).filter(Tag.tagName == tag.tagName).first()
        if not db_tag:
            db_tag = Tag(tagName=tag.tagName)
            db.add(db_tag)
        db_event.tags.append(db_tag)

    # Update Event images
    db.query(EventImages).filter(EventImages.event_id == event_id).delete()
    for image in event.eventImages:
        db_image = EventImages(
            imageUrl=image.imageUrl,
            imageDescription=image.imageDescription,
            event=db_event
        )
        db.add(db_image)

    db.commit()
    db.refresh(db_event)
    return db_event


@router.delete("/event/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """ Delete event """
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(db_event)
    db.commit()
    return {"message": "Event deleted successfully"}


@router.get("/tags", response_model=List[TagResponse])
def get_all_tags(db: Session = Depends(get_db)):
    """ Get all tags """
    tags = db.query(Tag).all()
    return tags


@router.get("/event-images", response_model=List[EventImageResponse])
def get_all_events(db: Session = Depends(get_db)):
    """ Get all images """
    event_images = db.query(EventImages).all()
    return event_images


@router.patch("/events/{event_id}")
def update_event_partial(event_id: int, update_data: EventUpdateRequest, db: Session = Depends(get_db)):
    # Find the event by ID
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Update only the fields provided in the request
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(event, key, value)

    # Save changes
    db.commit()
    db.refresh(event)
    return event
