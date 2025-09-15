#!/usr/bin/env python3
"""
Remote Code Orchestrator Module

Main orchestrator class that coordinates all components for remote VS Code development.
This class brings together GCloud management, SSH operations, Git management, and VS Code launching.
"""

import os
from typing import Optional
from gcloud_manager import GCloudManager
from ssh_manager import SSHManager
from git_manager import GitManager
from vscode_launcher import VSCodeLauncher


class RemoteCodeOrchestrator:
    """Main orchestrator for remote VS Code development workflow."""
    
    def __init__(
        self, 
        project: str, 
        remote: str, 
        project_id: str = "software-265220", 
        zone: str = "us-central1-a", 
        remote_home: str = None, 
        ssh_forwarding: bool = True,
        repo_origin: str = None, 
        auto_clone: bool = True
    ):
        self.project = project
        self.remote = remote
        self.remote_home = remote_home
        self.auto_clone = auto_clone
        
        # Build the full remote path
        if self.remote_home and not self.project.startswith('/'):
            self.full_remote_path = f"{self.remote_home}/{self.project}"
        else:
            self.full_remote_path = self.project
        
        # Initialize component managers
        self.gcloud_manager = GCloudManager(project_id, zone)
        self.ssh_manager = SSHManager(project_id, zone, ssh_forwarding)
        self.git_manager = GitManager(self.ssh_manager, repo_origin)
        self.vscode_launcher = VSCodeLauncher(ssh_forwarding)
    
    def ensure_instance_ready(self) -> bool:
        """Ensure the remote instance is running and reachable."""
        print(f"Checking status of remote instance: {self.remote}")
        
        # Ensure instance is running
        if not self.gcloud_manager.ensure_instance_running(self.remote):
            return False
        
        # Check SSH connectivity
        print("Checking SSH connectivity...")
        if not self.ssh_manager.check_instance_reachable(self.remote):
            print("Instance is running but not yet reachable via SSH. Waiting...")
            # Wait a bit more for SSH to be ready
            import time
            time.sleep(30)
            
            if not self.ssh_manager.check_instance_reachable(self.remote):
                print("Instance is still not reachable via SSH.")
                return False
        
        print("Instance is reachable via SSH.")
        return True
    
    def ensure_repository_ready(self) -> bool:
        """Ensure the repository is available on the remote machine."""
        if not self.auto_clone:
            print("Auto-clone is disabled. Skipping repository setup.")
            return True
        
        if self.git_manager.check_repository_exists(self.remote, self.project, self.remote_home):
            print(f"Remote folder '{self.full_remote_path}' exists and is a git repository.")
            return True
        
        print(f"Remote folder '{self.full_remote_path}' does not exist or is not a git repository.")
        
        if not self.git_manager.repo_origin:
            print("No repository origin specified. VS Code will create the directory if needed.")
            return True
        
        print("Attempting to clone repository...")
        if not self.git_manager.clone_repository(self.remote, self.project, self.remote_home):
            print("Failed to clone repository. Continuing with VS Code connection...")
            return True
        
        return True
    
    def launch_development_environment(self) -> bool:
        """Launch the complete development environment."""
        # Validate remote path (optional, will continue even if validation fails)
        self.ssh_manager.validate_remote_path(self.remote, self.full_remote_path)
        
        # Launch VS Code remote connection
        success = self.vscode_launcher.launch_remote_connection(self.remote, self.full_remote_path)
        
        if success and self.ssh_manager.ssh_forwarding:
            self.vscode_launcher.print_ssh_forwarding_instructions()
        
        return success
    
    def run(self) -> bool:
        """Main execution flow - orchestrates the entire workflow."""
        print("="*60)
        print("REMOTE VS CODE DEVELOPMENT LAUNCHER")
        print("="*60)
        print(f"Project: {self.project}")
        print(f"Remote Instance: {self.remote}")
        print(f"Remote Path: {self.full_remote_path}")
        print(f"Auto-clone: {self.auto_clone}")
        if self.git_manager.repo_origin:
            print(f"Repository Origin: {self.git_manager.repo_origin}")
        print("="*60)
        
        # Step 1: Ensure instance is ready
        if not self.ensure_instance_ready():
            print("❌ Failed to prepare remote instance")
            return False
        
        # Step 2: Ensure repository is ready
        if not self.ensure_repository_ready():
            print("❌ Failed to prepare repository")
            return False
        
        # Step 3: Launch development environment
        if not self.launch_development_environment():
            print("❌ Failed to launch VS Code")
            return False
        
        print("✅ Remote development environment launched successfully!")
        return True
    
    def get_repository_status(self) -> dict:
        """Get detailed status of the remote repository."""
        return self.git_manager.get_repository_status(self.remote, self.project, self.remote_home)
    
    def test_ssh_forwarding(self) -> bool:
        """Test SSH forwarding to the remote machine."""
        return self.ssh_manager.test_ssh_forwarding(self.remote)
