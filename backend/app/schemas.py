from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ──────────────────────────── Auth ────────────────────────────

class UserCreate(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    username: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=4, max_length=128)


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ──────────────────────────── CheckIn ────────────────────────────

VALID_ACTIVITIES = [
    "coffee", "meal", "coding", "exercise", "meeting",
    "nap", "reading", "entertainment", "meditation", "socializing"
]

VALID_EMOTIONS = [
    "motivated", "calm", "happy", "neutral", "tired",
    "stressed", "anxious", "bored", "energized", "sleepy"
]


class CheckInCreate(BaseModel):
    energy_level: int = Field(..., ge=1, le=5)
    focus_level: int | None = Field(None, ge=1, le=5)
    activity: str = Field(..., min_length=1)
    emotions: list[str] | None = None
    note: str | None = Field(None, max_length=200)
    timestamp: datetime | None = None  # if None, server sets current time


class CheckInUpdate(BaseModel):
    energy_level: int | None = Field(None, ge=1, le=5)
    focus_level: int | None = Field(None, ge=1, le=5)
    activity: str | None = None
    emotions: list[str] | None = None
    note: str | None = Field(None, max_length=200)


class CheckInResponse(BaseModel):
    id: int
    user_id: int
    energy_level: int
    focus_level: int | None
    activity: str
    emotions: list[str] | None
    note: str | None
    timestamp: datetime

    class Config:
        from_attributes = True


# ──────────────────────────── Analytics ────────────────────────────

class DailyInsightResponse(BaseModel):
    date: str
    avg_energy: float
    avg_focus: float | None
    peak_hour: str | None
    peak_energy: float | None
    low_hour: str | None
    low_energy: float | None
    total_checkins: int
    recommendation: str


class HeatmapCell(BaseModel):
    day_of_week: int  # 0=Monday, 6=Sunday
    hour: int         # 6-22
    avg_energy: float
    count: int


class HeatmapResponse(BaseModel):
    cells: list[HeatmapCell]


class CorrelationItem(BaseModel):
    activity: str
    avg_energy: float
    avg_focus: float | None
    delta_energy: float  # difference from global average
    count: int
    insight: str


class EmotionCorrelation(BaseModel):
    emotion: str
    avg_energy: float
    avg_focus: float | None
    count: int


class CorrelationResponse(BaseModel):
    global_avg_energy: float
    global_avg_focus: float | None
    activity_correlations: list[CorrelationItem]
    emotion_correlations: list[EmotionCorrelation]
    top_booster: str | None
    top_drainer: str | None


class ScheduleBlock(BaseModel):
    hour: int
    avg_energy: float
    zone: str           # "high", "medium", "low"
    suggestion: str
    emoji: str
    tips: list[str] | None = None  # remedial tips for low-energy hours


class ScheduleResponse(BaseModel):
    hourly: list[ScheduleBlock]
    peak_block: str | None
    dip_block: str | None
    golden_hour: str | None
    summary: str


# ──────────────────────────── Task Planner ────────────────────────────

class TaskItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    duration_minutes: int = Field(60, ge=15, le=480)
    priority: str = Field("medium", pattern="^(high|medium|low)$")

class TaskPlanRequest(BaseModel):
    tasks: list[TaskItem] = Field(..., min_length=1, max_length=20)
    start_date: str | None = None  # YYYY-MM-DD, defaults to N days ago
    end_date: str | None = None    # YYYY-MM-DD, defaults to today
    days: int | None = 14

class PlannedTask(BaseModel):
    name: str
    start_hour: int
    end_hour: int
    zone: str
    priority: str
    reason: str

class TaskPlanResponse(BaseModel):
    planned_tasks: list[PlannedTask]
    unplanned_tasks: list[str]
    summary: str

