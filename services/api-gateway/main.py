"""
Atlas4D Base - Minimal API Gateway
Provides health check and basic observation queries
"""
import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager

import asyncpg
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "atlas4d")
POSTGRES_USER = os.getenv("POSTGRES_USER", "atlas4d_app")
POSTGRES_PASSWORD = os.getenv("PGPASSWORD", "atlas4d_dev")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Global connections
db_pool: Optional[asyncpg.Pool] = None
redis_client: Optional[redis.Redis] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global db_pool, redis_client
    
    # Startup
    print("🚀 Starting Atlas4D Base API Gateway...")
    
    # Connect to PostgreSQL
    for attempt in range(5):
        try:
            db_pool = await asyncpg.create_pool(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                database=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                min_size=2,
                max_size=10
            )
            print("✅ PostgreSQL connected")
            break
        except Exception as e:
            print(f"⏳ Waiting for PostgreSQL... ({attempt + 1}/5)")
            await asyncio.sleep(2)
    
    # Connect to Redis
    try:
        redis_client = redis.from_url(REDIS_URL)
        await redis_client.ping()
        print("✅ Redis connected")
    except Exception as e:
        print(f"⚠️ Redis not available: {e}")
        redis_client = None
    
    print("🎉 Atlas4D Base API Gateway ready!")
    
    yield
    
    # Shutdown
    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()
    print("👋 Atlas4D Base API Gateway stopped")


app = FastAPI(
    title="Atlas4D Base API",
    description="Minimal API for Atlas4D Base - Open 4D Spatiotemporal Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class HealthResponse(BaseModel):
    status: str
    postgres: str
    redis: str
    version: str


class Observation(BaseModel):
    id: int
    t: datetime
    lat: float
    lon: float
    source_type: Optional[str]
    speed_ms: Optional[float]
    heading_deg: Optional[float]


class ObservationCreate(BaseModel):
    lat: float
    lon: float
    source_type: str = "manual"
    speed_ms: Optional[float] = None
    heading_deg: Optional[float] = None
    metadata: Optional[dict] = None


class StatsResponse(BaseModel):
    total_observations: int
    total_anomalies: int
    sources: dict
    last_observation: Optional[datetime]


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    pg_status = "healthy"
    redis_status = "healthy"
    
    # Check PostgreSQL
    if db_pool:
        try:
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
        except Exception:
            pg_status = "unhealthy"
    else:
        pg_status = "not connected"
    
    # Check Redis
    if redis_client:
        try:
            await redis_client.ping()
        except Exception:
            redis_status = "unhealthy"
    else:
        redis_status = "not connected"
    
    return HealthResponse(
        status="healthy" if pg_status == "healthy" else "degraded",
        postgres=pg_status,
        redis=redis_status,
        version="1.0.0"
    )


@app.get("/api/observations", response_model=List[Observation])
async def get_observations(
    lat: Optional[float] = Query(None, description="Center latitude"),
    lon: Optional[float] = Query(None, description="Center longitude"),
    radius_km: float = Query(10, description="Radius in kilometers"),
    hours: int = Query(24, description="Hours to look back"),
    limit: int = Query(100, description="Maximum results")
):
    """Get observations, optionally filtered by location and time"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")
    
    async with db_pool.acquire() as conn:
        if lat is not None and lon is not None:
            # Spatial query
            query = """
                SELECT id, t, lat, lon, source_type, speed_ms, heading_deg
                FROM atlas4d.observations_core
                WHERE t > NOW() - INTERVAL '%s hours'
                AND ST_DWithin(
                    geom::geography,
                    ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
                    $3 * 1000
                )
                ORDER BY t DESC
                LIMIT $4
            """
            rows = await conn.fetch(query.replace('%s', str(hours)), lon, lat, radius_km, limit)
        else:
            # Simple time-based query
            query = """
                SELECT id, t, lat, lon, source_type, speed_ms, heading_deg
                FROM atlas4d.observations_core
                WHERE t > NOW() - INTERVAL '%s hours'
                ORDER BY t DESC
                LIMIT $1
            """
            rows = await conn.fetch(query.replace('%s', str(hours)), limit)
        
        return [Observation(**dict(row)) for row in rows]


@app.post("/api/observations", response_model=dict)
async def create_observation(obs: ObservationCreate):
    """Create a new observation"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")
    
    async with db_pool.acquire() as conn:
        query = """
            INSERT INTO atlas4d.observations_core 
            (t, lat, lon, geom, source_type, speed_ms, heading_deg, metadata)
            VALUES (
                NOW(), $1, $2, 
                ST_SetSRID(ST_MakePoint($3, $4), 4326),
                $5, $6, $7, $8
            )
            RETURNING id
        """
        obs_id = await conn.fetchval(
            query, 
            obs.lat, obs.lon, obs.lon, obs.lat,
            obs.source_type, obs.speed_ms, obs.heading_deg,
            obs.metadata or {}
        )
        return {"id": obs_id, "status": "created"}


@app.get("/api/anomalies", response_model=List[dict])
async def get_anomalies(
    hours: int = Query(24, description="Hours to look back"),
    severity_min: int = Query(1, description="Minimum severity (1-5)"),
    limit: int = Query(50, description="Maximum results")
):
    """Get recent anomalies"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")
    
    async with db_pool.acquire() as conn:
        query = """
            SELECT a.id, a.anomaly_type, a.severity, a.score, a.detected_at,
                   o.lat, o.lon, o.source_type
            FROM atlas4d.anomalies a
            LEFT JOIN atlas4d.observations_core o ON a.observation_id = o.id
            WHERE a.detected_at > NOW() - INTERVAL '%s hours'
            AND a.severity >= $1
            ORDER BY a.detected_at DESC
            LIMIT $2
        """
        rows = await conn.fetch(query.replace('%s', str(hours)), severity_min, limit)
        return [dict(row) for row in rows]


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get platform statistics"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")
    
    async with db_pool.acquire() as conn:
        # Total observations
        total_obs = await conn.fetchval(
            "SELECT COUNT(*) FROM atlas4d.observations_core"
        ) or 0
        
        # Total anomalies
        total_anom = await conn.fetchval(
            "SELECT COUNT(*) FROM atlas4d.anomalies"
        ) or 0
        
        # Sources breakdown
        sources_rows = await conn.fetch("""
            SELECT source_type, COUNT(*) as count
            FROM atlas4d.observations_core
            GROUP BY source_type
        """)
        sources = {row['source_type'] or 'unknown': row['count'] for row in sources_rows}
        
        # Last observation
        last_obs = await conn.fetchval(
            "SELECT MAX(t) FROM atlas4d.observations_core"
        )
        
        return StatsResponse(
            total_observations=total_obs,
            total_anomalies=total_anom,
            sources=sources,
            last_observation=last_obs
        )


@app.get("/api/geojson/observations")
async def get_observations_geojson(
    hours: int = Query(24, description="Hours to look back"),
    limit: int = Query(500, description="Maximum results")
):
    """Get observations as GeoJSON for map display"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")
    
    async with db_pool.acquire() as conn:
        query = """
            SELECT id, t, lat, lon, source_type, speed_ms
            FROM atlas4d.observations_core
            WHERE t > NOW() - INTERVAL '%s hours'
            ORDER BY t DESC
            LIMIT $1
        """
        rows = await conn.fetch(query.replace('%s', str(hours)), limit)
        
        features = []
        for row in rows:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row['lon'], row['lat']]
                },
                "properties": {
                    "id": row['id'],
                    "time": row['t'].isoformat() if row['t'] else None,
                    "source_type": row['source_type'],
                    "speed_ms": row['speed_ms']
                }
            })
        
        return {
            "type": "FeatureCollection",
            "features": features
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
