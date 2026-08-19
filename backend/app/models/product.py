from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    brand = Column(String(100), nullable=True)
    price = Column(Float, nullable=False)
    size = Column(String(50), nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)
    season = Column(String(50), nullable=True)
    # JSON list of substitute product names or IDs
    substitutes = Column(JSON, nullable=True, default=list)
