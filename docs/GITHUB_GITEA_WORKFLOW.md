# GitHub + Gitea Dual‑Remote Workflow

## Overview
GitHub is the primary remote.  
Gitea is a mirrored DevOps environment inside your VM.

## Setup
1. Create GitHub repo  
2. Clone locally  
3. Deploy Gitea  
4. Create Gitea repo  
5. Enable pull mirroring from GitHub  
6. Add Gitea as secondary remote  

## Commands
### Push to GitHub (primary)
```
git push origin main
```

### Push to Gitea (optional)
```
git push gitea main
```

## Why this setup?
- GitHub = reliable, always online  
- Gitea = private DevOps environment  
- Mirroring keeps everything in sync  

