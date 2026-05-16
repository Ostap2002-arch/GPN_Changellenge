from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class DeviceReadingCreate(BaseModel):
    """Schema for creating device reading"""
    x: float
    y: float
    z: float


class DeviceReadingResponse(BaseModel):
    """Schema for device reading response"""
    id: int
    device_id: int
    x: float
    y: float
    z: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AnalysisResult(BaseModel):
    """Schema for analysis results"""
    min: float
    max: float
    count: int
    sum: float
    median: float
    mean: float


class AnalysisResponse(BaseModel):
    """Schema for analysis response"""
    device_id: str
    analysis_x: AnalysisResult
    analysis_y: AnalysisResult
    analysis_z: AnalysisResult
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class AggregatedAnalysisResponse(BaseModel):
    """Schema for aggregated analysis"""
    devices: List[AnalysisResponse]
    total_analysis_x: AnalysisResult
    total_analysis_y: AnalysisResult
    total_analysis_z: AnalysisResult


class TaskResponse(BaseModel):
    """Schema for async task response"""
    task_id: str
    status: str


class DeviceCreate(BaseModel):
    """Schema for creating device"""
    device_id: str
    name: str


class DeviceResponse(BaseModel):
    """Schema for device response"""
    id: int
    device_id: str
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Schema for creating user"""
    username: str
    email: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True
