import datetime
import copy
import uuid
import random
import json
from typing import Dict, Any

_initial_user_email_to_uuid_map = {}
_initial_song_id_to_uuid_map = {}
_initial_album_id_to_uuid_map = {}
_initial_playlist_id_to_uuid_map = {}
_initial_artist_id_to_uuid_map = {}
_initial_payment_card_id_to_uuid_map = {}

def generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365*5):
    delta_days = random.randint(days_ago_min, days_ago_max)
    time_offset = datetime.timedelta(days=delta_days, 
                                     hours=random.randint(0, 23), 
                                     minutes=random.randint(0, 59), 
                                     seconds=random.randint(0, 59))
    dt = datetime.datetime.now(datetime.timezone.utc) - time_offset
    return dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

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
    converted_data = copy.deepcopy(initial_data)

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

    new_songs = {}
    for old_id, song_data in converted_data.get("songs", {}).items():
        new_id = str(uuid.uuid4())
        _initial_song_id_to_uuid_map[old_id] = new_id
        song_data["id"] = new_id
        if "release_date" not in song_data or not song_data["release_date"]:
            song_data["release_date"] = generate_random_iso_timestamp(days_ago_min=30, days_ago_max=365*3)
        if "popularity_score" not in song_data:
            song_data["popularity_score"] = random.randint(30, 95)
        if "explicit" not in song_data:
            song_data["explicit"] = random.random() < 0.15
        if "language" not in song_data:
            song_data["language"] = random.choice(languages)
        if "stream_count" not in song_data:
            song_data["stream_count"] = random.randint(1000, 50000000)
        new_songs[new_id] = song_data
    converted_data["songs"] = new_songs

    new_albums = {}
    for old_id, album_data in converted_data.get("albums", {}).items():
        new_id = str(uuid.uuid4())
        _initial_album_id_to_uuid_map[old_id] = new_id
        album_data["id"] = new_id
        if "release_date" not in album_data or not album_data["release_date"]:
            album_data["release_date"] = generate_random_iso_timestamp(days_ago_min=30, days_ago_max=365*4)
        album_data["tracks"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in album_data.get("tracks", [])]
        
        if "album_type" not in album_data:
            album_data["album_type"] = random.choice(album_types)
        if "total_tracks" not in album_data:
            album_data["total_tracks"] = len(album_data["tracks"])
        if "label" not in album_data:
            album_data["label"] = random.choice(["Indie Records", "MegaMusic Inc.", "SoundWave Studio", "Harmony Arts"])
        new_albums[new_id] = album_data
    converted_data["albums"] = new_albums

    new_artists = {}
    for old_id, artist_data in converted_data.get("artists", {}).items():
        new_id = str(uuid.uuid4())
        _initial_artist_id_to_uuid_map[old_id] = new_id
        artist_data["id"] = new_id
        artist_data["albums"] = [_initial_album_id_to_uuid_map.get(a_id, a_id) for a_id in artist_data.get("albums", [])]
        
        if "bio" not in artist_data:
            artist_data["bio"] = f"A talented artist known for their unique blend of {artist_data.get('genre', 'music')}."
        if "country_origin" not in artist_data:
            artist_data["country_origin"] = random.choice(countries)
        if "followers_count" not in artist_data:
            artist_data["followers_count"] = random.randint(500, 10000000)
        if "is_verified" not in artist_data:
            artist_data["is_verified"] = random.random() < 0.7
        new_artists[new_id] = artist_data
    converted_data["artists"] = new_artists

    new_playlists = {}
    for old_id, playlist_data in converted_data.get("playlists", {}).items():
        new_id = str(uuid.uuid4())
        _initial_playlist_id_to_uuid_map[old_id] = new_id
        playlist_data["id"] = new_id
        if "created_at" not in playlist_data or not playlist_data["created_at"]:
            playlist_data["created_at"] = generate_random_iso_timestamp(days_ago_min=60, days_ago_max=365*2)
        if "updated_at" not in playlist_data or not playlist_data["updated_at"]:
            playlist_data["updated_at"] = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=60)
        playlist_data["tracks"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in playlist_data.get("tracks", [])]
        
        if "follower_count" not in playlist_data:
            playlist_data["follower_count"] = random.randint(10, 500000)
        if "collaborative" not in playlist_data:
            playlist_data["collaborative"] = random.random() < 0.1
        if "image_url" not in playlist_data:
            playlist_data["image_url"] = f"https://example.com/playlists/{new_id}.jpg"
        new_playlists[new_id] = playlist_data
    converted_data["playlists"] = new_playlists

    new_users = {}
    for email, user_data in converted_data.get("users", {}).items():
        user_id = str(uuid.uuid4())
        _initial_user_email_to_uuid_map[email] = user_id
        user_data["id"] = user_id
        
        user_data["liked_songs"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in user_data.get("liked_songs", [])]
        user_data["liked_albums"] = [_initial_album_id_to_uuid_map.get(a_id, a_id) for a_id in user_data.get("liked_albums", [])]
        user_data["liked_playlists"] = [_initial_playlist_id_to_uuid_map.get(p_id, p_id) for p_id in user_data.get("liked_playlists", [])]
        user_data["following_artists"] = [_initial_artist_id_to_uuid_map.get(ar_id, ar_id) for ar_id in user_data.get("following_artists", [])]
        user_data["library_songs"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in user_data.get("library_songs", [])]
        user_data["library_albums"] = [_initial_album_id_to_uuid_map.get(a_id, a_id) for a_id in user_data.get("library_albums", [])]
        user_data["downloaded_songs"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in user_data.get("downloaded_songs", [])]

        if "registration_date" not in user_data:
            user_data["registration_date"] = generate_random_iso_timestamp(days_ago_min=365, days_ago_max=365*5)
        if "last_active_date" not in user_data:
            user_data["last_active_date"] = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=30)
        if "preferred_genre" not in user_data:
            user_data["preferred_genre"] = random.choice(common_genres)
        if "total_play_time_ms" not in user_data:
            user_data["total_play_time_ms"] = random.randint(1000000, 900000000)

        if "country" not in user_data:
            user_data["country"] = random.choice(countries)
        if "device_type" not in user_data:
            user_data["device_type"] = random.choice(device_types)
        
        new_users[user_id] = user_data
    converted_data["users"] = new_users

    new_payment_cards = {}
    for old_id, card_data in converted_data.get("payment_cards", {}).items():
        new_id = str(uuid.uuid4())
        _initial_payment_card_id_to_uuid_map[old_id] = new_id
        card_data["id"] = new_id
        user_email_for_card = card_data.get("user_email")
        if user_email_for_card and user_email_for_card in _initial_user_email_to_uuid_map:
            card_data["user_id"] = _initial_user_email_to_uuid_map[user_email_for_card]
        else:
            card_data["user_id"] = random.choice(list(new_users.keys())) 
        
        del card_data["user_email"]
        
        if "card_type" not in card_data:
            card_data["card_type"] = random.choice(card_types)
        if "billing_address" not in card_data:
            card_data["billing_address"] = f"{random.randint(100, 999)} {random.choice(['Elm', 'Pine', 'Oak'])} St, Anytown, {random.choice(['NY', 'CA', 'TX'])}"

        new_payment_cards[new_id] = card_data
    converted_data["payment_cards"] = new_payment_cards

    return converted_data

RAW_DEFAULT_STATE = {
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

DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)

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
        albums.append(generate_album_data(artist_id))
    
    for album_uuid, album_data in albums:
        DEFAULT_STATE["albums"][album_uuid] = album_data
        all_albums_uuid.append(album_uuid)

    artist_data = {
        "id": artist_id,
        "name": name,
        "genre": genre,
        "albums": [album[0] for album in albums],
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
    duration_ms = random.randint(150000, 300000)
    genre = random.choice(common_genres)
    
    album_release_dt = datetime.datetime.fromisoformat(album_release_date.replace('Z', '+00:00'))
    song_release_dt = album_release_dt + datetime.timedelta(days=random.randint(0, 30))
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
    public = random.random() < 0.7
    
    num_tracks = random.randint(5, 50)
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
        "owner_id": user_id,
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
    is_default = random.random() < 0.5

    card_name = f"{random.choice(first_names)}'s {card_type}"
    billing_address = f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Maple', 'Pine'])} St, {random.choice(['Springfield', 'Rivertown', 'Metropolis'])}, {random.choice(['NY', 'CA', 'TX', 'FL'])}, {random.randint(10001, 99999)}"

    return card_id, {
        "id": card_id,
        "card_name": card_name,
        "user_id": user_id,
        "card_number": card_number,
        "expiry_year": expiry_year,
        "expiry_month": expiry_month,
        "cvv_number": "XXX",
        "is_default": is_default,
        "card_type": card_type,
        "billing_address": billing_address
    }

num_additional_users = 48
num_artists_to_add = 20
num_playlists_to_add = 30

for _ in range(num_artists_to_add):
    artist_uuid, artist_data = generate_artist_data()
    DEFAULT_STATE["artists"][artist_uuid] = artist_data
    all_artists_uuid.append(artist_uuid)

for i in range(num_additional_users):
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = f"{first.lower()}.{last.lower()}{random.randint(1, 999)}@{random.choice(email_domains)}"
    
    all_current_emails = set([u["email"] for u in DEFAULT_STATE["users"].values()])
    while email in all_current_emails:
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 999)}@{random.choice(email_domains)}"

    user_id = str(uuid.uuid4())
    _initial_user_email_to_uuid_map[email] = user_id

    num_liked_songs = random.randint(5, min(50, len(all_songs_uuid)))
    num_liked_albums = random.randint(1, min(10, len(all_albums_uuid)))
    num_following_artists = random.randint(1, min(8, len(all_artists_uuid)))
    num_library_songs = random.randint(10, min(100, len(all_songs_uuid)))
    num_library_albums = random.randint(2, min(20, len(all_albums_uuid)))
    num_downloaded_songs = random.randint(0, min(20, len(all_songs_uuid)))

    new_user_data = {
        "id": user_id,
        "first_name": first,
        "last_name": last,
        "email": email,
        "verified": random.random() < 0.9,
        "liked_songs": random.sample(all_songs_uuid, num_liked_songs),
        "liked_albums": random.sample(all_albums_uuid, num_liked_albums),
        "liked_playlists": [],
        "following_artists": random.sample(all_artists_uuid, num_following_artists),
        "library_songs": random.sample(all_songs_uuid, num_library_songs),
        "library_albums": random.sample(all_albums_uuid, num_library_albums),
        "downloaded_songs": random.sample(all_songs_uuid, num_downloaded_songs),
        "premium": random.random() < 0.6,
        "registration_date": generate_random_iso_timestamp(days_ago_min=365, days_ago_max=365*5),
        "last_active_date": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=30),
        "preferred_genre": random.choice(common_genres),
        "total_play_time_ms": random.randint(5000000, 1000000000),
        "country": random.choice(countries),
        "device_type": random.choice(device_types)
    }
    DEFAULT_STATE["users"][user_id] = new_user_data

    if new_user_data["premium"] or random.random() < 0.3:
        card_id, card_data = generate_payment_card_data(user_id)
        DEFAULT_STATE["payment_cards"][card_id] = card_data

user_uuids = list(DEFAULT_STATE["users"].keys())
for _ in range(num_playlists_to_add):
    if user_uuids:
        owner_id = random.choice(user_uuids)
        playlist_uuid, playlist_data = generate_playlist_data(owner_id)
        DEFAULT_STATE["playlists"][playlist_uuid] = playlist_data
        all_playlists_uuid.append(playlist_uuid)

for user_data in DEFAULT_STATE["users"].values():
    if not user_data["liked_playlists"]:
        num_liked_playlists = random.randint(1, min(5, len(all_playlists_uuid)))
        if all_playlists_uuid:
            user_data["liked_playlists"] = random.sample(all_playlists_uuid, num_liked_playlists)

output_filename = 'diverse_spotify_state.json'
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Total number of users: {len(DEFAULT_STATE['users'])}")
print(f"Total number of songs: {len(DEFAULT_STATE['songs'])}")
print(f"Total number of albums: {len(DEFAULT_STATE['albums'])}")
print(f"Total number of artists: {len(DEFAULT_STATE['artists'])}")
print(f"Total number of playlists: {len(DEFAULT_STATE['playlists'])}")
print(f"Total number of payment cards: {len(DEFAULT_STATE['payment_cards'])}")
print(f"Generated DEFAULT_STATE saved to '{output_filename}'")