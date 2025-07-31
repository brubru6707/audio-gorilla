import uuid
import random
from datetime import datetime, timedelta
import json

"""Walmart Marketplace Backend Generator

Creates DEFAULT_STATE that roughly aligns with WalmartMarketplaceApis.py.  This
keeps the API class free of file-loading logic while giving demos and tests a
rich data set to work with.
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rand_date_iso(days_back: int = 90) -> str:
    delta = timedelta(days=random.randint(0, days_back), hours=random.randint(0, 23))
    return (datetime.utcnow() - delta).isoformat(timespec="seconds") + "Z"


_categories = ["Electronics", "Home & Garden", "Toys", "Health", "Clothing", "Automotive"]

# ---------------------------------------------------------------------------
# Items, inventory & price
# ---------------------------------------------------------------------------

items: dict[str, dict] = {}
inventory: dict[str, dict] = {}
prices: dict[str, dict] = {}

for idx in range(1, 11):  # 10 SKUs
    sku = f"SKU{idx:03d}"
    price_val = round(random.uniform(5.0, 150.0), 2)
    adjectives = ["Wireless", "Portable", "Eco-Friendly", "Smart", "Deluxe", "Compact", "Ultra", "Premium"]
    nouns = ["Speaker", "Vacuum", "Headphones", "Air Fryer", "Backpack", "Yoga Mat", "Coffee Maker", "Lamp"]
    product_name = f"{random.choice(adjectives)} {random.choice(nouns)}"
    description_templates = [
        "Experience unmatched quality with our {name} – built for everyday use.",
        "Upgrade your lifestyle with the new {name}.",
        "The {name} combines style and performance for modern households.",
        "Get ready for convenience on the go with this {name}."
    ]
    description = random.choice(description_templates).format(name=product_name)
    items[sku] = {
        "sku": sku,
        "product_name": product_name,
        "price": price_val,
        "description": description,
        "category": random.choice(_categories),
        "status": random.choice(["Active", "Inactive"]),
    }
    inventory[sku] = {
        "quantity": random.randint(0, 250),
        "fulfillment_center_id": f"FC{random.randint(1,3):03d}",
    }
    prices[sku] = {"price": price_val}

# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

orders: dict[str, dict] = {}
for idx in range(1, 6):
    po = f"PO{idx:03d}"
    sku_choice = random.choice(list(items.keys()))
    qty = random.randint(1, 4)
    total = round(items[sku_choice]["price"] * qty, 2)
    orders[po] = {
        "purchase_order_id": po,
        "order_date": _rand_date_iso(30),
        "status": random.choice(["Created", "Acknowledged", "Shipped", "Cancelled"]),
        "items": [{"sku": sku_choice, "quantity": qty, "price": items[sku_choice]["price"]}],
        "total_amount": total,
    }

# ---------------------------------------------------------------------------
# Promotions & Returns
# ---------------------------------------------------------------------------

promotions = {}
for idx in range(1, 3):
    pid = f"PROMO{idx:03d}"
    promotions[pid] = {
        "promo_id": pid,
        "name": f"Promo {idx}",
        "discount_percent": random.choice([5, 10, 15, 20]),
        "start_date": (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "end_date": (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "status": "Active",
    }

returns = {}
for idx in range(1, 3):
    rid = f"RET{idx:03d}"
    order_id = random.choice(list(orders.keys()))
    returns[rid] = {
        "return_id": rid,
        "order_id": order_id,
        "items": [{"sku": orders[order_id]["items"][0]["sku"], "quantity": 1}],
        "status": random.choice(["Pending", "Completed"]),
        "created_date": _rand_date_iso(7),
    }

DEFAULT_STATE = {
    "items": items,
    "inventory": inventory,
    "prices": prices,
    "orders": orders,
    "promotions": promotions,
    "returns": returns,
    "generated_at": datetime.utcnow().isoformat() + "Z",
}

if __name__ == "__main__":
    print("Walmart backend generated 🛒")
    print(f"Items   : {len(items)}")
    print(f"Orders  : {len(orders)}")
    print(f"Returns : {len(returns)}")

    # with open('diverse_walmart_state.json', 'w') as f:
    #     json.dump(DEFAULT_STATE, f, indent=2) 