from pathlib import Path
from fastapi.responses import FileResponse
from json import JSONDecodeError, loads
import os
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from auth.dependancies import get_current_user
from database.schema import Event, EventImages, Tag, User
from database.database import SessionLocal
from models.event_model import EventCreate, EventImageResponse, EventResponse, EventUpdateRequest, TagResponse

# Upload directory for event images
UPLOAD_DIR = "uploads/events"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


# @router.post("/event", response_model=EventResponse)
# def create_event(event: EventCreate, db: Session = Depends(get_db)):
#     """ Create event """
#     db_event = Event(title=event.title, paragraph=event.paragraph, type=event.type,
#                      image=event.image, venue=event.venue, eventDate=event.eventDate, description=event.description, registrationLink=event.registrationLink)
#     db.add(db_event)
#     db.commit()
#     db.refresh(db_event)

#     # Create Tags
#     for tag in event.tags:
#         db_tag = db.query(Tag).filter(Tag.tagName == tag.tagName).first()
#         if not db_tag:
#             db_tag = Tag(tagName=tag.tagName)
#             db.add(db_tag)
#         db_event.tags.append(db_tag)

#     # Create Event Images
#     for image in event.eventImages:
#         db_image = EventImages(imageUrl=image.imageUrl,
#                                imageDescription=image.imageDescription, imageTitle=image.imageTitle, event=db_event)
#         db.add(db_image)

#     db.commit()
#     db.refresh(db_event)
#     return db_event

@router.post("/event", response_model=EventResponse, status_code=201)
async def create_event(
    event: str = File(...),  # JSON payload as a string
    images: List[UploadFile] = File(...),  # File uploads
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Parse the JSON string into the EventCreate Pydantic model
    try:
        event_data = loads(event)
        event_obj = EventCreate(**event_data)
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

     # Ensure the image field is present
    if 'image' not in event_data:
        raise HTTPException(status_code=400, detail="Image field is required")

     # Save Event Images
    for image in images:
        if image.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Invalid file type")
    # Save event details
    event_date = "TBA" if event_obj.eventDate is None else event_obj.eventDate
    db_event = Event(
        title=event_obj.title,
        paragraph=event_obj.paragraph,
        image=event_obj.image,
        venue=event_obj.venue,
        type=event_obj.type,
        eventDate=event_date,
        description=event_obj.description,
        registrationLink=event_obj.registrationLink
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Create Tags
    for tag in event_obj.tags:
        db_tag = db.query(Tag).filter(Tag.tagName == tag.tagName).first()
        if not db_tag:
            db_tag = Tag(tagName=tag.tagName)
            db.add(db_tag)
        db_event.tags.append(db_tag)

    image_data = []
    # Save Event Images
    for image in images:
        if image.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Save file to the upload directory
        file_path = os.path.join(UPLOAD_DIR, f"event_{db_event.id}_{image.filename}")
        with open(file_path, "wb") as f:
            content = await image.read()
            f.write(content)

        # Get the image description and image title from the request body
        image_data = event_obj.eventImages[images.index(image)]

        # Create EventImages record
        db_image = EventImages(
            imageUrl=file_path,
            imageDescription=image_data.imageDescription,
            imageTitle=image_data.imageTitle,
            event=db_event
        )
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
def update_event(event_id: int, event: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
    db_event.eventDate = event.eventDate = "TBA" if event.eventDate is None else event.eventDate
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
def delete_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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


@router.get("/event/{event_id}/images", response_model=List[EventImageResponse])
def get_event_images(event_id: int, db: Session = Depends(get_db)):
    """Get all images for a specific event."""
    images = db.query(EventImages).filter(
        EventImages.event_id == event_id).all()
    if not images:
        raise HTTPException(
            status_code=404, detail="No images found for this event")
    return images


@router.delete("/event/{event_id}/images/{image_id}")
def delete_event_image(event_id: int, image_id: int, db: Session = Depends(get_db)):
    """Delete a specific image from an event."""
    image = db.query(EventImages).filter(EventImages.id ==
                                         image_id, EventImages.event_id == event_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Delete file from the filesystem
    image_path = Path(image.imageUrl)
    if image_path.exists():
        image_path.unlink()

    # Delete the database record
    db.delete(image)
    db.commit()
    return {"message": "Image deleted successfully"}


@router.put("/event/{event_id}/images")
async def update_event_images(
    event_id: int,
    new_images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Replace all images for a specific event."""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Delete existing images
    existing_images = db.query(EventImages).filter(
        EventImages.event_id == event_id).all()
    for image in existing_images:
        image_path = Path(image.imageUrl)
        if image_path.exists():
            image_path.unlink()
        db.delete(image)

    # Add new images
    for image in new_images:
        if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Save file to the upload directory
        file_path = os.path.join(UPLOAD_DIR, f"event_{event_id}_{image.filename}")
        with open(file_path, "wb") as f:
            content = await image.read()
            f.write(content)

        # Create new EventImages record
        db_image = EventImages(
            imageUrl=file_path,
            imageDescription="Updated event image",
            imageTitle=image.filename,
            event=db_event
        )
        db.add(db_image)

    db.commit()
    return {"message": "Event images updated successfully"}


@router.get("/event-images/{image_id}/file", response_class=FileResponse)
def download_event_image(image_id: int, db: Session = Depends(get_db)):
    """Download a specific image file by image ID."""
    image = db.query(EventImages).filter(EventImages.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = Path(image.imageUrl)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="application/octet-stream", filename=file_path.name)
