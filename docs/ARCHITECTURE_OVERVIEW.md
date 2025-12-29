# Architecture Overview — Phase One (GitHub + Gitea)

## Local PC
- GitHub (primary remote)  
- DevOps VM  
  - Gitea (mirror)  
- Deployment script  

## VPS
- WireGuard server  
- Admin panel (Flask)  
- Postgres  

## Data Flow
1. Local development → GitHub  
2. GitHub → mirrored into Gitea  
3. Deployment script pulls from GitHub  
4. Admin panel updates on VPS  

