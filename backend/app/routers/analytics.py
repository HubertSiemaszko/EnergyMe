from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import (
    DailyInsightResponse, HeatmapResponse, HeatmapCell,
    CorrelationResponse, CorrelationItem, EmotionCorrelation,
    ScheduleResponse, ScheduleBlock,
    TaskPlanRequest, TaskPlanResponse, PlannedTask,
)
from ..auth import get_current_user
from ..services.analytics import get_daily_insight, get_weekly_heatmap
from ..services.correlations import get_correlations
from ..services.scheduler import get_schedule_recommendations, plan_tasks

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/daily", response_model=DailyInsightResponse)
def daily_insight(
    target_date: str = Query(None, alias="date", description="Date (YYYY-MM-DD), defaults to today"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get daily energy insight with peak/low hours and recommendations (F4)."""
    if target_date:
        try:
            d = date.fromisoformat(target_date)
        except ValueError:
            d = date.today()
    else:
        d = date.today()

    result = get_daily_insight(db, current_user.id, d)
    return DailyInsightResponse(**result)


@router.get("/weekly", response_model=HeatmapResponse)
def weekly_heatmap(
    weeks: int = Query(2, ge=1, le=8, description="Number of weeks to include"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get heatmap data: average energy per (day_of_week, hour) cell (F6)."""
    cells = get_weekly_heatmap(db, current_user.id, weeks)
    return HeatmapResponse(cells=[HeatmapCell(**c) for c in cells])


@router.get("/correlations", response_model=CorrelationResponse)
def correlations(
    days: int = Query(14, ge=1, le=365),
    start_date: str = Query(None, alias="start"),
    end_date: str = Query(None, alias="end"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get activity & emotion correlations with energy/focus (F7)."""
    result = get_correlations(db, current_user.id, days)
    return CorrelationResponse(
        global_avg_energy=result["global_avg_energy"],
        global_avg_focus=result["global_avg_focus"],
        activity_correlations=[CorrelationItem(**a) for a in result["activity_correlations"]],
        emotion_correlations=[EmotionCorrelation(**e) for e in result["emotion_correlations"]],
        top_booster=result["top_booster"],
        top_drainer=result["top_drainer"],
    )


@router.get("/schedule", response_model=ScheduleResponse)
def schedule(
    days: int = Query(14, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get smart schedule recommendations based on energy patterns (F8)."""
    result = get_schedule_recommendations(db, current_user.id, days)
    return ScheduleResponse(
        hourly=[ScheduleBlock(**h) for h in result["hourly"]],
        peak_block=result["peak_block"],
        dip_block=result["dip_block"],
        golden_hour=result["golden_hour"],
        summary=result["summary"],
    )


@router.post("/plan", response_model=TaskPlanResponse)
def plan(
    request: TaskPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Plan user tasks into optimal time slots based on energy patterns."""
    start = None
    end = None
    if request.start_date:
        try:
            start = datetime.fromisoformat(request.start_date)
        except ValueError:
            pass
    if request.end_date:
        try:
            end = datetime.fromisoformat(request.end_date)
        except ValueError:
            pass

    tasks = [{"name": t.name, "duration_minutes": t.duration_minutes, "priority": t.priority} for t in request.tasks]
    result = plan_tasks(db, current_user.id, tasks, days=request.days or 14, start_date=start, end_date=end)
    return TaskPlanResponse(
        planned_tasks=[PlannedTask(**p) for p in result["planned_tasks"]],
        unplanned_tasks=result["unplanned_tasks"],
        summary=result["summary"],
    )

