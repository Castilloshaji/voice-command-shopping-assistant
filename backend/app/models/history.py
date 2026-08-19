from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class ShoppingHistory(Base):
    __tablename__ = "shopping_history"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True)
    quantity = Column(Float, default=1.0, nullable=False)
    purchased_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
