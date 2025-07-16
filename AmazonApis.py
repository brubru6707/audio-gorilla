from copy import deepcopy
from typing import Dict, Any, Optional, Union, cast

DEFAULT_STATE = {
    "users": {
        "john_doe": {
            "username": "john_doe",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "securepassword123",
            "membership": "prime",
            "join_date": "2022-01-15"
        }
    },
    "current_user": "john_doe",
    "products": {
        "Wireless Bluetooth Earbuds": {
            "id": 1,
            "price": 79.99,
            "category": "Electronics",
            "brand": "SoundMaster",
            "rating": 4.5,
            "stock": 150,
            "description": "High-quality wireless earbuds with 20hr battery life and noise cancellation.",
            "keywords": ["earbuds", "wireless", "bluetooth", "audio"]
        },
        "Stainless Steel Water Bottle": {
            "id": 2,
            "price": 24.99,
            "category": "Home & Kitchen",
            "brand": "HydroFlask",
            "rating": 4.8,
            "stock": 200,
            "description": "Insulated water bottle that keeps drinks cold for 24 hours or hot for 12 hours.",
            "keywords": ["water bottle", "steel", "insulated"]
        },
        "Organic Cotton T-Shirt": {
            "id": 3,
            "price": 29.99,
            "category": "Clothing",
            "brand": "EcoWear",
            "rating": 4.2,
            "stock": 75,
            "description": "Comfortable 100% organic cotton t-shirt, available in multiple colors.",
            "keywords": ["t-shirt", "cotton", "organic", "clothing"]
        },
        "4K Smart TV 55-inch": {
            "id": 4,
            "price": 599.99,
            "category": "Electronics",
            "brand": "Quantum",
            "rating": 4.7,
            "stock": 45,
            "description": "Crystal-clear 4K resolution with built-in streaming apps and voice control.",
            "keywords": ["tv", "smart tv", "4k", "television"]
        },
        "Espresso Machine": {
            "id": 5,
            "price": 129.99,
            "category": "Home & Kitchen",
            "brand": "BrewMaster",
            "rating": 4.4,
            "stock": 60,
            "description": "Professional-grade espresso maker with milk frother for cafe-quality drinks at home.",
            "keywords": ["coffee", "espresso", "machine"]
        },
        "Yoga Mat": {
            "id": 6,
            "price": 34.95,
            "category": "Sports & Fitness",
            "brand": "FlexiFit",
            "rating": 4.6,
            "stock": 120,
            "description": "Eco-friendly, non-slip yoga mat with carrying strap, perfect for all skill levels.",
            "keywords": ["yoga", "mat", "fitness", "exercise"]
        },
        "Wireless Charging Stand": {
            "id": 7,
            "price": 19.99,
            "category": "Electronics",
            "brand": "PowerUp",
            "rating": 4.3,
            "stock": 180,
            "description": "Fast-charging stand compatible with all Qi-enabled devices.",
            "keywords": ["charger", "wireless", "phone accessory"]
        },
        "Hardcover Notebook Set": {
            "id": 8,
            "price": 22.50,
            "category": "Office Supplies",
            "brand": "WriteRight",
            "rating": 4.5,
            "stock": 90,
            "description": "Premium set of 3 hardcover notebooks with dotted, lined, and blank pages.",
            "keywords": ["notebook", "journal", "stationery"]
        },
        "Digital Air Fryer": {
            "id": 9,
            "price": 89.99,
            "category": "Home & Kitchen",
            "brand": "CrispChef",
            "rating": 4.8,
            "stock": 55,
            "description": "Healthier frying with 75% less fat, featuring 7 cooking presets and digital controls.",
            "keywords": ["air fryer", "kitchen appliance", "cooking"]
        },
        "Running Shoes": {
            "id": 10,
            "price": 119.95,
            "category": "Sports & Fitness",
            "brand": "StridePro",
            "rating": 4.7,
            "stock": 85,
            "description": "Lightweight running shoes with responsive cushioning for maximum comfort.",
            "keywords": ["shoes", "running", "sneakers", "athletic"]
        },
        "Bluetooth Speaker": {
            "id": 11,
            "price": 49.99,
            "category": "Electronics",
            "brand": "BoomAudio",
            "rating": 4.4,
            "stock": 110,
            "description": "Portable waterproof speaker with 15-hour playtime and deep bass.",
            "keywords": ["speaker", "bluetooth", "audio", "portable"]
        },
        "Ceramic Cookware Set": {
            "id": 12,
            "price": 149.99,
            "category": "Home & Kitchen",
            "brand": "PureCook",
            "rating": 4.9,
            "stock": 40,
            "description": "10-piece non-toxic ceramic cookware set that's oven and dishwasher safe.",
            "keywords": ["cookware", "pots", "pans", "ceramic"]
        }
    },
    "carts": {
        "john_doe": {
            1: {
                "id": 1,
                "name": "Wireless Bluetooth Earbuds",
                "price": 79.99,
                "quantity": 1
            },
            2: {
                "id": 2,
                "name": "Stainless Steel Water Bottle",
                "price": 24.99,
                "quantity": 2
            }
        }
    },
    "wishlists": {
        "john_doe": { # Wishlists also need to be keyed by user, just like carts
            3: {
                "id": 3,
                "name": "Organic Cotton T-Shirt",
                "price": 29.99,
                "added_date": "2023-05-10"
            }
        }
    },
    "orders": {
        1: {
            "id": 1,
            "user_id": "john_doe",
            "items": [
                {
                    "id": 1,
                    "name": "Wireless Bluetooth Earbuds",
                    "price": 79.99,
                    "quantity": 1
                }
            ],
            "total": 79.99,
            "order_date": "2023-04-15",
            "status": "delivered",
            "shipping_address_id": 1, # Renamed for clarity to match payment_card_id
            "payment_method_id": 1
        }
    },
    "payment_cards": {
        1: {
            "id": 1,
            "user_id": "john_doe",
            "card_type": "Visa",
            "last_four": "4242",
            "exp_date": "12/25",
            "billing_address_id": 1
        }
    },
    "addresses": {
        1: {
            "id": 1,
            "user_id": "john_doe",
            "full_name": "John Doe",
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip_code": "12345",
            "country": "USA",
            "is_primary": True
        },
        2: {
            "id": 2,
            "user_id": "john_doe",
            "full_name": "John Doe",
            "street": "456 Work Ave",
            "city": "Businesstown",
            "state": "CA",
            "zip_code": "67890",
            "country": "USA",
            "is_primary": False
        }
    },
    "next_id_counters": {
        "product": 13, # Updated to reflect current product IDs
        "order": 2,
        "payment_card": 2,
        "address": 3,
        "cart_item": 3, # New counter for cart items if you want unique IDs
        "wishlist_item": 2 # New counter for wishlist items
    },
    "product_names": [
    "Wireless Bluetooth Earbuds",
    "Stainless Steel Water Bottle",
    "Organic Cotton T-Shirt",
    "4K Smart TV 55-inch",
    "Espresso Machine",
    "Yoga Mat",
    "Wireless Charging Stand",
    "Hardcover Notebook Set",
    "Digital Air Fryer",
    "Running Shoes",
    "Bluetooth Speaker",
    "Ceramic Cookware Set"
    ]
}

class AmazonApis:
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self.current_user: Optional[str] = None
        # Products keyed by name for easier lookup in audio context
        self.products: Dict[str, Dict[str, Any]] = {}
        self.carts: Dict[str, Dict[int, Dict[str, Any]]] = {}
        self.wishlists: Dict[str, Dict[int, Dict[str, Any]]] = {}
        self.orders: Dict[int, Dict[str, Any]] = {}
        self.payment_cards: Dict[int, Dict[str, Any]] = {}
        self.addresses: Dict[int, Dict[str, Any]] = {}
        self.next_id_counters: Dict[str, int] = {}
        self._api_description = "This tool belongs to the AmazonAPI, which provides core functionality for shopping, orders, payments, and account management on Amazon."
        self._load_scenario(DEFAULT_STATE)

    def _load_scenario(self, scenario: dict) -> None:
        """Load a scenario into the AmazonApis instance."""
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        # Map product names to IDs for easier access if products were keyed by ID in original state
        self.products = {
            name: {**details, "id": idx + 1} # Assign a dummy ID if not present
            for idx, (name, details) in enumerate(scenario.get("products", DEFAULT_STATE_COPY["products"]).items())
        }
        self.carts = scenario.get("carts", DEFAULT_STATE_COPY["carts"])
        self.wishlists = scenario.get("wishlists", DEFAULT_STATE_COPY["wishlists"])
        self.orders = scenario.get("orders", DEFAULT_STATE_COPY["orders"])
        self.payment_cards = scenario.get("payment_cards", DEFAULT_STATE_COPY["payment_cards"])
        self.addresses = scenario.get("addresses", DEFAULT_STATE_COPY["addresses"])
        self.next_id_counters = scenario.get("next_id_counters", DEFAULT_STATE_COPY["next_id_counters"])

    def _get_next_id(self, id_type: str) -> int:
        """Generate the next ID for a given type."""
        next_id = self.next_id_counters.get(id_type, 1) # Default to 1 if not found
        self.next_id_counters[id_type] = next_id + 1
        return next_id

    def show_product(self, product_query: str) -> Dict[str, Any]:
        """
        Show product information.

        Args:
            product_query (str): Query to search for a product.

        Returns:
            product_info (dict): Dictionary containing product details or search results.
                                 Includes 'status', 'product' (if singular match), 'message', and 'options' (if multiple matches).
        """
        search_result = self.search_products(product_query)

        if not search_result['status']:
            return {
                "status": False,
                "product": None,
                "message": f"I couldn't find any products matching '{product_query}'. Please try again with a different name."
            }

        found_products = list(search_result['products'].values())

        if len(found_products) == 1:
            product = found_products[0]
            return {
                "status": True,
                "product": product,
                "message": (
                    f"Here's the {product['name']} by {product['brand']}. "
                    f"It's priced at ${product['price']:.2f} and has a {product['rating']} star rating. "
                    f"{product['description']}"
                )
            }
        else:
            # For audio, limit the options to make it manageable
            options_message = ", ".join([p['name'] for p in found_products[:3]])
            return {
                "status": True,
                "product": None,
                "message": (
                    f"I found {len(found_products)} options for '{product_query}'. "
                    f"Did you mean {options_message} or something else?"
                ),
                "options": found_products[:3]
            }

    def search_products(self, query: str) -> Dict[str, Union[bool, Dict[str, Any]]]:
        """
        Search products by natural language query.

        Args:
            query (str): Natural language search query (e.g., "bluetooth earbuds" or "smart tv").

        Returns:
            dict: {
                "status": bool,
                "products": dict of matching products (empty if none found, keyed by product name)
            }
        """
        matches: Dict[str, Any] = {}
        query_lower = query.lower()

        for product_name, product_details in self.products.items():
            # Check product name
            if query_lower in product_name.lower():
                matches[product_name] = product_details
                continue
            # Check keywords
            if any(keyword.lower() in query_lower for keyword in product_details.get('keywords', [])):
                matches[product_name] = product_details
                continue
            # Check description (simplified for dummy)
            if query_lower in product_details.get('description', '').lower():
                matches[product_name] = product_details
                continue
            # Check brand
            if query_lower in product_details.get('brand', '').lower():
                matches[product_name] = product_details
                continue
            # Check category
            if query_lower in product_details.get('category', '').lower():
                matches[product_name] = product_details
                continue

        return {
            "status": len(matches) > 0,
            "products": matches
        }

    def show_cart(self) -> Dict[str, Any]:
        """
        Show current user's shopping cart.

        Returns:
            Dict[str, Any]: A dictionary with 'status' (bool), 'message' (str), and 'cart_items' (list of dicts).
        """
        if not self.current_user:
            return {
                "status": False,
                "message": "No user is currently logged in."
            }

        user_cart = self.carts.get(self.current_user, {})
        if not user_cart:
            return {
                "status": True,
                "message": "Your cart is empty."
            }

        cart_items_list = list(user_cart.values())
        total_price = sum(item['price'] * item['quantity'] for item in cart_items_list)
        item_details = [f"{item['quantity']} {item['name']}" for item in cart_items_list]
        return {
            "status": True,
            "message": f"In your cart, you have: {', '.join(item_details)}. The total is ${total_price:.2f}.",
            "cart_items": cart_items_list,
            "total_price": total_price
        }

    def add_product_to_cart(self, product_query: str, quantity: int = 1) -> Dict[str, Any]:
        """
        Add product to shopping cart.

        Args:
            product_query (str): Natural language query for the product name.
            quantity (int): Quantity to add.

        Returns:
            Dict[str, Any]: A dictionary indicating status, message, and potentially product details or options.
        """
        search_result = self.search_products(product_query)

        if not search_result['status']:
            return {
                "status": False,
                "message": f"I couldn't find '{product_query}'. Please try again."
            }

        found_products_dict = cast(Dict[str, Any], search_result['products'])
        found_products_list = list(found_products_dict.values())

        if len(found_products_list) > 1:
            options_message = ", ".join([p['name'] for p in found_products_list[:3]])
            return {
                "status": False,
                "message": (
                    f"I found multiple matches for '{product_query}': {options_message}. "
                    "Please specify which one you'd like to add."
                ),
                "options": found_products_list[:3]
            }

        product = found_products_list[0]
        product_id = product['id'] # Using the 'id' from the product dictionary

        if self.current_user is None:
            return {
                "status": False,
                "message": "No user is currently logged in. Please log in to add items to your cart."
            }

        if self.current_user not in self.carts:
            self.carts[self.current_user] = {}

        # Use product_id as the key in the cart for consistency
        if product_id in self.carts[self.current_user]:
            self.carts[self.current_user][product_id]["quantity"] += quantity
            action = "updated the quantity of"
        else:
            self.carts[self.current_user][product_id] = {
                "id": product_id,
                "name": product['name'],
                "price": product['price'],
                "quantity": quantity,
                "gift_wrapped": False,
            }
            action = "added"

        return {
            "status": True,
            "message": (
                f"Successfully {action} {quantity} of {product['name']} to your cart."
            ),
            "product": product
        }

    def update_product_quantity_in_cart(self, product_query: str, quantity: int) -> Dict[str, Union[bool, str]]:
        """
        Update product quantity in shopping cart.

        Args:
            product_query (str): Natural language query for the product name to update.
            quantity (int): New quantity.

        Returns:
            Dict[str, Union[bool, str]]: Status and message.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        search_result = self.search_products(product_query)
        if not search_result['status']:
            return {"status": False, "message": f"I couldn't find '{product_query}' in your products."}

        found_products_dict = cast(Dict[str, Any], search_result['products'])
        found_products_list = list(found_products_dict.values())

        if len(found_products_list) > 1:
            options_message = ", ".join([p['name'] for p in found_products_list[:3]])
            return {
                "status": False,
                "message": (
                    f"I found multiple matches for '{product_query}': {options_message}. "
                    "Please specify which one you'd like to update."
                ),
                "options": found_products_list[:3]
            }

        product = found_products_list[0]
        product_id = product['id']

        if product_id not in self.carts.get(self.current_user, {}):
            return {"status": False, "message": f"{product['name']} is not in your cart."}

        if quantity <= 0:
            del self.carts[self.current_user][product_id]
            return {"status": True, "message": f"Removed {product['name']} from your cart."}
        else:
            self.carts[self.current_user][product_id]["quantity"] = quantity
            return {"status": True, "message": f"Updated {product['name']} in your cart to {quantity}."}

    def remove_product_from_cart(self, product_query: str) -> Dict[str, Union[bool, str]]:
        """
        Remove product from shopping cart.

        Args:
            product_query (str): Natural language query for the product name to remove.

        Returns:
            Dict[str, Union[bool, str]]: Status and message.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        search_result = self.search_products(product_query)
        if not search_result['status']:
            return {"status": False, "message": f"I couldn't find '{product_query}' in your products."}

        found_products_dict = cast(Dict[str, Any], search_result['products'])
        found_products_list = list(found_products_dict.values())

        if len(found_products_list) > 1:
            options_message = ", ".join([p['name'] for p in found_products_list[:3]])
            return {
                "status": False,
                "message": (
                    f"I found multiple matches for '{product_query}': {options_message}. "
                    "Please specify which one you'd like to remove."
                ),
                "options": found_products_list[:3]
            }

        product = found_products_list[0]
        product_id = product['id']

        if product_id not in self.carts.get(self.current_user, {}):
            return {"status": False, "message": f"{product['name']} is not in your cart."}

        del self.carts[self.current_user][product_id]
        return {"status": True, "message": f"Successfully removed {product['name']} from your cart."}


    def clear_cart(self) -> Dict[str, Union[bool, str]]:
        """
        Clear all items from shopping cart.

        Returns:
            Dict[str, Union[bool, str]]: Status and message.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        if self.current_user in self.carts and self.carts[self.current_user]:
            self.carts[self.current_user] = {}
            return {"status": True, "message": "Your cart has been cleared."}
        else:
            return {"status": True, "message": "Your cart is already empty."}


    def show_wish_list(self) -> Dict[str, Any]:
        """
        Show current user's wish list.

        Returns:
            Dict[str, Any]: A dictionary with 'status' (bool), 'message' (str), and 'wishlist_items' (list of dicts).
        """
        if not self.current_user:
            return {
                "status": False,
                "message": "No user is currently logged in."
            }

        user_wishlist = self.wishlists.get(self.current_user, {})
        if not user_wishlist:
            return {
                "status": True,
                "message": "Your wish list is empty."
            }

        wishlist_items_list = list(user_wishlist.values())
        item_names = [item['name'] for item in wishlist_items_list]
        return {
            "status": True,
            "message": f"In your wish list, you have: {', '.join(item_names)}.",
            "wishlist_items": wishlist_items_list
        }

    def add_product_to_wish_list(self, product_query: str, quantity: int = 1) -> Dict[str, Any]:
        """
        Add product to wish list.

        Args:
            product_query (str): Natural language query for the product name.
            quantity (int): Quantity to add (default 1).

        Returns:
            Dict[str, Any]: A dictionary indicating status, message, and potentially product details or options.
        """
        search_result = self.search_products(product_query)

        if not search_result['status']:
            return {
                "status": False,
                "message": f"I couldn't find '{product_query}'. Please try again."
            }

        found_products_dict = cast(Dict[str, Any], search_result['products'])
        found_products_list = list(found_products_dict.values())

        if len(found_products_list) > 1:
            options_message = ", ".join([p['name'] for p in found_products_list[:3]])
            return {
                "status": False,
                "message": (
                    f"I found multiple matches for '{product_query}': {options_message}. "
                    "Please specify which one you'd like to add to your wish list."
                ),
                "options": found_products_list[:3]
            }

        product = found_products_list[0]
        product_id = product['id']

        if self.current_user is None:
            return {
                "status": False,
                "message": "No user is currently logged in."
            }

        if self.current_user not in self.wishlists:
            self.wishlists[self.current_user] = {}

        if product_id in self.wishlists[self.current_user]:
            self.wishlists[self.current_user][product_id]["quantity"] += quantity
            action = "updated the quantity of"
        else:
            self.wishlists[self.current_user][product_id] = {
                "id": product_id,
                "name": product['name'],
                "price": product['price'],
                "quantity": quantity,
                "added_date": "2023-07-15" # Dummy date
            }
            action = "added"

        return {
            "status": True,
            "message": (
                f"Successfully {action} {quantity} of {product['name']} to your wish list."
            ),
            "product": product
        }

    def remove_product_from_wish_list(self, product_query: str) -> Dict[str, Union[bool, str]]:
        """
        Remove product from wish list.

        Args:
            product_query (str): Natural language query for the product name to remove.

        Returns:
            Dict[str, Union[bool, str]]: Status and message.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        search_result = self.search_products(product_query)
        if not search_result['status']:
            return {"status": False, "message": f"I couldn't find '{product_query}' in your products."}

        found_products_dict = cast(Dict[str, Any], search_result['products'])
        found_products_list = list(found_products_dict.values())

        if len(found_products_list) > 1:
            options_message = ", ".join([p['name'] for p in found_products_list[:3]])
            return {
                "status": False,
                "message": (
                    f"I found multiple matches for '{product_query}': {options_message}. "
                    "Please specify which one you'd like to remove from your wish list."
                ),
                "options": found_products_list[:3]
            }

        product = found_products_list[0]
        product_id = product['id']

        if product_id not in self.wishlists.get(self.current_user, {}):
            return {"status": False, "message": f"{product['name']} is not in your wish list."}

        del self.wishlists[self.current_user][product_id]
        return {"status": True, "message": f"Successfully removed {product['name']} from your wish list."}

    def clear_wish_list(self) -> Dict[str, Union[bool, str]]:
        """
        Clear all items from wish list.

        Returns:
            Dict[str, Union[bool, str]]: Status and message.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        if self.current_user in self.wishlists and self.wishlists[self.current_user]:
            self.wishlists[self.current_user] = {}
            return {"status": True, "message": "Your wish list has been cleared."}
        else:
            return {"status": True, "message": "Your wish list is already empty."}

    def show_orders(self, query: Optional[str] = None, page_index: int = 1, page_limit: int = 5) -> Dict[str, Any]:
        """
        Show user's order history.

        Args:
            query (Optional[str]): Search query for orders (e.g., "recent", "delivered").
            page_index (int): Page number of results.
            page_limit (int): Number of results per page.

        Returns:
            Dict[str, Any]: Status, message, and a list of orders.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        user_orders = [order for order in self.orders.values() if order.get('user_id') == self.current_user]

        # Dummy filtering based on query
        filtered_orders = []
        if query:
            query_lower = query.lower()
            for order in user_orders:
                if query_lower in order.get('status', '').lower():
                    filtered_orders.append(order)
                elif any(query_lower in item.get('name', '').lower() for item in order.get('items', [])):
                    filtered_orders.append(order)
        else:
            filtered_orders = user_orders

        total_orders = len(filtered_orders)
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_orders = filtered_orders[start_index:end_index]

        if not paginated_orders:
            return {"status": True, "message": "You have no orders matching your criteria."}

        order_summaries = []
        for order in paginated_orders:
            item_names = ", ".join([item['name'] for item in order['items']])
            order_summaries.append(
                f"Order ID {order['id']}, placed on {order['order_date']}, total ${order['total']:.2f}, status: {order['status']}, items: {item_names}"
            )

        return {
            "status": True,
            "message": (
                f"Here are your orders (Page {page_index} of {((total_orders - 1) // page_limit) + 1}):\n"
                + "\n".join(order_summaries)
            ),
            "orders": paginated_orders,
            "total_orders": total_orders,
            "page_index": page_index,
            "page_limit": page_limit
        }

    def show_order_details(self, order_id: int) -> Dict[str, Any]:
        """
        Show details of a specific order.

        Args:
            order_id (int): ID of order to show.

        Returns:
            Dict[str, Any]: Status, message, and order details.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        order = self.orders.get(order_id)
        if not order or order.get('user_id') != self.current_user:
            return {"status": False, "message": f"Order with ID {order_id} not found or does not belong to you."}

        items_description = ", ".join([f"{item['quantity']} {item['name']}" for item in order['items']])
        shipping_address = self.addresses.get(order['shipping_address_id'], {})
        payment_method = self.payment_cards.get(order['payment_method_id'], {})

        message = (
            f"Details for Order ID {order_id}:\n"
            f"Status: {order['status']}\n"
            f"Order Date: {order['order_date']}\n"
            f"Total: ${order['total']:.2f}\n"
            f"Items: {items_description}\n"
            f"Shipping To: {shipping_address.get('full_name', '')}, {shipping_address.get('street', '')}, {shipping_address.get('city', '')}, {shipping_address.get('state', '')} {shipping_address.get('zip_code', '')}\n"
            f"Payment Method: {payment_method.get('card_type', '')} ending in {payment_method.get('last_four', '')}"
        )

        return {
            "status": True,
            "message": message,
            "order": order
        }

    def place_order(self, payment_card_query: str, shipping_address_query: str) -> Dict[str, Any]:
        """
        Place a new order using specified payment card and shipping address.

        Args:
            payment_card_query (str): Natural language query for the payment card (e.g., "my Visa card", "the card ending in 4242").
            shipping_address_query (str): Natural language query for the shipping address (e.g., "my home address", "the address on Main Street").

        Returns:
            Dict[str, Any]: Status, message, and new order details if successful.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        user_cart = self.carts.get(self.current_user, {})
        if not user_cart:
            return {"status": False, "message": "Your cart is empty. Please add items before placing an order."}

        # Dummy logic to find payment card by query (e.g., 'Visa', '4242')
        # In a real system, you'd have more robust fuzzy matching or an ID
        found_payment_card = None
        for card_id, card in self.payment_cards.items():
            if card.get('user_id') == self.current_user and (
                payment_card_query.lower() in card.get('card_type', '').lower() or
                payment_card_query in card.get('last_four', '')
            ):
                found_payment_card = card
                break
        if not found_payment_card:
            return {"status": False, "message": "I couldn't find a matching payment card. Please specify or add one."}

        # Dummy logic to find address by query (e.g., 'Main Street', 'home')
        found_shipping_address = None
        for address_id, address in self.addresses.items():
            if address.get('user_id') == self.current_user and (
                shipping_address_query.lower() in address.get('street', '').lower() or
                ('home' in shipping_address_query.lower() and address.get('is_primary', False))
            ):
                found_shipping_address = address
                break
        if not found_shipping_address:
            return {"status": False, "message": "I couldn't find a matching shipping address. Please specify or add one."}

        order_id = self._get_next_id("order")
        items_for_order = list(user_cart.values())
        total_order_price = sum(item['price'] * item['quantity'] for item in items_for_order)

        self.orders[order_id] = {
            "id": order_id,
            "user_id": self.current_user,
            "items": deepcopy(items_for_order),
            "total": total_order_price,
            "order_date": "2023-07-15", # Dummy date
            "status": "placed",
            "shipping_address_id": found_shipping_address['id'],
            "payment_method_id": found_payment_card['id']
        }

        # Clear the cart after placing order
        self.carts[self.current_user] = {}

        return {
            "status": True,
            "message": f"Your order with ID {order_id} has been placed successfully! It totals ${total_order_price:.2f}.",
            "order": self.orders[order_id]
        }

    def show_payment_cards(self) -> Dict[str, Any]:
        """
        Show user's saved payment cards.

        Returns:
            Dict[str, Any]: Status, message, and a list of payment cards.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        user_cards = [card for card in self.payment_cards.values() if card.get('user_id') == self.current_user]

        if not user_cards:
            return {"status": True, "message": "You have no saved payment cards."}

        card_summaries = []
        for card in user_cards:
            card_summaries.append(f"{card.get('card_type', 'Unknown')} ending in {card.get('last_four', '****')} (Expires: {card.get('exp_date', 'MM/YY')})")

        return {
            "status": True,
            "message": f"Here are your saved payment cards: {'; '.join(card_summaries)}.",
            "payment_cards": user_cards
        }

    def add_payment_card(self, card_type: str, last_four_digits: str, expiry_date: str) -> Dict[str, Any]:
        """
        Add a new payment card.
        For audio, we won't ask for full card number or CVV.

        Args:
            card_type (str): Type of card (e.g., "Visa", "Mastercard").
            last_four_digits (str): Last four digits of the card number.
            expiry_date (str): Expiry date (MM/YY).

        Returns:
            Dict[str, Any]: Status, message, and details of the added card.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        if not (card_type and last_four_digits and expiry_date):
            return {"status": False, "message": "Please provide the card type, last four digits, and expiry date."}

        card_id = self._get_next_id("payment_card")
        new_card = {
            "id": card_id,
            "user_id": self.current_user,
            "card_type": card_type,
            "last_four": last_four_digits,
            "exp_date": expiry_date,
            "billing_address_id": self._get_next_id("address") -1 # Assuming a primary address exists or will be added
        }
        self.payment_cards[card_id] = new_card

        return {
            "status": True,
            "message": f"Successfully added your {card_type} card ending in {last_four_digits}.",
            "payment_card": new_card
        }

    def delete_payment_card(self, card_query: str) -> Dict[str, Union[bool, str]]:
        """
        Delete a payment card.

        Args:
            card_query (str): Natural language query for the card to delete (e.g., "Visa card", "card ending in 4242").

        Returns:
            Dict[str, Union[bool, str]]: Status and message.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        card_to_delete_id = None
        card_name = None
        for card_id, card in self.payment_cards.items():
            if card.get('user_id') == self.current_user and (
                card_query.lower() in card.get('card_type', '').lower() or
                card_query in card.get('last_four', '')
            ):
                card_to_delete_id = card_id
                card_name = f"{card.get('card_type')} ending in {card.get('last_four')}"
                break

        if card_to_delete_id is None:
            return {"status": False, "message": f"I couldn't find a payment card matching '{card_query}'."}

        del self.payment_cards[card_to_delete_id]
        return {"status": True, "message": f"Successfully deleted your {card_name}."}

    def show_addresses(self) -> Dict[str, Any]:
        """
        Show user's saved addresses.

        Returns:
            Dict[str, Any]: Status, message, and a list of addresses.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        user_addresses = [addr for addr in self.addresses.values() if addr.get('user_id') == self.current_user]

        if not user_addresses:
            return {"status": True, "message": "You have no saved addresses."}

        address_summaries = []
        for addr in user_addresses:
            primary_tag = " (Primary)" if addr.get('is_primary') else ""
            address_summaries.append(
                f"{addr.get('full_name', '')}: {addr.get('street', '')}, {addr.get('city', '')}, {addr.get('state', '')} {addr.get('zip_code', '')}{primary_tag}"
            )

        return {
            "status": True,
            "message": f"Here are your saved addresses: {'; '.join(address_summaries)}.",
            "addresses": user_addresses
        }

    def add_address(self, full_name: str, street: str, city: str, state: str, zip_code: str, country: str = "USA", is_primary: bool = False) -> Dict[str, Any]:
        """
        Add a new address.

        Args:
            full_name (str): Full name for the address.
            street (str): Street address.
            city (str): City.
            state (str): State/province (e.g., "CA", "New York").
            zip_code (str): Zip/postal code.
            country (str): Country (default "USA").
            is_primary (bool): Whether this should be set as the primary address (default False).

        Returns:
            Dict[str, Any]: Status, message, and details of the added address.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        if not (full_name and street and city and state and zip_code):
            return {"status": False, "message": "Please provide full name, street, city, state, and zip code for the address."}

        address_id = self._get_next_id("address")
        new_address = {
            "id": address_id,
            "user_id": self.current_user,
            "full_name": full_name,
            "street": street,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "country": country,
            "is_primary": is_primary
        }
        self.addresses[address_id] = new_address

        # If setting as primary, update other addresses
        if is_primary:
            for addr_id, addr in self.addresses.items():
                if addr.get('user_id') == self.current_user and addr_id != address_id:
                    addr['is_primary'] = False

        return {
            "status": True,
            "message": f"Successfully added address for {full_name} at {street}, {city}, {state}.",
            "address": new_address
        }

    def delete_address(self, address_query: str) -> Dict[str, Union[bool, str]]:
        """
        Delete an address.

        Args:
            address_query (str): Natural language query for the address to delete (e.g., "home address", "address on Main Street").

        Returns:
            Dict[str, Union[bool, str]]: Status and message.
        """
        if not self.current_user:
            return {"status": False, "message": "No user is currently logged in."}

        address_to_delete_id = None
        address_description = None
        for addr_id, addr in self.addresses.items():
            if addr.get('user_id') == self.current_user and (
                address_query.lower() in addr.get('street', '').lower() or
                address_query.lower() in addr.get('full_name', '').lower() or
                ('home' in address_query.lower() and addr.get('is_primary', False))
            ):
                address_to_delete_id = addr_id
                address_description = f"{addr.get('full_name')}'s address at {addr.get('street')}"
                break

        if address_to_delete_id is None:
            return {"status": False, "message": f"I couldn't find an address matching '{address_query}'."}

        del self.addresses[address_to_delete_id]
        return {"status": True, "message": f"Successfully deleted {address_description}."}