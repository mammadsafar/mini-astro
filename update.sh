#!/bin/bash

set -e  # توقف در صورت بروز خطا

# رنگ‌ها
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[1;34m'
NC='\033[0m' # بدون رنگ

echo -e "${BLUE}🔄 Pulling latest changes from Git...${NC}"
git pull origin main || { echo -e "${RED}❌ Git pull failed. Check your repo and connection.${NC}"; exit 1; }

echo -e "${YELLOW}🔧 Building containers (dry-run)...${NC}"
docker compose -f docker compose.yml build || { echo -e "${RED}❌ Build failed. Aborting update.${NC}"; exit 1; }

echo -e "${YELLOW}🛑 Shutting down current containers...${NC}"
docker compose -f docker compose.yml down || { echo -e "${RED}❌ Failed to shut down containers.${NC}"; exit 1; }

echo -e "${GREEN}🚀 Starting new containers...${NC}"
docker compose -f docker compose.yml up -d || { echo -e "${RED}❌ Failed to start containers.${NC}"; exit 1; }

echo -e "${GREEN}✅ Update complete! Containers are up and running.${NC}"
