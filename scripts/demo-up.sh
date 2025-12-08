#!/bin/bash
# Atlas4D Base - Quick Demo Launcher
# Time to first map: ~3 minutes

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BOLD}🌐 Atlas4D Base - Quick Demo${NC}"
echo "================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker detected"

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from example..."
    cp .env.example .env
fi

# Start services
echo ""
echo -e "${BLUE}🚀 Starting Atlas4D services...${NC}"
echo ""

docker compose up -d --build

# Wait for health
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check health
MAX_WAIT=60
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8090/health | grep -q "ok"; then
        break
    fi
    sleep 2
    WAITED=$((WAITED + 2))
    echo "   Waiting... ($WAITED/$MAX_WAIT seconds)"
done

if [ $WAITED -ge $MAX_WAIT ]; then
    echo "⚠️  Services taking longer than expected. Check: docker compose logs"
else
    echo "✅ Services healthy!"
fi

# Print URLs
echo ""
echo -e "${GREEN}${BOLD}🎉 Atlas4D is ready!${NC}"
echo ""
echo "📍 Open in your browser:"
echo ""
echo -e "   ${BOLD}Map UI:${NC}        http://localhost:8091"
echo -e "   ${BOLD}API Health:${NC}    http://localhost:8090/health"
echo -e "   ${BOLD}API Stats:${NC}     http://localhost:8090/api/stats"
echo -e "   ${BOLD}Observations:${NC}  http://localhost:8090/api/observations?limit=10"
echo ""
echo "📚 Docs: https://github.com/crisbez/atlas4d-base/tree/main/docs"
echo ""
echo "To stop: docker compose down"
echo ""
