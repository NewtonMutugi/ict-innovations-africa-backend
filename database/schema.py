from sqlalchemy import Column, String, Float, DateTime, Integer
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


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    paragraph = Column(String, nullable=False)
    image = Column(String, nullable=False)
    venue = Column(String, nullable=False)
    type = Column(String, nullable=False)
    tags = Column(String, nullable=False)
    eventDate = Column(String, nullable=False)
    description = Column(String, nullable=False)
    eventImages = Column(String, nullable=False)
    registrationLink = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    

# {
#     id: 1,
#     title: "Preparing the Youth for the Future",
#     paragraph:
#     "Join us in an insightful session designed to empower and guide young leaders on using technology and becoming early adopters.",
#     image: "/images/events/monetize_ai.jpg",
#     venue: {
#         name: "Online",
#         image: "/images/blog/author-01.png",
#         designation: "Graphic Designer",
#     },
#     type: "online",
#     tags: ["AI Monetization", "technology", "future"],
#     eventDate: "To be Announced",
#     description:
#     "This session will equip participants with actionable strategies to navigate career path selection and cultivate life skills essential for professional and personal growth.<br />Participants will learn how to leverage AI for creating dynamic presentations, summarizing complex content, and extracting key insights from documents, including PDFs and YouTube videos. Discover how these tools can make learning more efficient and engaging.<br />We’ll also explore the monetization of AI, offering insights on how to capitalize on AI as early adopters, including creating visually stunning websites through AI-driven solutions.",
#     eventImages: [
#         {
#           image: "/images/events/enhancinglearningwithAI.jpg",

#           imageTitle: "Enhancing Learning with AI",
#           imageDescription:
#           "Streamline your studies with AI tools that make content accessible, engaging, and easy to manage.",
#         },
#         {
#             image: "/images/events/monetize_ai.jpg",
#             imageTitle: "Monetizing AI",
#             imageDescription:
#             "Discover how to create visually stunning websites through AI-driven solutions.",
#         },
#     ],
#     registrationLink: "https://forms.gle/QwHoJ7adbv1vJzDk9",
# },
# Create tables if they do not exist
Base.metadata.create_all(engine)
