#!/bin/bash

# Ensure .ssh directory exists
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Write SSH Private Key if provided
if [ -n "$GITHUB_SSH_PRIVATE_KEY" ]; then
    echo "Injecting SSH Private Key..."
    echo "$GITHUB_SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
else
    echo "Warning: GITHUB_SSH_PRIVATE_KEY not found in environment."
fi

# Write SSH Config for alias support
if [ -n "$GITHUB_SSH_ALIAS" ]; then
    echo "Configuring SSH alias for $GITHUB_SSH_ALIAS..."
    echo "Host $GITHUB_SSH_ALIAS
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no" > ~/.ssh/config
else
    # Default to github.com
    ssh-keyscan github.com >> ~/.ssh/known_hosts
fi

# Run the Python application
exec python main.py
