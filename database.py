from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Initialize the SQLite database
DATABASE_URL = "sqlite:///.knowledge_ai.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# Define the Conversation model
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=True)
    question = Column(String, nullable=True)
    query_question = Column(String, nullable=True)
    answer = Column(Text, nullable=True)
    request_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


# Create the table
Base.metadata.create_all(engine)


# Function to add a new conversation
def add_conversation(request_id, user_id, question, query_question=None, answer=None):
    session = SessionLocal()
    conversation = Conversation(
        user_id=user_id,
        question=question,
        query_question=query_question,
        answer=answer,
        request_id=request_id,
    )
    session.add(conversation)
    session.commit()
    session.close()


# Function to update an existing conversation by request_id
def update_conversation(request_id, new_answer):
    session = SessionLocal()
    conversation = session.query(Conversation).filter_by(request_id=request_id).first()
    if conversation:
        conversation.answer = new_answer
        conversation.created_at = datetime.now()  # Update timestamp if needed
        session.commit()
    else:
        print("Request ID not found.")
    session.close()
