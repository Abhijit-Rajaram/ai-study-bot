from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine("sqlite:///studybot.db", echo=False)  # SQLite database
SessionLocal = sessionmaker(bind=engine)

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    reply = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)
