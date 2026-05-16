# Tasks are defined in celery_app.py
# This file is kept for organization purposes
from device_data_service.celery_app import analyze_device_task, generate_report_task

__all__ = ["analyze_device_task", "generate_report_task"]
