#!/usr/bin/env python3
"""
Remote VS Code Launcher with gcloud Instance Management

Usage: python code_remote.py <project_folder> [remote_instance_name]
"""

import sys
import subprocess
import time
import socket
import argparse
import os
from typing import Optional, Tuple


class RemoteCodeLauncher:
    def __init__(self, project: str, remote: str, project_id: str = "software-265220", zone: str = "us-central1-a", remote_home: str = None, ssh_forwarding: bool = True, repo_origin: str = None, auto_clone: bool = True):
        self.project = project
        self.remote = remote
        self.project_id = project_id
        self.zone = zone
        self.remote_home = remote_home
        self.ssh_forwarding = ssh_forwarding
        self.ssh_port = 22  # Default SSH port
        self.repo_origin = repo_origin
        self.auto_clone = auto_clone
        
        # Build the full remote path
        if self.remote_home and not self.project.startswith('/'):
            self.full_remote_path = f"{self.remote_home}/{self.project}"
        else:
            self.full_remote_path = self.project
        
    def check_instance_status(self) -> str:
        """Check the status of the gcloud instance using gcloud API."""
        try:
            cmd = [
                "gcloud", "compute", "instances", "describe",
                f"{self.remote}",
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
    
    def check_instance_reachable(self) -> bool:
        """Check if the gcloud instance is reachable via SSH."""
        try:
            # Try to connect to the instance via SSH with optional key forwarding
            cmd = [
                "gcloud", "compute", "ssh", 
                f"{self.remote}",
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
    
    def start_gcloud_instance(self) -> bool:
        """Start the gcloud compute instance."""
        print(f"Starting gcloud instance: {self.remote}")
        
        try:
            cmd = [
                "gcloud", "compute", "instances", "start",
                f"--project={self.project_id}",
                f"--zone={self.zone}",
                self.remote
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Successfully started instance: {self.remote}")
                return True
            else:
                print(f"Failed to start instance: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("Error: gcloud CLI not found. Please install Google Cloud SDK.")
            return False
    
    def wait_for_instance_ready(self, max_wait_time: int = 120) -> bool:
        """Wait for the instance to be ready and reachable."""
        print("Waiting for instance to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            # Check status first
            status = self.check_instance_status()
            if status == "RUNNING":
                print(f"Instance is running, checking SSH connectivity...")
                if self.check_instance_reachable():
                    print("Instance is now reachable!")
                    return True
                else:
                    print("Instance is running but SSH not ready yet, waiting...")
            else:
                print(f"Instance status: {status}, waiting...")
            
            time.sleep(10)
        
        print("Timeout waiting for instance to be ready")
        return False
    
    def validate_remote_path(self) -> bool:
        """Validate that the remote path exists on the remote machine."""
        try:
            cmd = [
                "gcloud", "compute", "ssh", 
                f"{self.remote}",
                f"--project={self.project_id}",
                f"--zone={self.zone}",
                f"--command=test -d '{self.full_remote_path}' && echo 'Path exists' || echo 'Path does not exist'",
                "--quiet"
            ]
            
            # Add SSH forwarding if enabled
            if self.ssh_forwarding:
                cmd.extend(["--", "-A"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "Path exists" in result.stdout:
                return True
            else:
                print(f"Warning: Remote path '{self.full_remote_path}' may not exist on the remote machine.")
                print("VS Code will attempt to create the directory if it doesn't exist.")
                return True  # Continue anyway, let VS Code handle it
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            print(f"Warning: Could not validate remote path '{self.full_remote_path}'.")
            print("Continuing with VS Code remote connection...")
            return True  # Continue anyway
    
    def check_remote_folder_exists(self) -> bool:
        """Check if the remote folder exists and is a git repository."""
        try:
            cmd = [
                "gcloud", "compute", "ssh", 
                f"{self.remote}",
                f"--project={self.project_id}",
                f"--zone={self.zone}",
                f"--command=test -d '{self.full_remote_path}' && test -d '{self.full_remote_path}/.git' && echo 'Git repo exists' || echo 'Not a git repo or does not exist'",
                "--quiet"
            ]
            
            # Add SSH forwarding if enabled
            if self.ssh_forwarding:
                cmd.extend(["--", "-A"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "Git repo exists" in result.stdout:
                return True
            else:
                return False
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def clone_repository(self) -> bool:
        """Clone the repository if it doesn't exist on the remote machine."""
        if not self.repo_origin:
            print("No repository origin specified. Cannot clone repository.")
            return False
        
        # Extract folder name from project path
        folder_name = os.path.basename(self.project.rstrip('/'))
        
        # Construct the repository URL
        if not self.repo_origin.endswith('/'):
            repo_url = f"{self.repo_origin}/{folder_name}.git"
        else:
            repo_url = f"{self.repo_origin}{folder_name}.git"
        
        print(f"Attempting to clone repository: {repo_url}")
        print(f"Target directory: {self.full_remote_path}")
        
        try:
            # Create parent directory if it doesn't exist
            parent_dir = os.path.dirname(self.full_remote_path)
            create_dir_cmd = [
                "gcloud", "compute", "ssh", 
                f"{self.remote}",
                f"--project={self.project_id}",
                f"--zone={self.zone}",
                f"--command=mkdir -p '{parent_dir}'",
                "--quiet"
            ]
            
            if self.ssh_forwarding:
                create_dir_cmd.extend(["--", "-A"])
            
            subprocess.run(create_dir_cmd, capture_output=True, text=True, timeout=10)
            
            # Clone the repository
            clone_cmd = [
                "gcloud", "compute", "ssh", 
                f"{self.remote}",
                f"--project={self.project_id}",
                f"--zone={self.zone}",
                f"--command=cd '{parent_dir}' && git clone {repo_url} '{folder_name}'",
                "--quiet"
            ]
            
            if self.ssh_forwarding:
                clone_cmd.extend(["--", "-A"])
            
            result = subprocess.run(clone_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"Successfully cloned repository to: {self.full_remote_path}")
                return True
            else:
                print(f"Failed to clone repository: {result.stderr}")
                return False
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error cloning repository: {e}")
            return False
    
    def launch_vscode_remote(self) -> bool:
        """Launch VS Code with remote connection."""
        print(f"Launching VS Code remote connection to: {self.remote}")
        print(f"Remote path: {self.full_remote_path}")
        
        try:
            # For SSH forwarding to work with VS Code, we need to use a different approach
            # VS Code will use the SSH config, so we need to ensure SSH forwarding is configured
            
            if self.ssh_forwarding:
                print("SSH forwarding enabled - VS Code will use your local SSH keys")
                # VS Code will automatically use the SSH agent if it's running
                # The SSH forwarding is handled by the SSH agent and VS Code's SSH extension
            else:
                print("SSH forwarding disabled")
            
            # Construct the remote SSH URL
            remote_url = f"vscode-remote://ssh-remote+{self.remote}/{self.full_remote_path}"
            
            # Launch VS Code with the remote URL
            cmd = ["code", "--folder-uri", remote_url]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("VS Code remote connection launched successfully!")
                if self.ssh_forwarding:
                    print("Note: SSH keys should be forwarded to the remote machine.")
                    print("You can verify by running 'ssh-add -l' on the remote machine.")
                return True
            else:
                print(f"Failed to launch VS Code: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("Error: VS Code CLI not found. Please install VS Code and ensure 'code' command is available.")
            return False
    
    def troubleshoot_ssh_forwarding(self) -> bool:
        """Test SSH forwarding to the remote machine."""
        print("Testing SSH forwarding to remote machine...")
        
        try:
            cmd = [
                "gcloud", "compute", "ssh", 
                f"{self.remote}",
                f"--project={self.project_id}",
                f"--zone={self.zone}",
                "--command=ssh-add -l",
                "--quiet"
            ]
            
            # Add SSH forwarding if enabled
            if self.ssh_forwarding:
                cmd.extend(["--", "-A"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                if "no identities" in result.stdout.lower():
                    print("❌ SSH forwarding is NOT working - no keys found on remote")
                    print("   This means VS Code won't have access to your SSH keys")
                    return False
                else:
                    print("✅ SSH forwarding is working - keys found on remote")
                    print(f"   Keys: {result.stdout.strip()}")
                    return True
            else:
                print("❌ SSH forwarding test failed")
                print(f"   Error: {result.stderr}")
                return False
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Could not test SSH forwarding")
            return False
    
    def run(self) -> bool:
        """Main execution flow."""
        print(f"Checking status of remote instance: {self.remote}")
        
        # Check instance status first
        status = self.check_instance_status()
        print(f"Instance status: {status}")
        
        if status == "RUNNING":
            print("Instance is running, checking SSH connectivity...")
            if self.check_instance_reachable():
                print("Instance is reachable via SSH.")
            else:
                print("Instance is running but not yet reachable via SSH. Waiting...")
                if not self.wait_for_instance_ready():
                    return False
        elif status == "STOPPED":
            print(f"Instance {self.remote} is stopped. Starting...")
            
            # Start the instance
            if not self.start_gcloud_instance():
                return False
            
            # Wait for instance to be ready
            if not self.wait_for_instance_ready():
                return False
        elif status == "TERMINATED":
            print(f"Instance {self.remote} is terminated. Starting...")
            
            # Start the instance
            if not self.start_gcloud_instance():
                return False
            
            # Wait for instance to be ready
            if not self.wait_for_instance_ready():
                return False
        else:
            print(f"Unknown instance status: {status}")
            print("Attempting to start instance...")
            
            # Try to start the instance
            if not self.start_gcloud_instance():
                return False
            
            # Wait for instance to be ready
            if not self.wait_for_instance_ready():
                return False
        
        # Check if remote folder exists and clone if needed
        if self.auto_clone and not self.check_remote_folder_exists():
            print(f"Remote folder '{self.full_remote_path}' does not exist or is not a git repository.")
            if self.repo_origin:
                print("Attempting to clone repository...")
                if not self.clone_repository():
                    print("Failed to clone repository. Continuing with VS Code connection...")
            else:
                print("No repository origin specified. VS Code will create the directory if needed.")
        else:
            print(f"Remote folder '{self.full_remote_path}' exists and is a git repository.")
        
        # Validate remote path (optional, will continue even if validation fails)
        self.validate_remote_path()
        
        # Launch VS Code remote connection
        success = self.launch_vscode_remote()
        
        if success and self.ssh_forwarding:
            print("\n" + "="*60)
            print("SSH FORWARDING VERIFICATION")
            print("="*60)
            print("To verify SSH keys are forwarded to the remote machine:")
            print("1. Open a terminal in VS Code on the remote machine")
            print("2. Run: ssh-add -l")
            print("3. You should see your local SSH keys listed")
            print("4. If you see 'Could not open a connection to your authentication agent'")
            print("   or 'The agent has no identities', SSH forwarding is not working")
            print("="*60)
        
        return success


def main():
    parser = argparse.ArgumentParser(
        description="Launch VS Code with remote gcloud instance connection"
    )
    parser.add_argument(
        "project_folder", 
        help="Path to the project folder to open"
    )
    parser.add_argument(
        "remote", 
        nargs="?", 
        default="default-instance",
        help="Name of the gcloud instance (default: default-instance)"
    )
    parser.add_argument(
        "--project-id",
        default="software-265220",
        help="Google Cloud project ID (default: software-265220)"
    )
    parser.add_argument(
        "--zone",
        default="us-west2-b",
        help="Google Cloud zone (default: us-central1-a)"
    )
    parser.add_argument(
        "--remote-home",
        default="/data/manas/",
        help="Default home directory on remote machine to prepend to project path"
    )
    parser.add_argument(
        "--no-ssh-forwarding",
        action="store_true",
        help="Disable SSH key forwarding (enabled by default)"
    )
    parser.add_argument(
        "--test-ssh-forwarding",
        action="store_true",
        help="Test SSH key forwarding to the remote machine"
    )
    parser.add_argument(
        "--repo-origin",
        default="git@github.com:recogni",
        help="Default repository origin URL for cloning (default: git@github.com:recogni)"
    )
    parser.add_argument(
        "--no-auto-clone",
        action="store_true",
        help="Disable automatic repository cloning (enabled by default)"
    )
    
    args = parser.parse_args()
    
    # Create launcher and run
    launcher = RemoteCodeLauncher(
        project=args.project_folder,  # Use the path as-is for remote
        remote=args.remote,
        project_id=args.project_id,
        zone=args.zone,
        remote_home=args.remote_home,
        ssh_forwarding=not args.no_ssh_forwarding,
        repo_origin=args.repo_origin,
        auto_clone=not args.no_auto_clone
    )
    
    if args.test_ssh_forwarding:
        success = launcher.troubleshoot_ssh_forwarding()
    else:
        success = launcher.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 