#!/bin/bash

GITEA_URL="http://localhost:3000"
GITEA_USER="YOURUSER"
GITEA_TOKEN="YOUR_GITEA_API_TOKEN"
GITHUB_REPO="https://github.com/YOURUSER/wg-admin.git"

# Create repo in Gitea
curl -X POST "${GITEA_URL}/api/v1/user/repos" \
  -H "Authorization: token ${GITEA_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"wg-admin\",\"private\":true}"

# Enable pull mirroring
curl -X POST "${GITEA_URL}/api/v1/repos/${GITEA_USER}/wg-admin/mirror" \
  -H "Authorization: token ${GITEA_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
        \"repo_name\": \"wg-admin\",
        \"mirror_address\": \"${GITHUB_REPO}\",
        \"mirror_interval\": \"1h\",
        \"mirror_direction\": \"pull\"
      }"

