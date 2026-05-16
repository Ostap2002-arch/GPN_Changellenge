from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from device_data_service.models import Device, DeviceReading, User
from device_data_service.schemas import AnalysisResult
import numpy as np


class StatisticsAnalyzer:
    """Service for analyzing device statistics"""
    
    @staticmethod
    def calculate_analysis(values: List[float]) -> AnalysisResult:
        """Calculate statistical analysis for values"""
        if not values:
            return AnalysisResult(
                min=0,
                max=0,
                count=0,
                sum=0,
                median=0,
                mean=0
            )
        
        arr = np.array(values)
        return AnalysisResult(
            min=float(np.min(arr)),
            max=float(np.max(arr)),
            count=len(arr),
            sum=float(np.sum(arr)),
            median=float(np.median(arr)),
            mean=float(np.mean(arr))
        )


class DeviceService:
    """Service for managing devices"""
    
    @staticmethod
    def create_device(db: Session, device_id: str, name: str, user_id: Optional[int] = None) -> Device:
        """Create a new device"""
        db_device = Device(device_id=device_id, name=name, user_id=user_id)
        db.add(db_device)
        db.commit()
        db.refresh(db_device)
        return db_device
    
    @staticmethod
    def get_device_by_id(db: Session, device_id: str) -> Optional[Device]:
        """Get device by device_id"""
        return db.query(Device).filter(Device.device_id == device_id).first()
    
    @staticmethod
    def get_all_devices(db: Session) -> List[Device]:
        """Get all devices"""
        return db.query(Device).all()
    
    @staticmethod
    def delete_device(db: Session, device_id_str: str) -> bool:
        """Delete device by device_id"""
        device = DeviceService.get_device_by_id(db, device_id_str)
        if device:
            db.delete(device)
            db.commit()
            return True
        return False


class ReadingService:
    """Service for managing device readings"""
    
    @staticmethod
    def save_reading(db: Session, device_id_str: str, x: float, y: float, z: float) -> DeviceReading:
        """Save a device reading"""
        device = DeviceService.get_device_by_id(db, device_id_str)
        if not device:
            device = DeviceService.create_device(db, device_id_str, f"Device {device_id_str}")
        
        reading = DeviceReading(device_id=device.id, x=x, y=y, z=z)
        db.add(reading)
        db.commit()
        db.refresh(reading)
        return reading
    
    @staticmethod
    def get_readings(
        db: Session,
        device_id_str: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 1000
    ) -> List[DeviceReading]:
        """Get readings for a device within optional time range (with pagination)"""
        device = DeviceService.get_device_by_id(db, device_id_str)
        if not device:
            return []
        
        query = db.query(DeviceReading).filter(DeviceReading.device_id == device.id)
        
        if start_time:
            query = query.filter(DeviceReading.timestamp >= start_time)
        if end_time:
            query = query.filter(DeviceReading.timestamp <= end_time)
        
        # Sort by timestamp descending for consistent results, then apply pagination
        query = query.order_by(DeviceReading.timestamp.desc()).offset(skip).limit(limit)
        return query.all()
    
    @staticmethod
    def get_readings_by_device_internal_id(
        db: Session,
        device_pk_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[DeviceReading]:
        """Get readings for a device by internal ID"""
        query = db.query(DeviceReading).filter(DeviceReading.device_id == device_pk_id)
        
        if start_time:
            query = query.filter(DeviceReading.timestamp >= start_time)
        if end_time:
            query = query.filter(DeviceReading.timestamp <= end_time)
        
        return query.all()


class AnalysisService:
    """Service for analyzing device data"""
    
    @staticmethod
    def analyze_device(
        db: Session,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Analyze device readings"""
        # Use DB-side aggregations to avoid loading large result sets into memory
        device = DeviceService.get_device_by_id(db, device_id)
        if not device:
            return {
                "device_id": device_id,
                "analysis_x": AnalysisResult(min=0, max=0, count=0, sum=0, median=0, mean=0).dict(),
                "analysis_y": AnalysisResult(min=0, max=0, count=0, sum=0, median=0, mean=0).dict(),
                "analysis_z": AnalysisResult(min=0, max=0, count=0, sum=0, median=0, mean=0).dict(),
            }

        def _apply_time_filters(query):
            if start_time:
                query = query.filter(DeviceReading.timestamp >= start_time)
            if end_time:
                query = query.filter(DeviceReading.timestamp <= end_time)
            return query

        # helper to compute aggregates for one axis
        def _axis_aggregates(column):
            q = db.query(
                func.count(column),
                func.min(column),
                func.max(column),
                func.sum(column),
                func.avg(column),
            ).filter(DeviceReading.device_id == device.id)
            q = _apply_time_filters(q)
            count_val, min_val, max_val, sum_val, avg_val = q.one()

            if not count_val or count_val == 0:
                return AnalysisResult(min=0, max=0, count=0, sum=0, median=0, mean=0)

            # compute median with offset query to avoid materializing full list
            median_val = None
            try:
                offset = int(count_val) // 2
                med_q = db.query(column).filter(DeviceReading.device_id == device.id)
                med_q = _apply_time_filters(med_q)
                med_q = med_q.order_by(column)
                median_val = med_q.offset(offset).limit(1).scalar()
            except Exception:
                median_val = None

            return AnalysisResult(
                min=float(min_val) if min_val is not None else 0,
                max=float(max_val) if max_val is not None else 0,
                count=int(count_val),
                sum=float(sum_val) if sum_val is not None else 0,
                median=float(median_val) if median_val is not None else 0,
                mean=float(avg_val) if avg_val is not None else 0,
            )

        analysis_x = _axis_aggregates(DeviceReading.x)
        analysis_y = _axis_aggregates(DeviceReading.y)
        analysis_z = _axis_aggregates(DeviceReading.z)

        return {
            "device_id": device_id,
            "analysis_x": analysis_x.dict(),
            "analysis_y": analysis_y.dict(),
            "analysis_z": analysis_z.dict(),
            "period_start": start_time,
            "period_end": end_time,
        }
    
    @staticmethod
    def analyze_user_devices(
        db: Session,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Analyze all devices for a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"devices": [], "error": "User not found"}

        devices_analysis = []
        total_x_count = total_y_count = total_z_count = 0
        total_x_sum = total_y_sum = total_z_sum = 0.0

        def _apply_time_filters(query):
            if start_time:
                query = query.filter(DeviceReading.timestamp >= start_time)
            if end_time:
                query = query.filter(DeviceReading.timestamp <= end_time)
            return query

        for device in user.devices:
            # aggregates per device using DB queries
            def _device_axis_agg(column):
                q = db.query(
                    func.count(column), func.min(column), func.max(column), func.sum(column), func.avg(column)
                ).filter(DeviceReading.device_id == device.id)
                q = _apply_time_filters(q)
                count_val, min_val, max_val, sum_val, avg_val = q.one()
                if not count_val or count_val == 0:
                    return None

                # median
                try:
                    offset = int(count_val) // 2
                    med_q = db.query(column).filter(DeviceReading.device_id == device.id)
                    med_q = _apply_time_filters(med_q)
                    med_q = med_q.order_by(column)
                    median_val = med_q.offset(offset).limit(1).scalar()
                except Exception:
                    median_val = None

                return AnalysisResult(
                    min=float(min_val) if min_val is not None else 0,
                    max=float(max_val) if max_val is not None else 0,
                    count=int(count_val),
                    sum=float(sum_val) if sum_val is not None else 0,
                    median=float(median_val) if median_val is not None else 0,
                    mean=float(avg_val) if avg_val is not None else 0,
                )

            ax = _device_axis_agg(DeviceReading.x)
            ay = _device_axis_agg(DeviceReading.y)
            az = _device_axis_agg(DeviceReading.z)

            if ax or ay or az:
                devices_analysis.append({
                    "device_id": device.device_id,
                    "analysis_x": ax.dict() if ax else AnalysisResult(min=0, max=0, count=0, sum=0, median=0, mean=0).dict(),
                    "analysis_y": ay.dict() if ay else AnalysisResult(min=0, max=0, count=0, sum=0, median=0, mean=0).dict(),
                    "analysis_z": az.dict() if az else AnalysisResult(min=0, max=0, count=0, sum=0, median=0, mean=0).dict(),
                    "period_start": start_time,
                    "period_end": end_time,
                })

                if ax:
                    total_x_count += ax.count
                    total_x_sum += ax.sum
                if ay:
                    total_y_count += ay.count
                    total_y_sum += ay.sum
                if az:
                    total_z_count += az.count
                    total_z_sum += az.sum

        total_analysis_x = StatisticsAnalyzer.calculate_analysis([ ]) if total_x_count == 0 else AnalysisResult(min=0, max=0, count=total_x_count, sum=total_x_sum, median=0, mean=(total_x_sum/total_x_count if total_x_count else 0)).dict()
        total_analysis_y = StatisticsAnalyzer.calculate_analysis([ ]) if total_y_count == 0 else AnalysisResult(min=0, max=0, count=total_y_count, sum=total_y_sum, median=0, mean=(total_y_sum/total_y_count if total_y_count else 0)).dict()
        total_analysis_z = StatisticsAnalyzer.calculate_analysis([ ]) if total_z_count == 0 else AnalysisResult(min=0, max=0, count=total_z_count, sum=total_z_sum, median=0, mean=(total_z_sum/total_z_count if total_z_count else 0)).dict()

        return {
            "devices": devices_analysis,
            "total_analysis_x": total_analysis_x,
            "total_analysis_y": total_analysis_y,
            "total_analysis_z": total_analysis_z,
            "period_start": start_time,
            "period_end": end_time,
        }


class UserService:
    """Service for managing users"""
    
    @staticmethod
    def create_user(db: Session, username: str, email: str) -> User:
        """Create a new user"""
        db_user = User(username=username, email=email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
