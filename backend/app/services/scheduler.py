"""
Smart Scheduler service (F8).
Analyzes historical energy patterns to recommend an optimal daily schedule.
Includes activity time windows and context-aware remedial suggestions.
"""
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy.orm import Session

from ..models import CheckIn


# ── Activity time windows: (start_hour, end_hour) tuples ──
# Prevents absurd suggestions like "lunch at 11" or "coffee at 21"
ACTIVITY_WINDOWS = {
    "meal":          [(7, 9), (12, 14), (18, 20)],
    "coffee":        [(7, 11), (13, 16)],
    "exercise":      [(6, 9), (16, 20)],
    "nap":           [(13, 16)],
    "meditation":    [(6, 9), (19, 22)],
    "coding":        [(8, 20)],
    "meeting":       [(9, 17)],
    "reading":       [(6, 10), (19, 22)],
    "entertainment": [(18, 23)],
    "socializing":   [(10, 22)],
}

ACTIVITY_LABELS = {
    "coffee": "kawa", "meal": "posiłek", "coding": "kodowanie",
    "exercise": "ćwiczenia", "meeting": "spotkanie", "nap": "drzemka",
    "reading": "czytanie", "entertainment": "rozrywka",
    "meditation": "medytacja", "socializing": "rozmowy",
}


def _is_valid_time(activity: str, hour: int) -> bool:
    """Check if an activity makes sense at a given hour."""
    windows = ACTIVITY_WINDOWS.get(activity)
    if not windows:
        return True  # unknown/custom activities — always valid
    return any(start <= hour < end for start, end in windows)


def get_schedule_recommendations(db: Session, user_id: int, days: int = 14) -> dict:
    """
    Analyze the user's energy patterns over the past N days and generate
    an optimal daily schedule with productivity zones and remedial tips.
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
            "hourly": [],
            "peak_block": None,
            "dip_block": None,
            "golden_hour": None,
            "summary": "Potrzebuję więcej danych, aby wygenerować rekomendacje. Dodaj check-iny przez kilka dni!",
        }

    # ── Build hourly energy profile ──
    hourly_data = defaultdict(list)
    for c in checkins:
        hourly_data[c.timestamp.hour].append(c.energy_level)

    # ── Analyze activity → energy impact (for remedial tips) ──
    activity_energy = defaultdict(list)
    for c in checkins:
        activity_energy[c.activity].append(c.energy_level)

    # Calculate which activities historically boost energy
    global_avg = sum(c.energy_level for c in checkins) / len(checkins)
    activity_delta = {}
    for act, energies in activity_energy.items():
        avg = sum(energies) / len(energies)
        activity_delta[act] = round(avg - global_avg, 2)

    # Sort activities by positive impact (boosters first)
    boosters = sorted(
        [(act, delta) for act, delta in activity_delta.items() if delta > 0],
        key=lambda x: x[1], reverse=True,
    )

    # ── Generate schedule blocks for hours 6-22 ──
    hourly_blocks = []
    for hour in range(6, 23):
        energies = hourly_data.get(hour, [])
        if energies:
            avg_energy = round(sum(energies) / len(energies), 2)
        else:
            avg_energy = 3.0

        zone, suggestion, emoji = _classify_zone(avg_energy, hour)

        # Generate remedial tips for low/medium-low energy hours
        tips = None
        if avg_energy < 3.0:
            tips = _generate_tips(hour, avg_energy, boosters)

        hourly_blocks.append({
            "hour": hour,
            "avg_energy": avg_energy,
            "zone": zone,
            "suggestion": suggestion,
            "emoji": emoji,
            "tips": tips,
        })

    # ── Find peak and dip blocks ──
    peak_block = _find_best_block(hourly_blocks, "high")
    dip_block = _find_best_block(hourly_blocks, "low")

    # ── Find golden hour ──
    hours_with_data = [(h, sum(hourly_data[h]) / len(hourly_data[h]))
                       for h in hourly_data if hourly_data[h]]
    golden_hour = None
    if hours_with_data:
        best_hour, _ = max(hours_with_data, key=lambda x: x[1])
        golden_hour = f"{best_hour:02d}:00"

    summary = _generate_summary(peak_block, dip_block, golden_hour)

    return {
        "hourly": hourly_blocks,
        "peak_block": peak_block,
        "dip_block": dip_block,
        "golden_hour": golden_hour,
        "summary": summary,
    }


def _classify_zone(avg_energy: float, hour: int) -> tuple[str, str, str]:
    """Classify an hour into a productivity zone with time-aware suggestions."""
    if avg_energy >= 3.5:
        # High energy — suggest demanding work appropriate for the time
        if 8 <= hour <= 12:
            suggestion = "Deep work: kodowanie, trudne zadania, nauka"
        elif 13 <= hour <= 17:
            suggestion = "Produktywna praca: projekty, analiza, planowanie"
        else:
            suggestion = "Twórcza praca: side-projekty, nauka, pisanie"
        return ("high", suggestion, "")

    elif avg_energy >= 2.5:
        if 9 <= hour <= 17:
            suggestion = "Spotkania, code review, email, rutynowe zadania"
        elif hour >= 18:
            suggestion = "Lekkie zadania, porządki, planowanie jutra"
        else:
            suggestion = "Rozgrzewka dnia: email, planowanie, lekkie zadania"
        return ("medium", suggestion, "")

    else:
        if 12 <= hour <= 14:
            suggestion = "Przerwa obiadowa, spacer, odpoczynek"
        elif hour >= 19:
            suggestion = "Relaks, odpoczynek, przygotowanie do snu"
        else:
            suggestion = "Przerwa, spacer, rozciąganie, lekkie zadania"
        return ("low", suggestion, "")


def _generate_tips(hour: int, avg_energy: float, boosters: list[tuple[str, float]]) -> list[str]:
    """Generate contextual remedial tips for low-energy hours."""
    tips = []

    # Suggest activities that historically boosted energy AND are valid at this hour
    for act, delta in boosters[:5]:  # check top 5 boosters
        if _is_valid_time(act, hour):
            label = ACTIVITY_LABELS.get(act, act)
            tips.append(f"{label.capitalize()} — historycznie +{delta:.1f} do energii")
            if len(tips) >= 2:
                break

    # Time-specific contextual tips
    if 13 <= hour <= 15 and avg_energy < 2.5:
        tips.append("Popołudniowy dip — rozważ krótki spacer lub 15 min drzemki")
    elif 7 <= hour <= 9 and avg_energy < 3.0:
        tips.append("Trudny poranek — spróbuj rozruchu: rozciąganie lub lekkie ćwiczenia")
    elif hour >= 20 and avg_energy < 2.5:
        tips.append("Wieczorne zmęczenie — nie planuj wymagających zadań, odpocznij")

    # Don't return empty list
    return tips if tips else None


def _find_best_block(blocks: list[dict], target_zone: str) -> str | None:
    """Find the longest contiguous block of a given zone."""
    best_start = None
    best_length = 0
    current_start = None
    current_length = 0

    for block in blocks:
        if block["zone"] == target_zone:
            if current_start is None:
                current_start = block["hour"]
            current_length += 1
        else:
            if current_length > best_length:
                best_start = current_start
                best_length = current_length
            current_start = None
            current_length = 0

    if current_length > best_length:
        best_start = current_start
        best_length = current_length

    if best_start is not None and best_length > 0:
        end_hour = best_start + best_length
        return f"{best_start:02d}:00-{end_hour:02d}:00"
    return None


def _generate_summary(peak_block: str | None, dip_block: str | None, golden_hour: str | None) -> str:
    """Generate a natural language summary of the schedule recommendations."""
    parts = []

    if golden_hour:
        parts.append(f"Twoja złota godzina to {golden_hour} — wtedy masz najwięcej energii!")

    if peak_block:
        parts.append(f"Planuj trudne zadania na {peak_block}.")

    if dip_block:
        parts.append(f"Zaplanuj przerwę na {dip_block} — wtedy Twoja energia jest najniższa.")

    if not parts:
        return "Dodaj więcej check-inów, aby otrzymać spersonalizowane rekomendacje."

    return " ".join(parts)


def plan_tasks(db: Session, user_id: int, tasks: list[dict], days: int = 14,
               start_date: datetime | None = None, end_date: datetime | None = None) -> dict:
    """
    Given a list of tasks with priority and duration, assign them to optimal
    time slots based on the user's historical energy patterns.
    Uses activity time windows to avoid unrealistic scheduling.
    """
    if end_date is None:
        end_date = datetime.utcnow()
    if start_date is None:
        start_date = end_date - timedelta(days=days)

    checkins = (
        db.query(CheckIn)
        .filter(
            CheckIn.user_id == user_id,
            CheckIn.timestamp >= start_date,
            CheckIn.timestamp <= end_date,
        )
        .all()
    )

    if not checkins:
        return {
            "planned_tasks": [],
            "unplanned_tasks": [t["name"] for t in tasks],
            "summary": "Brak danych z wybranego okresu. Dodaj check-iny, aby system mógł zaplanować zadania.",
        }

    # Build hourly energy profile
    hourly_data = defaultdict(list)
    for c in checkins:
        hourly_data[c.timestamp.hour].append(c.energy_level)

    hourly_avg = {}
    for hour in range(6, 23):
        energies = hourly_data.get(hour, [])
        hourly_avg[hour] = round(sum(energies) / len(energies), 2) if energies else 3.0

    # Sort hours by energy (descending) for high-priority tasks
    hours_by_energy = sorted(hourly_avg.items(), key=lambda x: x[1], reverse=True)

    # Sort tasks: high priority first, then medium, then low
    priority_order = {"high": 0, "medium": 1, "low": 2}
    sorted_tasks = sorted(tasks, key=lambda t: priority_order.get(t["priority"], 1))

    # Assign tasks to time slots
    used_hours: set[int] = set()
    planned = []
    unplanned = []

    for task in sorted_tasks:
        duration_hours = max(1, round(task["duration_minutes"] / 60))
        assigned = False

        if task["priority"] == "low":
            candidates = sorted(hourly_avg.items(), key=lambda x: x[1])
        else:
            candidates = hours_by_energy

        for start_h, avg_e in candidates:
            slot_hours = list(range(start_h, start_h + duration_hours))
            if all(h in hourly_avg and h not in used_hours for h in slot_hours):
                for h in slot_hours:
                    used_hours.add(h)

                zone = "high" if avg_e >= 3.5 else ("medium" if avg_e >= 2.5 else "low")
                reason = _task_reason(task["priority"], zone, avg_e)
                planned.append({
                    "name": task["name"],
                    "start_hour": start_h,
                    "end_hour": start_h + duration_hours,
                    "zone": zone,
                    "priority": task["priority"],
                    "reason": reason,
                })
                assigned = True
                break

        if not assigned:
            unplanned.append(task["name"])

    planned.sort(key=lambda t: t["start_hour"])

    summary_parts = []
    high_tasks = [t for t in planned if t["priority"] == "high"]
    if high_tasks:
        summary_parts.append(f"{len(high_tasks)} ważnych zadań zaplanowanych w godzinach szczytowej energii.")
    if unplanned:
        summary_parts.append(f"{len(unplanned)} zadań nie zmieściło się w dostępnych slotach.")
    if not summary_parts:
        summary_parts.append(f"Zaplanowano {len(planned)} zadań w optymalnych godzinach.")

    return {
        "planned_tasks": planned,
        "unplanned_tasks": unplanned,
        "summary": " ".join(summary_parts),
    }


def _task_reason(priority: str, zone: str, avg_energy: float) -> str:
    if priority == "high" and zone == "high":
        return f"Szczytowa energia ({avg_energy:.1f}/5) — idealny moment na trudne zadanie."
    elif priority == "high" and zone == "medium":
        return f"Dobra energia ({avg_energy:.1f}/5) — wystarczająca na ważne zadanie."
    elif priority == "low" and zone == "low":
        return f"Niska energia ({avg_energy:.1f}/5) — odpowiedni czas na lekkie zadanie."
    else:
        return f"Energia {avg_energy:.1f}/5 w tym slocie."
