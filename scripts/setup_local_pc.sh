#!/bin/bash

# --- GitHub Setup ---
git clone git@github.com:jobryantai/wg-admin.git
cd wg-admin

# --- Add Gitea Remote (after Gitea is online) ---
git remote add gitea ssh://git@localhost:2222/jobryantai/wg-admin.git

# --- Add VPS Remote (optional Git push deploy) ---
#git remote add vps ssh://USER@VPS_IP:/opt/wg-admin

# --- Verify Remotes ---
git remote -v

