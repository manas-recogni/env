#!/usr/bin/env python3
"""
GCloud Instance Management Module

Handles all Google Cloud Compute Engine instance operations including
status checking, starting instances, and waiting for readiness.
"""

import subprocess
import time
from typing import Optional


class GCloudManager:
    """Manages Google Cloud Compute Engine instances."""
    
    def __init__(self, project_id: str = "software-265220", zone: str = "us-central1-a"):
        self.project_id = project_id
        self.zone = zone
    
    def check_instance_status(self, instance_name: str) -> str:
        """Check the status of a gcloud instance using gcloud API."""
        try:
            cmd = [
                "gcloud", "compute", "instances", "describe",
                f"{instance_name}",
                f"--project={self.project_id}",
                f"--zone={self.zone}",
                "--format=value(status)"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "UNKNOWN"
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return "UNKNOWN"
    
    def start_instance(self, instance_name: str) -> bool:
        """Start a gcloud compute instance."""
        print(f"Starting gcloud instance: {instance_name}")
        
        try:
            cmd = [
                "gcloud", "compute", "instances", "start",
                f"--project={self.project_id}",
                f"--zone={self.zone}",
                instance_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Successfully started instance: {instance_name}")
                return True
            else:
                print(f"Failed to start instance: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("Error: gcloud CLI not found. Please install Google Cloud SDK.")
            return False
    
    def wait_for_instance_ready(self, instance_name: str, max_wait_time: int = 120) -> bool:
        """Wait for the instance to be ready and reachable."""
        print("Waiting for instance to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            status = self.check_instance_status(instance_name)
            if status == "RUNNING":
                print(f"Instance is running, checking SSH connectivity...")
                return True
            else:
                print(f"Instance status: {status}, waiting...")
            
            time.sleep(10)
        
        print("Timeout waiting for instance to be ready")
        return False
    
    def ensure_instance_running(self, instance_name: str) -> bool:
        """Ensure the instance is running, starting it if necessary."""
        status = self.check_instance_status(instance_name)
        print(f"Instance status: {status}")
        
        if status == "RUNNING":
            print("Instance is already running.")
            return True
        elif status in ["STOPPED", "TERMINATED"]:
            print(f"Instance {instance_name} is {status.lower()}. Starting...")
            
            if not self.start_instance(instance_name):
                return False
            
            return self.wait_for_instance_ready(instance_name)
        else:
            print(f"Unknown instance status: {status}")
            print("Attempting to start instance...")
            
            if not self.start_instance(instance_name):
                return False
            
            return self.wait_for_instance_ready(instance_name)
