#!/usr/bin/env python3
"""
Git Repository Management Module

Handles git repository operations including cloning, checking repository status,
and managing remote repositories on Google Cloud instances.
"""

import os
from typing import Optional
from ssh_manager import SSHManager


class GitManager:
    """Manages git repository operations on remote instances."""
    
    def __init__(self, ssh_manager: SSHManager, repo_origin: str = None):
        self.ssh_manager = ssh_manager
        self.repo_origin = repo_origin
    
    def clone_repository(self, instance_name: str, project_folder: str, remote_home: str = None) -> bool:
        """Clone the repository if it doesn't exist on the remote machine."""
        if not self.repo_origin:
            print("No repository origin specified. Cannot clone repository.")
            return False
        
        # Build the full remote path
        if remote_home and not project_folder.startswith('/'):
            full_remote_path = f"{remote_home}/{project_folder}"
        else:
            full_remote_path = project_folder
        
        # Extract folder name from project path
        folder_name = os.path.basename(project_folder.rstrip('/'))
        
        # Construct the repository URL
        if not self.repo_origin.endswith('/'):
            repo_url = f"{self.repo_origin}/{folder_name}.git"
        else:
            repo_url = f"{self.repo_origin}{folder_name}.git"
        
        print(f"Attempting to clone repository: {repo_url}")
        print(f"Target directory: {full_remote_path}")
        
        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(full_remote_path)
        success, stdout, stderr = self.ssh_manager.execute_remote_command(
            instance_name, 
            f"mkdir -p '{parent_dir}'"
        )
        
        if not success:
            print(f"Warning: Could not create parent directory: {stderr}")
        
        # Clone the repository
        clone_command = f"cd '{parent_dir}' && git clone {repo_url} '{folder_name}'"
        success, stdout, stderr = self.ssh_manager.execute_remote_command(
            instance_name, 
            clone_command, 
            timeout=60
        )
        
        if success:
            print(f"Successfully cloned repository to: {full_remote_path}")
            return True
        else:
            print(f"Failed to clone repository: {stderr}")
            return False
    
    def check_repository_exists(self, instance_name: str, project_folder: str, remote_home: str = None) -> bool:
        """Check if the remote folder exists and is a git repository."""
        # Build the full remote path
        if remote_home and not project_folder.startswith('/'):
            full_remote_path = f"{remote_home}/{project_folder}"
        else:
            full_remote_path = project_folder
        
        return self.ssh_manager.check_remote_folder_exists(instance_name, full_remote_path)
    
    def get_repository_status(self, instance_name: str, project_folder: str, remote_home: str = None) -> dict:
        """Get detailed repository status information."""
        # Build the full remote path
        if remote_home and not project_folder.startswith('/'):
            full_remote_path = f"{remote_home}/{project_folder}"
        else:
            full_remote_path = project_folder
        
        status = {
            'path': full_remote_path,
            'exists': False,
            'is_git_repo': False,
            'has_uncommitted_changes': False,
            'current_branch': None,
            'remote_url': None
        }
        
        # Check if path exists
        success, stdout, stderr = self.ssh_manager.execute_remote_command(
            instance_name, 
            f"test -d '{full_remote_path}' && echo 'exists' || echo 'not_exists'"
        )
        
        if success and "exists" in stdout:
            status['exists'] = True
            
            # Check if it's a git repository
            success, stdout, stderr = self.ssh_manager.execute_remote_command(
                instance_name, 
                f"test -d '{full_remote_path}/.git' && echo 'is_git' || echo 'not_git'"
            )
            
            if success and "is_git" in stdout:
                status['is_git_repo'] = True
                
                # Get current branch
                success, stdout, stderr = self.ssh_manager.execute_remote_command(
                    instance_name, 
                    f"cd '{full_remote_path}' && git branch --show-current"
                )
                
                if success:
                    status['current_branch'] = stdout.strip()
                
                # Check for uncommitted changes
                success, stdout, stderr = self.ssh_manager.execute_remote_command(
                    instance_name, 
                    f"cd '{full_remote_path}' && git status --porcelain"
                )
                
                if success:
                    status['has_uncommitted_changes'] = len(stdout.strip()) > 0
                
                # Get remote URL
                success, stdout, stderr = self.ssh_manager.execute_remote_command(
                    instance_name, 
                    f"cd '{full_remote_path}' && git remote get-url origin"
                )
                
                if success:
                    status['remote_url'] = stdout.strip()
        
        return status
