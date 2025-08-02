import uuid
from datetime import datetime, timedelta
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
            "street_address": f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Elm', 'Maple', 'Pine'])} {random.choice(['Street', 'Avenue', 'Road', 'Lane'])}",
            "city": random.choice(["Springfield", "Fairview", "Riverside", "Lakewood", "Centerville"]),
            "state": random.choice(["CA", "NY", "TX", "FL", "IL", "GA", "WA"]),
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

def generate_product(product_id, existing_seller_ids):
    products_structured = []

    product_names = [
        "Smartwatch", "Wireless Earbuds", "Portable Speaker", "E-Reader", "Fitness Tracker",
        "Coffee Maker", "Air Fryer", "Blender", "Robot Vacuum", "Electric Kettle",
        "Graphic Novel", "Sci-Fi Novel", "Cookbook", "History Book", "Children's Book",
        "Gaming Headset", "VR Headset", "Drone", "Action Camera", "Projector",
        "Backpack", "Travel Mug", "Water Bottle", "Yoga Mat", "Dumbbell Set",
        "Scented Candle", "Hand Cream", "Face Mask", "Essential Oil Diffuser", "Bath Bomb",
        "Laptop", "Desktop Computer", "Tablet", "Smartphone", "Monitor",
        "Keyboard", "Mouse", "Printer", "Scanner", "Webcam",
        "Desk Lamp", "Office Chair", "Standing Desk", "Bookshelf", "File Cabinet",
        "Running Shoes", "Hiking Boots", "Sandals", "Sneakers", "Dress Shoes",
        "Winter Coat", "Rain Jacket", "Sweater", "T-Shirt", "Jeans",
        "Dress", "Skirt", "Shorts", "Socks", "Hat",
        "Umbrella", "Sunglasses", "Watch", "Necklace", "Bracelet",
        "Earrings", "Ring", "Wallet", "Handbag", "Backpack",
        "Suitcase", "Duffel Bag", "Messenger Bag", "Camera Bag", "Laptop Bag",
        "Tent", "Sleeping Bag", "Camping Stove", "Flashlight", "Lantern",
        "Fishing Rod", "Tackle Box", "Bicycle", "Helmet", "Water Bottle",
        "Tennis Racket", "Soccer Ball", "Basketball", "Football", "Baseball Glove",
        "Golf Clubs", "Golf Balls", "Yoga Block", "Resistance Bands", "Jump Rope",
        "Foam Roller", "Massage Gun", "Protein Powder", "Energy Bar", "Sports Drink",
        "Hair Dryer", "Curling Iron", "Straightener", "Shampoo", "Conditioner",
        "Body Wash", "Lotion", "Deodorant", "Toothbrush", "Toothpaste",
        "Mouthwash", "Floss", "Razor", "Shaving Cream", "Aftershave",
        "Perfume", "Cologne", "Lipstick", "Mascara", "Eyeliner",
        "Eyeshadow", "Blush", "Foundation", "Concealer", "Makeup Remover",
        "Nail Polish", "Nail File", "Cuticle Oil", "Face Serum", "Face Scrub",
        "Moisturizer", "Sunscreen", "Face Mask", "Sheet Mask", "Eye Cream",
        "Night Cream", "Day Cream", "Spot Treatment", "Acne Patch", "Pimple Cream",
        "Dog Food", "Cat Food", "Bird Seed", "Fish Food", "Pet Shampoo",
        "Pet Collar", "Pet Leash", "Pet Bed", "Pet Toy", "Pet Carrier",
        "Vacuum Cleaner", "Steam Mop", "Broom", "Dustpan", "Trash Can",
        "Recycling Bin", "Laundry Basket", "Iron", "Ironing Board", "Drying Rack",
        "Dish Soap", "Sponges", "Scrub Brush", "Paper Towels", "Cleaning Spray",
        "Air Purifier", "Humidifier", "Dehumidifier", "Space Heater", "Fan",
        "Window AC", "Portable AC", "Ceiling Fan", "Light Bulb", "Smart Plug",
        "Smart Thermostat", "Security Camera", "Doorbell Camera", "Smoke Detector", "Carbon Monoxide Detector"
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
    "Create a calming atmosphere.", "Fizz and relax.",
    "High performance for work and play.", "Powerful desktop for productivity.",
    "Portable and versatile tablet.", "Latest smartphone technology.",
    "Vivid display for gaming and movies.", "Responsive keys for fast typing.",
    "Precision mouse for smooth navigation.", "Print documents and photos easily.",
    "Scan important papers quickly.", "HD webcam for video calls.",
    "Brighten your workspace.", "Ergonomic chair for comfort.",
    "Adjustable desk for standing or sitting.", "Organize your books and files.",
    "Secure storage for documents.", "Run faster and longer.",
    "Tough boots for outdoor adventures.", "Comfortable sandals for summer.",
    "Stylish sneakers for everyday wear.", "Elegant shoes for formal occasions.",
    "Warm coat for winter weather.", "Waterproof jacket for rainy days.",
    "Soft sweater for chilly nights.", "Casual t-shirt for daily use.",
    "Classic jeans for any outfit.", "Beautiful dress for special events.",
    "Trendy skirt for summer.", "Cool shorts for hot days.",
    "Cozy socks for comfort.", "Fashionable hat for sun protection.",
    "Stay dry with a sturdy umbrella.", "Protect your eyes with sunglasses.",
    "Keep time with a stylish watch.", "Elegant necklace for any occasion.",
    "Chic bracelet for your wrist.", "Sparkling earrings for parties.",
    "Shiny ring for celebrations.", "Organize your cash and cards.",
    "Carry your essentials in style.", "Spacious backpack for travel.",
    "Pack for trips with a durable suitcase.", "Roomy duffel bag for gym.",
    "Messenger bag for work.", "Protect your camera on the go.",
    "Laptop bag for professionals.", "Camp comfortably outdoors.",
    "Stay warm with a sleeping bag.", "Cook meals at the campsite.",
    "Light up the night with a flashlight.", "Lantern for camping.",
    "Catch fish with a reliable rod.", "Store tackle for fishing.",
    "Ride with a sturdy bicycle.", "Protect your head with a helmet.",
    "Hydrate during rides.", "Play tennis with a quality racket.",
    "Kick goals with a soccer ball.", "Shoot hoops with a basketball.",
    "Throw passes with a football.", "Catch with a baseball glove.",
    "Improve your golf game.", "Practice with golf balls.",
    "Support your yoga practice.", "Increase resistance for workouts.",
    "Jump rope for cardio.", "Relieve muscle tension.",
    "Massage gun for recovery.", "Boost energy with protein powder.",
    "Snack on energy bars.", "Stay hydrated with sports drinks.",
    "Dry your hair quickly.", "Style with a curling iron.",
    "Straighten hair easily.", "Cleanse with shampoo.",
    "Condition for smooth hair.", "Wash your body gently.",
    "Moisturize skin daily.", "Stay fresh with deodorant.",
    "Brush teeth thoroughly.", "Whiten with toothpaste.",
    "Freshen breath with mouthwash.", "Clean between teeth with floss.",
    "Shave smoothly with a razor.", "Protect skin with shaving cream.",
    "Soothe with aftershave.", "Smell great with perfume.",
    "Cologne for men.", "Color lips with lipstick.",
    "Define lashes with mascara.", "Shape eyes with eyeliner.",
    "Blend eyeshadow for looks.", "Add color with blush.",
    "Even skin tone with foundation.", "Cover blemishes with concealer.",
    "Remove makeup easily.", "Polish nails for shine.",
    "Shape nails with a file.", "Nourish cuticles.",
    "Hydrate with face serum.", "Exfoliate with face scrub.",
    "Moisturize for softness.", "Protect with sunscreen.",
    "Detox with a face mask.", "Relax with a sheet mask.",
    "Brighten eyes with cream.", "Repair skin overnight.",
    "Hydrate during the day.", "Treat spots quickly.",
    "Cover pimples with patches.", "Reduce acne with cream.",
    "Nutritious food for dogs.", "Healthy food for cats.",
    "Feed birds with seeds.", "Fish food for aquariums.",
    "Clean pets with shampoo.", "Secure pets with a collar.",
    "Walk pets with a leash.", "Comfortable bed for pets.",
    "Fun toys for pets.", "Carry pets safely.",
    "Clean floors with a vacuum.", "Sanitize with a steam mop.",
    "Sweep with a broom.", "Collect dirt with a dustpan.",
    "Dispose waste in a trash can.", "Recycle with a bin.",
    "Carry laundry in a basket.", "Remove wrinkles with an iron.",
    "Iron clothes on a board.", "Dry clothes on a rack.",
    "Wash dishes with soap.", "Scrub with sponges.",
    "Clean with a brush.", "Wipe with paper towels.",
    "Spray for cleaning.", "Purify air at home.",
    "Add moisture with a humidifier.", "Remove moisture with a dehumidifier.",
    "Warm up with a space heater.", "Cool down with a fan.",
    "Window AC for summer.", "Portable AC for any room.",
    "Ceiling fan for airflow.", "Light up with bulbs.",
    "Control devices with a smart plug.", "Regulate temperature with a smart thermostat.",
    "Monitor home with a security camera.", "See visitors with a doorbell camera.",
    "Detect smoke for safety.", "Detect carbon monoxide for safety."
    ]

    category_map = {
        "Smartwatch": "Electronics", "Wireless Earbuds": "Electronics", "Portable Speaker": "Electronics", "E-Reader": "Electronics",
        "Fitness Tracker": "Electronics", "Coffee Maker": "Home Appliances", "Air Fryer": "Home Appliances", "Blender": "Home Appliances",
        "Robot Vacuum": "Home Appliances", "Electric Kettle": "Home Appliances", "Graphic Novel": "Books", "Sci-Fi Novel": "Books",
        "Cookbook": "Books", "History Book": "Books", "Children's Book": "Books", "Gaming Headset": "Gaming & Hobbies",
        "VR Headset": "Gaming & Hobbies", "Drone": "Electronics", "Action Camera": "Electronics", "Projector": "Electronics",
        "Backpack": "Travel & Luggage", "Travel Mug": "Home Decor", "Water Bottle": "Fitness & Outdoors", "Yoga Mat": "Fitness & Outdoors",
        "Dumbbell Set": "Fitness & Outdoors", "Scented Candle": "Home Decor", "Hand Cream": "Health & Beauty", "Face Mask": "Health & Beauty",
        "Essential Oil Diffuser": "Home Decor", "Bath Bomb": "Health & Beauty", "Laptop": "Electronics", "Desktop Computer": "Electronics",
        "Tablet": "Electronics", "Smartphone": "Electronics", "Monitor": "Electronics", "Keyboard": "Electronics", "Mouse": "Electronics",
        "Printer": "Electronics", "Scanner": "Electronics", "Webcam": "Electronics", "Desk Lamp": "Home Decor", "Office Chair": "Office Supplies",
        "Standing Desk": "Office Supplies", "Bookshelf": "Home Decor", "File Cabinet": "Office Supplies", "Running Shoes": "Fitness & Outdoors",
        "Hiking Boots": "Fitness & Outdoors", "Sandals": "Clothing & Accessories", "Sneakers": "Clothing & Accessories", "Dress Shoes": "Clothing & Accessories",
        "Winter Coat": "Clothing & Accessories", "Rain Jacket": "Clothing & Accessories", "Sweater": "Clothing & Accessories", "T-Shirt": "Clothing & Accessories",
        "Jeans": "Clothing & Accessories", "Dress": "Clothing & Accessories", "Skirt": "Clothing & Accessories", "Shorts": "Clothing & Accessories",
        "Socks": "Clothing & Accessories", "Hat": "Clothing & Accessories", "Umbrella": "Travel & Luggage", "Sunglasses": "Clothing & Accessories",
        "Watch": "Clothing & Accessories", "Necklace": "Clothing & Accessories", "Bracelet": "Clothing & Accessories", "Earrings": "Clothing & Accessories",
        "Ring": "Clothing & Accessories", "Wallet": "Clothing & Accessories", "Handbag": "Clothing & Accessories", "Suitcase": "Travel & Luggage",
        "Duffel Bag": "Travel & Luggage", "Messenger Bag": "Travel & Luggage", "Camera Bag": "Travel & Luggage", "Laptop Bag": "Travel & Luggage",
        "Tent": "Camping & Outdoors", "Sleeping Bag": "Camping & Outdoors", "Camping Stove": "Camping & Outdoors", "Flashlight": "Camping & Outdoors",
        "Lantern": "Camping & Outdoors", "Fishing Rod": "Sports Equipment", "Tackle Box": "Sports Equipment", "Bicycle": "Sports Equipment",
        "Helmet": "Sports Equipment", "Tennis Racket": "Sports Equipment", "Soccer Ball": "Sports Equipment", "Basketball": "Sports Equipment",
        "Football": "Sports Equipment", "Baseball Glove": "Sports Equipment", "Golf Clubs": "Sports Equipment", "Golf Balls": "Sports Equipment",
        "Yoga Block": "Fitness & Outdoors", "Resistance Bands": "Fitness & Outdoors", "Jump Rope": "Fitness & Outdoors", "Foam Roller": "Fitness & Outdoors",
        "Massage Gun": "Health & Beauty", "Protein Powder": "Health & Beauty", "Energy Bar": "Health & Beauty", "Sports Drink": "Health & Beauty",
        "Hair Dryer": "Personal Care", "Curling Iron": "Personal Care", "Straightener": "Personal Care", "Shampoo": "Personal Care",
        "Conditioner": "Personal Care", "Body Wash": "Personal Care", "Lotion": "Personal Care", "Deodorant": "Personal Care",
        "Toothbrush": "Personal Care", "Toothpaste": "Personal Care", "Mouthwash": "Personal Care", "Floss": "Personal Care",
        "Razor": "Personal Care", "Shaving Cream": "Personal Care", "Aftershave": "Personal Care", "Perfume": "Personal Care",
        "Cologne": "Personal Care", "Lipstick": "Personal Care", "Mascara": "Personal Care", "Eyeliner": "Personal Care",
        "Eyeshadow": "Personal Care", "Blush": "Personal Care", "Foundation": "Personal Care", "Concealer": "Personal Care",
        "Makeup Remover": "Personal Care", "Nail Polish": "Personal Care", "Nail File": "Personal Care", "Cuticle Oil": "Personal Care",
        "Face Serum": "Personal Care", "Face Scrub": "Personal Care", "Moisturizer": "Personal Care", "Sunscreen": "Personal Care",
        "Face Mask": "Personal Care", "Sheet Mask": "Personal Care", "Eye Cream": "Personal Care", "Night Cream": "Personal Care",
        "Day Cream": "Personal Care", "Spot Treatment": "Personal Care", "Acne Patch": "Personal Care", "Pimple Cream": "Personal Care",
        "Dog Food": "Pet Supplies", "Cat Food": "Pet Supplies", "Bird Seed": "Pet Supplies", "Fish Food": "Pet Supplies",
        "Pet Shampoo": "Pet Supplies", "Pet Collar": "Pet Supplies", "Pet Leash": "Pet Supplies", "Pet Bed": "Pet Supplies",
        "Pet Toy": "Pet Supplies", "Pet Carrier": "Pet Supplies", "Vacuum Cleaner": "Home Appliances", "Steam Mop": "Home Appliances",
        "Broom": "Cleaning Supplies", "Dustpan": "Cleaning Supplies", "Trash Can": "Cleaning Supplies", "Recycling Bin": "Cleaning Supplies",
        "Laundry Basket": "Cleaning Supplies", "Iron": "Home Appliances", "Ironing Board": "Home Appliances", "Drying Rack": "Home Appliances",
        "Dish Soap": "Cleaning Supplies", "Sponges": "Cleaning Supplies", "Scrub Brush": "Cleaning Supplies", "Paper Towels": "Cleaning Supplies",
        "Cleaning Spray": "Cleaning Supplies", "Air Purifier": "Home Appliances", "Humidifier": "Home Appliances", "Dehumidifier": "Home Appliances",
        "Space Heater": "Home Appliances", "Fan": "Home Appliances", "Window AC": "Home Appliances", "Portable AC": "Home Appliances",
        "Ceiling Fan": "Home Appliances", "Light Bulb": "Home Appliances", "Smart Plug": "Smart Home", "Smart Thermostat": "Smart Home",
        "Security Camera": "Safety & Security", "Doorbell Camera": "Safety & Security", "Smoke Detector": "Safety & Security", "Carbon Monoxide Detector": "Safety & Security"
    }

    name = product_names[i]
    description = product_descriptions[i]
    category_name = category_map.get(name, "Miscellaneous")

    return {
        "name": name,
        "description": description,
        "price": round(random.uniform(5.00, 1500.00), 2),
        "stock": random.randint(0, 100),
        "category": category_name
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
    if random.random() < 0.7:
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

alice_info, alice_id = generate_user(existing_uuids, "Alice", "Smith", "alice.smith@gmail.com", 125.75)
bob_info, bob_id = generate_user(existing_uuids, "Bob", "Johnson", "bob.johnson@gmail.com", 50.25)
DEFAULT_STATE["users"].update(alice_info)
DEFAULT_STATE["users"].update(bob_info)

for _ in range(48):
    new_user_info, new_user_id = generate_user(existing_uuids)
    DEFAULT_STATE["users"].update(new_user_info)

num_initial_products = len(DEFAULT_STATE["products"])
for i in range(3, 6):
    DEFAULT_STATE["sellers"][i] = generate_seller(i)

existing_seller_ids = list(DEFAULT_STATE["sellers"].keys())

for i in range(num_initial_products + 1, num_initial_products + 101):
    DEFAULT_STATE["products"][str(uuid.uuid4())] = generate_product(i, existing_seller_ids)

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

if all_user_ids:
    for ticket_id in DEFAULT_STATE["customer_service_tickets"]:
        DEFAULT_STATE["customer_service_tickets"][ticket_id]["user_id"] = random.choice(all_user_ids)

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")
print(f"Total number of products generated: {len(DEFAULT_STATE['products'])}")
print(f"Total number of sellers generated: {len(DEFAULT_STATE['sellers'])}")

with open('diverse_amazon_state.json', 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)