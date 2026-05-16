from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from device_data_service.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    
    # Relationships
    devices = relationship("Device", back_populates="user")


class Device(Base):
    """Device model"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="devices")
    readings = relationship("DeviceReading", back_populates="device", cascade="all, delete-orphan")


class DeviceReading(Base):
    """Device reading/statistic model"""
    __tablename__ = "device_readings"
    __table_args__ = (
        Index("idx_device_id_timestamp", "device_id", "timestamp"),
        Index("idx_timestamp", "timestamp"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), index=True)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    device = relationship("Device", back_populates="readings")
