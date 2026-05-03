import json
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    checkins = relationship("CheckIn", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    energy_level = Column(Integer, nullable=False)  # 1-5
    focus_level = Column(Integer, nullable=True)     # 1-5, optional
    activity = Column(String(50), nullable=False)
    emotions = Column(Text, nullable=True)  # JSON string: ["motivated", "calm"]
    note = Column(String(200), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="checkins")

    @property
    def emotions_list(self) -> list[str]:
        """Parse the JSON emotions string into a list."""
        if self.emotions:
            try:
                return json.loads(self.emotions)
            except json.JSONDecodeError:
                return []
        return []

    @emotions_list.setter
    def emotions_list(self, value: list[str]):
        """Set emotions as a JSON string."""
        self.emotions = json.dumps(value) if value else None

    def __repr__(self):
        return f"<CheckIn(id={self.id}, energy={self.energy_level}, activity='{self.activity}')>"
