sudo apt update
sudo apt install -y postgresql postgresql-contrib


sudo -u postgres psql <<EOF
CREATE DATABASE wgadmin_dev;
CREATE USER wguser WITH PASSWORD 'devpassword';
GRANT ALL PRIVILEGES ON DATABASE wgadmin_dev TO wguser;
EOF

