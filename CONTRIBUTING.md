# Contributing to Atlas4D Base

Thank you for your interest in contributing to Atlas4D Base! This document provides guidelines for contributing.

## 🚀 Quick Start for Contributors

### 1. Fork and Clone
```bash
git clone https://github.com/YOUR_USERNAME/atlas4d-base.git
cd atlas4d-base
```

### 2. Start the Stack
```bash
docker compose up -d
```

### 3. Verify Everything Works
```bash
# Health check
curl http://localhost:8090/health

# Load demo data
docker compose exec postgres psql -U atlas4d_app -d atlas4d \
  -f /docker-entrypoint-initdb.d/seed/demo_burgas.sql

# Test API
curl http://localhost:8090/api/stats
```

### 4. Open the Map

Visit http://localhost:8091 - you should see the Burgas demo.

---

## 📁 Project Structure
```
atlas4d-base/
├── docker-compose.yml      # Main stack definition
├── .env.example            # Environment template
├── sql/
│   ├── schema/             # Database schema (runs on init)
│   │   └── 001_init.sql    # Core tables + extensions
│   └── seed/               # Demo data
│       ├── demo_burgas.sql # Mobility scenario
│       └── demo_telecom.sql# Network scenario
├── services/
│   ├── api-gateway/        # FastAPI backend
│   │   ├── main.py         # API endpoints
│   │   └── Dockerfile
│   └── frontend/           # Leaflet map UI
│       ├── index.html      # Single-page app
│       └── nginx.conf      # Reverse proxy config
└── docs/                   # Documentation
```

---

## 🔧 Development Workflow

### Adding a New API Endpoint

1. Edit `services/api-gateway/main.py`
2. Add your endpoint:
```python
@app.get("/api/your-endpoint")
async def your_endpoint():
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM atlas4d.your_table LIMIT 10")
        return [dict(row) for row in rows]
```

3. Rebuild and test:
```bash
docker compose build api-gateway
docker compose up -d api-gateway
curl http://localhost:8090/api/your-endpoint
```

### Adding a New Demo Seed

1. Create `sql/seed/demo_your_scenario.sql`:
```sql
-- Your Demo Scenario
-- Description: What this demo shows

INSERT INTO atlas4d.observations_core (t, lat, lon, geom, source_type, metadata)
SELECT 
    NOW() - (random() * INTERVAL '24 hours'),
    42.5 + (random() - 0.5) * 0.1,
    27.46 + (random() - 0.5) * 0.1,
    ST_SetSRID(ST_MakePoint(
        27.46 + (random() - 0.5) * 0.1,
        42.5 + (random() - 0.5) * 0.1
    ), 4326),
    'your_source_type',
    '{"demo": true, "scenario": "your_scenario"}'::jsonb
FROM generate_series(1, 100);

DO $$
BEGIN
    RAISE NOTICE 'Your demo loaded: 100 observations';
END $$;
```

2. Load it:
```bash
docker compose exec postgres psql -U atlas4d_app -d atlas4d \
  -f /docker-entrypoint-initdb.d/seed/demo_your_scenario.sql
```

### Modifying the Frontend

1. Edit `services/frontend/index.html`
2. Rebuild:
```bash
docker compose build frontend
docker compose up -d frontend
```

3. Hard refresh browser (Ctrl+Shift+R)

---

## ✅ Before Submitting a PR

### Run Smoke Tests
```bash
# Stack is healthy
curl -s http://localhost:8090/health | jq '.status'
# Should return: "healthy"

# API returns data
curl -s http://localhost:8090/api/stats | jq '.total_observations'
# Should return: a number > 0

# Frontend loads
curl -s -o /dev/null -w "%{http_code}" http://localhost:8091
# Should return: 200
```

### Code Style

- Python: Follow PEP 8
- SQL: Use lowercase keywords, uppercase table names
- Commit messages: Use conventional commits (`feat:`, `fix:`, `docs:`)

### PR Description Template
```markdown
## What does this PR do?

Brief description of changes.

## How to test

1. Step one
2. Step two
3. Expected result

## Checklist

- [ ] Stack starts with `docker compose up -d`
- [ ] Health endpoint returns healthy
- [ ] No breaking changes to existing API
```

---

## 🐛 Reporting Issues

When reporting issues, please include:

1. **Environment**: OS, Docker version
2. **Steps to reproduce**
3. **Expected vs actual behavior**
4. **Logs**: `docker compose logs <service>`

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.

---

## 💬 Questions?

Open a [GitHub Issue](https://github.com/crisbez/atlas4d-base/issues) or reach out at office@atlas4d.tech.
