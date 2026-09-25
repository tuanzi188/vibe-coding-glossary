"""行程管理示例的 FastAPI 入口。"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Literal
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .database import fetch_all, get_connection, initialize_database


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"



@asynccontextmanager
async def application_lifespan(_application: FastAPI):
    """服务启动时初始化数据库，关闭时结束生命周期。"""

    initialize_database()
    yield


app = FastAPI(
    title="行程管理主线项目",
    version="0.1.0",
    lifespan=application_lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TripCreate(BaseModel):
    """新增行程的请求体。"""

    title: str = Field(min_length=1, max_length=80)
    destination: str = Field(min_length=1, max_length=40)
    days: int = Field(ge=1, le=30)
    budget: float = Field(ge=0, le=10_000_000)
    status: Literal["draft", "planned", "done"] = "draft"


class TripItem(BaseModel):
    """对外返回的行程结构。"""

    id: int
    title: str
    destination: str
    days: int
    budget: float
    status: str
    created_at: str


class TripPage(BaseModel):
    """分页返回结构。"""

    items: list[TripItem]
    page: int
    size: int
    total: int
    page_count: int
    has_next: bool


@app.get("/healthz")
def health_check() -> dict[str, str]:
    """返回服务健康状态。"""

    return {"status": "ok"}


@app.get("/api/trips", response_model=TripPage)
def list_trips(
    status_filter: Literal["draft", "planned", "done"] | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=6, ge=1, le=50),
) -> TripPage:
    """按状态分页查询行程。"""

    where = ""
    parameters: list[str] = []
    if status_filter:
        where = "WHERE status = ?"
        parameters.append(status_filter)
    rows = fetch_all(f"SELECT * FROM trips {where} ORDER BY id DESC", parameters)
    total = len(rows)
    page_count = max(1, math.ceil(total / size))
    if page > page_count:
        items: list[TripItem] = []
    else:
        start = (page - 1) * size
        items = [TripItem(**dict(row)) for row in rows[start : start + size]]
    return TripPage(
        items=items,
        page=page,
        size=size,
        total=total,
        page_count=page_count,
        has_next=page < page_count,
    )


@app.post("/api/trips", response_model=TripItem, status_code=status.HTTP_201_CREATED)
def create_trip(payload: TripCreate) -> TripItem:
    """创建一个行程。"""

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO trips (title, destination, days, budget, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (payload.title, payload.destination, payload.days, payload.budget, payload.status),
        )
        row = connection.execute(
            "SELECT * FROM trips WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return TripItem(**dict(row))


@app.delete("/api/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int) -> None:
    """删除一个行程。"""

    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="行程不存在")


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
