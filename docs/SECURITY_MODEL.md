# Security Model — Phase One

## Goals
- No public exposure  
- Local-only access  
- Strong authentication  
- Safe WireGuard operations  

## Controls
- Admin panel bound to 127.0.0.1  
- Access via SSH tunnel  
- Password hashing (bcrypt)  
- CSRF protection  
- Input validation  
- No private keys stored in DB  

