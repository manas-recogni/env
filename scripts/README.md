# Remote VS Code Launcher

A modular Python tool for launching VS Code with remote Google Cloud instances, featuring automatic repository cloning and SSH key forwarding.

## 🏗️ Architecture

The tool has been refactored into a modular architecture with clear separation of concerns:

```
code_remote.py (Main Entry Point)
├── RemoteCodeOrchestrator (Main Coordinator)
    ├── GCloudManager (Instance Management)
    ├── SSHManager (SSH Operations)
    ├── GitManager (Repository Operations)
    └── VSCodeLauncher (VS Code Integration)
```

### Component Overview

#### 1. **RemoteCodeOrchestrator** (`remote_code_orchestrator.py`)
- **Purpose**: Main coordinator that orchestrates the entire workflow
- **Responsibilities**:
  - Coordinate all component managers
  - Execute the complete development environment setup
  - Provide high-level workflow management
  - Handle error propagation and user feedback

#### 2. **GCloudManager** (`gcloud_manager.py`)
- **Purpose**: Manages Google Cloud Compute Engine instances
- **Responsibilities**:
  - Check instance status (RUNNING, STOPPED, TERMINATED)
  - Start stopped/terminated instances
  - Wait for instances to become ready
  - Ensure instances are running before proceeding

#### 3. **SSHManager** (`ssh_manager.py`)
- **Purpose**: Handles SSH connectivity and remote operations
- **Responsibilities**:
  - Test SSH connectivity to instances
  - Execute remote commands via SSH
  - Test SSH key forwarding
  - Validate remote paths and directories

#### 4. **GitManager** (`git_manager.py`)
- **Purpose**: Manages git repositories on remote instances
- **Responsibilities**:
  - Check if repositories exist on remote machines
  - Clone repositories when needed
  - Get detailed repository status information
  - Handle repository URL construction

#### 5. **VSCodeLauncher** (`vscode_launcher.py`)
- **Purpose**: Handles VS Code remote connection launching
- **Responsibilities**:
  - Launch VS Code with remote SSH connections
  - Provide SSH forwarding verification instructions
  - Handle VS Code CLI integration

## 🚀 Usage

### Basic Usage

```bash
# Launch VS Code with a remote project
python code_remote.py my-project

# Specify a custom instance name
python code_remote.py my-project my-dev-instance

# Use custom project ID and zone
python code_remote.py my-project --project-id "my-project" --zone "us-west1-a"
```

### Advanced Usage

```bash
# Disable automatic repository cloning
python code_remote.py my-project --no-auto-clone

# Use custom repository origin
python code_remote.py my-project --repo-origin "https://gitlab.com/your-username"

# Disable SSH key forwarding
python code_remote.py my-project --no-ssh-forwarding

# Test SSH forwarding without launching VS Code
python code_remote.py my-project --test-ssh-forwarding
```

### Command Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `project_folder` | Required | Path to the project folder to open |
| `remote` | `default-instance` | Name of the gcloud instance |
| `--project-id` | `software-265220` | Google Cloud project ID |
| `--zone` | `us-west2-b` | Google Cloud zone |
| `--remote-home` | `/data/manas/` | Default home directory on remote machine |
| `--repo-origin` | `git@github.com:recogni` | Repository origin URL for cloning |
| `--no-ssh-forwarding` | False | Disable SSH key forwarding |
| `--no-auto-clone` | False | Disable automatic repository cloning |
| `--test-ssh-forwarding` | False | Test SSH key forwarding only |

## 🔧 Prerequisites

### Required Tools
- **Google Cloud SDK**: For managing GCloud instances
- **VS Code**: With Remote-SSH extension installed
- **Python 3.7+**: For running the script

### Setup
1. Install Google Cloud SDK and authenticate:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. Install VS Code with Remote-SSH extension

3. Ensure your SSH keys are set up for GitHub/GitLab access

## 📋 Workflow

The tool follows this workflow:

1. **Instance Management**: Check if the GCloud instance is running, start it if needed
2. **SSH Connectivity**: Verify SSH access to the instance
3. **Repository Setup**: Check if the project folder exists, clone it if needed
4. **VS Code Launch**: Launch VS Code with remote SSH connection
5. **Verification**: Provide instructions for verifying SSH key forwarding

## 🛠️ Extending the Tool

### Adding New Features

The modular architecture makes it easy to extend functionality:

#### Example: Add Docker Support

1. Create `docker_manager.py`:
   ```python
   class DockerManager:
       def __init__(self, ssh_manager):
           self.ssh_manager = ssh_manager
       
       def ensure_containers_running(self, instance_name, project_path):
           # Implementation here
   ```

2. Integrate into `RemoteCodeOrchestrator`:
   ```python
   def __init__(self, ...):
       # ... existing code ...
       self.docker_manager = DockerManager(self.ssh_manager)
   ```

#### Example: Add Database Management

1. Create `database_manager.py`:
   ```python
   class DatabaseManager:
       def __init__(self, ssh_manager):
           self.ssh_manager = ssh_manager
       
       def setup_database(self, instance_name, db_config):
           # Implementation here
   ```

### Customizing Component Behavior

Each component can be customized by:

1. **Inheritance**: Extend existing classes
2. **Composition**: Create wrapper classes
3. **Configuration**: Modify constructor parameters

#### Example: Custom GCloud Manager

```python
class CustomGCloudManager(GCloudManager):
    def __init__(self, project_id, zone, custom_config):
        super().__init__(project_id, zone)
        self.custom_config = custom_config
    
    def start_instance(self, instance_name):
        # Custom startup logic
        return super().start_instance(instance_name)
```

## 🐛 Troubleshooting

### Common Issues

1. **Instance Not Starting**
   - Check GCloud permissions
   - Verify instance name and zone
   - Check billing status

2. **SSH Connection Failed**
   - Verify SSH keys are configured
   - Check firewall rules
   - Ensure instance is fully booted

3. **Repository Clone Failed**
   - Verify repository URL is correct
   - Check SSH key access to repository
   - Ensure repository exists

4. **VS Code Not Launching**
   - Verify VS Code is installed
   - Check `code` command is in PATH
   - Install Remote-SSH extension

### Debug Mode

Add debug output by modifying the orchestrator:

```python
def run(self):
    print(f"Debug: Project={self.project}")
    print(f"Debug: Remote={self.remote}")
    # ... rest of implementation
```

## 📁 File Structure

```
scripts/
├── code_remote.py                 # Main entry point
├── remote_code_orchestrator.py   # Main orchestrator
├── gcloud_manager.py             # GCloud instance management
├── ssh_manager.py                # SSH operations
├── git_manager.py                # Git repository management
├── vscode_launcher.py            # VS Code integration
└── README.md                     # This file
```

## 🤝 Contributing

1. Follow the modular architecture pattern
2. Add comprehensive docstrings
3. Include error handling
4. Update this README for new features
5. Test with different GCloud configurations

## 📄 License

This project is part of your development environment setup scripts.
