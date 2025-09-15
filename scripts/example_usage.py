#!/usr/bin/env python3
"""
Example Usage of Remote Code Launcher Components

This script demonstrates how to use the modular components individually
for custom workflows and integrations.
"""

from gcloud_manager import GCloudManager
from ssh_manager import SSHManager
from git_manager import GitManager
from vscode_launcher import VSCodeLauncher
from remote_code_orchestrator import RemoteCodeOrchestrator


def example_individual_components():
    """Example of using components individually."""
    print("=== Individual Component Usage Example ===")
    
    # Initialize managers
    gcloud = GCloudManager(project_id="my-project", zone="us-west1-a")
    ssh = SSHManager(project_id="my-project", zone="us-west1-a", ssh_forwarding=True)
    git = GitManager(ssh, repo_origin="git@github.com:my-org")
    vscode = VSCodeLauncher(ssh_forwarding=True)
    
    instance_name = "my-dev-instance"
    project_path = "my-project"
    remote_home = "/home/user"
    
    # Check instance status
    status = gcloud.check_instance_status(instance_name)
    print(f"Instance status: {status}")
    
    # Ensure instance is running
    if gcloud.ensure_instance_running(instance_name):
        print("Instance is ready!")
        
        # Test SSH connectivity
        if ssh.check_instance_reachable(instance_name):
            print("SSH connection successful!")
            
            # Check repository status
            repo_status = git.get_repository_status(instance_name, project_path, remote_home)
            print(f"Repository status: {repo_status}")
            
            # Test SSH forwarding
            if ssh.test_ssh_forwarding(instance_name):
                print("SSH forwarding is working!")
            else:
                print("SSH forwarding is not working!")


def example_custom_orchestrator():
    """Example of creating a custom orchestrator."""
    print("\n=== Custom Orchestrator Example ===")
    
    class CustomOrchestrator(RemoteCodeOrchestrator):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.custom_setup_done = False
        
        def custom_setup(self):
            """Custom setup before launching VS Code."""
            print("Performing custom setup...")
            # Add your custom logic here
            # e.g., install dependencies, configure environment, etc.
            self.custom_setup_done = True
        
        def run(self):
            """Override run method to include custom setup."""
            # Call parent setup
            if not self.ensure_instance_ready():
                return False
            
            if not self.ensure_repository_ready():
                return False
            
            # Add custom setup
            self.custom_setup()
            
            # Launch VS Code
            return self.launch_development_environment()
    
    # Use custom orchestrator
    orchestrator = CustomOrchestrator(
        project="my-project",
        remote="my-instance",
        project_id="my-project",
        zone="us-west1-a"
    )
    
    # This would run the custom workflow
    # success = orchestrator.run()


def example_batch_operations():
    """Example of batch operations across multiple instances."""
    print("\n=== Batch Operations Example ===")
    
    instances = ["dev-instance-1", "dev-instance-2", "test-instance"]
    gcloud = GCloudManager(project_id="my-project", zone="us-west1-a")
    
    for instance in instances:
        print(f"Checking {instance}...")
        status = gcloud.check_instance_status(instance)
        print(f"  Status: {status}")
        
        if status != "RUNNING":
            print(f"  Starting {instance}...")
            if gcloud.start_instance(instance):
                print(f"  ✅ {instance} started successfully")
            else:
                print(f"  ❌ Failed to start {instance}")


def example_repository_management():
    """Example of advanced repository management."""
    print("\n=== Repository Management Example ===")
    
    ssh = SSHManager(project_id="my-project", zone="us-west1-a")
    git = GitManager(ssh, repo_origin="git@github.com:my-org")
    
    instance_name = "my-instance"
    projects = ["project-a", "project-b", "project-c"]
    
    for project in projects:
        print(f"Managing repository: {project}")
        
        # Check if repository exists
        if git.check_repository_exists(instance_name, project):
            print(f"  ✅ {project} exists")
            
            # Get detailed status
            status = git.get_repository_status(instance_name, project)
            print(f"  Branch: {status['current_branch']}")
            print(f"  Has changes: {status['has_uncommitted_changes']}")
        else:
            print(f"  ❌ {project} does not exist")
            
            # Clone if needed
            if git.clone_repository(instance_name, project):
                print(f"  ✅ {project} cloned successfully")
            else:
                print(f"  ❌ Failed to clone {project}")


if __name__ == "__main__":
    print("Remote Code Launcher - Component Usage Examples")
    print("=" * 50)
    
    # Run examples
    example_individual_components()
    example_custom_orchestrator()
    example_batch_operations()
    example_repository_management()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("Note: These examples show the API usage but don't actually")
    print("execute commands. Modify as needed for your use case.")
