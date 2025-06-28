#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status


echo "?? Building containers (dry-run)..."
docker-compose -f docker-compose.yml build || { echo "? Build failed. Aborting update."; exit 1; }

echo "?? Shutting down current containers..."
docker-compose -f docker-compose.yml down

echo "?? Starting new containers..."
docker-compose -f docker-compose.yml up -d

echo "? Update complete!"
exit 0chmo