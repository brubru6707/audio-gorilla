import uuid
import random
from datetime import datetime, timedelta
import json
from fake_data import first_names, last_names, domains, seller_names_based_on_categories, products_based_on_categories, product_descriptions_based_on_categories, states, street_names, city_names, product_qa_based_on_categories, user_count, first_and_last_names

class User:
    def __init__(self, user_id: str, email: str = None):
        self.user_id = user_id
        self.email = email

flattened_product_titles = []
flattened_product_descriptions = []
flattened_categories = {}
category_index = 0
def flatten_categories(data_dict):
    global category_index
    for key, value in data_dict.items():
        category_index += len(data_dict) + 1
        flattened_categories[key] = category_index
        if isinstance(value, dict):
            flatten_categories(value)
        else:
            flattened_product_titles.extend(value)

def flatten_descriptions(data_dict):
    global category_index
    for key, value in data_dict.items():
        category_index += len(data_dict) + 1
        flattened_categories[key] = category_index
        if isinstance(value, dict):
            flatten_descriptions(value)
        else:
            flattened_product_descriptions.extend(value)

flatten_categories(products_based_on_categories)
flatten_descriptions(product_descriptions_based_on_categories)

def get_all_values(d):
    values = []
    for value in d.values():
        if isinstance(value, dict):
            values.extend(get_all_values(value))
        else:
            values.append(value)
    return values

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
        first_name = random.choice(first_names)
    if not last_name:
        last_name = random.choice(last_names)
    if not email:
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"
    if balance is None:
        balance = round(random.uniform(0.00, 2500.00), 2)
        
    payment_cards = {}
    for _ in range(random.randint(0, 2)):
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
    for _ in range(random.randint(1, 2)):
        address_id = str(uuid.uuid4())
        existing_uuids["addresses"].add(address_id)
        address_type = "Home Address" if random.random() < 0.7 else "Work Address"
        addresses[address_id] = {
            "name": address_type,
            "street_address": f"{random.randint(100, 999)} {random.choice(street_names)} {random.choice(['Street', 'Avenue', 'Road', 'Lane'])}",
            "city": random.choice(city_names),
            "state": random.choice(states),
            "country": "USA",
            "zip_code": random.randint(10000, 99999),
        }

    cart = {}
    for _ in range(random.randint(0, 3)):
        product_id = random.randint(1, 15)
        cart[product_id] = random.randint(1, 3)

    wish_list = {}
    for _ in range(random.randint(0, 2)):
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
    if random.random() < 0.3:
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
    num_returns = random.randint(0, min(num_orders, 1))
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
            "payment_cards": payment_cards,
            "addresses": addresses,
            "cart": cart,
            "wish_list": wish_list,
            "orders": orders,
            "prime_subscriptions": prime_subscriptions,
            "returns": returns,
        }
    }, user_id

def flatten_dict_values(d):
    values_list = []
    for value in d.values():
        if isinstance(value, dict):
            values_list.extend(flatten_dict_values(value))
        else:
            values_list.extend(value)
    return values_list

def generate_product(product_id):
    main_category_name = ""

    for key, value in flattened_categories.items():
        if product_id <= value:
            main_and_sub_category_dictionary = {
                "Wearables & Accessories": "Electronics",
                "Computers & Tablets": "Electronics",
                "Audio & Video": "Electronics",
                "Smart Devices": "Electronics",
                "Peripherals & Components": "Electronics",
                "Gaming": "Electronics",
                "Kitchen Appliances": "Home Appliances",
                "Cleaning Appliances": "Home Appliances",
                "Climate Control": "Home Appliances",
                "Small Appliances": "Home Appliances",
                "Bags & Luggage": "Travel & Luggage",
                "Travel Accessories": "Travel & Luggage",
                "Trip Planning": "Travel & Luggage"
                }
            
            if key in main_and_sub_category_dictionary:
                main_category_name = main_and_sub_category_dictionary[key]
            else: 
                main_category_name = key
            break
    if main_category_name == "":
        seller_name = "Amazon First Time Seller"
    elif type(main_category_name) == str:
        seller_name = seller_names_based_on_categories[main_category_name]
    else: 
        seller_name = random.choice(flatten_dict_values(seller_names_based_on_categories[main_category_name])) 
    product = {
        "name": flattened_product_titles[product_id],
        "description": flattened_product_titles[product_id],
        "seller": seller_name,
        "price": round(random.uniform(5.00, 1500.00), 2),
        "stock": random.randint(0, 100) + 1,
        "category": main_category_name
    }
    

    return product

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

def generate_question(product_id, existing_user_ids, index):
    question_id = str(uuid.uuid4())
    user_id = random.choice(list(existing_user_ids)) if existing_user_ids else str(uuid.uuid4())

    q_and_as = []
    for value in flatten_dict_values(product_qa_based_on_categories)[index]['q_and_a']:
        q_and_as.append({
            "id": str(uuid.uuid4()),
            "question": value["question"],
            "answer": value["answer"],
            "date": generate_random_date(2020, 2025),
        })

    return {
        "product_id": product_id,
        "id": question_id,
        "user_id": user_id,
        "q_and_as": q_and_as,
    }

DEFAULT_STATE = {
    "users": {},
    "products": {},
    "sellers": {},
    "product_reviews": {},
    "product_questions": {},
    "promotions": {
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
    "customer_service_tickets": {
        str(uuid.uuid4()): {
            "user_id": "",
            "subject": "Missing Item in Order",
            "description": "Order TRK123456789 arrived, but Product 5 was missing.",
            "status": "open",
            "created_date": "2025-07-20",
            "last_updated_date": "2025-07-25",
            "agent_notes": "Checked inventory, sending replacement for Product 5."
        },
        str(uuid.uuid4()): {
            "user_id": "",
            "subject": "Issue with Payment",
            "description": "My card was declined for order TRK987654321.",
            "status": "closed",
            "created_date": "2025-06-01",
            "last_updated_date": "2025-06-05",
            "agent_notes": "User updated card details, payment successful now."
        }
    }
}

existing_uuids = {
    "users": set(),
    "payment_cards": set(),
    "addresses": set(),
    "orders": set(),
    "returns": set()
}

for index in range(user_count + len(first_and_last_names)):
    if index > user_count:
        first_name,_, last_name = first_and_last_names[index - user_count].partition(" ")
        new_user_info, new_user_id = generate_user(existing_uuids, first_name=first_name, last_name=last_name)
        DEFAULT_STATE["users"].update(new_user_info)
    else:
        new_user_info, new_user_id = generate_user(existing_uuids)
        DEFAULT_STATE["users"].update(new_user_info)   

num_initial_products = len(DEFAULT_STATE["products"])

existing_seller_ids = list(DEFAULT_STATE["sellers"].keys())

all_product_ids = list(DEFAULT_STATE["products"].keys())
all_user_ids = list(DEFAULT_STATE["users"].keys())

for i in range(num_initial_products + 1, len(flattened_product_titles)):
    product_id = str(uuid.uuid4())
    DEFAULT_STATE["products"][product_id] = generate_product(i)
    DEFAULT_STATE["product_questions"][product_id] = generate_question(product_id, all_user_ids, i)

for product_id in all_product_ids:
    if product_id not in DEFAULT_STATE["product_reviews"]:
        DEFAULT_STATE["product_reviews"][product_id] = []
    if product_id not in DEFAULT_STATE["product_questions"]:
        DEFAULT_STATE["product_questions"][product_id] = []

    num_reviews = random.randint(0, 5)
    for _ in range(num_reviews):
        DEFAULT_STATE["product_reviews"][product_id].append(generate_review(product_id, all_user_ids))

if all_user_ids:
    for ticket_id in DEFAULT_STATE["customer_service_tickets"]:
        DEFAULT_STATE["customer_service_tickets"][ticket_id]["user_id"] = random.choice(all_user_ids)

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")
print(f"Total number of products generated: {len(DEFAULT_STATE['products'])}")
print(f"Total number of sellers generated: {len(DEFAULT_STATE['sellers'])}")

with open('diverse_amazon_state.json', 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)