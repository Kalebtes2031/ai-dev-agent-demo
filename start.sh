#!/bin/bash

# Ensure .ssh directory exists
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# --- ROBUST SSH KEY RECONSTRUCTION ---
if [ -n "$GITHUB_SSH_PRIVATE_KEY" ]; then
    echo "Processing GitHub SSH Private Key..."
    
    # Strip any literal '\n' characters, spaces, or surrounding quotes
    CLEAN_KEY=$(echo "$GITHUB_SSH_PRIVATE_KEY" | sed 's/\\n/\n/g' | sed 's/\"//g' | xargs -0)
    
    # If the key doesn't start with the header, it's likely a raw base64 or partial blob
    if [[ ! "$CLEAN_KEY" =~ "BEGIN" ]]; then
        echo "Detected raw key blob. Reconstructing PEM format..."
        # Re-wrap in headers
        {
            echo "-----BEGIN OPENSSH PRIVATE KEY-----"
            echo "$CLEAN_KEY" | fold -w 64
            echo "-----END OPENSSH PRIVATE KEY-----"
        } > ~/.ssh/id_rsa
    else
        echo "Detected valid PEM format."
        echo "$CLEAN_KEY" > ~/.ssh/id_rsa
    fi
    
    chmod 600 ~/.ssh/id_rsa
else
    echo "Warning: GITHUB_SSH_PRIVATE_KEY not found."
fi

# --- GIT IDENTITY SETUP ---
GITHUB_USER=${GITHUB_USERNAME:-"Mekonnen44"}
git config --global user.name "$GITHUB_USER"
git config --global user.email "bot@mekonnen.tech"
echo "Git identity set to: $GITHUB_USER"

# --- SSH CONFIG & ALIAS ---
SSH_ALIAS=${GITHUB_SSH_ALIAS:-"github.com"}
echo "Configuring SSH alias for $SSH_ALIAS..."
cat <<EOF > ~/.ssh/config
Host $SSH_ALIAS
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
EOF

# Ensure github.com is in known_hosts
ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null

# Final check
echo "Reconstructing environment done. Starting bot..."
exec python main.py
