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
        "Apple Watch Series 9 GPS 45mm Midnight Aluminum Case with Midnight Sport Band", 
        "Sony WF-1000XM4 Industry Leading Noise Canceling Truly Wireless Earbud Headphones", 
        "JBL Charge 5 Portable Bluetooth Speaker with IP67 Waterproof and USB Charge Out", 
        "Amazon Kindle Paperwhite (11th Generation) 6.8 inch Display with Adjustable Warm Light", 
        "Fitbit Charge 5 Advanced Fitness and Health Tracker with Built-in GPS",
        "Ninja CP307 Hot and Cold Brewed System Auto-iQ Tea and Coffee Maker", 
        "COSORI Pro LE 5-Qt Air Fryer with Rapid Air Circulation Technology", 
        "Vitamix A3500 Ascent Series Smart Blender with Touch Screen Controls", 
        "iRobot Roomba j7+ Self-Emptying Robot Vacuum with Smart Mapping", 
        "Breville BKE820XL Variable-Temperature 1.8L Electric Kettle with LCD Display",
        "Watchmen: The Complete Collection by Alan Moore Deluxe Hardcover Edition", 
        "Dune by Frank Herbert - 50th Anniversary Deluxe Hardcover with Dust Jacket", 
        "Salt, Fat, Acid, Heat by Samin Nosrat - James Beard Award Winner Cookbook", 
        "Sapiens: A Brief History of Humankind by Yuval Noah Harari Paperback", 
        "Where the Crawdads Sing by Delia Owens #1 New York Times Bestseller",
        "SteelSeries Arctis 7P Wireless Gaming Headset with DTS Headphone:X v2.0", 
        "Meta Quest 2 Advanced All-In-One Virtual Reality Headset 128GB", 
        "DJI Mini 3 Pro Drone with 4K/60fps Video and Intelligent Flight Modes", 
        "GoPro HERO11 Black Waterproof Action Camera with 5.3K60 Ultra HD Video", 
        "WEMAX Dice Mini Projector 1080P HD with Android TV 9.0 Built-in",
        "Patagonia Black Hole Pack 32L Recycled Polyester Daypack with Laptop Sleeve", 
        "YETI Rambler 20oz Travel Mug with Handle and MagSlider Lid Stainless Steel", 
        "Hydro Flask Standard Mouth 21oz Water Bottle with Flex Cap TempShield", 
        "Gaiam Premium 6mm Print Yoga Mat with Carrying Strap Non-Slip", 
        "Bowflex SelectTech 552 Adjustable Dumbbells Set 5-52.5 lbs per Dumbbell",
        "Bath & Body Works 3-Wick Candle Mahogany Teakwood 14.5oz with Essential Oils", 
        "Burt's Bees Hand Salve with Almond & Milk 3oz Deeply Moisturizing", 
        "TONYMOLY I'm Real Sheet Mask Variety Pack 11 Different Types", 
        "URPOWER Essential Oil Diffuser 300ml Ultrasonic Aromatherapy with 7 LED Colors", 
        "Lush Intergalactic Bath Bomb with Peppermint Oil and Popping Candy 6.3oz",
        "Apple MacBook Pro 14-inch M2 Pro Chip 16GB RAM 512GB SSD Space Gray", 
        "Dell OptiPlex 7000 Desktop Computer Intel Core i7 16GB RAM 1TB SSD", 
        "Apple iPad Air 5th Generation 10.9-inch Liquid Retina Display 256GB WiFi", 
        "iPhone 14 Pro Max 128GB Deep Purple Unlocked with A16 Bionic Chip", 
        "Samsung Odyssey G7 32 inch Curved Gaming Monitor 1440p 240Hz G-Sync Compatible",
        "Logitech MX Keys Advanced Wireless Illuminated Keyboard for Mac and PC", 
        "Logitech MX Master 3S Advanced Wireless Mouse with Ultra-Fast Scrolling", 
        "HP OfficeJet Pro 9015e All-in-One Wireless Color Printer with Smart Tasks", 
        "Epson Perfection V39 Color Photo and Document Scanner with 4800 DPI", 
        "Logitech C920x HD Pro Webcam 1080p Video Calling with Dual Stereo Audio",
        "BenQ e-Reading LED Desk Lamp with Auto-Dimming and Halo Technology", 
        "Herman Miller Aeron Ergonomic Office Chair Size B Graphite Carbon", 
        "UPLIFT V2 Standing Desk 48x30 Bamboo Desktop with Advanced Keypad", 
        "IKEA HEMNES Bookcase White Stain 35 3/8x77 1/2 inch with Adjustable Shelves", 
        "Steelcase Universal Mobile File Cabinet with Lock and Full Extension Drawers",
        "Nike Air Zoom Pegasus 39 Men's Road Running Shoes Breathable Mesh Upper", 
        "Merrell Moab 3 Mid Waterproof Hiking Boot Men's with Vibram TC5+ Outsole", 
        "Birkenstock Arizona Essentials EVA Sandals Unisex Waterproof Double Strap", 
        "Adidas Ultraboost 22 Running Shoes Women's with BOOST Midsole Technology", 
        "Cole Haan Grand Crosscourt II Leather Dress Sneaker Men's Handcrafted",
        "Patagonia Better Sweater Fleece Jacket Women's Recycled Polyester Full-Zip", 
        "The North Face Venture 2 Jacket Men's DryVent Waterproof Rain Shell", 
        "Everlane Cashmere Crew Sweater Women's Grade-A Mongolian Cashmere", 
        "Hanes Beefy-T Adult Short-Sleeve T-Shirt 100% Cotton Pre-Shrunk", 
        "Levi's 511 Slim Jeans Men's Advanced Stretch Denim Dark Stonewash",
        "Reformation Petites Juliette Wrap Dress Sustainable Viscose Midi Length", 
        "J.Crew Pleated Mini Skirt in Wool Flannel Women's High-Waisted", 
        "Patagonia Baggies Shorts 5 inch Men's 100% Recycled Nylon with DWR Coating", 
        "Bombas Ankle Socks Men's Merino Wool Blend Cushioned Sole 4-Pack", 
        "Patagonia P-6 Logo Trucker Hat Unisex Organic Cotton with Mesh Back",
        "Repel Windproof Travel Umbrella Compact 42 inch Canopy Teflon Coating", 
        "Ray-Ban Aviator Classic Sunglasses RB3025 Gold Frame Green Lens", 
        "Casio G-Shock Digital Watch Men's Solar Powered 200M Water Resistant", 
        "Pandora Moments Snake Chain Sterling Silver Bracelet with Heart Clasp", 
        "Tiffany & Co. Return to Tiffany Heart Tag Bracelet Sterling Silver", 
        "Apple AirPods Pro 2nd Generation with MagSafe Charging Case Active Noise Cancellation", 
        "Cartier Love Ring 18k White Gold Size 6 Screw Design Luxury", 
        "Ridge Wallet The Original Minimalist Metal Wallet RFID Blocking Carbon Fiber", 
        "Coach Signature City Zip Tote Bag Brown Canvas with Leather Trim", 
        "Osprey Farpoint 40 Travel Backpack Men's Carry-On Sized with Laptop Sleeve",
        "Samsonite Winfield 3 DLX Hardside Expandable Luggage 28 inch Spinner Brushed Anthracite", 
        "Patagonia Black Hole Duffel Bag 60L Recycled Polyester Weather Resistant", 
        "Peak Design Everyday Messenger Bag 15 inch V2 Charcoal Camera Bag", 
        "Thule Accent Laptop Bag 15.6 inch with SafeZone Compartment Black", 
        "Incase ICON Laptop Backpack 15 inch with Woolenex and Flight Nylon",
        "REI Co-op Quarter Dome SL 2 Tent Ultralight Backpacking 3-Season", 
        "Marmot Trestles Elite Eco 20 Sleeping Bag Synthetic Fill 20°F Rating", 
        "Jetboil Flash Camping Stove System 1.0L Fast Boil Cooking System", 
        "Streamlight ProTac 2L-X Tactical Flashlight 500 Lumens CR123A Battery", 
        "Goal Zero Lighthouse 600 Lantern and USB Power Hub 5200mAh Battery",
        "Ugly Stik Elite Spinning Rod 7ft Medium Heavy Action Graphite Composite", 
        "Plano 3700 Tackle Box with Adjustable Dividers Clear Lid Organization", 
        "Trek FX 3 Disc Hybrid Bike 2023 Alpha Gold Aluminum with Disc Brakes", 
        "Giro Register MIPS Adult Recreational Cycling Helmet Universal Adult", 
        "CamelBak Chute Mag Water Bottle 32oz BPA-Free Magnetic Cap",
        "Wilson Pro Staff 97 v13 Tennis Racket 16x19 String Pattern 315g", 
        "Adidas Tango España Soccer Ball Size 5 FIFA Quality Pro Machine Stitched", 
        "Spalding NBA Official Game Basketball Indoor/Outdoor Composite Leather", 
        "Wilson NFL Official Size Football Composite Leather Traditional Shape", 
        "Rawlings Heart of the Hide Baseball Glove 11.75 inch Pro H Web",
        "Callaway Rogue ST Max Driver 10.5° Right Hand Regular Flex Graphite Shaft", 
        "Titleist Pro V1 Golf Balls Dozen White High Performance Urethane Cover", 
        "Manduka PRO Yoga Block 4 inch High Density EVA Foam Studio Quality", 
        "Bodylastics Resistance Bands Set 5 Tubes with Door Anchor and Exercise Guide", 
        "Crossrope Get Lean Weighted Jump Rope Set Fast Clip Connection System",
        "TriggerPoint GRID Foam Roller 13 inch Original Density Multi-Zone Massage", 
        "Theragun PRO Plus Percussive Therapy Device 6 Attachments Professional Grade", 
        "Optimum Nutrition Gold Standard 100% Whey Protein Powder Double Rich Chocolate 5lbs", 
        "CLIF BAR Energy Bars Variety Pack 12 Count Organic Oat Fiber", 
        "Gatorade Thirst Quencher Sports Drink Variety Pack 20oz Bottles 12 Count",
        "Dyson V15 Detect Cordless Vacuum Cleaner with Laser Dust Detection", 
        "Conair 1875 Watt Ionic Ceramic Hair Dryer with Diffuser and Concentrator", 
        "T3 Whirl Trio Interchangeable Styling Wand 1.25-1.75 inch Barrels", 
        "GHD Platinum+ Professional Hair Straightener with Ultra-Zone Technology", 
        "Olaplex No.4 Bond Maintenance Shampoo 8.5oz Sulfate-Free Color Safe",
        "Olaplex No.5 Bond Maintenance Conditioner 8.5oz All Hair Types", 
        "Dove Body Wash Deep Moisture 22oz with NutriumMoisture Technology", 
        "CeraVe Daily Moisturizing Lotion 12oz with Hyaluronic Acid and Ceramides", 
        "Degree Men MotionSense Antiperspirant Deodorant Cool Rush 2.7oz 4-Pack", 
        "Oral-B Pro 1000 Electric Toothbrush with Pressure Sensor CrossAction Head",
        "Crest 3D White Toothpaste Radiant Mint 4.1oz Enamel Safe Teeth Whitening", 
        "TheraBreath Fresh Breath Oral Rinse 16oz Dentist Formulated Alcohol-Free", 
        "Oral-B Glide Pro-Health Dental Floss Comfort Plus 40m Deep Clean", 
        "Gillette Fusion5 Men's Razor with Precision Trimmer 5 Anti-Friction Blades", 
        "Cremo Original Shave Cream 6oz Astonishingly Superior Smooth Shave",
        "Nivea Men Sensitive Post Shave Balm 3.3oz with Chamomile and Vitamin E", 
        "Chanel No. 5 Eau de Parfum Spray 3.4oz Classic French Luxury Fragrance", 
        "Dior Sauvage Eau de Toilette Men's 3.4oz Fresh Spicy Woody Scent", 
        "Charlotte Tilbury Matte Revolution Lipstick Pillow Talk Medium-Full Coverage", 
        "Maybelline Lash Sensational Sky High Mascara Very Black Washable Formula", 
        "Urban Decay 24/7 Glide-On Eye Pencil Zero Black Smudge-Proof Waterproof",
        "Anastasia Beverly Hills Soft Glam Eyeshadow Palette 14 Shades Matte Shimmer", 
        "NARS Blush Orgasm 4.8g Peachy Pink with Golden Undertones Cult Classic", 
        "Fenty Beauty Pro Filt'r Soft Matte Longwear Foundation 32ml Medium Coverage", 
        "NARS Radiant Creamy Concealer 6ml Full Coverage Weightless Formula", 
        "Neutrogena Makeup Remover Cleansing Towelettes 25 Count Ultra-Soft Cloths",
        "Essie Nail Polish Ballet Slippers 0.46oz Sheer Pink Classic Shade", 
        "OPI Nail File 7 inch Professional Salon Quality 180/240 Grit", 
        "Burt's Bees Lemon Butter Cuticle Cream 0.6oz Natural Moisturizing", 
        "The Ordinary Niacinamide 10% + Zinc 1% Serum 30ml Blemish Control", 
        "Paula's Choice SKIN PERFECTING 2% BHA Liquid Exfoliant 4oz Salicylic Acid",
        "CeraVe AM Facial Moisturizing Lotion SPF 30 3oz with Zinc Oxide", 
        "EltaMD UV Clear Broad-Spectrum SPF 46 Sunscreen 1.7oz Zinc Oxide Tinted", 
        "Freeman Charcoal & Black Sugar Polishing Mask 6oz Deep Cleansing", 
        "The Face Shop Real Nature Rice Face Mask Sheet 10 Pack Brightening", 
        "Kiehl's Creamy Eye Treatment with Avocado 0.5oz Rich Under Eye Cream",
        "Olay Regenerist Night Recovery Cream 1.7oz with Niacinamide and Amino-Peptides", 
        "Neutrogena Hydra Boost Water Gel Daily Vitamin C Facial Moisturizer 1.7oz", 
        "La Roche-Posay Effaclar Duo Dual Action Acne Spot Treatment 1.35oz", 
        "COSRX Acne Pimple Master Patch 24 Count Hydrocolloid Healing", 
        "Differin Adapalene Gel 0.1% Acne Treatment 1.6oz Retinoid Prescription Strength",
        "Blue Buffalo Life Protection Formula Adult Chicken & Brown Rice Dry Dog Food 30lbs", 
        "Hill's Science Diet Adult Indoor Cat Food Chicken Recipe 15.5lb Bag", 
        "Kaytee Wild Bird Food Classic Mixed Seed Blend 10lb Bag Sunflower Seeds", 
        "TetraMin Tropical Flakes Fish Food 7.06oz Nutritionally Balanced", 
        "Earthbath All Natural Pet Shampoo Oatmeal & Aloe 16oz Vanilla Almond",
        "Seresto Flea and Tick Collar for Dogs 8-Month Protection Adjustable", 
        "Flexi New Classic Retractable Dog Leash 16ft Cord Medium Dogs up to 44lbs", 
        "FurHaven Pet Bed Orthopedic Sofa Dog Bed Medium Faux Fleece Espresso", 
        "KONG Classic Dog Toy Medium Red Durable Natural Rubber Mental Stimulation", 
        "Sherpa Original Deluxe Pet Carrier Medium Airline Approved Soft-Sided",
        "Shark Navigator Lift-Away Professional Upright Vacuum NV356E Anti-Allergen", 
        "Bissell CrossWave Pet Pro All-in-One Wet Dry Vacuum 1985 Multi-Surface", 
        "O-Cedar EasyWring Microfiber Spin Mop & Bucket Floor Cleaning System", 
        "Libman Large Precision Angle Broom with Dustpan Flagged Bristles", 
        "Rubbermaid Step-On Wastebasket 13 Gallon White Plastic with Tight-Fitting Lid",
        "Simple Houseware 2-Bag Heavy Duty Rolling Laundry Sorter Cart Chrome", 
        "BLACK+DECKER Digital Advantage Professional Steam Iron D3030 Auto-Off", 
        "Honey-Can-Do Tabletop Ironing Board 32 inch Retractable Iron Rest", 
        "SONGMICS Clothes Drying Rack Foldable 3-Tier Laundry Rack Stainless Steel", 
        "Dawn Ultra Dishwashing Liquid Original Scent 75oz Concentrated Formula",
        "Scrub Daddy Texture Changing Sponges 8 Count Firm in Cold Soft in Warm", 
        "OXO Good Grips Dish Brush with Replaceable Head Non-Slip Grip", 
        "Bounty Select-A-Size Paper Towels 8 Double Rolls White 2-Ply", 
        "Method All-Purpose Cleaner Spray French Lavender 28oz Plant-Based",
        "Levoit Core 300 Air Purifier H13 True HEPA Filter Covers 219 sq ft", 
        "Pure Enrichment MistAire Ultrasonic Cool Mist Humidifier 1.5L Tank", 
        "hOmeLabs 4500 Sq Ft Dehumidifier Energy Star 50 Pint Continuous Drain", 
        "Lasko 754200 Ceramic Heater with Adjustable Thermostat Compact Design", 
        "Honeywell QuietSet Whole Room Tower Fan 5-Speed Settings Remote Control",
        "Frigidaire 8000 BTU Window Air Conditioner FFRA0822U1 Electronic Controls", 
        "BLACK+DECKER 8000 BTU Portable Air Conditioner BPACT08WT Remote Control", 
        "Hunter Dempsey 44 inch Ceiling Fan with LED Light Remote Control", 
        "Philips LED A19 Light Bulb 60W Equivalent Daylight 5000K 4-Pack", 
        "TP-Link Kasa Smart Plug Mini WiFi Outlet Works with Alexa 4-Pack",
        "Nest Learning Thermostat 3rd Generation Works with Alexa Stainless Steel", 
        "Ring Indoor Cam 1080p HD Security Camera with Two-Way Talk Works with Alexa", 
        "Ring Video Doorbell Pro 2 1536p HD Head-to-Toe Video Advanced Motion Detection", 
        "First Alert Smoke Detector Alarm 10-Year Battery Photoelectric Sensor", 
        "First Alert Carbon Monoxide Detector Alarm 10-Year Battery Digital Display"
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