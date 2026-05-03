"""
Seed data generator for demo purposes.
Creates a demo user and 14 days of realistic check-in data.
"""
import json
import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .models import User, CheckIn
from .auth import hash_password


ACTIVITIES = ["coffee", "meal", "coding", "exercise", "meeting", "nap", "reading", "entertainment", "meditation", "socializing"]

EMOTIONS = ["motivated", "calm", "happy", "neutral", "tired", "stressed", "anxious", "bored", "energized", "sleepy"]

# Realistic energy patterns by time of day (hour -> base energy)
ENERGY_PROFILE = {
    7: 2.5, 8: 3.0, 9: 3.8, 10: 4.2, 11: 4.0,
    12: 3.5, 13: 2.8, 14: 2.3, 15: 2.8, 16: 3.2,
    17: 3.5, 18: 3.0, 19: 2.8, 20: 2.5, 21: 2.0,
}

# Activity effect on energy (delta from base)
ACTIVITY_EFFECTS = {
    "coffee": 0.8, "meal": -0.3, "coding": 0.2, "exercise": 1.0,
    "meeting": -0.5, "nap": 0.5, "reading": 0.0, "entertainment": 0.3,
    "meditation": 0.6, "socializing": 0.1,
}

# Typical activities by time of day
TYPICAL_ACTIVITIES = {
    7: ["coffee", "meal"],
    8: ["coffee", "coding", "reading"],
    9: ["coding", "meeting", "coffee"],
    10: ["coding", "meeting"],
    11: ["coding", "meeting", "coffee"],
    12: ["meal", "socializing"],
    13: ["meal", "coding", "nap"],
    14: ["coding", "meeting", "coffee"],
    15: ["coding", "meeting", "coffee"],
    16: ["coding", "exercise", "coffee"],
    17: ["exercise", "coding", "socializing"],
    18: ["meal", "exercise", "socializing"],
    19: ["entertainment", "reading", "socializing"],
    20: ["entertainment", "reading", "meditation"],
    21: ["meditation", "reading", "entertainment"],
}


def seed_demo_data(db: Session) -> dict:
    """
    Create or reset the demo user and generate 14 days of realistic check-in data.
    Returns info about what was created.
    """
    # Create or get demo user
    demo_user = db.query(User).filter(User.email == "demo@energymap.com").first()

    if demo_user:
        # Delete existing check-ins for demo user
        db.query(CheckIn).filter(CheckIn.user_id == demo_user.id).delete()
    else:
        demo_user = User(
            email="demo@energymap.com",
            username="demo",
            password_hash=hash_password("demo123"),
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

    # Generate 14 days of check-ins
    now = datetime.utcnow()
    checkins_created = 0

    for day_offset in range(14, 0, -1):
        day = now - timedelta(days=day_offset)

        # Skip some weekend hours randomly
        is_weekend = day.weekday() >= 5

        # Generate 3-5 check-ins per day
        num_checkins = random.randint(3, 5) if not is_weekend else random.randint(2, 4)
        hours = sorted(random.sample(list(ENERGY_PROFILE.keys()), min(num_checkins, len(ENERGY_PROFILE))))

        for hour in hours:
            # Skip early hours on weekends
            if is_weekend and hour < 9:
                continue

            # Pick activity based on time
            possible_activities = TYPICAL_ACTIVITIES.get(hour, ACTIVITIES)
            activity = random.choice(possible_activities)

            # Calculate energy with some randomness
            base_energy = ENERGY_PROFILE.get(hour, 3.0)
            activity_effect = ACTIVITY_EFFECTS.get(activity, 0)
            energy = base_energy + activity_effect + random.uniform(-0.5, 0.5)
            energy = max(1, min(5, round(energy)))

            # Focus correlates with energy but with some variance
            focus = max(1, min(5, energy + random.randint(-1, 1)))

            # Pick 1-3 random emotions (biased by energy)
            if energy >= 4:
                emotion_pool = ["motivated", "energized", "happy", "calm"]
            elif energy >= 3:
                emotion_pool = ["neutral", "calm", "happy", "motivated"]
            else:
                emotion_pool = ["tired", "stressed", "bored", "sleepy", "anxious"]
            num_emotions = random.randint(1, 2)
            emotions = random.sample(emotion_pool, min(num_emotions, len(emotion_pool)))

            # Random notes (occasional)
            note = None
            if random.random() < 0.3:
                notes_pool = [
                    "Dobry flow!", "Ciężko się skupić", "Po przerwie lepiej",
                    "Zmęczony po spotkaniu", "Kawa pomogła", "Świetna sesja kodowania",
                    "Trzeba się przejść", "Produktywny poranek", "Za mało snu",
                    "Energia wraca", "Długi meeting", "Trening dał kopa",
                ]
                note = random.choice(notes_pool)

            # Create timestamp with some minute randomness
            timestamp = day.replace(hour=hour, minute=random.randint(0, 45), second=0, microsecond=0)

            checkin = CheckIn(
                user_id=demo_user.id,
                energy_level=energy,
                focus_level=focus,
                activity=activity,
                emotions=json.dumps(emotions),
                note=note,
                timestamp=timestamp,
            )
            db.add(checkin)
            checkins_created += 1

    db.commit()

    return {
        "message": "Demo data loaded successfully!",
        "user_email": "demo@energymap.com",
        "user_password": "demo123",
        "checkins_created": checkins_created,
        "days": 14,
    }
