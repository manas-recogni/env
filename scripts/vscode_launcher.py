#!/usr/bin/env python3
"""
VS Code Launcher Module

Handles VS Code remote connection launching and SSH forwarding verification.
"""

import subprocess
from typing import Optional


class VSCodeLauncher:
    """Manages VS Code remote connection launching."""
    
    def __init__(self, ssh_forwarding: bool = True):
        self.ssh_forwarding = ssh_forwarding
    
    def launch_remote_connection(self, instance_name: str, remote_path: str) -> bool:
        """Launch VS Code with remote connection."""
        print(f"Launching VS Code remote connection to: {instance_name}")
        print(f"Remote path: {remote_path}")
        
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
            remote_url = f"vscode-remote://ssh-remote+{instance_name}/{remote_path}"
            
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
    
    def print_ssh_forwarding_instructions(self):
        """Print instructions for verifying SSH forwarding."""
        if not self.ssh_forwarding:
            return
        
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
