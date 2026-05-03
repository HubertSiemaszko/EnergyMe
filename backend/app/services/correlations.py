"""
Correlations service (F7).
Analyzes how different activities and emotions correlate with energy and focus levels.
"""
import json
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy.orm import Session

from ..models import CheckIn


def get_correlations(db: Session, user_id: int, days: int = 14) -> dict:
    """
    Compute correlations between activities/emotions and energy/focus levels.
    
    Returns:
        - global averages
        - per-activity energy & focus averages with delta from global
        - per-emotion energy & focus averages
        - top booster and drainer activities
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    checkins = (
        db.query(CheckIn)
        .filter(
            CheckIn.user_id == user_id,
            CheckIn.timestamp >= start_date,
        )
        .all()
    )

    if not checkins:
        return {
            "global_avg_energy": 0,
            "global_avg_focus": None,
            "activity_correlations": [],
            "emotion_correlations": [],
            "top_booster": None,
            "top_drainer": None,
        }

    # ── Global averages ──
    all_energy = [c.energy_level for c in checkins]
    global_avg_energy = round(sum(all_energy) / len(all_energy), 2)

    focus_vals = [c.focus_level for c in checkins if c.focus_level is not None]
    global_avg_focus = round(sum(focus_vals) / len(focus_vals), 2) if focus_vals else None

    # ── Activity correlations ──
    by_activity = defaultdict(list)
    for c in checkins:
        by_activity[c.activity].append(c)

    activity_labels = {
        "coffee": "Kawa/herbata ☕", "meal": "Posiłek 🍽️",
        "coding": "Kodowanie 💻", "exercise": "Ćwiczenia 🏃",
        "meeting": "Spotkanie 🤝", "nap": "Drzemka 😴",
        "reading": "Czytanie 📖", "entertainment": "Rozrywka 🎮",
        "meditation": "Medytacja 🧘", "socializing": "Rozmowy 💬",
    }

    activity_correlations = []
    for activity, group in by_activity.items():
        avg_e = round(sum(c.energy_level for c in group) / len(group), 2)
        focus_g = [c.focus_level for c in group if c.focus_level is not None]
        avg_f = round(sum(focus_g) / len(focus_g), 2) if focus_g else None
        delta = round(avg_e - global_avg_energy, 2)

        insight = _generate_activity_insight(activity, delta, avg_e, activity_labels)

        activity_correlations.append({
            "activity": activity,
            "avg_energy": avg_e,
            "avg_focus": avg_f,
            "delta_energy": delta,
            "count": len(group),
            "insight": insight,
        })

    # Sort by delta (highest boost first)
    activity_correlations.sort(key=lambda x: x["delta_energy"], reverse=True)

    # ── Emotion correlations ──
    by_emotion = defaultdict(list)
    for c in checkins:
        if c.emotions:
            try:
                emotions = json.loads(c.emotions)
                for emotion in emotions:
                    by_emotion[emotion].append(c)
            except json.JSONDecodeError:
                pass

    emotion_correlations = []
    for emotion, group in by_emotion.items():
        avg_e = round(sum(c.energy_level for c in group) / len(group), 2)
        focus_g = [c.focus_level for c in group if c.focus_level is not None]
        avg_f = round(sum(focus_g) / len(focus_g), 2) if focus_g else None

        emotion_correlations.append({
            "emotion": emotion,
            "avg_energy": avg_e,
            "avg_focus": avg_f,
            "count": len(group),
        })

    emotion_correlations.sort(key=lambda x: x["avg_energy"], reverse=True)

    # ── Top booster / drainer ──
    top_booster = activity_correlations[0]["activity"] if activity_correlations and activity_correlations[0]["delta_energy"] > 0 else None
    top_drainer = activity_correlations[-1]["activity"] if activity_correlations and activity_correlations[-1]["delta_energy"] < 0 else None

    return {
        "global_avg_energy": global_avg_energy,
        "global_avg_focus": global_avg_focus,
        "activity_correlations": activity_correlations,
        "emotion_correlations": emotion_correlations,
        "top_booster": top_booster,
        "top_drainer": top_drainer,
    }


def _generate_activity_insight(activity: str, delta: float, avg_energy: float, labels: dict) -> str:
    """Generate a textual insight for an activity's correlation with energy."""
    label = labels.get(activity, activity)
    abs_delta = abs(delta)

    if delta > 0.5:
        return f"Po {label} Twoja energia jest wyższa o {abs_delta:.1f} pkt od średniej! To Twój energy booster 🚀"
    elif delta > 0:
        return f"Po {label} masz lekko wyższą energię (+{abs_delta:.1f}). Dobry wpływ!"
    elif delta > -0.5:
        return f"Po {label} Twoja energia jest lekko niższa ({delta:.1f}). Nic niepokojącego."
    else:
        return f"Po {label} Twoja energia spada o {abs_delta:.1f} pkt. Rozważ przerwę po tej aktywności 💡"
