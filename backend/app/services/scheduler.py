"""
Smart Scheduler service (F8).
Analyzes historical energy patterns to recommend an optimal daily schedule.
"""
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy.orm import Session

from ..models import CheckIn


def get_schedule_recommendations(db: Session, user_id: int, days: int = 14) -> dict:
    """
    Analyze the user's energy patterns over the past N days and generate
    an optimal daily schedule with productivity zones.
    
    Zones:
        - high (avg >= 3.5): Deep work, coding, complex tasks
        - medium (2.5 <= avg < 3.5): Meetings, code review, email
        - low (avg < 2.5): Break, walk, relaxation
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
        hour = c.timestamp.hour
        hourly_data[hour].append(c.energy_level)

    # Generate schedule blocks for hours 6-22
    hourly_blocks = []
    for hour in range(6, 23):
        energies = hourly_data.get(hour, [])
        if energies:
            avg_energy = round(sum(energies) / len(energies), 2)
        else:
            avg_energy = 3.0  # default to medium if no data for this hour

        zone, suggestion, emoji = _classify_zone(avg_energy)
        hourly_blocks.append({
            "hour": hour,
            "avg_energy": avg_energy,
            "zone": zone,
            "suggestion": suggestion,
            "emoji": emoji,
        })

    # ── Find peak and dip blocks ──
    peak_block = _find_best_block(hourly_blocks, "high")
    dip_block = _find_best_block(hourly_blocks, "low")

    # ── Find golden hour (single highest energy hour) ──
    hours_with_data = [(h, sum(hourly_data[h]) / len(hourly_data[h]))
                       for h in hourly_data if hourly_data[h]]
    golden_hour = None
    if hours_with_data:
        best_hour, best_avg = max(hours_with_data, key=lambda x: x[1])
        golden_hour = f"{best_hour:02d}:00"

    # ── Generate summary ──
    summary = _generate_summary(peak_block, dip_block, golden_hour)

    return {
        "hourly": hourly_blocks,
        "peak_block": peak_block,
        "dip_block": dip_block,
        "golden_hour": golden_hour,
        "summary": summary,
    }


def _classify_zone(avg_energy: float) -> tuple[str, str, str]:
    """Classify an hour into a productivity zone."""
    if avg_energy >= 3.5:
        return (
            "high",
            "Deep work: kodowanie, trudne zadania, nauka",
            "💻"
        )
    elif avg_energy >= 2.5:
        return (
            "medium",
            "Spotkania, code review, email, rutynowe zadania",
            "🤝"
        )
    else:
        return (
            "low",
            "Przerwa, spacer, relaks, lekkie zadania",
            "☕"
        )


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

    # Check last block
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
        parts.append(f"Planuj coding i trudne zadania na {peak_block}.")

    if dip_block:
        parts.append(f"Zaplanuj przerwę lub spacer na {dip_block} — wtedy Twoja energia jest najniższa.")

    if not parts:
        return "Dodaj więcej check-inów, aby otrzymać spersonalizowane rekomendacje."

    return " ".join(parts)


def plan_tasks(db: Session, user_id: int, tasks: list[dict], days: int = 14,
               start_date: datetime | None = None, end_date: datetime | None = None) -> dict:
    """
    Given a list of tasks with priority and duration, assign them to optimal
    time slots based on the user's historical energy patterns.
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

        # For high priority → pick highest energy slots
        # For low priority → pick lowest energy slots (save high energy for important tasks)
        if task["priority"] == "low":
            candidates = sorted(hourly_avg.items(), key=lambda x: x[1])
        else:
            candidates = hours_by_energy

        for start_h, avg_e in candidates:
            # Check if we have enough contiguous hours
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

    # Sort planned tasks by start hour
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

