from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base
from database.database import engine


class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    country = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    paymentReference = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ContactForm(Base):
    __tablename__ = 'webGenerator_contact_form'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# Many-to-many relationship tab;e
event_tags = Table(
    'events_tags',
    Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id')),
    Column('tag_id', Integer, ForeignKey('eventTags.id'))
)


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    paragraph = Column(String, nullable=False)
    image = Column(String, nullable=False)
    venue = Column(String, nullable=False)
    type = Column(String, nullable=False)
    tags = relationship("Tag", secondary=event_tags,
                        back_populates='events')  # Many-to-many relationship
    eventDate = Column(String, nullable=False)
    description = Column(String, nullable=False)
    eventImages = relationship(
        'EventImages', back_populates='event')
    registrationLink = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class EventImages(Base):
    __tablename__ = 'eventImages'

    id = Column(Integer, primary_key=True, index=True)
    imageUrl = Column(String, nullable=False)
    imageDescription = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    event_id = Column(Integer, ForeignKey('events.id')
                      )  # Foreign key to events table
    event = relationship('Event', back_populates='eventImages')


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    tagName = Column(String, nullable=False)
    event = relationship("Event", secondary=event_tags, back_populates="tags")


# Create tables if they do not exist
Base.metadata.create_all(engine)
