import datetime
import json
import copy
import uuid
import random
from typing import Dict, Any
from fake_data import first_names, last_names, domains, social_media_bios, post_texts

_initial_user_id_map = {}
_initial_post_id_map = {}
_initial_dm_conv_id_map = {}


def _convert_initial_data_to_uuids(initial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Converts the initial RAW_DEFAULT_STATE data to use UUIDs for all relevant IDs and adds realism."""

    converted_data = copy.deepcopy(initial_data)

    global _initial_user_id_map
    global _initial_post_id_map
    global _initial_dm_conv_id_map

    _initial_user_id_map = {}
    _initial_post_id_map = {}
    _initial_dm_conv_id_map = {}

    current_time_iso = (
        datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")
        + "Z"
    )

    new_users = {}
    for old_user_id, user_data in converted_data.get("users", {}).items():
        user_uuid = str(uuid.uuid4())
        _initial_user_id_map[old_user_id] = user_uuid
        user_data["id"] = user_uuid

        if "followers" in user_data:
            user_data["followers"] = [f_id for f_id in user_data["followers"]]
        if "following" in user_data:
            user_data["following"] = [f_id for f_id in user_data["following"]]

        if "joined_date" in user_data and not isinstance(user_data["joined_date"], str):
            user_data["joined_date"] = (
                user_data["joined_date"].isoformat(timespec="milliseconds") + "Z"
            )

        new_users[user_uuid] = user_data
    converted_data["users"] = new_users

    new_posts = {}
    for old_post_id, post_data in converted_data.get("posts", {}).items():
        post_uuid = str(uuid.uuid4())
        _initial_post_id_map[old_post_id] = post_uuid
        post_data["id"] = post_uuid

        if "author_id" in post_data:
            post_data["author_id"] = _initial_user_id_map.get(
                post_data["author_id"], post_data["author_id"]
            )

        if "created_at" in post_data and not isinstance(post_data["created_at"], str):
            post_data["created_at"] = (
                post_data["created_at"].isoformat(timespec="milliseconds") + "Z"
            )
        elif "created_at" not in post_data:
            post_data["created_at"] = current_time_iso

        if "likes" in post_data:
            post_data["likes"] = [
                _initial_user_id_map.get(l_id, l_id) for l_id in post_data["likes"]
            ]

        new_posts[post_uuid] = post_data
    converted_data["posts"] = new_posts

    for user_uuid, user_data in converted_data["users"].items():
        if "liked_posts" in user_data:
            user_data["liked_posts"] = [
                _initial_post_id_map.get(p_id, p_id)
                for p_id in user_data["liked_posts"]
            ]

            user_data["liked_posts"] = [
                p_id for p_id in user_data["liked_posts"] if p_id in new_posts
            ]

        if "posts" in user_data:
            user_data["posts"] = [
                _initial_post_id_map.get(p_id, p_id) for p_id in user_data["posts"]
            ]

            user_data["posts"] = [
                p_id for p_id in user_data["posts"] if p_id in new_posts
            ]

        if "followers" in user_data:
            user_data["followers"] = [
                _initial_user_id_map.get(f_id, f_id) for f_id in user_data["followers"]
            ]
            user_data["followers"] = [
                f_id for f_id in user_data["followers"] if f_id in new_users
            ]
        if "following" in user_data:
            user_data["following"] = [
                _initial_user_id_map.get(f_id, f_id) for f_id in user_data["following"]
            ]
            user_data["following"] = [
                f_id for f_id in user_data["following"] if f_id in new_users
            ]

    new_direct_messages = {}
    for old_dm_conv_id, dm_conv_data in converted_data.get(
        "direct_messages", {}
    ).items():
        dm_conv_uuid = str(uuid.uuid4())
        _initial_dm_conv_id_map[old_dm_conv_id] = dm_conv_uuid
        dm_conv_data["id"] = dm_conv_uuid

        if "participants" in dm_conv_data:
            dm_conv_data["participants"] = [
                _initial_user_id_map.get(p_id, p_id)
                for p_id in dm_conv_data["participants"]
            ]

            dm_conv_data["participants"] = [
                p_id for p_id in dm_conv_data["participants"] if p_id in new_users
            ]

        new_messages = []
        for message in dm_conv_data.get("messages", []):
            message_uuid = str(uuid.uuid4())
            message["id"] = message_uuid

            if "sender_id" in message:
                message["sender_id"] = _initial_user_id_map.get(
                    message["sender_id"], message["sender_id"]
                )

            if "timestamp" not in message:
                message["timestamp"] = current_time_iso
            elif not isinstance(message["timestamp"], str):
                message["timestamp"] = (
                    message["timestamp"].isoformat(timespec="milliseconds") + "Z"
                )

            new_messages.append(message)
        dm_conv_data["messages"] = new_messages

        new_direct_messages[dm_conv_uuid] = dm_conv_data
    converted_data["direct_messages"] = new_direct_messages

    return converted_data


def generate_random_iso_timestamp(days_ago_min=0, days_ago_max=365 * 5):
    """Generates a random ISO 8601 timestamp within a given range of days ago."""
    delta_days = random.randint(days_ago_min, days_ago_max)
    time_offset = datetime.timedelta(
        days=delta_days,
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    dt = datetime.datetime.now(datetime.timezone.utc) - time_offset
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")

dm_messages = [
    "Hey, how have you been?",
    "Did you see that article I sent you?",
    "What are you up to this weekend?",
    "Can you help me with something?",
    "Just wanted to say hi!",
    "Thinking of you.",
    "Let's catch up soon.",
    "Got any recommendations?",
    "That was hilarious!",
    "I agree with you.",
    "Thanks for the help!",
    "No problem, happy to assist.",
    "I'll get back to you on that.",
    "Sounds good!",
    "See you later!",
    "Hope you're having a great day.",
    "I just saw your latest post, amazing!",
    "Thinking of getting into a new hobby, any suggestions?",
    "Need to vent for a second...",
    "Just wanted to share some good news!",
]


RAW_DEFAULT_STATE = {
    "users": {
        "usr_alice_smith": {
            "id": "usr_alice_smith",
            "username": "alice_smith",
            "name": "Alice Smith",
            "email": "alice.smith@hostinger.com",
            "joined_date": datetime.datetime(
                2023, 1, 15, 10, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "bio": "Tech enthusiast and amateur photographer. Sharing my thoughts on AI and the digital world.",
            "profile_picture_url": "https://x.com/profiles/alice_smith.jpg",
            "followers": ["usr_john_doe", "usr_emily_white"],
            "following": ["usr_john_doe", "usr_bob_johnson"],
            "liked_posts": ["post_002", "post_005"],
            "posts": ["post_001", "post_004", "post_006"],
            "api_usage": {"posts_created": 3, "dms_sent": 2, "profile_views": 15},
            "is_verified": True,
        },
        "usr_john_doe": {
            "id": "usr_john_doe",
            "username": "john_doe",
            "name": "John Doe",
            "email": "john.doe@hostinger.com",
            "joined_date": datetime.datetime(
                2022, 11, 1, 14, 30, 0, tzinfo=datetime.timezone.utc
            ),
            "bio": "Software developer and open-source contributor.",
            "profile_picture_url": "https://x.com/profiles/john_doe.jpg",
            "followers": ["usr_alice_smith"],
            "following": ["usr_alice_smith", "usr_emily_white"],
            "liked_posts": ["post_001", "post_003"],
            "posts": ["post_002", "post_003"],
            "api_usage": {"posts_created": 2, "dms_sent": 3, "profile_views": 10},
            "is_verified": False,
        },
        "usr_emily_white": {
            "id": "usr_emily_white",
            "username": "emily_white",
            "name": "Emily White",
            "email": "emily.white@hostinger.com",
            "joined_date": datetime.datetime(
                2024, 3, 20, 9, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "bio": "Digital artist exploring new creative frontiers.",
            "profile_picture_url": "https://x.com/profiles/emily_white.jpg",
            "followers": ["usr_alice_smith", "usr_john_doe"],
            "following": [],
            "liked_posts": [],
            "posts": ["post_005"],
            "api_usage": {"posts_created": 1, "dms_sent": 1, "profile_views": 8},
            "is_verified": False,
        },
        "usr_bob_johnson": {
            "id": "usr_bob_johnson",
            "username": "bob_johnson",
            "name": "Bob Johnson",
            "email": "bob.johnson@hostinger.com",
            "joined_date": datetime.datetime(
                2023, 5, 1, 11, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "bio": "Musician and foodie.",
            "profile_picture_url": "https://x.com/profiles/bob_johnson.jpg",
            "followers": ["usr_alice_smith"],
            "following": [],
            "liked_posts": [],
            "posts": [],
            "api_usage": {},
            "is_verified": False,
        },
    },
    "posts": {
        "post_001": {
            "id": "post_001",
            "author_id": "usr_alice_smith",
            "text": "Excited about the new AI developments!",
            "created_at": datetime.datetime(
                2024, 7, 20, 8, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "likes": ["usr_john_doe"],
            "reposts": [],
            "replies": [],
            "metrics": {"views": 150, "likes": 1, "reposts": 0, "replies": 0},
        },
        "post_002": {
            "id": "post_002",
            "author_id": "usr_john_doe",
            "text": "Just pushed a new update to my GitHub repo. Check it out!",
            "created_at": datetime.datetime(
                2024, 7, 21, 10, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "likes": ["usr_alice_smith"],
            "reposts": [],
            "replies": [],
            "metrics": {"views": 100, "likes": 1, "reposts": 0, "replies": 0},
        },
        "post_003": {
            "id": "post_003",
            "author_id": "usr_john_doe",
            "text": "Having a great time learning about quantum computing. Mind-blowing stuff!",
            "created_at": datetime.datetime(
                2024, 7, 22, 15, 30, 0, tzinfo=datetime.timezone.utc
            ),
            "likes": ["usr_john_doe"],
            "reposts": [],
            "replies": [],
            "metrics": {"views": 80, "likes": 1, "reposts": 0, "replies": 0},
        },
        "post_004": {
            "id": "post_004",
            "author_id": "usr_alice_smith",
            "text": "Exploring new camera lenses. Any recommendations for landscape photography?",
            "created_at": datetime.datetime(
                2024, 7, 23, 9, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "likes": [],
            "reposts": [],
            "replies": [],
            "metrics": {"views": 70, "likes": 0, "reposts": 0, "replies": 0},
        },
        "post_005": {
            "id": "post_005",
            "author_id": "usr_emily_white",
            "text": "New digital art piece in progress! What do you think?",
            "created_at": datetime.datetime(
                2024, 7, 24, 11, 45, 0, tzinfo=datetime.timezone.utc
            ),
            "likes": ["usr_alice_smith"],
            "reposts": [],
            "replies": [],
            "metrics": {"views": 120, "likes": 1, "reposts": 0, "replies": 0},
        },
        "post_006": {
            "id": "post_006",
            "author_id": "usr_alice_smith",
            "text": "Just finished a great book on mindful living. Highly recommend!",
            "created_at": datetime.datetime(
                2024, 7, 25, 14, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "likes": [],
            "reposts": [],
            "replies": [],
            "metrics": {"views": 60, "likes": 0, "reposts": 0, "replies": 0},
        },
    },
    "direct_messages": {
        "dm_conv_alice_john": {
            "id": "dm_conv_alice_john",
            "participants": ["usr_alice_smith", "usr_john_doe"],
            "messages": [
                {
                    "sender_id": "usr_alice_smith",
                    "text": "Hey John, did you see the latest tech news?",
                    "timestamp": (
                        datetime.datetime.now(datetime.timezone.utc)
                        - datetime.timedelta(days=2)
                    ).isoformat(timespec="milliseconds")
                    + "Z",
                },
                {
                    "sender_id": "usr_john_doe",
                    "text": "Not yet, Alice! Anything exciting happening?",
                    "timestamp": (
                        datetime.datetime.now(datetime.timezone.utc)
                        - datetime.timedelta(days=2, minutes=5)
                    ).isoformat(timespec="milliseconds")
                    + "Z",
                },
                {
                    "sender_id": "usr_alice_smith",
                    "text": "Just read about a breakthrough in AI ethics!",
                    "timestamp": (
                        datetime.datetime.now(datetime.timezone.utc)
                        - datetime.timedelta(days=1)
                    ).isoformat(timespec="milliseconds")
                    + "Z",
                },
            ],
        },
        "dm_conv_alice_emily": {
            "id": "dm_conv_alice_emily",
            "participants": ["usr_alice_smith", "usr_emily_white"],
            "messages": [
                {
                    "sender_id": "usr_alice_smith",
                    "text": "Loved your new art piece, Emily! Stunning!",
                    "timestamp": (
                        datetime.datetime.now(datetime.timezone.utc)
                        - datetime.timedelta(hours=10)
                    ).isoformat(timespec="milliseconds")
                    + "Z",
                },
                {
                    "sender_id": "usr_emily_white",
                    "text": "Thanks, Alice! Glad you liked it.",
                    "timestamp": (
                        datetime.datetime.now(datetime.timezone.utc)
                        - datetime.timedelta(hours=9)
                    ).isoformat(timespec="milliseconds")
                    + "Z",
                },
            ],
        },
    },
}


DEFAULT_STATE = _convert_initial_data_to_uuids(RAW_DEFAULT_STATE)

num_initial_users = len(DEFAULT_STATE["users"])
num_users_to_add = 50 - num_initial_users

existing_usernames = set(
    user_data["username"] for user_data in DEFAULT_STATE["users"].values()
)
existing_emails = set(
    user_data["email"] for user_data in DEFAULT_STATE["users"].values()
)

new_user_ids = []

for i in range(num_users_to_add):
    first = random.choice(first_names)
    last = random.choice(last_names)
    username = f"{first.lower()}_{last.lower()}{random.randint(10, 99)}"
    email = f"{first.lower()}.{last.lower()}{random.randint(100, 9999)}@{random.choice(domains)}"

    while username in existing_usernames:
        username = f"{first.lower()}_{last.lower()}{random.randint(10, 99)}"
    while email in existing_emails:
        email = f"{first.lower()}.{last.lower()}{random.randint(100, 9999)}@{random.choice(domains)}"

    existing_usernames.add(username)
    existing_emails.add(email)

    user_id = str(uuid.uuid4())
    new_user_ids.append(user_id)

    new_user_data = {
        "id": user_id,
        "username": username,
        "name": f"{first} {last}",
        "email": email,
        "joined_date": generate_random_iso_timestamp(
            days_ago_min=365, days_ago_max=365 * 4
        ),
        "bio": random.choice(social_media_bios),
        "profile_picture_url": f"[https://x.com/profiles/](https://x.com/profiles/){username}.jpg",
        "followers": [],
        "following": [],
        "liked_posts": [],
        "posts": [],
        "api_usage": {
            "posts_created": random.randint(0, 50),
            "dms_sent": random.randint(0, 100),
            "profile_views": random.randint(5, 500),
        },
        "is_verified": random.random() < 0.1,
    }
    DEFAULT_STATE["users"][user_id] = new_user_data

all_user_uuids = list(DEFAULT_STATE["users"].keys())


for user_id in all_user_uuids:
    user_data = DEFAULT_STATE["users"][user_id]

    num_followers = random.randint(0, min(20, len(all_user_uuids) - 1))
    possible_followers = [uid for uid in all_user_uuids if uid != user_id]
    user_data["followers"].extend(random.sample(possible_followers, num_followers))

    num_following = random.randint(0, min(15, len(all_user_uuids) - 1))
    possible_following = [
        uid
        for uid in all_user_uuids
        if uid != user_id and uid not in user_data["followers"]
    ]
    user_data["following"].extend(random.sample(possible_following, num_following))

    user_data["followers"] = [f for f in user_data["followers"] if f != user_id]
    user_data["following"] = [f for f in user_data["following"] if f != user_id]

    for followed_id in list(user_data["following"]):
        if random.random() < 0.3:
            if user_id not in DEFAULT_STATE["users"][followed_id]["followers"]:
                DEFAULT_STATE["users"][followed_id]["followers"].append(user_id)

    for follower_id in list(user_data["followers"]):
        if random.random() < 0.1:
            if follower_id not in user_data["following"]:
                user_data["following"].append(follower_id)

    user_data["followers"] = list(set(user_data["followers"]))
    user_data["following"] = list(set(user_data["following"]))


num_posts_to_add = 150

for i in range(num_posts_to_add):
    author_id = random.choice(all_user_uuids)
    post_uuid = str(uuid.uuid4())
    created_at = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=180)

    num_likes = random.choices(
        [0, 1, 2, 3, 5, 10, 20], weights=[0.4, 0.2, 0.15, 0.1, 0.05, 0.05, 0.05], k=1
    )[0]
    possible_likers = [uid for uid in all_user_uuids if uid != author_id]
    likes = random.sample(possible_likers, min(num_likes, len(possible_likers)))

    num_reposts = random.choices([0, 1, 2, 3], weights=[0.6, 0.2, 0.1, 0.1], k=1)[0]
    num_replies = random.choices([0, 1, 2, 3], weights=[0.5, 0.25, 0.15, 0.1], k=1)[0]

    post_data = {
        "id": post_uuid,
        "author_id": author_id,
        "text": random.choice(post_texts),
        "created_at": created_at,
        "likes": likes,
        "reposts": [],
        "replies": [],
        "metrics": {
            "views": random.randint(10, 2000),
            "likes": len(likes),
            "reposts": num_reposts,
            "replies": num_replies,
        },
    }
    DEFAULT_STATE["posts"][post_uuid] = post_data
    DEFAULT_STATE["users"][author_id]["posts"].append(post_uuid)

    for liker_id in likes:
        if random.random() < 0.8:
            DEFAULT_STATE["users"][liker_id]["liked_posts"].append(post_uuid)

    for user_id in all_user_uuids:
        DEFAULT_STATE["users"][user_id]["liked_posts"] = list(
            set(DEFAULT_STATE["users"][user_id]["liked_posts"])
        )


num_dm_convs_to_add = 30

for i in range(num_dm_convs_to_add):

    if len(all_user_uuids) < 2:
        break

    participants = random.sample(all_user_uuids, 2)
    p1_id, p2_id = participants[0], participants[1]

    dm_conv_uuid = str(uuid.uuid4())

    num_messages = random.randint(2, 15)
    messages = []
    for m_idx in range(num_messages):
        sender_id = random.choice([p1_id, p2_id])
        timestamp = generate_random_iso_timestamp(days_ago_min=0, days_ago_max=30)
        messages.append(
            {
                "id": str(uuid.uuid4()),
                "sender_id": sender_id,
                "text": random.choice(dm_messages),
                "timestamp": timestamp,
            }
        )

    messages.sort(key=lambda x: x["timestamp"])

    DEFAULT_STATE["direct_messages"][dm_conv_uuid] = {
        "id": dm_conv_uuid,
        "participants": participants,
        "messages": messages,
    }

    for message in messages:
        sender_uuid = message["sender_id"]
        if "api_usage" in DEFAULT_STATE["users"][sender_uuid]:
            DEFAULT_STATE["users"][sender_uuid]["api_usage"]["dms_sent"] = (
                DEFAULT_STATE["users"][sender_uuid]["api_usage"].get("dms_sent", 0) + 1
            )
        else:
            DEFAULT_STATE["users"][sender_uuid]["api_usage"] = {"dms_sent": 1}


output_filename = "diverse_x_state.json"
with open(output_filename, "w") as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Total number of users: {len(DEFAULT_STATE['users'])}")
print(f"Total number of posts: {len(DEFAULT_STATE['posts'])}")
print(
    f"Total number of direct message conversations: {len(DEFAULT_STATE['direct_messages'])}"
)
print(f"Generated DEFAULT_STATE saved to '{output_filename}'")
