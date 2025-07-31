import uuid
import random
from datetime import datetime, timedelta
import json

"""SmartHome Backend Generator

This script builds a realistic but compact DEFAULT_STATE structure for the
SmartHome API.  The schema does *not* have to match the public API one-for-one –
it simply needs to be rich enough for demos / tests.  Feel free to expand the
state further as new SmartHome API features get added.
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _random_iso_date(days_back: int = 365) -> str:
    """Return an ISO-8601 timestamp sometime in the last *days_back* days."""
    delta = timedelta(days=random.randint(0, days_back),
                     hours=random.randint(0, 23),
                     minutes=random.randint(0, 59),
                     seconds=random.randint(0, 59))
    return (datetime.utcnow() - delta).isoformat(timespec="seconds") + "Z"


_first_names = [
    "Olivia", "Liam", "Emma", "Noah", "Ava", "Elijah", "Sophia", "Lucas",
    "Isabella", "Mason", "Mia", "Ethan", "Charlotte", "Logan", "Amelia",
]
_last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzales",
]
_email_domains = ["gmail.com", "yahoo.com", "outlook.com", "proton.me", "icloud.com"]
_room_names = [
    "Living Room", "Kitchen", "Bedroom", "Bathroom", "Garage", "Office",
    "Patio", "Hallway", "Dining Room", "Basement", "Laundry Room", "Guest Room",
    "Nursery", "Balcony", "Attic"
]
_device_types = ["light", "thermostat", "lock", "switch", "sensor"]


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def _generate_user() -> tuple[str, dict]:
    first = random.choice(_first_names)
    last = random.choice(_last_names)
    user_id = str(uuid.uuid4())
    return user_id, {
        "first_name": first,
        "last_name": last,
        "email": f"{first.lower()}.{last.lower()}@{random.choice(_email_domains)}",
        "joined": _random_iso_date(365 * 3),
    }


def _generate_device(room: str | None = None) -> tuple[str, dict]:
    device_id = str(uuid.uuid4())
    d_type = random.choice(_device_types)

    if d_type == "light":
        state = {
            "on": random.random() < 0.7,
            "level": random.randint(0, 100),
            "color": {"hue": random.randint(0, 360), "saturation": random.randint(0, 100)},
        }
    elif d_type == "thermostat":
        state = {
            "mode": random.choice(["off", "heat", "cool", "auto"]),
            "temperature": random.randint(60, 80),
        }
    elif d_type == "lock":
        state = {"locked": random.random() < 0.5}
    elif d_type == "switch":
        state = {"on": random.random() < 0.5}
    else:  # sensor
        state = {
            "temperature": round(random.uniform(20, 35), 1),
            "humidity": random.randint(20, 80),
        }

    return device_id, {
        "name": f"{room} {d_type.title()}" if room else f"{d_type.title()} {device_id[:4]}",
        "type": d_type,
        "room": room,
        "state": state,
        "last_updated": _random_iso_date(30),
    }


# ---------------------------------------------------------------------------
# Build DEFAULT_STATE
# ---------------------------------------------------------------------------

DEFAULT_STATE: dict = {
    "users": {},
    "devices": {},
    "rooms": {},
    "scenes": {},
    "current_user": None,
}

# Users ----------------------------------------------------------------------
for _ in range(20):
    uid, udata = _generate_user()
    DEFAULT_STATE["users"][uid] = udata

DEFAULT_STATE["current_user"] = next(iter(DEFAULT_STATE["users"]))

# Rooms ----------------------------------------------------------------------
for r_name in _room_names:
    room_id = str(uuid.uuid4())
    DEFAULT_STATE["rooms"][room_id] = {"name": r_name}

# Devices --------------------------------------------------------------------
room_ids = list(DEFAULT_STATE["rooms"].keys())
for _ in range(200):  # generate ~200 devices
    room_choice = random.choice(room_ids)
    did, ddata = _generate_device(DEFAULT_STATE["rooms"][room_choice]["name"])
    ddata["room_id"] = room_choice
    DEFAULT_STATE["devices"][did] = ddata

# Scenes ---------------------------------------------------------------------
for _ in range(40):
    scene_id = str(uuid.uuid4())
    picked_devices = random.sample(list(DEFAULT_STATE["devices"].keys()), k=3)
    actions = []
    for pd in picked_devices:
        dev = DEFAULT_STATE["devices"][pd]
        if dev["type"] in ("light", "switch"):
            actions.append({"device_id": pd, "action": "on"})
        elif dev["type"] == "lock":
            actions.append({"device_id": pd, "action": "lock"})
        elif dev["type"] == "thermostat":
            actions.append({"device_id": pd, "action": "set", "temperature": 72})
    DEFAULT_STATE["scenes"][scene_id] = {
        "name": f"Scene {scene_id[:4]}",
        "actions": actions,
    }

# ---------------------------------------------------------------------------
# Debug summary print (for script usage)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("SmartHome backend generated ✨")
    print(f"Users      : {len(DEFAULT_STATE['users'])}")
    print(f"Rooms      : {len(DEFAULT_STATE['rooms'])}")
    print(f"Devices    : {len(DEFAULT_STATE['devices'])}")
    print(f"Scenes     : {len(DEFAULT_STATE['scenes'])}")

    # Optionally dump to JSON for offline usage
    # with open('diverse_smart_home_state.json', 'w') as f:
    #     json.dump(DEFAULT_STATE, f, indent=2) 