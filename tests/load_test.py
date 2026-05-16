from locust import HttpUser, task, between, TaskSet, events
from datetime import datetime, timedelta
import json
import random
import time
import statistics


class DeviceAPITasks(TaskSet):
    """Load testing tasks for device API"""
    
    def on_start(self):
        """Setup before task execution"""
        self.device_id = f"device_{random.randint(1, 100)}"
        self.user_id = None
    
    @task(5)
    def add_device_reading(self):
        """Task: Add device reading"""
        data = {
            "x": random.uniform(-100, 100),
            "y": random.uniform(-100, 100),
            "z": random.uniform(-100, 100)
        }
        self.client.post(
            f"/devices/{self.device_id}/readings",
            json=data
        )
    
    @task(3)
    def get_device_readings(self):
        """Task: Get device readings"""
        self.client.get(f"/devices/{self.device_id}/readings")
    
    @task(4)
    def analyze_device_all_time(self):
        """Task: Analyze device (all time)"""
        self.client.get(f"/analysis/device/{self.device_id}")
    
    @task(3)
    def analyze_device_last_24h(self):
        """Task: Analyze device (last 24h)"""
        self.client.get(f"/analysis/device/{self.device_id}/last-24h")
    
    @task(2)
    def analyze_device_last_7d(self):
        """Task: Analyze device (last 7d)"""
        self.client.get(f"/analysis/device/{self.device_id}/last-7d")
    
    @task(2)
    def create_device(self):
        """Task: Create device"""
        device_id = f"device_{int(time.time())}_{random.randint(1, 1000)}"
        data = {
            "device_id": device_id,
            "name": f"Test Device {device_id}"
        }
        response = self.client.post("/devices", json=data)
        if response.status_code == 200:
            self.device_id = device_id
    
    @task(1)
    def list_devices(self):
        """Task: List all devices"""
        self.client.get("/devices")
    
    @task(1)
    def get_single_device(self):
        """Task: Get single device"""
        self.client.get(f"/devices/{self.device_id}")
    
    @task(2)
    def create_user(self):
        """Task: Create user"""
        username = f"user_{int(time.time())}_{random.randint(1, 10000)}"
        data = {
            "username": username,
            "email": f"{username}@example.com"
        }
        response = self.client.post("/users", json=data)
        if response.status_code == 200:
            self.user_id = response.json().get("id")
    
    @task(1)
    def health_check(self):
        """Task: Health check"""
        self.client.get("/health")


class DeviceAPIUser(HttpUser):
    """Load test user for device API"""
    tasks = [DeviceAPITasks]
    wait_time = between(0.5, 2.0)  # Random wait between 0.5s and 2s


# Statistics collector
response_times = []
request_count = 0
error_count = 0


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Collect request statistics"""
    global response_times, request_count, error_count
    response_times.append(response_time)
    request_count += 1
    if exception:
        error_count += 1


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print test statistics"""
    print("\n" + "="*50)
    print("Load Test Results Summary")
    print("="*50)
    print(f"Total Requests: {request_count}")
    print(f"Total Errors: {error_count}")
    print(f"Error Rate: {(error_count/request_count*100):.2f}%")
    
    if response_times:
        print(f"\nResponse Time Statistics (ms):")
        print(f"  Min: {min(response_times):.2f}")
        print(f"  Max: {max(response_times):.2f}")
        print(f"  Avg: {statistics.mean(response_times):.2f}")
        print(f"  Median: {statistics.median(response_times):.2f}")
        if len(response_times) > 1:
            print(f"  StdDev: {statistics.stdev(response_times):.2f}")
        
        percentiles = [50, 90, 95, 99]
        sorted_times = sorted(response_times)
        for p in percentiles:
            idx = int(len(sorted_times) * p / 100)
            print(f"  P{p}: {sorted_times[idx]:.2f}")
    
    print("="*50 + "\n")
