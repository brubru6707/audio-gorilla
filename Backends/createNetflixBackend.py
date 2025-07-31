import uuid
import random
import time
from datetime import datetime, timedelta
import json

"""Netflix Backend Generator

Generates DEFAULT_STATE with a handful of random profiles, movies, and series to
mirror what *NetflixApis.py* expects.  IDs are short human-readable strings so
that unit-tests are easier to read.
"""

# ---------------------------------------------------------------------------
# Helpers & seed data
# ---------------------------------------------------------------------------

_movie_titles = [
    "The Matrix", "Inception", "Interstellar", "Parasite", "Whiplash",
    "The Dark Knight", "Fight Club", "Forrest Gump", "Gladiator", "Se7en",
]
_show_titles = [
    "Breaking Bad", "Stranger Things", "The Crown", "Money Heist",
    "The Witcher", "Ozark", "Dark", "Narcos", "Friends", "The Office",
]
_profile_names = [
    "Main", "Kids", "Guest", "Dad", "Mom", "Roommate",
]
_languages = ["en", "es", "fr", "de", "pt", "it", "nl"]
_maturity_levels = ["kids", "teen", "adult"]


def _random_date() -> str:
    """ISO date within the last 10 years."""
    days = random.randint(0, 3650)
    return (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")


def _rand_rating() -> str:
    return random.choice(["G", "PG", "PG-13", "R", "TV-MA", "TV-14"])


# ---------------------------------------------------------------------------
# Build content library
# ---------------------------------------------------------------------------

content: dict[str, dict] = {}

for idx, title in enumerate(_movie_titles, start=1):
    cid = f"M{idx:03d}"
    content[cid] = {
        "id": cid,
        "title": title,
        "type": "movie",
        "year": random.randint(1990, 2024),
        "rating": _rand_rating(),
        "duration": random.randint(80, 180),  # minutes
        "genre": random.sample(["Drama", "Action", "Comedy", "Thriller", "Sci-Fi"], k=2),
    }

for idx, title in enumerate(_show_titles, start=1):
    cid = f"S{idx:03d}"
    seasons = random.randint(1, 7)
    content[cid] = {
        "id": cid,
        "title": title,
        "type": "series",
        "year": random.randint(1990, 2024),
        "rating": _rand_rating(),
        "seasons": seasons,
        "genre": random.sample(["Drama", "Action", "Comedy", "Thriller", "Fantasy"], k=2),
    }

all_content_ids = list(content.keys())

# Generate extra synthetic movies
adjectives = ["Silent", "Lost", "Hidden", "Golden", "Scarlet", "Shattered", "Burning", "Forgotten"]
nouns = ["Dreams", "River", "Empire", "Gate", "Legacy", "Shadow", "Secret", "Galaxy"]
for idx in range(11, 111):  # creates up to M110
    cid = f"M{idx:03d}"
    title = f"{random.choice(adjectives)} {random.choice(nouns)}"
    content[cid] = {
        "id": cid,
        "title": title,
        "type": "movie",
        "year": random.randint(1980, 2024),
        "rating": _rand_rating(),
        "duration": random.randint(75, 190),
        "genre": random.sample(["Drama", "Action", "Comedy", "Thriller", "Sci-Fi", "Romance", "Fantasy"], k=2),
    }

# Extra synthetic shows
for idx in range(11, 71):  # S011-S070
    cid = f"S{idx:03d}"
    title = f"The {random.choice(nouns)} Chronicles"
    content[cid] = {
        "id": cid,
        "title": title,
        "type": "series",
        "year": random.randint(1990, 2024),
        "rating": _rand_rating(),
        "seasons": random.randint(1, 10),
        "genre": random.sample(["Drama", "Action", "Comedy", "Thriller", "Fantasy", "Sci-Fi"], k=2),
    }

all_content_ids = list(content.keys())

# ---------------------------------------------------------------------------
# Build profiles & related state
# ---------------------------------------------------------------------------

profiles: dict[str, dict] = {}
watchlist: dict[str, list] = {}
ratings: dict[str, dict] = {}
continue_watching: dict[str, list] = {}

extra_names = ["Liam", "Noah", "Olivia", "Mason", "Ava", "Emma", "Ethan", "Sophia", "Logan", "Isabella"]
profile_pool = _profile_names + extra_names

for idx, name in enumerate(profile_pool, start=1):
    pid = f"P{idx:03d}"
    profiles[pid] = {
        "id": pid,
        "name": name,
        "avatar": f"https://cdn.moviestream.net/avatars/{pid}.png",
        "maturity_level": random.choice(_maturity_levels),
        "language": random.choice(_languages),
        "autoplay": random.random() < 0.8,
    }

    # Sample watchlist (1-15 items)
    wl_count = random.randint(1, 15)
    watchlist[pid] = [content[cid] for cid in random.sample(all_content_ids, k=wl_count)]

    # Sample ratings (0-3 items)
    r_count = random.randint(0, 10)
    ratings[pid] = {cid: random.randint(1, 5) for cid in random.sample(all_content_ids, k=r_count)}

    # Continue watching (maybe)
    if random.random() < 0.5:
        cw_item = random.choice(all_content_ids)
        progress = random.randint(1, 90)
        continue_watching[pid] = [{
            "content_id": cw_item,
            "progress": progress,  # percent
            "resume_time": int(progress / 100 * 7200),  # rough seconds
            "updated": int(time.time()),
        }]
    else:
        continue_watching[pid] = []

# ---------------------------------------------------------------------------
DEFAULT_STATE = {
    "profiles": profiles,
    "content": content,
    "watchlist": watchlist,
    "ratings": ratings,
    "continue_watching": continue_watching,
    "generated_at": datetime.utcnow().isoformat() + "Z",
}

# Summary --------------------------------------------------------------------
if __name__ == "__main__":
    print("Netflix backend generated 🍿")
    print(f"Profiles : {len(profiles)}")
    print(f"Content  : {len(content)} (movies+shows)")
    total_wl = sum(len(v) for v in watchlist.values())
    print(f"Watchlist: {total_wl} total entries")

    # with open('diverse_netflix_state.json', 'w') as f:
    #     json.dump(DEFAULT_STATE, f, indent=2) 