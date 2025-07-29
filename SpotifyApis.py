import datetime
import copy
import uuid
import random
import json
from typing import Dict, List, Any, Optional, Union, Literal

# Global maps to store UUIDs during processing
_initial_user_email_to_uuid_map = {}
_initial_song_id_to_uuid_map = {}
_initial_album_id_to_uuid_map = {}
_initial_playlist_id_to_uuid_map = {}
_initial_artist_id_to_uuid_map = {}
_initial_payment_card_id_to_uuid_map = {}

# Helper function for realistic timestamp generation
def generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365*5):
    """Generates a random ISO 8601 formatted datetime string (with Z for UTC) in the past."""
    delta_days = random.randint(days_ago_min, days_ago_max)
    time_offset = datetime.timedelta(days=delta_days, 
                                     hours=random.randint(0, 23), 
                                     minutes=random.randint(0, 59), 
                                     seconds=random.randint(0, 59))
    dt = datetime.datetime.now(datetime.timezone.utc) - time_offset
    return dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

# --- Data for generating new users, artists, songs, albums, playlists ---
# Moved these definitions to the top so they are available when _convert_initial_data_to_uuids is called
first_names = ["Ava", "Noah", "Olivia", "Liam", "Emma", "Charlotte", "Amelia", "Sophia", "Isabella", "Mia", "Harper", "Evelyn", "Abigail", "Emily", "Elizabeth", "Mila", "Ella", "Avery", "Sofia", "Camila", "Aria", "Scarlett", "Victoria", "Madison", "Luna", "Grace", "Chloe", "Penelope", "Layla", "Riley", "Zoey", "Nora", "Lily", "Eleanor", "Hannah", "Lillian", "Addison", "Aubrey", "Ellie", "Stella", "Natalie", "Zoe", "Leah", "Hazel", "Violet", "Aurora", "Savannah", "Brooklyn", "Bella", "Skylar"]
last_names = ["Smith", "Jones", "Williams", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Sanchez"]
email_domains = ["melodify.com", "tunebloom.net", "rhythmnest.org", "sonicwave.app", "audiosphere.co"]
common_genres = ["Pop", "Electronic", "Acoustic", "Folk", "Funk", "Rock", "Hip Hop", "R&B", "Jazz", "Classical", "Country", "Indie", "Blues", "Metal", "Reggae", "Dance", "Ambient", "Soul", "Gospel", "Latin"]
album_types = ["album", "single", "ep", "compilation", "live"]
card_types = ["Visa", "Mastercard", "Amex", "Discover", "JCB"]
countries = ["US", "CA", "GB", "DE", "AU", "JP", "IN", "BR", "FR", "MX", "ES", "IT", "NL", "SE", "NO", "DK", "CH", "AT", "NZ", "IE"]
device_types = ["mobile", "web", "desktop", "smart_speaker", "tablet", "car_audio"]
languages = ["en", "es", "fr", "de", "jp", "ko", "zh", "pt", "it"]
playlist_descriptions = [
    "Tracks to get you going in the morning.",
    "Perfect background music for studying or working.",
    "High-energy beats for your workout session.",
    "Chill vibes for winding down after a long day.",
    "A collection of timeless classics.",
    "Discover new indie gems.",
    "Feel-good songs for a sunny day.",
    "Deep focus music to enhance concentration.",
    "Sing along to your favorite pop anthems.",
    "Unwind with soothing instrumental pieces."
]

def _convert_initial_data_to_uuids(initial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Converts the initial DEFAULT_STATE data to use UUIDs for all relevant IDs and adds new fields."""
    
    converted_data = copy.deepcopy(initial_data)

    # Clear global maps for each run to ensure fresh UUIDs
    global _initial_user_email_to_uuid_map
    global _initial_song_id_to_uuid_map
    global _initial_album_id_to_uuid_map
    global _initial_playlist_id_to_uuid_map
    global _initial_artist_id_to_uuid_map
    global _initial_payment_card_id_to_uuid_map
    
    _initial_user_email_to_uuid_map = {}
    _initial_song_id_to_uuid_map = {}
    _initial_album_id_to_uuid_map = {}
    _initial_playlist_id_to_uuid_map = {}
    _initial_artist_id_to_uuid_map = {}
    _initial_payment_card_id_to_uuid_map = {}

    current_time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

    # --- Process Songs First ---
    new_songs = {}
    for old_id, song_data in converted_data.get("songs", {}).items():
        new_id = str(uuid.uuid4())
        _initial_song_id_to_uuid_map[old_id] = new_id
        song_data["id"] = new_id
        if "release_date" not in song_data or not song_data["release_date"]:
            song_data["release_date"] = generate_random_iso_timestamp(days_ago_min=30, days_ago_max=365*3) # Last month to 3 years ago
        if "popularity_score" not in song_data:
            song_data["popularity_score"] = random.randint(30, 95)
        if "explicit" not in song_data:
            song_data["explicit"] = random.random() < 0.15 # 15% chance
        if "language" not in song_data:
            song_data["language"] = random.choice(languages) # Use defined list
        if "stream_count" not in song_data:
            song_data["stream_count"] = random.randint(1000, 50000000) # Wide range
        new_songs[new_id] = song_data
    converted_data["songs"] = new_songs

    # --- Process Albums ---
    new_albums = {}
    for old_id, album_data in converted_data.get("albums", {}).items():
        new_id = str(uuid.uuid4())
        _initial_album_id_to_uuid_map[old_id] = new_id
        album_data["id"] = new_id
        if "release_date" not in album_data or not album_data["release_date"]:
            album_data["release_date"] = generate_random_iso_timestamp(days_ago_min=30, days_ago_max=365*4) # Last month to 4 years ago
        album_data["tracks"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in album_data.get("tracks", [])]
        
        # New album fields
        if "album_type" not in album_data:
            album_data["album_type"] = random.choice(album_types) # Use defined list
        if "total_tracks" not in album_data:
            album_data["total_tracks"] = len(album_data["tracks"])
        if "label" not in album_data:
            album_data["label"] = random.choice(["Indie Records", "MegaMusic Inc.", "SoundWave Studio", "Harmony Arts"])
        new_albums[new_id] = album_data
    converted_data["albums"] = new_albums

    # --- Process Artists ---
    new_artists = {}
    for old_id, artist_data in converted_data.get("artists", {}).items():
        new_id = str(uuid.uuid4())
        _initial_artist_id_to_uuid_map[old_id] = new_id
        artist_data["id"] = new_id
        artist_data["albums"] = [_initial_album_id_to_uuid_map.get(a_id, a_id) for a_id in artist_data.get("albums", [])]
        
        # New artist fields
        if "bio" not in artist_data:
            artist_data["bio"] = f"A talented artist known for their unique blend of {artist_data.get('genre', 'music')}."
        if "country_origin" not in artist_data:
            artist_data["country_origin"] = random.choice(countries) # Use defined list
        if "followers_count" not in artist_data:
            artist_data["followers_count"] = random.randint(500, 10000000)
        if "is_verified" not in artist_data:
            artist_data["is_verified"] = random.random() < 0.7 # 70% chance to be verified
        new_artists[new_id] = artist_data
    converted_data["artists"] = new_artists

    # --- Process Playlists ---
    new_playlists = {}
    for old_id, playlist_data in converted_data.get("playlists", {}).items():
        new_id = str(uuid.uuid4())
        _initial_playlist_id_to_uuid_map[old_id] = new_id
        playlist_data["id"] = new_id
        if "created_at" not in playlist_data or not playlist_data["created_at"]:
            playlist_data["created_at"] = generate_random_iso_timestamp(days_ago_min=60, days_ago_max=365*2) # 2 months to 2 years ago
        if "updated_at" not in playlist_data or not playlist_data["updated_at"]:
            playlist_data["updated_at"] = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=60) # Last 60 days
        playlist_data["tracks"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in playlist_data.get("tracks", [])]
        
        # New playlist fields
        if "follower_count" not in playlist_data:
            playlist_data["follower_count"] = random.randint(10, 500000)
        if "collaborative" not in playlist_data:
            playlist_data["collaborative"] = random.random() < 0.1 # 10% chance
        if "image_url" not in playlist_data:
            playlist_data["image_url"] = f"https://example.com/playlists/{new_id}.jpg"
        new_playlists[new_id] = playlist_data
    converted_data["playlists"] = new_playlists

    # --- Process Users ---
    new_users = {}
    for email, user_data in converted_data.get("users", {}).items():
        user_id = str(uuid.uuid4())
        _initial_user_email_to_uuid_map[email] = user_id
        user_data["id"] = user_id
        
        # Update IDs based on global maps
        user_data["liked_songs"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in user_data.get("liked_songs", [])]
        user_data["liked_albums"] = [_initial_album_id_to_uuid_map.get(a_id, a_id) for a_id in user_data.get("liked_albums", [])]
        user_data["liked_playlists"] = [_initial_playlist_id_to_uuid_map.get(p_id, p_id) for p_id in user_data.get("liked_playlists", [])]
        user_data["following_artists"] = [_initial_artist_id_to_uuid_map.get(ar_id, ar_id) for ar_id in user_data.get("following_artists", [])]
        user_data["library_songs"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in user_data.get("library_songs", [])]
        user_data["library_albums"] = [_initial_album_id_to_uuid_map.get(a_id, a_id) for a_id in user_data.get("library_albums", [])]
        user_data["downloaded_songs"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in user_data.get("downloaded_songs", [])]

        # Add new user fields
        if "registration_date" not in user_data:
            user_data["registration_date"] = generate_random_iso_timestamp(days_ago_min=365, days_ago_max=365*5) # 1 to 5 years ago
        if "last_active_date" not in user_data:
            user_data["last_active_date"] = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=30) # Last 30 days
        if "preferred_genre" not in user_data:
            user_data["preferred_genre"] = random.choice(common_genres) # Use defined list
        if "total_play_time_ms" not in user_data:
            user_data["total_play_time_ms"] = random.randint(1000000, 900000000) # 1M ms (16 mins) to 900M ms (15000 mins or 250 hours)

        # Profile additions
        if "country" not in user_data:
            user_data["country"] = random.choice(countries) # Use defined list
        if "device_type" not in user_data:
            user_data["device_type"] = random.choice(device_types) # Use defined list
        
        new_users[user_id] = user_data
    converted_data["users"] = new_users

    # --- Process Payment Cards ---
    new_payment_cards = {}
    for old_id, card_data in converted_data.get("payment_cards", {}).items():
        new_id = str(uuid.uuid4())
        _initial_payment_card_id_to_uuid_map[old_id] = new_id
        card_data["id"] = new_id
        # Ensure user_id is linked by UUID
        user_email_for_card = card_data.get("user_email")
        if user_email_for_card and user_email_for_card in _initial_user_email_to_uuid_map:
            card_data["user_id"] = _initial_user_email_to_uuid_map[user_email_for_card]
        else: # Fallback if user_email not found (e.g., for newly created users)
            # This should pick a user that was *just* converted or an initial one
            card_data["user_id"] = random.choice(list(new_users.keys())) 
        
        del card_data["user_email"] # Remove the temporary email key
        
        # Add new payment card fields
        if "card_type" not in card_data:
            card_data["card_type"] = random.choice(card_types) # Use defined list
        if "billing_address" not in card_data:
            card_data["billing_address"] = f"{random.randint(100, 999)} {random.choice(['Elm', 'Pine', 'Oak'])} St, Anytown, {random.choice(['NY', 'CA', 'TX'])}"

        new_payment_cards[new_id] = card_data
    converted_data["payment_cards"] = new_payment_cards
    
    # Update username to the UUID of the default user
    initial_default_email = initial_data.get("username")
    if initial_default_email and initial_default_email in _initial_user_email_to_uuid_map:
        converted_data["username"] = _initial_user_email_to_uuid_map[initial_default_email]
    else:
        # If the default user wasn't in the initial data, pick a random one
        converted_data["username"] = list(new_users.keys())[0] if new_users else None


    return converted_data


# --- Raw Initial Data (used as a template) ---
RAW_DEFAULT_STATE = {
    "username": "samantha.davis@melodify.com",
    "users": {
        "samantha.davis@melodify.com": {
            "first_name": "Samantha",
            "last_name": "Davis",
            "email": "samantha.davis@melodify.com",
            "verified": True,
            "liked_songs": [101, 103, 106],
            "liked_albums": [201, 204],
            "liked_playlists": [301, 303],
            "following_artists": [401, 404],
            "library_songs": [101, 102, 103, 106, 107],
            "library_albums": [201, 204, 205],
            "downloaded_songs": [101, 106],
            "premium": True
        },
        "liam.wilson@melodify.com": {
            "first_name": "Liam",
            "last_name": "Wilson",
            "email": "liam.wilson@melodify.com",
            "verified": True,
            "liked_songs": [102, 104, 105],
            "liked_albums": [202, 203],
            "liked_playlists": [302],
            "following_artists": [402, 403],
            "library_songs": [102, 104, 105, 108],
            "library_albums": [202, 203],
            "downloaded_songs": [104],
            "premium": False
        }
    },
    "payment_cards": {
        1: {"id": 1, "card_name": "Samantha's Visa", "user_email": "samantha.davis@melodify.com", "card_number": "4111********1111", "expiry_year": 2028, "expiry_month": 12, "cvv_number": "XXX", "is_default": True},
        2: {"id": 2, "card_name": "Samantha's Mastercard", "user_email": "samantha.davis@melodify.com", "card_number": "5222********2222", "expiry_year": 2027, "expiry_month": 7, "cvv_number": "YYY", "is_default": False},
        3: {"id": 3, "card_name": "Liam's Visa", "user_email": "liam.wilson@melodify.com", "card_number": "4333********3333", "expiry_year": 2026, "expiry_month": 5, "cvv_number": "ZZZ", "is_default": True}
    },
    "songs": {
        101: {"id": 101, "title": "Summer Vibes", "artist_id": 401, "album_id": 201, "duration_ms": 180000, "genre": "Pop", "release_date": "2023-06-01"},
        102: {"id": 102, "title": "Coding Flow", "artist_id": 402, "album_id": 202, "duration_ms": 240000, "genre": "Electronic", "release_date": "2022-09-15"},
        103: {"id": 103, "title": "Acoustic Dreams", "artist_id": 403, "album_id": 203, "duration_ms": 210000, "genre": "Acoustic", "release_date": "2021-11-20"},
        104: {"id": 104, "title": "City Lights", "artist_id": 401, "album_id": 204, "duration_ms": 200000, "genre": "Pop", "release_date": "2024-01-10"},
        105: {"id": 105, "title": "Rainy Days", "artist_id": 402, "album_id": 202, "duration_ms": 270000, "genre": "Ambient", "release_date": "2022-10-05"},
        106: {"id": 106, "title": "Upbeat Morning", "artist_id": 404, "album_id": 205, "duration_ms": 195000, "genre": "Folk", "release_date": "2023-03-25"},
        107: {"id": 107, "title": "Midnight Serenade", "artist_id": 403, "album_id": 203, "duration_ms": 225000, "genre": "Classical", "release_date": "2021-12-01"},
        108: {"id": 108, "title": "Groovy Bassline", "artist_id": 404, "album_id": 205, "duration_ms": 205000, "genre": "Funk", "release_date": "2023-04-10"}
    },
    "albums": {
        201: {"id": 201, "title": "Bright Future", "artist_id": 401, "release_date": "2023-05-20", "tracks": [101]},
        202: {"id": 202, "title": "Digital Landscapes", "artist_id": 402, "release_date": "2022-09-01", "tracks": [102, 105]},
        203: {"id": 203, "title": "Whispering Woods", "artist_id": 403, "release_date": "2021-11-10", "tracks": [103, 107]},
        204: {"id": 204, "title": "Urban Echoes", "artist_id": 401, "release_date": "2024-01-01", "tracks": [104]},
        205: {"id": 205, "title": "Rustic Rhythms", "artist_id": 404, "release_date": "2023-03-15", "tracks": [106, 108]}
    },
    "playlists": {
        301: {"id": 301, "name": "Morning Chill", "user_email": "samantha.davis@melodify.com", "description": "Relaxing tracks for your morning routine.", "public": True, "tracks": [101, 103, 106]},
        302: {"id": 302, "name": "Workout Mix", "user_email": "liam.wilson@melodify.com", "description": "High energy songs for your workout.", "public": False, "tracks": [102, 104, 105]},
        303: {"id": 303, "name": "Focus Beats", "user_email": "samantha.davis@melodify.com", "description": "Background music for deep work.", "public": False, "tracks": [107, 108]}
    },
    "artists": {
        401: {"id": 401, "name": "Vocal Fusion", "genre": "Pop", "albums": [201, 204]},
        402: {"id": 402, "name": "Synthwave Collective", "genre": "Electronic", "albums": [202]},
        403: {"id": 403, "name": "Acoustic Soul", "genre": "Acoustic", "albums": [203]},
        404: {"id": 404, "name": "Groove Masters", "genre": "Funk/Folk", "albums": [205]}
    }
}

# Ensure DEFAULT_STATE is initialized with UUIDs from the RAW_DEFAULT_STATE
# before we start adding new items, so that the UUID maps are populated.
# This makes sure the existing items are converted and available for linking.
DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)


# These global lists should be populated *after* DEFAULT_STATE is initialized
# because _convert_initial_data_to_uuids already converts the initial data
# and populates the _initial_*_id_to_uuid_map variables.
# We then use these maps for generating new data, linking back to existing UUIDs where appropriate.

# Initialize with existing UUIDs after initial conversion
all_artists_uuid = list(_initial_artist_id_to_uuid_map.values())
all_songs_uuid = list(_initial_song_id_to_uuid_map.values())
all_albums_uuid = list(_initial_album_id_to_uuid_map.values())
all_playlists_uuid = list(_initial_playlist_id_to_uuid_map.values())

def generate_artist_data():
    artist_id = str(uuid.uuid4())
    name = f"{random.choice(['The', 'New', 'Old', 'Fresh'])} {random.choice(first_names)} {random.choice(['Band', 'Collective', 'Orchestra', 'Project'])}"
    genre = random.choice(common_genres)
    albums_count = random.randint(1, 5)
    albums = []
    for _ in range(albums_count):
        albums.append(generate_album_data(artist_id)) # Generate albums associated with this artist
    
    # Add generated albums to the global albums dict
    for album_uuid, album_data in albums:
        DEFAULT_STATE["albums"][album_uuid] = album_data
        all_albums_uuid.append(album_uuid)

    artist_data = {
        "id": artist_id,
        "name": name,
        "genre": genre,
        "albums": [album[0] for album in albums], # Store only UUIDs
        "bio": f"Known for their {genre} sound, {name} has captivated audiences worldwide.",
        "country_origin": random.choice(countries),
        "followers_count": random.randint(10000, 50000000),
        "is_verified": random.random() < 0.8
    }
    return artist_id, artist_data

def generate_album_data(artist_id):
    album_id = str(uuid.uuid4())
    title = f"{random.choice(['Echoes', 'Visions', 'Rhythms', 'Dreams'])} of {random.choice(['Tomorrow', 'Yesterday', 'Life', 'The City'])} {random.randint(1,99)}"
    release_date = generate_random_iso_timestamp(days_ago_min=30, days_ago_max=365*4)
    num_tracks = random.randint(3, 15)
    tracks = []
    for _ in range(num_tracks):
        song_id, song_data = generate_song_data(artist_id, album_id, release_date)
        tracks.append(song_id)
        DEFAULT_STATE["songs"][song_id] = song_data
        all_songs_uuid.append(song_id)
        
    album_data = {
        "id": album_id,
        "title": title,
        "artist_id": artist_id,
        "release_date": release_date,
        "tracks": tracks,
        "album_type": random.choice(album_types),
        "total_tracks": num_tracks,
        "label": random.choice(["Indie Records", "MegaMusic Inc.", "SoundWave Studio", "Harmony Arts", "Global Beats"])
    }
    return album_id, album_data

def generate_song_data(artist_id, album_id, album_release_date):
    song_id = str(uuid.uuid4())
    title = f"{random.choice(['Fading', 'Rising', 'Silent', 'Electric'])} {random.choice(['Stars', 'Waves', 'Voices', 'Skies'])} {random.randint(1,99)}"
    duration_ms = random.randint(150000, 300000) # 2:30 to 5:00 minutes
    genre = random.choice(common_genres)
    
    # Ensure song release date is on or after album release date
    album_release_dt = datetime.datetime.fromisoformat(album_release_date.replace('Z', '+00:00'))
    song_release_dt = album_release_dt + datetime.timedelta(days=random.randint(0, 30)) # up to 30 days after album
    release_date = song_release_dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

    song_data = {
        "id": song_id,
        "title": title,
        "artist_id": artist_id,
        "album_id": album_id,
        "duration_ms": duration_ms,
        "genre": genre,
        "release_date": release_date,
        "popularity_score": random.randint(20, 99),
        "explicit": random.random() < 0.1,
        "language": random.choice(languages),
        "stream_count": random.randint(5000, 100000000)
    }
    return song_id, song_data

def generate_playlist_data(user_id):
    playlist_id = str(uuid.uuid4())
    name = f"{random.choice(first_names)}'s {random.choice(['Workout', 'Chill', 'Study', 'Party', 'Road Trip'])} Mix"
    description = random.choice(playlist_descriptions)
    public = random.random() < 0.7 # 70% chance to be public
    
    num_tracks = random.randint(5, 50)
    # Ensure we only pick from already generated songs
    tracks = random.sample(all_songs_uuid, min(num_tracks, len(all_songs_uuid))) if all_songs_uuid else []
    
    created_at = generate_random_iso_timestamp(days_ago_min=60, days_ago_max=365*2)
    updated_at_dt = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00')) + datetime.timedelta(days=random.randint(0, 60))
    updated_at = updated_at_dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

    playlist_data = {
        "id": playlist_id,
        "name": name,
        "description": description,
        "public": public,
        "tracks": tracks,
        "owner_id": user_id, # Link to user UUID
        "created_at": created_at,
        "updated_at": updated_at,
        "follower_count": random.randint(5, 50000),
        "collaborative": random.random() < 0.05,
        "image_url": f"https://example.com/playlists/{playlist_id}.jpg"
    }
    return playlist_id, playlist_data

def generate_payment_card_data(user_id):
    card_id = str(uuid.uuid4())
    card_type = random.choice(card_types)
    last_four = ''.join(random.choices('0123456789', k=4))
    card_number = f"{random.choice(['4', '5', '3'])}{random.choices('0123456789', k=3)}********{last_four}"
    expiry_year = random.randint(2026, 2032)
    expiry_month = random.randint(1, 12)
    cvv_number = ''.join(random.choices('0123456789', k=3))
    is_default = random.random() < 0.5 # 50% chance to be default for simplicity

    card_name = f"{random.choice(first_names)}'s {card_type}" # Use random first name here too for diversity
    billing_address = f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Maple', 'Pine'])} St, {random.choice(['Springfield', 'Rivertown', 'Metropolis'])}, {random.choice(['NY', 'CA', 'TX', 'FL'])}, {random.randint(10001, 99999)}"

    return card_id, {
        "id": card_id,
        "card_name": card_name,
        "user_id": user_id,
        "card_number": card_number,
        "expiry_year": expiry_year,
        "expiry_month": expiry_month,
        "cvv_number": "XXX", # Mask CVV for realism
        "is_default": is_default,
        "card_type": card_type, # New field
        "billing_address": billing_address # New field
    }

# --- Generate additional data ---
num_additional_users = 48 # Target 50 total users (2 initial + 48 new)
num_artists_to_add = 20 # Add more artists
num_playlists_to_add = 30 # Add more playlists

# Populate artists, albums, songs first globally
for _ in range(num_artists_to_add):
    artist_uuid, artist_data = generate_artist_data()
    DEFAULT_STATE["artists"][artist_uuid] = artist_data
    all_artists_uuid.append(artist_uuid)

# Now, generate new users and connect them to the content
for i in range(num_additional_users):
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = f"{first.lower()}.{last.lower()}{random.randint(1, 999)}@{random.choice(email_domains)}"
    
    # Ensure unique email
    # Check against values in _initial_user_email_to_uuid_map as well as current DEFAULT_STATE users
    all_current_emails = set([u["email"] for u in DEFAULT_STATE["users"].values()])
    while email in all_current_emails:
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 999)}@{random.choice(email_domains)}"

    user_id = str(uuid.uuid4())
    _initial_user_email_to_uuid_map[email] = user_id # Add to map for payment card linking

    # Generate user preferences/library
    num_liked_songs = random.randint(5, min(50, len(all_songs_uuid)))
    num_liked_albums = random.randint(1, min(10, len(all_albums_uuid)))
    # num_liked_playlists = random.randint(1, min(5, len(all_playlists_uuid))) # Will be filled after playlists are generated
    num_following_artists = random.randint(1, min(8, len(all_artists_uuid)))
    num_library_songs = random.randint(10, min(100, len(all_songs_uuid)))
    num_library_albums = random.randint(2, min(20, len(all_albums_uuid)))
    num_downloaded_songs = random.randint(0, min(20, len(all_songs_uuid)))

    new_user_data = {
        "id": user_id,
        "first_name": first,
        "last_name": last,
        "email": email,
        "verified": random.random() < 0.9, # 90% chance to be verified
        "liked_songs": random.sample(all_songs_uuid, num_liked_songs),
        "liked_albums": random.sample(all_albums_uuid, num_liked_albums),
        "liked_playlists": [], # Will be filled after playlists are generated
        "following_artists": random.sample(all_artists_uuid, num_following_artists),
        "library_songs": random.sample(all_songs_uuid, num_library_songs),
        "library_albums": random.sample(all_albums_uuid, num_library_albums),
        "downloaded_songs": random.sample(all_songs_uuid, num_downloaded_songs),
        "premium": random.random() < 0.6, # 60% chance for premium
        "registration_date": generate_random_iso_timestamp(days_ago_min=365, days_ago_max=365*5),
        "last_active_date": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=30),
        "preferred_genre": random.choice(common_genres),
        "total_play_time_ms": random.randint(5000000, 1000000000), # More significant play time
        "country": random.choice(countries),
        "device_type": random.choice(device_types)
    }
    DEFAULT_STATE["users"][user_id] = new_user_data

    # Add payment card for new users, especially premium ones
    if new_user_data["premium"] or random.random() < 0.3: # All premium users get a card, plus 30% of free users
        card_id, card_data = generate_payment_card_data(user_id)
        DEFAULT_STATE["payment_cards"][card_id] = card_data

# Now generate playlists, linking them to existing users
user_uuids = list(DEFAULT_STATE["users"].keys())
for _ in range(num_playlists_to_add):
    if user_uuids:
        owner_id = random.choice(user_uuids)
        playlist_uuid, playlist_data = generate_playlist_data(owner_id)
        DEFAULT_STATE["playlists"][playlist_uuid] = playlist_data
        all_playlists_uuid.append(playlist_uuid)

# Now that playlists are generated, update user's liked_playlists for new users
for user_data in DEFAULT_STATE["users"].values():
    if not user_data["liked_playlists"]: # Only for new users who don't have this populated yet
        num_liked_playlists = random.randint(1, min(5, len(all_playlists_uuid)))
        if all_playlists_uuid: # Ensure there are playlists to pick from
            user_data["liked_playlists"] = random.sample(all_playlists_uuid, num_liked_playlists)


# Ensure the "username" (current user) is set to a UUID
if RAW_DEFAULT_STATE["username"] in _initial_user_email_to_uuid_map: # Use RAW_DEFAULT_STATE for the original email
    DEFAULT_STATE["username"] = _initial_user_email_to_uuid_map[RAW_DEFAULT_STATE["username"]]
else:
    # If original username wasn't in the map (e.g., deleted), pick a random user
    DEFAULT_STATE["username"] = random.choice(list(DEFAULT_STATE["users"].keys())) if DEFAULT_STATE["users"] else None


# --- Output the generated DEFAULT_STATE ---
# output_filename = 'diverse_spotify_state.json'
# with open(output_filename, 'w') as f:
#     json.dump(DEFAULT_STATE, f, indent=2)

print(f"Total number of users: {len(DEFAULT_STATE['users'])}")
print(f"Total number of songs: {len(DEFAULT_STATE['songs'])}")
print(f"Total number of albums: {len(DEFAULT_STATE['albums'])}")
print(f"Total number of artists: {len(DEFAULT_STATE['artists'])}")
print(f"Total number of playlists: {len(DEFAULT_STATE['playlists'])}")
print(f"Total number of payment cards: {len(DEFAULT_STATE['payment_cards'])}")
print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

class SpotifyApis:
    """
    A dummy API class for simulating Spotify operations.
    This class provides an in-memory backend for development and testing purposes.
    """

    def __init__(self):
        """
        Initializes the SpotifyApis instance, setting up the in-memory
        data stores and loading the default scenario.
        """
        self._api_description = "This tool belongs to the Spotify API, which provides core functionality for managing music, playlists, and user profiles."
        self.users: Dict[str, Any] = {}
        self.payment_cards: Dict[str, Any] = {}
        self.songs: Dict[str, Any] = {}
        self.albums: Dict[str, Any] = {}
        self.playlists: Dict[str, Any] = {}
        self.artists: Dict[str, Any] = {}
        self.username: Optional[str] = None

        self._load_scenario(DEFAULT_STATE)
        if DEFAULT_STATE.get("username"):
            self.username = DEFAULT_STATE["username"]


    def _load_scenario(self, scenario: Dict) -> None:
        """
        Loads a predefined scenario into the dummy backend's state.

        Args:
            scenario (Dict): A dictionary representing the state to load.
                             It should contain "users", "payment_cards", "songs", etc.
        """
        scenario_copy = copy.deepcopy(scenario)
        self.users = scenario_copy.get("users", {})
        self.payment_cards = scenario_copy.get("payment_cards", {})
        self.songs = scenario_copy.get("songs", {})
        self.albums = scenario_copy.get("albums", {})
        self.playlists = scenario_copy.get("playlists", {})
        self.artists = scenario_copy.get("artists", {})
        self.username = scenario_copy.get("username")
        print("SpotifyApis: Loaded scenario with UUIDs for all entities.")

    def _generate_unique_id(self) -> str:
        """
        Generates a unique UUID for dummy entities.
        """
        return str(uuid.uuid4())

    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """Helper to get user_id (UUID) from email (string)."""
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                return user_id
        return None

    def _get_user_email_by_id(self, user_id: str) -> Optional[str]:
        """Helper to get user email (string) from user_id (UUID)."""
        user_data = self.users.get(user_id)
        return user_data.get("email") if user_data else None

    def _get_current_user_data(self) -> Optional[Dict]:
        """Helper to get the data of the currently logged-in user (identified by self.username UUID)."""
        if not self.username:
            return None
        return self.users.get(self.username)

    def _get_user_payment_cards(self, user_id: str) -> Dict[str, Any]:
        """Helper to get a user's payment cards, keyed by UUID."""
        cards = {}
        for card_id, card_data in self.payment_cards.items():
            if card_data.get("user_id") == user_id:
                cards[card_id] = card_data
        return cards

    def set_current_user(self, user_email: str) -> Dict[str, bool]:
        """
        Sets the current authenticated user for the API session.

        Args:
            user_email (str): The email address of the user to set as current.

        Returns:
            Dict[str, bool]: A dictionary with 'status' indicating success or failure.
        """
        user_id = self._get_user_id_by_email(user_email)
        if user_id:
            self.username = user_id
            return {"status": True, "message": f"User set to {user_email} (ID: {user_id})."}
        return {"status": False, "message": f"User with email {user_email} not found."}


    def show_account(self) -> Dict[str, Any]:
        """
        Shows the account information for the current user.
        """
        user_data = self._get_current_user_data()
        if user_data:
            profile = {k: v for k, v in user_data.items() if k not in ["id"]}
            profile["email"] = self._get_user_email_by_id(self.username)
            return {"status": "success", "profile": profile}
        return {"status": "error", "message": "User not authenticated or not found."}

    def add_payment_method(
        self,
        card_name: str,
        card_number: str,
        expiry_year: int,
        expiry_month: int,
        cvv_number: str,
        is_default: bool = False,
    ) -> Dict[str, Any]:
        """
        Adds a new payment method for the current user.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}

        new_card_id = self._generate_unique_id()
        user_id = user_data["id"]

        if is_default:
            for card_id, card_info in self.payment_cards.items():
                if card_info.get("user_id") == user_id and card_info.get("is_default"):
                    self.payment_cards[card_id]["is_default"] = False
                    break

        new_card = {
            "id": new_card_id,
            "card_name": card_name,
            "user_id": user_id,
            "card_number": card_number,
            "expiry_year": expiry_year,
            "expiry_month": expiry_month,
            "cvv_number": cvv_number,
            "is_default": is_default,
        }
        self.payment_cards[new_card_id] = new_card
        return {"status": "success", "payment_method": copy.deepcopy(new_card)}

    def show_payment_methods(self) -> Dict[str, Any]:
        """
        Shows all payment methods associated with the current user.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}

        user_id = user_data["id"]
        payment_methods = [
            copy.deepcopy(card_info)
            for card_id, card_info in self.payment_cards.items()
            if card_info.get("user_id") == user_id
        ]
        return {"status": "success", "payment_methods": payment_methods}

    def set_default_payment_method(self, payment_method_id: str) -> Dict[str, bool]:
        """
        Set a specific payment method as the default for the current user.
        Args:
            payment_method_id (str): The ID (UUID) of the payment method to set as default.
        Returns:
            Dict[str, bool]: {"set_default_status": True} if successful, {"set_default_status": False} otherwise.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"set_default_status": False, "message": "User not authenticated."}

        if payment_method_id not in self.payment_cards:
            return {"set_default_status": False, "message": f"Payment method with ID {payment_method_id} not found."}

        if self.payment_cards[payment_method_id]["user_id"] != user_data["id"]:
            return {"set_default_status": False, "message": "You do not have permission to set this as default."}

        for card_id, card_info in self.payment_cards.items():
            if card_info["user_id"] == user_data["id"] and card_info["is_default"]:
                self.payment_cards[card_id]["is_default"] = False
                break

        self.payment_cards[payment_method_id]["is_default"] = True
        return {"set_default_status": True, "message": f"Payment method {payment_method_id} set as default."}

    def get_user_liked_songs(self) -> Dict[str, Any]:
        """
        Retrieves the list of songs liked by the current user.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        liked_songs_ids = user_data.get("liked_songs", [])
        liked_songs_details = [copy.deepcopy(self.songs[s_id]) for s_id in liked_songs_ids if s_id in self.songs]
        return {"status": "success", "liked_songs": liked_songs_details}

    def like_song(self, song_id: str) -> Dict[str, bool]:
        """
        Adds a song to the current user's liked songs.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if song_id not in self.songs:
            return {"status": False, "message": f"Song with ID {song_id} not found."}

        if song_id not in user_data.get("liked_songs", []):
            user_data.setdefault("liked_songs", []).append(song_id)
            return {"status": True, "message": f"Song {song_id} liked."}
        return {"status": False, "message": f"Song {song_id} already liked."}

    def unlike_song(self, song_id: str) -> Dict[str, bool]:
        """
        Removes a song from the current user's liked songs.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if song_id not in self.songs:
            return {"status": False, "message": f"Song with ID {song_id} not found."}

        if song_id in user_data.get("liked_songs", []):
            user_data["liked_songs"].remove(song_id)
            return {"status": True, "message": f"Song {song_id} unliked."}
        return {"status": False, "message": f"Song {song_id} not in liked songs."}

    def get_user_library_songs(self) -> Dict[str, Any]:
        """
        Retrieves the list of songs in the current user's library.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        library_songs_ids = user_data.get("library_songs", [])
        library_songs_details = [copy.deepcopy(self.songs[s_id]) for s_id in library_songs_ids if s_id in self.songs]
        return {"status": "success", "library_songs": library_songs_details}

    def add_song_to_library(self, song_id: str) -> Dict[str, bool]:
        """
        Adds a song to the current user's library.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if song_id not in self.songs:
            return {"status": False, "message": f"Song with ID {song_id} not found."}

        if song_id not in user_data.get("library_songs", []):
            user_data.setdefault("library_songs", []).append(song_id)
            return {"status": True, "message": f"Song {song_id} added to library."}
        return {"status": False, "message": f"Song {song_id} already in library."}

    def remove_song_from_library(self, song_id: str) -> Dict[str, bool]:
        """
        Removes a song from the current user's library.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if song_id not in self.songs:
            return {"status": False, "message": f"Song with ID {song_id} not found."}

        if song_id in user_data.get("library_songs", []):
            user_data["library_songs"].remove(song_id)
            return {"status": True, "message": f"Song {song_id} removed from library."}
        return {"status": False, "message": f"Song {song_id} not in library."}

    def get_user_downloaded_songs(self) -> Dict[str, Any]:
        """
        Retrieves the list of songs downloaded by the current user.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        downloaded_songs_ids = user_data.get("downloaded_songs", [])
        downloaded_songs_details = [copy.deepcopy(self.songs[s_id]) for s_id in downloaded_songs_ids if s_id in self.songs]
        return {"status": "success", "downloaded_songs": downloaded_songs_details}


    def get_user_liked_albums(self) -> Dict[str, Any]:
        """
        Retrieves the list of albums liked by the current user.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        liked_albums_ids = user_data.get("liked_albums", [])
        liked_albums_details = [copy.deepcopy(self.albums[a_id]) for a_id in liked_albums_ids if a_id in self.albums]
        return {"status": "success", "liked_albums": liked_albums_details}

    def like_album(self, album_id: str) -> Dict[str, bool]:
        """
        Adds an album to the current user's liked albums.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if album_id not in self.albums:
            return {"status": False, "message": f"Album with ID {album_id} not found."}

        if album_id not in user_data.get("liked_albums", []):
            user_data.setdefault("liked_albums", []).append(album_id)
            return {"status": True, "message": f"Album {album_id} liked."}
        return {"status": False, "message": f"Album {album_id} already liked."}

    def unlike_album(self, album_id: str) -> Dict[str, bool]:
        """
        Removes an album from the current user's liked albums.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if album_id not in self.albums:
            return {"status": False, "message": f"Album with ID {album_id} not found."}

        if album_id in user_data.get("liked_albums", []):
            user_data["liked_albums"].remove(album_id)
            return {"status": True, "message": f"Album {album_id} unliked."}
        return {"status": False, "message": f"Album {album_id} not in liked albums."}

    def get_user_library_albums(self) -> Dict[str, Any]:
        """
        Retrieves the list of albums in the current user's library.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        library_albums_ids = user_data.get("library_albums", [])
        library_albums_details = [copy.deepcopy(self.albums[a_id]) for a_id in library_albums_ids if a_id in self.albums]
        return {"status": "success", "library_albums": library_albums_details}

    def add_album_to_library(self, album_id: str) -> Dict[str, bool]:
        """
        Adds an album to the current user's library.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if album_id not in self.albums:
            return {"status": False, "message": f"Album with ID {album_id} not found."}

        if album_id not in user_data.get("library_albums", []):
            user_data.setdefault("library_albums", []).append(album_id)
            return {"status": True, "message": f"Album {album_id} added to library."}
        return {"status": False, "message": f"Album {album_id} already in library."}

    def remove_album_from_library(self, album_id: str) -> Dict[str, bool]:
        """
        Removes an album from the current user's library.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if album_id not in self.albums:
            return {"status": False, "message": f"Album with ID {album_id} not found."}

        if album_id in user_data.get("library_albums", []):
            user_data["library_albums"].remove(album_id)
            return {"status": True, "message": f"Album {album_id} removed from library."}
        return {"status": False, "message": f"Album {album_id} not in library."}

    def get_user_liked_playlists(self) -> Dict[str, Any]:
        """
        Retrieves the list of playlists liked by the current user.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        liked_playlists_ids = user_data.get("liked_playlists", [])
        liked_playlists_details = [copy.deepcopy(self.playlists[p_id]) for p_id in liked_playlists_ids if p_id in self.playlists]
        return {"status": "success", "liked_playlists": liked_playlists_details}

    def like_playlist(self, playlist_id: str) -> Dict[str, bool]:
        """
        Adds a playlist to the current user's liked playlists.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if playlist_id not in self.playlists:
            return {"status": False, "message": f"Playlist with ID {playlist_id} not found."}

        if playlist_id not in user_data.get("liked_playlists", []):
            user_data.setdefault("liked_playlists", []).append(playlist_id)
            return {"status": True, "message": f"Playlist {playlist_id} liked."}
        return {"status": False, "message": f"Playlist {playlist_id} already liked."}

    def unlike_playlist(self, playlist_id: str) -> Dict[str, bool]:
        """
        Removes a playlist from the current user's liked playlists.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if playlist_id not in self.playlists:
            return {"status": False, "message": f"Playlist with ID {playlist_id} not found."}

        if playlist_id in user_data.get("liked_playlists", []):
            user_data["liked_playlists"].remove(playlist_id)
            return {"status": True, "message": f"Playlist {playlist_id} unliked."}
        return {"status": False, "message": f"Playlist {playlist_id} not in liked playlists."}


    def get_user_following_artists(self) -> Dict[str, Any]:
        """
        Retrieves the list of artists followed by the current user.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        following_artists_ids = user_data.get("following_artists", [])
        following_artists_details = [copy.deepcopy(self.artists[a_id]) for a_id in following_artists_ids if a_id in self.artists]
        return {"status": "success", "following_artists": following_artists_details}

    def follow_artist(self, artist_id: str) -> Dict[str, bool]:
        """
        Adds an artist to the current user's followed artists.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if artist_id not in self.artists:
            return {"status": False, "message": f"Artist with ID {artist_id} not found."}

        if artist_id not in user_data.get("following_artists", []):
            user_data.setdefault("following_artists", []).append(artist_id)
            return {"status": True, "message": f"Artist {artist_id} followed."}
        return {"status": False, "message": f"Artist {artist_id} already followed."}

    def unfollow_artist(self, artist_id: str) -> Dict[str, bool]:
        """
        Removes an artist from the current user's followed artists.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        if artist_id not in self.artists:
            return {"status": False, "message": f"Artist with ID {artist_id} not found."}

        if artist_id in user_data.get("following_artists", []):
            user_data["following_artists"].remove(artist_id)
            return {"status": True, "message": f"Artist {artist_id} unfollowed."}
        return {"status": False, "message": f"Artist {artist_id} not followed."}

    def create_playlist(
        self,
        name: str,
        description: Optional[str] = None,
        public: bool = True,
    ) -> Dict[str, Any]:
        """
        Creates a new playlist for the current user.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}

        new_playlist_id = self._generate_unique_id()
        current_time_iso = datetime.datetime.now().isoformat() + "Z"

        new_playlist = {
            "id": new_playlist_id,
            "name": name,
            "user_id": user_data["id"],
            "description": description,
            "public": public,
            "tracks": [],
            "created_at": current_time_iso,
            "updated_at": current_time_iso,
        }
        self.playlists[new_playlist_id] = new_playlist
        
        user_data.setdefault("liked_playlists", []).append(new_playlist_id)

        return {"status": "success", "playlist": copy.deepcopy(new_playlist)}

    def delete_playlist(self, playlist_id: str) -> Dict[str, bool]:
        """
        Deletes a playlist owned by the current user.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        
        if playlist_id in self.playlists and self.playlists[playlist_id]["user_id"] == user_data["id"]:
            if playlist_id in user_data.get("liked_playlists", []):
                user_data["liked_playlists"].remove(playlist_id)
            del self.playlists[playlist_id]
            return {"status": True, "message": f"Playlist {playlist_id} deleted."}
        return {"status": False, "message": f"Playlist {playlist_id} not found or not owned by user."}

    def add_song_to_playlist(self, playlist_id: str, song_id: str) -> Dict[str, bool]:
        """
        Adds a song to a specific playlist owned by the current user.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        
        if playlist_id not in self.playlists:
            return {"status": False, "message": f"Playlist {playlist_id} not found."}
        if self.playlists[playlist_id]["user_id"] != user_data["id"]:
            return {"status": False, "message": "You do not own this playlist."}
        if song_id not in self.songs:
            return {"status": False, "message": f"Song {song_id} not found."}

        playlist = self.playlists[playlist_id]
        if song_id not in playlist["tracks"]:
            playlist["tracks"].append(song_id)
            playlist["updated_at"] = datetime.datetime.now().isoformat() + "Z"
            return {"status": True, "message": f"Song {song_id} added to playlist {playlist_id}."}
        return {"status": False, "message": f"Song {song_id} already in playlist {playlist_id}."}

    def remove_song_from_playlist(self, playlist_id: str, song_id: str) -> Dict[str, bool]:
        """
        Removes a song from a specific playlist owned by the current user.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": False, "message": "User not authenticated."}
        
        if playlist_id not in self.playlists:
            return {"status": False, "message": f"Playlist {playlist_id} not found."}
        if self.playlists[playlist_id]["user_id"] != user_data["id"]:
            return {"status": False, "message": "You do not own this playlist."}
        if song_id not in self.songs:
            return {"status": False, "message": f"Song {song_id} not found."}

        playlist = self.playlists[playlist_id]
        if song_id in playlist["tracks"]:
            playlist["tracks"].remove(song_id)
            playlist["updated_at"] = datetime.datetime.now().isoformat() + "Z"
            return {"status": True, "message": f"Song {song_id} removed from playlist {playlist_id}."}
        return {"status": False, "message": f"Song {song_id} not in playlist {playlist_id}."}

    def update_playlist_details(
        self,
        playlist_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        public: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Updates details of a playlist owned by the current user.
        """
        user_data = self._get_current_user_data()
        if not user_data:
            return {"status": "error", "message": "User not authenticated."}
        
        if playlist_id not in self.playlists:
            return {"status": "error", "message": f"Playlist {playlist_id} not found."}
        if self.playlists[playlist_id]["user_id"] != user_data["id"]:
            return {"status": "error", "message": "You do not own this playlist."}

        playlist = self.playlists[playlist_id]
        if name is not None:
            playlist["name"] = name
        if description is not None:
            playlist["description"] = description
        if public is not None:
            playlist["public"] = public
        
        playlist["updated_at"] = datetime.datetime.now().isoformat() + "Z"
        return {"status": "success", "playlist": copy.deepcopy(playlist)}

    def get_all_songs(self) -> Dict[str, Any]:
        """
        Retrieves a list of all songs available on the platform.
        """
        return {"status": "success", "songs": [copy.deepcopy(s) for s in self.songs.values()]}

    def get_song_details(self, song_id: str) -> Dict[str, Any]:
        """
        Retrieves details for a specific song.
        """
        song = self.songs.get(song_id)
        if song:
            return {"status": "success", "song": copy.deepcopy(song)}
        return {"status": "error", "message": f"Song {song_id} not found."}

    def get_all_albums(self) -> Dict[str, Any]:
        """
        Retrieves a list of all albums available on the platform.
        """
        return {"status": "success", "albums": [copy.deepcopy(a) for a in self.albums.values()]}

    def get_album_details(self, album_id: str) -> Dict[str, Any]:
        """
        Retrieves details for a specific album.
        """
        album = self.albums.get(album_id)
        if album:
            return {"status": "success", "album": copy.deepcopy(album)}
        return {"status": "error", "message": f"Album {album_id} not found."}

    def get_all_playlists(self) -> Dict[str, Any]:
        """
        Retrieves a list of all public playlists available on the platform.
        """
        public_playlists = [copy.deepcopy(p) for p in self.playlists.values() if p.get("public")]
        return {"status": "success", "playlists": public_playlists}

    def get_playlist_details(self, playlist_id: str) -> Dict[str, Any]:
        """
        Retrieves details for a specific playlist.
        """
        playlist = self.playlists.get(playlist_id)
        user_data = self._get_current_user_data()

        if playlist:
            if playlist.get("public") or (user_data and playlist.get("user_id") == user_data["id"]):
                return {"status": "success", "playlist": copy.deepcopy(playlist)}
            return {"status": "error", "message": "Access denied to private playlist."}
        return {"status": "error", "message": f"Playlist {playlist_id} not found."}


    def get_all_artists(self) -> Dict[str, Any]:
        """
        Retrieves a list of all artists available on the platform.
        """
        return {"status": "success", "artists": [copy.deepcopy(a) for a in self.artists.values()]}

    def get_artist_details(self, artist_id: str) -> Dict[str, Any]:
        """
        Retrieves details for a specific artist.
        """
        artist = self.artists.get(artist_id)
        if artist:
            return {"status": "success", "artist": copy.deepcopy(artist)}
        return {"status": "error", "message": f"Artist {artist_id} not found."}

    def search_content(self, query: str, content_type: Literal["song", "album", "playlist", "artist", "all"] = "all") -> Dict[str, Any]:
        """
        Searches for content (songs, albums, playlists, artists) by a given query.
        """
        results = {}

        if content_type in ["song", "all"]:
            matched_songs = [copy.deepcopy(s) for s in self.songs.values() if query.lower() in s["title"].lower()]
            results["songs"] = matched_songs
        
        if content_type in ["album", "all"]:
            matched_albums = [copy.deepcopy(a) for a in self.albums.values() if query.lower() in a["title"].lower()]
            results["albums"] = matched_albums

        if content_type in ["playlist", "all"]:
            user_data = self._get_current_user_data()
            matched_playlists = []
            for p in self.playlists.values():
                if query.lower() in p["name"].lower():
                    if p.get("public") or (user_data and p.get("user_id") == user_data["id"]):
                        matched_playlists.append(copy.deepcopy(p))
            results["playlists"] = matched_playlists

        if content_type in ["artist", "all"]:
            matched_artists = [copy.deepcopy(ar) for ar in self.artists.values() if query.lower() in ar["name"].lower()]
            results["artists"] = matched_artists

        return {"status": "success", "results": results}

    def play_content(self, content_type: Literal["song", "album", "playlist"], content_id: str) -> Dict[str, Any]:
        """
        Simulates playing a song, album, or playlist.
        """
        content = None
        if content_type == "song":
            content = self.songs.get(content_id)
        elif content_type == "album":
            content = self.albums.get(content_id)
        elif content_type == "playlist":
            content = self.playlists.get(content_id)
            user_data = self._get_current_user_data()
            if content and not content.get("public") and (not user_data or content.get("user_id") != user_data["id"]):
                return {"status": "error", "message": "Access denied to private playlist."}

        if content:
            return {"status": "success", "message": f"Now playing {content_type}: {content.get('title') or content.get('name')} (ID: {content_id})."}
        return {"status": "error", "message": f"{content_type.capitalize()} with ID {content_id} not found."}


    def reset_data(self) -> Dict[str, bool]:
        """
        Resets all simulated data in the dummy backend to its default state.
        This is a utility function for testing and not a standard API endpoint.

        Returns:
            Dict: A dictionary indicating the success of the reset operation.
        """
        global DEFAULT_STATE
        DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)
        self._load_scenario(DEFAULT_STATE)
        print("SpotifyApis: All dummy data reset to default state.")
        return {"reset_status": True}