import uuid
from typing import Dict, List, Union, Literal, Any
from datetime import datetime, timedelta
from copy import deepcopy
import json

class User:
    def __init__(self, user_id: str, email: str = None):
        self.user_id = user_id
        self.email = email

import uuid
import random
from datetime import datetime, timedelta

def generate_random_date(start_year, end_year):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date.strftime("%Y-%m-%d")

def generate_user(existing_uuids, first_name=None, last_name=None, email=None, balance=None):
    user_id = str(uuid.uuid4())
    existing_uuids["users"].add(user_id)

    if not first_name:
        first_name = random.choice(["Emma", "Liam", "Olivia", "Noah", "Ava", "Isabella", "Sophia", "Jackson", "Aria", "Lucas", "Charlotte", "Ethan", "Amelia", "Mason", "Harper", "Evelyn", "Abigail", "Mia", "Benjamin", "Ella", "James", "Scarlett", "Henry", "Grace", "Alexander", "Chloe", "William", "Victoria", "Daniel", "Zoe"])
    if not last_name:
        last_name = random.choice(["Miller", "Davis", "Garcia", "Rodriguez", "Wilson", "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White", "Lopez", "Lee", "Gonzalez", "Harris", "Clark", "Lewis", "Robinson", "Walker", "Perez", "Hall", "Young", "Allen", "Sanchez", "Wright", "King"])
    if not email:
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(['gmail.com', 'yahoo.com', 'zscaler.org', 'darkhorse.net'])}"
    if balance is None:
        balance = round(random.uniform(0.00, 2500.00), 2)

    num_friends = random.randint(0, 5)
    friends = []
    if existing_uuids["users"]:
        friends = random.sample(list(existing_uuids["users"] - {user_id}), min(num_friends, len(existing_uuids["users"]) - 1))

    payment_cards = {}
    for _ in range(random.randint(0, 2)): # 0 to 2 cards per user
        card_id = str(uuid.uuid4())
        existing_uuids["payment_cards"].add(card_id)
        card_name = random.choice(["Visa", "Mastercard", "Amex", "Discover"])
        payment_cards[card_id] = {
            "card_name": f"{first_name}'s {card_name}",
            "owner_name": f"{first_name} {last_name}",
            "card_number_last4": ''.join(random.choices('0123456789', k=4)),
            "expiry_year": random.randint(datetime.now().year + 1, datetime.now().year + 6),
            "expiry_month": random.randint(1, 12),
        }

    addresses = {}
    for _ in range(random.randint(1, 2)): # 1 to 2 addresses per user
        address_id = str(uuid.uuid4())
        existing_uuids["addresses"].add(address_id)
        address_type = "Home Address" if random.random() < 0.7 else "Work Address"
        addresses[address_id] = {
            "name": address_type,
            "street_address": f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Elm', 'Maple', 'Pine'])} {random.choice(['Street', 'Avenue', 'Road', 'Lane'])}",
            "city": random.choice(["Springfield", "Fairview", "Riverside", "Lakewood", "Centerville"]),
            "state": random.choice(["CA", "NY", "TX", "FL", "IL", "GA", "WA"]),
            "country": "USA",
            "zip_code": random.randint(10000, 99999),
        }

    cart = {}
    for _ in range(random.randint(0, 3)): # 0 to 3 items in cart
        product_id = random.randint(1, 15) # Assuming more products will be added
        cart[product_id] = random.randint(1, 3)

    wish_list = {}
    for _ in range(random.randint(0, 2)): # 0 to 2 items in wish list
        product_id = random.randint(1, 15)
        wish_list[product_id] = {"added_date": generate_random_date(2023, 2024)}

    orders = {}
    num_orders = random.randint(0, 3)
    user_address_ids = list(addresses.keys())
    user_card_ids = list(payment_cards.keys())

    for _ in range(num_orders):
        order_id = str(uuid.uuid4())
        order_date = generate_random_date(2023, 2025)
        total_amount = round(random.uniform(10.00, 1500.00), 2)
        products_in_order = {}
        for _ in range(random.randint(1, 3)):
            product_id = random.randint(1, 15)
            products_in_order[product_id] = random.randint(1, 2)

        delivery_address_id = random.choice(user_address_ids) if user_address_ids else None
        payment_card_id = random.choice(user_card_ids) if user_card_ids else None
        status = random.choice(["delivered", "shipped", "pending", "cancelled"])
        promo_code_applied = random.choice([None, "WELCOME10", "SAVE20", "FREESHIP"])
        tracking_number = f"TRK{''.join(random.choices('0123456789', k=9))}" if status != "cancelled" else None

        orders[order_id] = {
            "order_date": order_date,
            "total_amount": total_amount,
            "products": products_in_order,
            "delivery_address_id": delivery_address_id,
            "payment_card_id": payment_card_id,
            "status": status,
            "promo_code_applied": promo_code_applied,
            "tracking_number": tracking_number,
        }
        existing_uuids["orders"].add(order_id)

    prime_subscriptions = {}
    if random.random() < 0.3: # 30% chance of prime subscription
        sub_id = str(uuid.uuid4())
        start_date = generate_random_date(2022, 2024)
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=365 * random.randint(1, 3))).strftime("%Y-%m-%d")
        prime_subscriptions[sub_id] = {
            "start_date": start_date,
            "end_date": end_date,
            "plan_type": random.choice(["yearly", "monthly"]),
            "status": random.choice(["active", "expired"]),
        }

    returns = {}
    num_returns = random.randint(0, min(num_orders, 1)) # Max 1 return per user for simplicity
    if num_returns > 0 and orders:
        order_to_return_id = random.choice(list(orders.keys()))
        order_products = list(orders[order_to_return_id]["products"].keys())
        if order_products:
            product_to_return = random.choice(order_products)
            return_id = str(uuid.uuid4())
            returns[return_id] = {
                "order_id": order_to_return_id,
                "product_id": product_to_return,
                "return_date": generate_random_date(2023, 2025),
                "reason": random.choice(["item damaged", "wrong size", "not as described", "changed mind"]),
                "status": random.choice(["pending", "processed", "rejected"]),
            }
            existing_uuids["returns"].add(return_id)


    return {
        user_id: {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "balance": balance,
            "friends": friends,
            "payment_cards": payment_cards,
            "addresses": addresses,
            "cart": cart,
            "wish_list": wish_list,
            "orders": orders,
            "prime_subscriptions": prime_subscriptions,
            "returns": returns,
        }
    }, user_id

def generate_product(product_id, existing_seller_ids):
    product_names = [
        "Smartwatch", "Wireless Earbuds", "Portable Speaker", "E-Reader", "Fitness Tracker",
        "Coffee Maker", "Air Fryer", "Blender", "Robot Vacuum", "Electric Kettle",
        "Graphic Novel", "Sci-Fi Novel", "Cookbook", "History Book", "Children's Book",
        "Gaming Headset", "VR Headset", "Drone", "Action Camera", "Projector",
        "Backpack", "Travel Mug", "Water Bottle", "Yoga Mat", "Dumbbell Set",
        "Scented Candle", "Hand Cream", "Face Mask", "Essential Oil Diffuser", "Bath Bomb"
    ]
    product_descriptions = [
        "Advanced features and sleek design.", "Crystal clear audio and comfortable fit.",
        "Powerful sound in a compact design.", "Read thousands of books on the go.",
        "Track your health and fitness goals.", "Brew the perfect cup every time.",
        "Healthy frying with less oil.", "Smoothies and more with ease.",
        "Effortless cleaning for your home.", "Boil water quickly and safely.",
        "Stunning visuals and engaging story.", "Epic adventure awaits.",
        "Delicious recipes for every occasion.", "Dive into the past.",
        "Fun and educational stories.", "Immersive sound for gaming.",
        "Experience virtual worlds.", "Capture breathtaking aerial views.",
        "Record your adventures in 4K.", "Big screen entertainment anywhere.",
        "Durable and spacious for daily use.", "Keep your drinks hot or cold.",
        "Stay hydrated in style.", "Comfortable and non-slip.",
        "Build strength and tone muscles.", "Relaxing aroma for your home.",
        "Nourish and moisturize your hands.", "Revitalize your skin.",
        "Create a calming atmosphere.", "Fizz and relax."
    ]
    product_categories = [
        "Electronics", "Home Appliances", "Books", "Gaming & Hobbies",
        "Fitness & Outdoors", "Health & Beauty", "Home Decor"
    ]

    seller_id = random.choice(list(existing_seller_ids)) if existing_seller_ids else 1 # Fallback if no sellers

    return {
        "name": random.choice(product_names),
        "description": random.choice(product_descriptions),
        "price": round(random.uniform(5.00, 1500.00), 2),
        "category": random.choice(product_categories),
        "stock": random.randint(0, 100),
        "seller_id": seller_id,
    }

def generate_seller(seller_id):
    seller_names = [
        "Global Gadgets", "Home & Hearth Emporium", "Bookworm Haven",
        "Active Life Gear", "Beauty Oasis", "The Tech Zone", "Gourmet Kitchenware",
        "Paperback Paradise", "Outdoor Adventures Inc.", "Wellness Wonders"
    ]
    return {
        "name": random.choice(seller_names),
        "rating": round(random.uniform(3.0, 5.0), 1),
    }

def generate_review(product_id, existing_user_ids):
    review_id = str(uuid.uuid4())
    user_id = random.choice(list(existing_user_ids)) if existing_user_ids else str(uuid.uuid4())
    return {
        "review_id": review_id,
        "user_id": user_id,
        "rating": random.randint(1, 5),
        "comment": random.choice([
            "Absolutely fantastic!", "Works great, highly recommend.",
            "Good value for money.", "Decent product, met expectations.",
            "It's okay, but could be better.", "Not impressed, had issues.",
            "Loved it!", "Could be improved.", "Very satisfied."
        ]),
        "date": generate_random_date(2023, 2025),
    }

def generate_question(product_id, existing_user_ids):
    question_id = str(uuid.uuid4())
    user_id = random.choice(list(existing_user_ids)) if existing_user_ids else str(uuid.uuid4())
    question_texts = [
        "Is this compatible with X device?", "What's the battery life like?",
        "Does it come with a warranty?", "Is assembly required?",
        "What materials is this made from?", "Can it be used outdoors?",
        "Is it waterproof?", "How long does shipping usually take?"
    ]
    answer_texts = [
        "Yes, it is.", "About 8 hours.", "Yes, a 1-year warranty.",
        "Minimal assembly.", "High-quality plastic and metal.",
        "It's designed for indoor use.", "No, it is not.",
        "Typically 3-5 business days."
    ]
    answers = []
    if random.random() < 0.7: # 70% chance of an answer
        answer_id = str(uuid.uuid4())
        answer_user_id = random.choice(list(existing_user_ids)) if existing_user_ids else str(uuid.uuid4())
        answers.append({
            "answer_id": answer_id,
            "user_id": answer_user_id,
            "answer": random.choice(answer_texts),
            "date": generate_random_date(2023, 2025),
        })

    return {
        "question_id": question_id,
        "user_id": user_id,
        "question": random.choice(question_texts),
        "date": generate_random_date(2023, 2025),
        "answers": answers,
    }

# Initialize the DEFAULT_STATE structure
DEFAULT_STATE = {
    "users": {},
    "current_user": None,
    "products": {},
    "sellers": {},
    "product_reviews": {},
    "product_questions": {},
    "promotions": { # Adding a new section for promotions
        str(uuid.uuid4()): {
            "code": "SUMMERFUN",
            "discount_percentage": 15,
            "min_purchase_amount": 50.00,
            "expiry_date": "2025-08-31",
            "description": "15% off orders over $50 for summer!",
            "is_active": True
        },
        str(uuid.uuid4()): {
            "code": "NEWCUSTOMER20",
            "discount_percentage": 20,
            "min_purchase_amount": 0.00,
            "expiry_date": "2025-12-31",
            "description": "20% off your first order!",
            "is_active": True
        }
    },
    "customer_service_tickets": { # Adding a new section for customer service tickets
        str(uuid.uuid4()): {
            "user_id": "", # Will be linked to a generated user
            "subject": "Missing Item in Order",
            "description": "Order TRK123456789 arrived, but Product 5 was missing.",
            "status": "open",
            "created_date": "2025-07-20",
            "last_updated_date": "2025-07-25",
            "agent_notes": "Checked inventory, sending replacement for Product 5."
        },
        str(uuid.uuid4()): {
            "user_id": "", # Will be linked to a generated user
            "subject": "Issue with Payment",
            "description": "My card was declined for order TRK987654321.",
            "status": "closed",
            "created_date": "2025-06-01",
            "last_updated_date": "2025-06-05",
            "agent_notes": "User updated card details, payment successful now."
        }
    }
}

# Keep track of generated UUIDs for linking friends, orders, etc.
existing_uuids = {
    "users": set(),
    "payment_cards": set(),
    "addresses": set(),
    "orders": set(),
    "returns": set()
}

# --- Add initial users (Alice and Bob) and ensure their IDs are tracked ---
alice_info, alice_id = generate_user(existing_uuids, "Alice", "Smith", "alice.smith@gmail.com", 125.75)
bob_info, bob_id = generate_user(existing_uuids, "Bob", "Johnson", "bob.johnson@gmail.com", 50.25)
DEFAULT_STATE["users"].update(alice_info)
DEFAULT_STATE["users"].update(bob_info)

# Manually ensure Alice and Bob can be friends
if bob_id not in DEFAULT_STATE["users"][alice_id]["friends"]:
    DEFAULT_STATE["users"][alice_id]["friends"].append(bob_id)
if alice_id not in DEFAULT_STATE["users"][bob_id]["friends"]:
    DEFAULT_STATE["users"][bob_id]["friends"].append(alice_id)

# --- Generate 48 more diverse users ---
for _ in range(48):
    new_user_info, new_user_id = generate_user(existing_uuids)
    DEFAULT_STATE["users"].update(new_user_info)

# --- Add more products (totaling around 15-20) ---
num_initial_products = len(DEFAULT_STATE["products"])
# Add a few more sellers first
for i in range(3, 6): # Add sellers 3, 4, 5
    DEFAULT_STATE["sellers"][i] = generate_seller(i)

existing_seller_ids = list(DEFAULT_STATE["sellers"].keys())

for i in range(num_initial_products + 1, num_initial_products + 16): # Add 15 more products
    DEFAULT_STATE["products"][i] = generate_product(i, existing_seller_ids)

# --- Generate more product reviews and questions ---
all_product_ids = list(DEFAULT_STATE["products"].keys())
all_user_ids = list(DEFAULT_STATE["users"].keys())

for product_id in all_product_ids:
    if product_id not in DEFAULT_STATE["product_reviews"]:
        DEFAULT_STATE["product_reviews"][product_id] = []
    if product_id not in DEFAULT_STATE["product_questions"]:
        DEFAULT_STATE["product_questions"][product_id] = []

    num_reviews = random.randint(0, 5)
    for _ in range(num_reviews):
        DEFAULT_STATE["product_reviews"][product_id].append(generate_review(product_id, all_user_ids))

    num_questions = random.randint(0, 3)
    for _ in range(num_questions):
        DEFAULT_STATE["product_questions"][product_id].append(generate_question(product_id, all_user_ids))

# --- Link customer service tickets to actual user IDs ---
if all_user_ids:
    for ticket_id in DEFAULT_STATE["customer_service_tickets"]:
        DEFAULT_STATE["customer_service_tickets"][ticket_id]["user_id"] = random.choice(all_user_ids)

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")
print(f"Total number of products generated: {len(DEFAULT_STATE['products'])}")
print(f"Total number of sellers generated: {len(DEFAULT_STATE['sellers'])}")

# You would save DEFAULT_STATE to a JSON file or similar for your application
# with open('diverse_amazon_state.json', 'w') as f:
#     json.dump(DEFAULT_STATE, f, indent=2)
