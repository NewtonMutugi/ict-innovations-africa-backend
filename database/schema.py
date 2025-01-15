from sqlalchemy import Boolean, Column, String, Float, DateTime, Integer, ForeignKey, Table
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


class HostingPayment(Base):
    __tablename__ = 'hosting_payments'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    hosting_plan_id = Column(Integer, ForeignKey('hosting_plans.id'))
    status = Column(String, nullable=False)
    paymentReference = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    hosting_plan = relationship('HostingPlans', back_populates='hosting_payments')


class HostingPlans(Base):
    __tablename__ = 'hosting_plans'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    monthly_price = Column(Float, nullable=False)
    annual_price = Column(Float, nullable=False)
    subtitle = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class HostingPlanFeatures(Base):
    __tablename__ = 'hosting_plan_features'

    id = Column(Integer, primary_key=True, index=True)
    feature = Column(String, nullable=False)
    hosting_plan_id = Column(Integer, ForeignKey('hosting_plans.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    hosting_plan = relationship(
        'HostingPlans', back_populates='hosting_plan_features')


class ContactForm(Base):
    __tablename__ = 'webGenerator_contact_form'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# Many-to-many relationship tab;e
event_tag_table = Table(
    'event_tag', Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    paragraph = Column(String, nullable=False)
    image = Column(String, nullable=False)
    venue = Column(String, nullable=False)
    type = Column(String, nullable=False)
    eventDate = Column(String, nullable=False)
    description = Column(String, nullable=False)

    registrationLink = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    tags = relationship('Tag', secondary=event_tag_table,
                        back_populates='events')
    eventImages = relationship('EventImages', back_populates='event')


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    tagName = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    events = relationship(
        'Event', secondary=event_tag_table, back_populates='tags')


class EventImages(Base):
    __tablename__ = 'eventImages'

    id = Column(Integer, primary_key=True, index=True)
    imageTitle = Column(String, nullable=False)
    imageUrl = Column(String, nullable=False)
    imageDescription = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    event_id = Column(Integer, ForeignKey('events.id'))

    event = relationship('Event', back_populates='eventImages')


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


# Create tables if they do not exist
Base.metadata.create_all(engine)
