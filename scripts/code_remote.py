#!/usr/bin/env python3
"""
Remote VS Code Launcher with gcloud Instance Management

Usage: python code_remote.py <project_folder> [remote_instance_name]

This is the main entry point that uses the modular RemoteCodeOrchestrator.
"""

import sys
import argparse
from remote_code_orchestrator import RemoteCodeOrchestrator


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
    
    # Create orchestrator and run
    orchestrator = RemoteCodeOrchestrator(
        project=args.project_folder,
        remote=args.remote,
        project_id=args.project_id,
        zone=args.zone,
        remote_home=args.remote_home,
        ssh_forwarding=not args.no_ssh_forwarding,
        repo_origin=args.repo_origin,
        auto_clone=not args.no_auto_clone
    )
    
    if args.test_ssh_forwarding:
        success = orchestrator.test_ssh_forwarding()
    else:
        success = orchestrator.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()