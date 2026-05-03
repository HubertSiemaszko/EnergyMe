"""
Analytics service — Daily Insights (F4).
Analyzes check-in data to find energy patterns within a single day.
"""
import json
from datetime import datetime, date, timedelta
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import CheckIn


def get_daily_insight(db: Session, user_id: int, target_date: date) -> dict:
    """Generate daily insight for a given date."""
    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date, datetime.max.time())

    checkins = (
        db.query(CheckIn)
        .filter(
            CheckIn.user_id == user_id,
            CheckIn.timestamp >= start,
            CheckIn.timestamp <= end,
        )
        .order_by(CheckIn.timestamp)
        .all()
    )

    if not checkins:
        return {
            "date": target_date.isoformat(),
            "avg_energy": 0,
            "avg_focus": None,
            "peak_hour": None,
            "peak_energy": None,
            "low_hour": None,
            "low_energy": None,
            "total_checkins": 0,
            "recommendation": "Brak danych na ten dzień. Dodaj check-iny, aby otrzymać rekomendacje!",
        }

    # Calculate averages
    energies = [c.energy_level for c in checkins]
    avg_energy = round(sum(energies) / len(energies), 2)

    focus_values = [c.focus_level for c in checkins if c.focus_level is not None]
    avg_focus = round(sum(focus_values) / len(focus_values), 2) if focus_values else None

    # Find peak and low points
    peak_checkin = max(checkins, key=lambda c: c.energy_level)
    low_checkin = min(checkins, key=lambda c: c.energy_level)

    peak_hour = peak_checkin.timestamp.strftime("%H:%M")
    low_hour = low_checkin.timestamp.strftime("%H:%M")

    # Generate recommendation
    recommendation = _generate_recommendation(
        peak_hour, peak_checkin.energy_level,
        low_hour, low_checkin.energy_level,
        avg_energy, peak_checkin.activity, low_checkin.activity
    )

    return {
        "date": target_date.isoformat(),
        "avg_energy": avg_energy,
        "avg_focus": avg_focus,
        "peak_hour": peak_hour,
        "peak_energy": peak_checkin.energy_level,
        "low_hour": low_hour,
        "low_energy": low_checkin.energy_level,
        "total_checkins": len(checkins),
        "recommendation": recommendation,
    }


def get_weekly_heatmap(db: Session, user_id: int, weeks: int = 2) -> list[dict]:
    """
    Generate heatmap data: average energy per (day_of_week, hour) slot.
    Returns a list of cells for the heatmap grid.
    """
    start_date = datetime.utcnow() - timedelta(weeks=weeks)

    checkins = (
        db.query(CheckIn)
        .filter(
            CheckIn.user_id == user_id,
            CheckIn.timestamp >= start_date,
        )
        .all()
    )

    # Group by (day_of_week, hour)
    slots = defaultdict(list)
    for c in checkins:
        dow = c.timestamp.weekday()  # 0=Monday, 6=Sunday
        hour = c.timestamp.hour
        slots[(dow, hour)].append(c.energy_level)

    cells = []
    for (dow, hour), energies in slots.items():
        cells.append({
            "day_of_week": dow,
            "hour": hour,
            "avg_energy": round(sum(energies) / len(energies), 2),
            "count": len(energies),
        })

    return cells


def _generate_recommendation(
    peak_hour: str, peak_energy: int,
    low_hour: str, low_energy: int,
    avg_energy: float, peak_activity: str, low_activity: str
) -> str:
    """Generate a personalized recommendation based on daily patterns."""
    activity_labels = {
        "coffee": "kawie", "meal": "posiłku", "coding": "kodowaniu",
        "exercise": "ćwiczeniach", "meeting": "spotkaniu", "nap": "drzemce",
        "reading": "czytaniu", "entertainment": "rozrywce",
        "meditation": "medytacji", "socializing": "rozmowach",
    }

    parts = []

    # Peak recommendation
    peak_label = activity_labels.get(peak_activity, peak_activity)
    parts.append(
        f"Twój szczyt energii ({peak_energy}/5) był o {peak_hour} — "
        f"planuj najtrudniejsze zadania w tej porze."
    )

    # Low recommendation
    if low_energy <= 2:
        low_label = activity_labels.get(low_activity, low_activity)
        parts.append(
            f"Spadek energii ({low_energy}/5) o {low_hour} po {low_label} — "
            f"zaplanuj wtedy przerwę lub spacer."
        )

    # Overall assessment
    if avg_energy >= 4:
        parts.append("Świetny dzień! Twoja średnia energia była bardzo wysoka.")
    elif avg_energy >= 3:
        parts.append("Dobry dzień. Spróbuj lepiej zarządzać przerwami, aby utrzymać energię.")
    else:
        parts.append("Ciężki dzień. Zastanów się, co mogło obniżyć Twoją energię i zadbaj o odpoczynek.")

    return " ".join(parts)
