#!/usr/bin/env python3
"""
SSH Management Module

Handles SSH connectivity, key forwarding, and remote command execution
for Google Cloud instances.
"""

import subprocess
from typing import Optional


class SSHManager:
    """Manages SSH connections and operations for remote instances."""
    
    def __init__(self, project_id: str = "software-265220", zone: str = "us-central1-a", ssh_forwarding: bool = True):
        self.project_id = project_id
        self.zone = zone
        self.ssh_forwarding = ssh_forwarding
    
    def check_instance_reachable(self, instance_name: str) -> bool:
        """Check if the gcloud instance is reachable via SSH."""
        try:
            cmd = [
                "gcloud", "compute", "ssh", 
                f"{instance_name}",
                f"--project={self.project_id}",
                f"--zone={self.zone}",
                "--command=echo 'Connection successful'",
                "--quiet"
            ]
            
            # Add SSH forwarding if enabled
            if self.ssh_forwarding:
                cmd.extend(["--", "-A"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def execute_remote_command(self, instance_name: str, command: str, timeout: int = 10) -> tuple[bool, str, str]:
        """Execute a command on the remote instance via SSH."""
        try:
            cmd = [
                "gcloud", "compute", "ssh", 
                f"{instance_name}",
                f"--project={self.project_id}",
                f"--zone={self.zone}",
                f"--command={command}",
                "--quiet"
            ]
            
            # Add SSH forwarding if enabled
            if self.ssh_forwarding:
                cmd.extend(["--", "-A"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0, result.stdout, result.stderr
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            return False, "", str(e)
    
    def test_ssh_forwarding(self, instance_name: str) -> bool:
        """Test SSH forwarding to the remote machine."""
        print("Testing SSH forwarding to remote machine...")
        
        success, stdout, stderr = self.execute_remote_command(instance_name, "ssh-add -l", timeout=15)
        
        if success:
            if "no identities" in stdout.lower():
                print("❌ SSH forwarding is NOT working - no keys found on remote")
                print("   This means VS Code won't have access to your SSH keys")
                return False
            else:
                print("✅ SSH forwarding is working - keys found on remote")
                print(f"   Keys: {stdout.strip()}")
                return True
        else:
            print("❌ SSH forwarding test failed")
            print(f"   Error: {stderr}")
            return False
    
    def validate_remote_path(self, instance_name: str, remote_path: str) -> bool:
        """Validate that the remote path exists on the remote machine."""
        success, stdout, stderr = self.execute_remote_command(
            instance_name, 
            f"test -d '{remote_path}' && echo 'Path exists' || echo 'Path does not exist'"
        )
        
        if success and "Path exists" in stdout:
            return True
        else:
            print(f"Warning: Remote path '{remote_path}' may not exist on the remote machine.")
            print("VS Code will attempt to create the directory if it doesn't exist.")
            return True  # Continue anyway, let VS Code handle it
    
    def check_remote_folder_exists(self, instance_name: str, remote_path: str) -> bool:
        """Check if the remote folder exists and is a git repository."""
        success, stdout, stderr = self.execute_remote_command(
            instance_name,
            f"test -d '{remote_path}' && test -d '{remote_path}/.git' && echo 'Git repo exists' || echo 'Not a git repo or does not exist'"
        )
        
        return success and "Git repo exists" in stdout
