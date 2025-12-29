# Phase One Project Plan — WireGuard Admin Panel (GitHub + Self‑Hosted Gitea)

## Overview
Phase One establishes the foundation of your WireGuard admin ecosystem.  
This updated version includes:

- GitHub as the **primary remote**
- Gitea (self‑hosted VM) as a **mirrored DevOps environment**
- Automatic GitHub → Gitea mirroring
- Deployment pulling from GitHub for reliability

No public exposure occurs in Phase One.

---

## Architecture Summary

### Local PC
- DevOps VM  
  - Docker  
    - Gitea  
- GitHub (cloud)  
- WireGuard client  
- Deployment script  

### VPS
- WireGuard server  
- Python admin panel  
- Postgres  
- Apache (unused in Phase One)  

---

## Milestones
1. DevOps VM Setup  
2. GitHub + Gitea Setup  
3. VPS Preparation  
4. Admin Backend Development  
5. Core Feature Implementation  
6. Deployment Workflow Setup  
7. Testing & Validation  
8. Documentation & Organization  

---

## Detailed Tasks
(See TASKS.csv for full hierarchical breakdown.)

