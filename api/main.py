import os
from contextlib import asynccontextmanager
from datetime import datetime

import asyncpg
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel, Field, field_validator

load_dotenv()


BBOX = (48.68, -122.55, 48.82, -122.35)


def validate_bellingham(lat: float, lon: float) -> None:
    south, west, north, east = BBOX
    if not (south <= lat <= north and west <= lon <= east):
        raise ValueError(f"Coordinates ({lat}, {lon}) outside Bellingham bbox")


class ObstacleCreate(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    obstacle_type: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("lon")
    @classmethod
    def validate_bbox(cls, lon: float, info):
        lat = info.data.get("lat")
        if lat is not None:
            validate_bellingham(lat, lon)
        return lon


class ObstacleRead(BaseModel):
    id: int
    lat: float
    lon: float
    obstacle_type: str
    description: str | None
    created_at: datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        os.getenv("DATABASE_URL"),
        min_size=1,
        max_size=5,
    )
    yield
    await app.state.pool.close()


app = FastAPI(lifespan=lifespan)


async def get_db(request: Request) -> asyncpg.Connection:
    async with request.app.state.pool.acquire() as conn:
        yield conn


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/obstacles", response_model=ObstacleRead, status_code=201)
async def create_obstacle(
    obstacle: ObstacleCreate,
    conn: asyncpg.Connection = Depends(get_db),
):
    row = await conn.fetchrow(
        """
        INSERT INTO obstacles (lat, lon, obstacle_type, description)
        VALUES ($1, $2, $3, $4)
        RETURNING id, lat, lon, obstacle_type, description, created_at
        """,
        obstacle.lat,
        obstacle.lon,
        obstacle.obstacle_type,
        obstacle.description,
    )
    return dict(row)
