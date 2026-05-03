import json
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, CheckIn
from ..schemas import CheckInCreate, CheckInUpdate, CheckInResponse
from ..auth import get_current_user

router = APIRouter(prefix="/api/checkins", tags=["Check-ins"])


def _checkin_to_response(checkin: CheckIn) -> CheckInResponse:
    """Convert a CheckIn ORM object to a response schema."""
    emotions = None
    if checkin.emotions:
        try:
            emotions = json.loads(checkin.emotions)
        except json.JSONDecodeError:
            emotions = []
    return CheckInResponse(
        id=checkin.id,
        user_id=checkin.user_id,
        energy_level=checkin.energy_level,
        focus_level=checkin.focus_level,
        activity=checkin.activity,
        emotions=emotions,
        note=checkin.note,
        timestamp=checkin.timestamp,
    )


@router.post("/", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def create_checkin(
    data: CheckInCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new energy check-in."""
    checkin = CheckIn(
        user_id=current_user.id,
        energy_level=data.energy_level,
        focus_level=data.focus_level,
        activity=data.activity,
        emotions=json.dumps(data.emotions) if data.emotions else None,
        note=data.note,
        timestamp=data.timestamp or datetime.utcnow(),
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)

    return _checkin_to_response(checkin)


@router.get("/", response_model=list[CheckInResponse])
def get_checkins(
    date_str: str | None = Query(None, alias="date", description="Filter by date (YYYY-MM-DD)"),
    from_date: str | None = Query(None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(None, alias="to", description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get check-ins filtered by date or date range."""
    query = db.query(CheckIn).filter(CheckIn.user_id == current_user.id)

    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date, datetime.max.time())
        query = query.filter(CheckIn.timestamp >= start, CheckIn.timestamp <= end)
    elif from_date or to_date:
        if from_date:
            try:
                start = datetime.combine(date.fromisoformat(from_date), datetime.min.time())
                query = query.filter(CheckIn.timestamp >= start)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid 'from' date format")
        if to_date:
            try:
                end = datetime.combine(date.fromisoformat(to_date), datetime.max.time())
                query = query.filter(CheckIn.timestamp <= end)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid 'to' date format")

    checkins = query.order_by(CheckIn.timestamp.asc()).all()
    return [_checkin_to_response(c) for c in checkins]


@router.put("/{checkin_id}", response_model=CheckInResponse)
def update_checkin(
    checkin_id: int,
    data: CheckInUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing check-in."""
    checkin = db.query(CheckIn).filter(
        CheckIn.id == checkin_id,
        CheckIn.user_id == current_user.id
    ).first()

    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")

    if data.energy_level is not None:
        checkin.energy_level = data.energy_level
    if data.focus_level is not None:
        checkin.focus_level = data.focus_level
    if data.activity is not None:
        checkin.activity = data.activity
    if data.emotions is not None:
        checkin.emotions = json.dumps(data.emotions)
    if data.note is not None:
        checkin.note = data.note

    db.commit()
    db.refresh(checkin)

    return _checkin_to_response(checkin)


@router.delete("/{checkin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkin(
    checkin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a check-in."""
    checkin = db.query(CheckIn).filter(
        CheckIn.id == checkin_id,
        CheckIn.user_id == current_user.id
    ).first()

    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")

    db.delete(checkin)
    db.commit()
