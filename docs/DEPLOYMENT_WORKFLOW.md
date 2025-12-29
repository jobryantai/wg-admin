# Deployment Workflow — Phase One (GitHub Source)

## Overview
Deployment is performed from your local PC to the VPS through WireGuard.

## Steps
1. Modify code locally  
2. Commit changes  
3. Push to GitHub  
4. Run `./deploy.sh`  
5. Script connects to VPS  
6. Script pulls from GitHub  
7. Script installs dependencies  
8. Script restarts systemd service  

## Why GitHub?
- Always online  
- Reliable  
- Gitea VM may be offline  

