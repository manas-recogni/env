#!/usr/bin/env python3
"""
Configuration Example for Remote Code Launcher

This file shows how to create configuration files for different environments
and use cases.
"""

# Default configuration
DEFAULT_CONFIG = {
    "project_id": "software-265220",
    "zone": "us-west2-b",
    "remote_home": "/data/manas/",
    "repo_origin": "git@github.com:recogni",
    "ssh_forwarding": True,
    "auto_clone": True,
    "default_instance": "default-instance"
}

# Development environment configuration
DEV_CONFIG = {
    **DEFAULT_CONFIG,
    "project_id": "dev-project-123",
    "zone": "us-central1-a",
    "remote_home": "/home/dev/",
    "default_instance": "dev-instance"
}

# Production environment configuration
PROD_CONFIG = {
    **DEFAULT_CONFIG,
    "project_id": "prod-project-456",
    "zone": "us-east1-b",
    "remote_home": "/opt/projects/",
    "default_instance": "prod-instance",
    "auto_clone": False  # Don't auto-clone in production
}

# Team-specific configurations
TEAM_CONFIGS = {
    "backend": {
        **DEFAULT_CONFIG,
        "default_instance": "backend-dev",
        "repo_origin": "git@github.com:recogni/backend"
    },
    "frontend": {
        **DEFAULT_CONFIG,
        "default_instance": "frontend-dev",
        "repo_origin": "git@github.com:recogni/frontend"
    },
    "ml": {
        **DEFAULT_CONFIG,
        "default_instance": "ml-dev",
        "zone": "us-west1-a",  # Different zone for ML workloads
        "repo_origin": "git@github.com:recogni/ml"
    }
}

# Project-specific configurations
PROJECT_CONFIGS = {
    "recogni-core": {
        "default_instance": "recogni-core-dev",
        "repo_origin": "git@github.com:recogni/core",
        "remote_home": "/data/recogni/"
    },
    "recogni-api": {
        "default_instance": "recogni-api-dev",
        "repo_origin": "git@github.com:recogni/api",
        "remote_home": "/data/recogni/"
    }
}


def get_config(environment="default", team=None, project=None):
    """
    Get configuration based on environment, team, and project.
    
    Args:
        environment: "default", "dev", "prod"
        team: "backend", "frontend", "ml"
        project: specific project name
    
    Returns:
        dict: Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    
    # Apply environment-specific config
    if environment == "dev":
        config.update(DEV_CONFIG)
    elif environment == "prod":
        config.update(PROD_CONFIG)
    
    # Apply team-specific config
    if team and team in TEAM_CONFIGS:
        config.update(TEAM_CONFIGS[team])
    
    # Apply project-specific config
    if project and project in PROJECT_CONFIGS:
        config.update(PROJECT_CONFIGS[project])
    
    return config


def create_launcher_from_config(project_folder, remote_instance=None, **overrides):
    """
    Create a RemoteCodeOrchestrator from configuration.
    
    Args:
        project_folder: Path to the project folder
        remote_instance: Instance name (overrides config default)
        **overrides: Additional configuration overrides
    
    Returns:
        RemoteCodeOrchestrator: Configured orchestrator
    """
    from remote_code_orchestrator import RemoteCodeOrchestrator
    
    # Get base configuration
    config = get_config()
    
    # Apply overrides
    config.update(overrides)
    
    # Use provided instance or default
    instance = remote_instance or config["default_instance"]
    
    return RemoteCodeOrchestrator(
        project=project_folder,
        remote=instance,
        project_id=config["project_id"],
        zone=config["zone"],
        remote_home=config["remote_home"],
        ssh_forwarding=config["ssh_forwarding"],
        repo_origin=config["repo_origin"],
        auto_clone=config["auto_clone"]
    )


# Example usage functions
def launch_backend_project(project_name):
    """Launch a backend project with appropriate configuration."""
    config = get_config(environment="dev", team="backend")
    launcher = create_launcher_from_config(project_name, **config)
    return launcher.run()


def launch_ml_project(project_name):
    """Launch an ML project with appropriate configuration."""
    config = get_config(environment="dev", team="ml")
    launcher = create_launcher_from_config(project_name, **config)
    return launcher.run()


def launch_production_project(project_name):
    """Launch a production project with appropriate configuration."""
    config = get_config(environment="prod")
    launcher = create_launcher_from_config(project_name, **config)
    return launcher.run()


if __name__ == "__main__":
    # Example of using configurations
    print("Configuration Examples:")
    print("=" * 30)
    
    # Show different configurations
    print("Default config:", get_config())
    print("Dev config:", get_config("dev"))
    print("Backend team config:", get_config(team="backend"))
    print("ML team config:", get_config(team="ml"))
    
    # Example of creating a launcher
    launcher = create_launcher_from_config(
        "my-project",
        environment="dev",
        team="backend"
    )
    print(f"Created launcher for: {launcher.project} on {launcher.remote}")
