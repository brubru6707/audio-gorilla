import datetime
import copy
import uuid
import random
import json
from typing import Dict, Any
# Assuming fake_data.py contains the necessary lists (first_names, etc.)
from fake_data import first_names, last_names, domains, playlist_bios, playlist_titles, artist_names, countries, artist_bios, user_count, first_and_last_names

# --- MAPPING AND STATE INITIALIZATION ---
_initial_user_email_to_uuid_map = {}
_initial_song_id_to_uuid_map = {}
_initial_album_id_to_uuid_map = {}
_initial_playlist_id_to_uuid_map = {}
_initial_artist_id_to_uuid_map = {}
_initial_payment_card_id_to_uuid_map = {}

# --- HELPER FUNCTIONS AND CONSTANTS ---
def generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365*5):
    """Generates a random UTC ISO 8601 timestamp in the past."""
    delta_days = random.randint(days_ago_min, days_ago_max)
    time_offset = datetime.timedelta(days=delta_days,
                                     hours=random.randint(0, 23),
                                     minutes=random.randint(0, 59),
                                     seconds=random.randint(0, 59))
    dt = datetime.datetime.now(datetime.timezone.utc) - time_offset
    return dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

music_genres = ["Pop", "Electronic", "Acoustic", "Folk", "Funk", "Rock", "Hip Hop", "R&B", "Jazz", "Classical", "Country", "Indie", "Blues", "Metal", "Reggae", "Dance", "Ambient", "Soul", "Gospel", "Latin"]
album_types = ["album", "single", "ep", "compilation", "live"]
card_types = ["Visa", "Mastercard", "Amex", "Discover", "JCB"]
device_types = ["mobile", "web", "desktop", "smart_speaker", "tablet", "car_audio"]
languages = ["en", "es", "fr", "de", "jp", "ko", "zh", "pt", "it"]

def _convert_initial_data_to_uuids(initial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Processes an initial data structure, converting IDs to UUIDs and filling in missing fields."""
    converted_data = copy.deepcopy(initial_data)

    global _initial_user_email_to_uuid_map, _initial_song_id_to_uuid_map, _initial_album_id_to_uuid_map
    global _initial_playlist_id_to_uuid_map, _initial_artist_id_to_uuid_map, _initial_payment_card_id_to_uuid_map
    
    # Reset maps
    _initial_user_email_to_uuid_map = {}
    _initial_song_id_to_uuid_map = {}
    _initial_album_id_to_uuid_map = {}
    _initial_playlist_id_to_uuid_map = {}
    _initial_artist_id_to_uuid_map = {}
    _initial_payment_card_id_to_uuid_map = {}

    # Process songs
    new_songs = {}
    for old_id, song_data in converted_data.get("songs", {}).items():
        new_id = str(uuid.uuid4())
        _initial_song_id_to_uuid_map[old_id] = new_id
        song_data["id"] = new_id
        if "release_date" not in song_data or not song_data["release_date"]:
            song_data["release_date"] = generate_random_iso_timestamp(days_ago_min=30, days_ago_max=365*3)
        if "popularity_score" not in song_data:
            song_data["popularity_score"] = random.randint(30, 95)
        song_data.setdefault("explicit", random.random() < 0.15)
        song_data.setdefault("language", random.choice(languages))
        song_data.setdefault("stream_count", random.randint(1000, 50000000))
        new_songs[new_id] = song_data
    converted_data["songs"] = new_songs

    # Process albums
    new_albums = {}
    for old_id, album_data in converted_data.get("albums", {}).items():
        new_id = str(uuid.uuid4())
        _initial_album_id_to_uuid_map[old_id] = new_id
        album_data["id"] = new_id
        if "release_date" not in album_data or not album_data["release_date"]:
            album_data["release_date"] = generate_random_iso_timestamp(days_ago_min=30, days_ago_max=365*4)
        album_data["tracks"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in album_data.get("tracks", [])]
        album_data.setdefault("album_type", random.choice(album_types))
        album_data.setdefault("total_tracks", len(album_data["tracks"]))
        album_data.setdefault("label", random.choice(["Indie Records", "MegaMusic Inc.", "SoundWave Studio", "Harmony Arts"]))
        new_albums[new_id] = album_data
    converted_data["albums"] = new_albums

    # Process artists
    new_artists = {}
    for old_id, artist_data in converted_data.get("artists", {}).items():
        new_id = str(uuid.uuid4())
        _initial_artist_id_to_uuid_map[old_id] = new_id
        artist_data["id"] = new_id
        artist_data["albums"] = [_initial_album_id_to_uuid_map.get(a_id, a_id) for a_id in artist_data.get("albums", [])]
        artist_data.setdefault("bio", f"A talented artist known for their unique blend of {artist_data.get('genre', 'music')}.")
        artist_data.setdefault("country_origin", random.choice(countries))
        artist_data.setdefault("followers_count", random.randint(500, 10000000))
        artist_data.setdefault("is_verified", random.random() < 0.7)
        new_artists[new_id] = artist_data
    converted_data["artists"] = new_artists

    # Process playlists
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
        playlist_data.setdefault("follower_count", random.randint(10, 500000))
        playlist_data.setdefault("collaborative", random.random() < 0.1)
        playlist_data.setdefault("image_url", f"https://spotify.com/playlists/{new_id}.jpg")
        new_playlists[new_id] = playlist_data
    converted_data["playlists"] = new_playlists

    # Process users
    new_users = {}
    for email, user_data in converted_data.get("users", {}).items():
        user_id = str(uuid.uuid4())
        _initial_user_email_to_uuid_map[email] = user_id
        user_data["id"] = user_id
        
        # Convert linked IDs to UUIDs
        user_data["liked_songs"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in user_data.get("liked_songs", [])]
        user_data["liked_albums"] = [_initial_album_id_to_uuid_map.get(a_id, a_id) for a_id in user_data.get("liked_albums", [])]
        user_data["liked_playlists"] = [_initial_playlist_id_to_uuid_map.get(p_id, p_id) for p_id in user_data.get("liked_playlists", [])]
        user_data["following_artists"] = [_initial_artist_id_to_uuid_map.get(ar_id, ar_id) for ar_id in user_data.get("following_artists", [])]
        user_data["library_songs"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in user_data.get("library_songs", [])]
        user_data["library_albums"] = [_initial_album_id_to_uuid_map.get(a_id, a_id) for a_id in user_data.get("library_albums", [])]
        user_data["downloaded_songs"] = [_initial_song_id_to_uuid_map.get(s_id, s_id) for s_id in user_data.get("downloaded_songs", [])]

        # Fill missing fields
        user_data.setdefault("registration_date", generate_random_iso_timestamp(days_ago_min=365, days_ago_max=365*5))
        user_data.setdefault("last_active_date", generate_random_iso_timestamp(days_ago_min=0, days_ago_max=30))
        user_data.setdefault("preferred_genre", random.choice(music_genres))
        user_data.setdefault("total_play_time_ms", random.randint(1000000, 900000000))
        user_data.setdefault("country", random.choice(countries))
        user_data.setdefault("device_type", random.choice(device_types))
        
        new_users[user_id] = user_data
    converted_data["users"] = new_users

    # Process payment cards
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
        
        card_data.setdefault("card_type", random.choice(card_types))
        card_data.setdefault("billing_address", f"{random.randint(100, 999)} {random.choice(['Elm', 'Pine', 'Oak'])} St, Anytown, {random.choice(['NY', 'CA', 'TX'])}")

        new_payment_cards[new_id] = card_data
    converted_data["payment_cards"] = new_payment_cards

    return converted_data

RAW_DEFAULT_STATE = {"users": {}, "payment_cards": {}, "songs": {}, "albums": {}, "playlists": {}, "artists": {}}
DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)

all_artists_uuid = list(_initial_artist_id_to_uuid_map.values())
all_songs_uuid = list(_initial_song_id_to_uuid_map.values())
all_albums_uuid = list(_initial_album_id_to_uuid_map.values())
all_playlists_uuid = list(_initial_playlist_id_to_uuid_map.values())

# --- DATA GENERATION FUNCTIONS ---
def generate_song_data(artist_id, album_id, album_release_date):
    song_id = str(uuid.uuid4())
    title = f"{random.choice(['Fading', 'Rising', 'Silent', 'Electric'])} {random.choice(['Stars', 'Waves', 'Voices', 'Skies'])} {random.randint(1,99)}"
    
    album_release_dt = datetime.datetime.fromisoformat(album_release_date.replace('Z', '+00:00'))
    song_release_dt = album_release_dt + datetime.timedelta(days=random.randint(0, 30))
    release_date = song_release_dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

    song_data = {
        "id": song_id,
        "title": title,
        "artist_id": artist_id,
        "album_id": album_id,
        "duration_ms": random.randint(150000, 300000),
        "genre": random.choice(music_genres),
        "release_date": release_date,
        "popularity_score": random.randint(20, 99),
        "explicit": random.random() < 0.1,
        "language": random.choice(languages),
        "stream_count": random.randint(5000, 100000000)
    }
    return song_id, song_data

def generate_album_data(artist_id):
    album_id = str(uuid.uuid4())
    release_date = generate_random_iso_timestamp(days_ago_min=30, days_ago_max=365*4)
    num_tracks = random.randint(3, 15)
    
    tracks = []
    for _ in range(num_tracks):
        song_id, song_data = generate_song_data(artist_id, album_id, release_date)
        tracks.append(song_id)
        # Modify global state directly
        DEFAULT_STATE["songs"][song_id] = song_data
        all_songs_uuid.append(song_id)
        
    album_data = {
        "id": album_id,
        "title": f"{random.choice(['Echoes', 'Visions', 'Rhythms', 'Dreams'])} of {random.choice(['Tomorrow', 'Yesterday', 'Life', 'The City'])} {random.randint(1,99)}",
        "artist_id": artist_id,
        "release_date": release_date,
        "tracks": tracks,
        "album_type": random.choice(album_types),
        "total_tracks": num_tracks,
        "label": random.choice(["Indie Records", "MegaMusic Inc.", "SoundWave Studio", "Harmony Arts", "Global Beats"])
    }
    return album_id, album_data

def generate_artist_data(current_index):
    artist_id = str(uuid.uuid4())
    
    albums = []
    for _ in range(random.randint(1, 5)):
        album_uuid, album_data = generate_album_data(artist_id)
        albums.append(album_uuid)
        # Modify global state directly
        DEFAULT_STATE["albums"][album_uuid] = album_data
        all_albums_uuid.append(album_uuid)

    artist_data = {
        "id": artist_id,
        "name": artist_names[current_index],
        "genre": random.choice(music_genres),
        "albums": albums,
        "bio": artist_bios[current_index],
        "country_origin": random.choice(countries),
        "followers_count": random.randint(10000, 50000000),
        "is_verified": random.random() < 0.8
    }
    return artist_id, artist_data

def generate_playlist_data(user_id, current_index):
    playlist_id = str(uuid.uuid4())
    num_tracks = random.randint(5, 50)
    tracks = random.sample(all_songs_uuid, min(num_tracks, len(all_songs_uuid))) if all_songs_uuid else []
    
    # --- CHANGE START: Corrected timestamp logic ---
    created_at_str = generate_random_iso_timestamp(days_ago_min=60, days_ago_max=365*2)
    created_at_dt = datetime.datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
    
    # Ensure updated_at is always after created_at
    update_offset = datetime.timedelta(
        days=random.randint(0, 50),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    updated_at_dt = min(created_at_dt + update_offset, datetime.datetime.now(datetime.timezone.utc))
    updated_at_str = updated_at_dt.isoformat(timespec='seconds').replace('+00:00', 'Z')
    # --- CHANGE END ---

    playlist_data = {
        "id": playlist_id,
        "name": playlist_titles[current_index],
        "description": playlist_bios[current_index],
        "public": random.random() < 0.7,
        "tracks": tracks,
        "owner_id": user_id,
        "created_at": created_at_str,
        "updated_at": updated_at_str, # Use the corrected timestamp
        "follower_count": random.randint(5, 50000),
        "collaborative": random.random() < 0.05,
        "image_url": f"https://spotify.com/playlists/{playlist_id}.jpg"
    }
    return playlist_id, playlist_data

def generate_payment_card_data(user_id):
    card_id = str(uuid.uuid4())
    card_type = random.choice(card_types)
    last_four = ''.join(random.choices('0123456789', k=4))
    
    return card_id, {
        "id": card_id,
        "card_name": f"{random.choice(first_names)}'s {card_type}",
        "user_id": user_id,
        "card_number": f"{random.choice(['4', '5', '3'])}{''.join(random.choices('0123456789', k=11))}{last_four}",
        "expiry_year": random.randint(2026, 2032),
        "expiry_month": random.randint(1, 12),
        "cvv_number": ''.join(random.choices('0123456789', k=3)),
        "is_default": random.random() < 0.5,
        "card_type": card_type,
        "billing_address": f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Maple'])} {random.choice(['St', 'Ave'])}, {random.choice(['Springfield', 'Rivertown'])}, {random.choice(countries)}, {random.randint(10001, 99999)}"
    }

# --- CHANGE START: Refactored user generation function ---
def generate_user(first_name=None, last_name=None):
    """Generates user data and returns it, does NOT modify global state."""
    first = random.choice(first_names) if first_name is None else first_name
    last = random.choice(last_names) if last_name is None else last_name
    
    # Ensure email is unique
    email = f"{first.lower()}.{last.lower()}{random.randint(1, 999)}@{random.choice(domains)}"
    all_current_emails = set(u["email"] for u in DEFAULT_STATE["users"].values())
    while email in all_current_emails:
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 999)}@{random.choice(domains)}"

    user_id = str(uuid.uuid4())
    _initial_user_email_to_uuid_map[email] = user_id

    # Safely sample from existing data
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
        "liked_songs": random.sample(all_songs_uuid, num_liked_songs) if all_songs_uuid else [],
        "liked_albums": random.sample(all_albums_uuid, num_liked_albums) if all_albums_uuid else [],
        "liked_playlists": [],
        "following_artists": random.sample(all_artists_uuid, num_following_artists) if all_artists_uuid else [],
        "library_songs": random.sample(all_songs_uuid, num_library_songs) if all_songs_uuid else [],
        "library_albums": random.sample(all_albums_uuid, num_library_albums) if all_albums_uuid else [],
        "downloaded_songs": random.sample(all_songs_uuid, num_downloaded_songs) if all_songs_uuid else [],
        "premium": random.random() < 0.6,
        "registration_date": generate_random_iso_timestamp(days_ago_min=365, days_ago_max=365*5),
        "last_active_date": generate_random_iso_timestamp(days_ago_min=0, days_ago_max=30),
        "preferred_genre": random.choice(music_genres),
        "total_play_time_ms": random.randint(5000000, 1000000000),
        "country": random.choice(countries),
        "device_type": random.choice(device_types)
    }
    # Return the data instead of modifying state from within the function
    return user_id, new_user_data
# --- CHANGE END ---

# --- MAIN SCRIPT EXECUTION ---
print("Generating artists, albums, and songs...")
for i in range(len(artist_names)):
    artist_uuid, artist_data = generate_artist_data(i)
    DEFAULT_STATE["artists"][artist_uuid] = artist_data
    all_artists_uuid.append(artist_uuid)

print("Generating users and payment cards...")
total_users_to_generate = user_count + len(first_and_last_names)
for i in range(total_users_to_generate):
    # --- CHANGE START: Corrected user generation loop ---
    if i >= user_count:
        # Use partition for safety in case a name has no space
        first_name, _, last_name = first_and_last_names[i - user_count].partition(" ")
        user_id, user_data = generate_user(first_name=first_name, last_name=last_name)
    else:
        user_id, user_data = generate_user()
    
    # Add the generated user to the global state
    DEFAULT_STATE["users"][user_id] = user_data

    # Handle payment card generation here, not inside generate_user
    if user_data["premium"] or random.random() < 0.3:
        card_id, card_data = generate_payment_card_data(user_id)
        DEFAULT_STATE["payment_cards"][card_id] = card_data
    # --- CHANGE END ---

print("Generating playlists...")
user_uuids = list(DEFAULT_STATE["users"].keys())
num_playlists_to_add = 30
for i in range(num_playlists_to_add):
    if user_uuids:
        owner_id = random.choice(user_uuids)
        playlist_uuid, playlist_data = generate_playlist_data(owner_id, i)
        DEFAULT_STATE["playlists"][playlist_uuid] = playlist_data
        all_playlists_uuid.append(playlist_uuid)

print("Assigning liked playlists to users...")
for user_data in DEFAULT_STATE["users"].values():
    if not user_data["liked_playlists"] and all_playlists_uuid:
        num_liked_playlists = random.randint(1, min(5, len(all_playlists_uuid)))
        user_data["liked_playlists"] = random.sample(all_playlists_uuid, num_liked_playlists)

# --- OUTPUT RESULTS ---
output_filename = 'diverse_spotify_state.json'
print(f"Saving generated data to '{output_filename}'...")
with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print("\n--- Generation Summary ---")
print(f"Total number of users: {len(DEFAULT_STATE['users'])}")
print(f"Total number of songs: {len(DEFAULT_STATE['songs'])}")
print(f"Total number of albums: {len(DEFAULT_STATE['albums'])}")
print(f"Total number of artists: {len(DEFAULT_STATE['artists'])}")
print(f"Total number of playlists: {len(DEFAULT_STATE['playlists'])}")
print(f"Total number of payment cards: {len(DEFAULT_STATE['payment_cards'])}")
print(f"Generated DEFAULT_STATE saved to '{output_filename}'")