from typing import Dict, List, Union, Literal, Any
from datetime import datetime, timedelta
from copy import deepcopy

class EmailStr(str):
    pass

class User:
    def __init__(self, email: str):
        self.email = email

DEFAULT_STATE = {
    "users": {
        "alice.smith@example.com": {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@example.com",
            "balance": 125.75,
            "friends": ["charlie.brown@example.com"],
            "payment_cards": {
                1: {"card_name": "Alice's Visa", "owner_name": "Alice Smith", "card_number": 4111, "expiry_year": 2028, "expiry_month": 12, "cvv_number": 123},
                6: {"card_name": "Alice's Mastercard", "owner_name": "Alice Smith", "card_number": 5222, "expiry_year": 2027, "expiry_month": 7, "cvv_number": 456}
            },
            "addresses": {
                1: {"name": "Home Address", "street_address": "123 Oak Avenue", "city": "Springfield", "state": "IL", "country": "USA", "zip_code": 62704},
                6: {"name": "Cabin Getaway", "street_address": "789 Lake View Rd", "city": "Lakefield", "state": "WI", "country": "USA", "zip_code": 54123}
            },
            "cart": {
                2: {"product_id": 2, "name": "Wireless Earbuds", "quantity": 1, "price": 49.99}
            },
            "wish_list": {
                4: {"product_id": 4, "name": "Coffee Maker", "price": 80.00}
            },
            "orders": {
                101: {
                    "order_id": 101,
                    "order_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                    "total_amount": 75.00,
                    "status": "delivered",
                    "products": {
                        1: {"product_id": 1, "name": "Laptop", "quantity": 1, "price": 75.00}
                    }
                },
                105: {
                    "order_id": 105,
                    "order_date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
                    "total_amount": 30.00,
                    "status": "delivered",
                    "products": {
                        3: {"product_id": 3, "name": "T-Shirt", "quantity": 1, "price": 20.00},
                        5: {"product_id": 5, "name": "Water Bottle", "quantity": 1, "price": 10.00}
                    }
                },
            },
            "prime_subscriptions": {
                1: {
                    "subscription_id": 1,
                    "plan": "monthly",
                    "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                    "status": "active"
                }
            }
        },
        "bob.johnson@example.com": {
            "first_name": "Robert",
            "last_name": "Johnson",
            "email": "bob.johnson@example.com",
            "balance": 250.00,
            "friends": ["alice.smith@example.com", "diana.prince@example.com"],
            "payment_cards": {
                2: {"card_name": "Bob's Credit Card", "owner_name": "Robert Johnson", "card_number": 5678, "expiry_year": 2029, "expiry_month": 10, "cvv_number": 456}
            },
            "addresses": {
                2: {"name": "Work Address", "street_address": "456 Business Ave", "city": "Metropolis", "state": "NY", "country": "USA", "zip_code": 10001}
            },
            "cart": {},
            "wish_list": {
                3: {"product_id": 3, "name": "T-Shirt", "price": 20.00}
            },
            "orders": {
                102: {
                    "order_id": 102,
                    "order_date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                    "total_amount": 25.00,
                    "status": "shipped",
                    "products": {
                        2: {"product_id": 2, "name": "Wireless Mouse", "quantity": 1, "price": 25.00}
                    }
                }
            },
            "prime_subscriptions": {}
        },
        "charlie.brown@example.com": {
            "first_name": "Charles",
            "last_name": "Brown",
            "email": "charlie.brown@example.com",
            "balance": 50.00,
            "friends": ["alice.smith@example.com"],
            "payment_cards": {
                3: {"card_name": "Charlie's Card", "owner_name": "Charles Brown", "card_number": 9876, "expiry_year": 2027, "expiry_month": 6, "cvv_number": 789}
            },
            "addresses": {
                3: {"name": "Apartment", "street_address": "789 Pine Ln", "city": "Smallville", "state": "CA", "country": "USA", "zip_code": 90210}
            },
            "cart": {
                1: {"product_id": 1, "name": "Laptop", "quantity": 1, "price": 75.00}
            },
            "wish_list": {},
            "orders": {},
            "prime_subscriptions": {
                2: {
                    "subscription_id": 2,
                    "plan": "yearly",
                    "start_date": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
                    "end_date": (datetime.now() + timedelta(days=305)).strftime("%Y-%m-%d"),
                    "status": "active"
                }
            }
        },
        "diana.prince@example.com": {
            "first_name": "Diana",
            "last_name": "Prince",
            "email": "diana.prince@example.com",
            "balance": 500.00,
            "friends": ["bob.johnson@example.com"],
            "payment_cards": {
                4: {"card_name": "Diana's Visa", "owner_name": "Diana Prince", "card_number": 1122, "expiry_year": 2030, "expiry_month": 3, "cvv_number": 101}
            },
            "addresses": {
                4: {"name": "Vacation Home", "street_address": "321 Ocean Blvd", "city": "Beach City", "state": "FL", "country": "USA", "zip_code": 33455}
            },
            "cart": {},
            "wish_list": {
                1: {"product_id": 1, "name": "Laptop", "price": 75.00}
            },
            "orders": {
                103: {
                    "order_id": 103,
                    "order_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                    "total_amount": 40.00,
                    "status": "processing",
                    "products": {
                        3: {"product_id": 3, "name": "T-Shirt", "quantity": 2, "price": 20.00}
                    }
                },
                104: {
                    "order_id": 104,
                    "order_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                    "total_amount": 25.00,
                    "status": "pending",
                    "products": {
                        2: {"product_id": 2, "name": "Wireless Mouse", "quantity": 1, "price": 25.00}
                    }
                }
            },
            "prime_subscriptions": {
                3: {
                    "subscription_id": 3,
                    "plan": "monthly",
                    "start_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                    "end_date": (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d"),
                    "status": "active"
                }
            }
        },
        "eve.adams@example.com": {
            "first_name": "Eve",
            "last_name": "Adams",
            "email": "eve.adams@example.com",
            "balance": 150.00,
            "friends": ["charlie.brown@example.com"],
            "payment_cards": {
                5: {"card_name": "Eve's MasterCard", "owner_name": "Eve Adams", "card_number": 3344, "expiry_year": 2026, "expiry_month": 9, "cvv_number": 222}
            },
            "addresses": {
                5: {"name": "Primary Home", "street_address": "876 River Rd", "city": "Riverside", "state": "GA", "country": "USA", "zip_code": 30303}
            },
            "cart": {},
            "wish_list": {
                1: {"product_id": 1, "name": "Laptop", "price": 75.00}
            },
            "orders": {},
            "prime_subscriptions": {}
        },
        "frank.jones@example.com": {
            "first_name": "Frank",
            "last_name": "Jones",
            "email": "frank.jones@example.com",
            "balance": 80.00,
            "friends": [],
            "payment_cards": {},
            "addresses": {
                7: {"name": "Apartment", "street_address": "555 Cedar St", "city": "Townsville", "state": "TX", "country": "USA", "zip_code": 75001}
            },
            "cart": {
                5: {"product_id": 5, "name": "Water Bottle", "quantity": 2, "price": 10.00}
            },
            "wish_list": {},
            "orders": {
                106: {
                    "order_id": 106,
                    "order_date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                    "total_amount": 60.00,
                    "status": "shipped",
                    "products": {
                        4: {"product_id": 4, "name": "Coffee Maker", "quantity": 1, "price": 80.00}
                    }
                }
            },
            "prime_subscriptions": {
                4: {
                    "subscription_id": 4,
                    "plan": "monthly",
                    "start_date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                    "end_date": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
                    "status": "active"
                }
            }
        },
        "grace.taylor@example.com": {
            "first_name": "Grace",
            "last_name": "Taylor",
            "email": "grace.taylor@example.com",
            "balance": 300.00,
            "friends": ["alice.smith@example.com", "frank.jones@example.com"],
            "payment_cards": {
                8: {"card_name": "Grace's Discover", "owner_name": "Grace Taylor", "card_number": 9988, "expiry_year": 2029, "expiry_month": 11, "cvv_number": 333}
            },
            "addresses": {
                8: {"name": "Home", "street_address": "101 Elm Street", "city": "Maplewood", "state": "OR", "country": "USA", "zip_code": 97005}
            },
            "cart": {},
            "wish_list": {},
            "orders": {},
            "prime_subscriptions": {}
        },
    },
    "current_user": "alice.smith@example.com",
    "products": {
        1: {
            "product_id": 1,
            "name": "Laptop",
            "description": "Powerful laptop for all your needs with a 15-inch display.",
            "price": 750.00,
            "product_type": "electronics",
            "color": "silver",
            "relative_size": "medium",
            "product_rating": 4.5,
            "seller_id": 1,
            "stock": 10
        },
        2: {
            "product_id": 2,
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse with customizable buttons.",
            "price": 25.00,
            "product_type": "electronics",
            "color": "black",
            "relative_size": "small",
            "product_rating": 4.0,
            "seller_id": 1,
            "stock": 50
        },
        3: {
            "product_id": 3,
            "name": "T-Shirt",
            "description": "Comfortable 100% \cotton t-shirt, breathable and soft.",
            "price": 20.00,
            "product_type": "apparel",
            "color": "blue",
            "relative_size": "large",
            "product_rating": 4.2,
            "seller_id": 2,
            "stock": 100
        },
        4: {
            "product_id": 4,
            "name": "Coffee Maker",
            "description": "Automatic drip coffee maker with a 12-cup capacity.",
            "price": 80.00,
            "product_type": "home_appliances",
            "color": "black",
            "relative_size": "medium",
            "product_rating": 4.7,
            "seller_id": 3,
            "stock": 20
        },
        5: {
            "product_id": 5,
            "name": "Water Bottle",
            "description": "Insulated stainless steel water bottle, keeps drinks cold for 24 hours.",
            "price": 10.00,
            "product_type": "kitchen_dining",
            "color": "red",
            "relative_size": "small",
            "product_rating": 4.9,
            "seller_id": 2,
            "stock": 200
        },
        6: {
            "product_id": 6,
            "name": "Bluetooth Speaker",
            "description": "Portable Bluetooth speaker with rich bass and clear sound.",
            "price": 60.00,
            "product_type": "electronics",
            "color": "grey",
            "relative_size": "small",
            "product_rating": 4.3,
            "seller_id": 1,
            "stock": 30
        },
    },
    "sellers": {
        1: {
            "seller_id": 1,
            "name": "ElectroTech Solutions",
            "rating": 4.8
        },
        2: {
            "seller_id": 2,
            "name": "Trendy Threads Co.",
            "rating": 4.5
        },
        3: {
            "seller_id": 3,
            "name": "Home Comforts Ltd.",
            "rating": 4.7
        }
    },
    "product_reviews": {
        1: [
            {"review_id": 1, "product_id": 1, "user_email": "alice.smith@example.com", "rating": 5, "comment": "Amazing laptop for coding!", "is_verified": True},
            {"review_id": 2, "product_id": 1, "user_email": "diana.prince@example.com", "rating": 4, "comment": "Good value, but battery life could be better.", "is_verified": True}
        ],
        3: [
            {"review_id": 3, "product_id": 3, "user_email": "bob.johnson@example.com", "rating": 4, "comment": "Comfortable and fits well.", "is_verified": True}
        ],
        5: [
            {"review_id": 4, "product_id": 5, "user_email": "frank.jones@example.com", "rating": 5, "comment": "My new favorite water bottle!", "is_verified": True}
        ]
    },
    "product_questions": {
        1: [
            {"question_id": 1, "product_id": 1, "user_email": "charlie.brown@example.com", "question": "Does it come with Windows Pro or Home?", "answers": [
                {"answer_id": 1, "user_email": "ElectroTech Solutions", "answer": "It comes pre-installed with Windows 11 Home edition."}
            ]}
        ],
        4: [
            {"question_id": 2, "product_id": 4, "user_email": "grace.taylor@example.com", "question": "Is this coffee maker programmable?", "answers": []}
        ]
    },
    "deliverers": {
        1: {"deliverer_id": 1, "name": "Speedy Deliveries"},
        2: {"deliverer_id": 2, "name": "Global Freight"}
    },
    "prime_plans": {
        "monthly": {"price": 14.99, "description": "Monthly Prime subscription with free express shipping."},
        "yearly": {"price": 139.00, "description": "Yearly Prime subscription, saving you money, includes free express shipping and exclusive deals."}
    },
    "transaction_counter": 0,
    "payment_card_counter": 8,
    "address_counter": 8,
    "order_counter": 106,
    "return_counter": 0,
    "prime_subscription_counter": 4,
    "product_review_counter": 4,
    "product_question_counter": 2,
}

class AmazonApis:
    def __init__(self):
        self.users: Dict[EmailStr, Dict[str, Any]]
        self.current_user: EmailStr | None
        self.products: Dict[int, Dict[str, Any]]
        self.sellers: Dict[int, Dict[str, Any]]
        self.product_reviews: Dict[int, List[Dict[str, Any]]]
        self.product_questions: Dict[int, List[Dict[str, Any]]]
        self.deliverers: Dict[int, Dict[str, Any]]
        self.prime_plans: Dict[str, Dict[str, Any]]
        self.transaction_counter: int
        self.payment_card_counter: int
        self.address_counter: int
        self.order_counter: int
        self.return_counter: int
        self.prime_subscription_counter: int
        self.product_review_counter: int
        self.product_question_counter: int
        self._api_description = "This tool provides core functionalities for managing user accounts, Browse products, managing shopping cart and wish lists, placing orders, handling returns, and managing Prime subscriptions on Amazon."

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load a scenario into the AmazonApis instance.
        Args:
            scenario (dict): A dictionary containing Amazon data.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.products = scenario.get("products", DEFAULT_STATE_COPY["products"])
        self.sellers = scenario.get("sellers", DEFAULT_STATE_COPY["sellers"])
        self.product_reviews = scenario.get("product_reviews", DEFAULT_STATE_COPY["product_reviews"])
        self.product_questions = scenario.get("product_questions", DEFAULT_STATE_COPY["product_questions"])
        self.deliverers = scenario.get("deliverers", DEFAULT_STATE_COPY["deliverers"])
        self.prime_plans = scenario.get("prime_plans", DEFAULT_STATE_COPY["prime_plans"])
        self.transaction_counter = scenario.get("transaction_counter", DEFAULT_STATE_COPY["transaction_counter"])
        self.payment_card_counter = scenario.get("payment_card_counter", DEFAULT_STATE_COPY["payment_card_counter"])
        self.address_counter = scenario.get("address_counter", DEFAULT_STATE_COPY["address_counter"])
        self.order_counter = scenario.get("order_counter", DEFAULT_STATE_COPY["order_counter"])
        self.return_counter = scenario.get("return_counter", DEFAULT_STATE_COPY["return_counter"])
        self.prime_subscription_counter = scenario.get("prime_subscription_counter", DEFAULT_STATE_COPY["prime_subscription_counter"])
        self.product_review_counter = scenario.get("product_review_counter", DEFAULT_STATE_COPY["product_review_counter"])
        self.product_question_counter = scenario.get("product_question_counter", DEFAULT_STATE_COPY["product_question_counter"])

    def _get_user_data(self, user: User) -> Dict:
        """Helper to get user data."""
        return self.users.get(user.email, {})

    def _update_user_data(self, user: User, key: str, value: Any):
        """Helper to update user data."""
        if user.email in self.users:
            self.users[user.email][key] = value

    def show_profile(self, email: EmailStr) -> Dict[str, Union[bool, Dict]]:
        """
        Shows the profile of a user.

        Args:
            email (EmailStr): The email of the user whose profile is to be shown.

        Returns:
            Dict: A dictionary containing 'profile_status' (bool) and 'user_profile' (Dict) if successful.
        """
        user_profile = self.users.get(str(email))
        if user_profile:
            return {
                "profile_status": True,
                "user_profile": {
                    "first_name": user_profile["first_name"],
                    "last_name": user_profile["last_name"],
                    "email": user_profile["email"],
                },
            }
        return {"profile_status": False, "user_profile": {}}

    def show_account(self, user: User) -> Dict[str, Union[bool, Dict]]:
        """
        Shows the full account details of the current user.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'account_status' (bool) and 'user_account' (Dict) if successful.
        """
        user_data = self._get_user_data(user)
        if user_data:
            return {"account_status": True, "user_account": user_data}
        return {"account_status": False, "user_account": {}}

    def delete_account(self, user: User) -> Dict[str, Union[bool, str]]:
        """
        Deletes the account of the current user.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'delete_status' (bool) and 'message' (str).
        """
        if user.email in self.users:
            del self.users[user.email]
            if self.current_user == user.email:
                self.current_user = None
            return {"delete_status": True, "message": f"Account {user.email} deleted successfully."}
        return {"delete_status": False, "message": "User not found."}

    def show_product(self, product_id: int) -> Dict[str, Union[bool, Dict]]:
        """
        Shows the details of a specific product.

        Args:
            product_id (int): The ID of the product.

        Returns:
            Dict: A dictionary containing 'product_status' (bool) and 'product' (Dict) if successful.
        """
        product = self.products.get(product_id)
        if product:
            return {"product_status": True, "product": product}
        return {"product_status": False, "product": {}}

    def search_sellers(self, query: str = "", page_index: int = 1, page_limit: int = 10) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Searches for sellers, optionally filtered by a query.

        Args:
            query (str): Optional search query to filter sellers by name.
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.

        Returns:
            Dict: A dictionary containing 'sellers_status' (bool) and 'sellers' (List[Dict]) if successful.
        """
        all_sellers = list(self.sellers.values())
        filtered_sellers = [
            seller for seller in all_sellers
            if query.lower() in seller["name"].lower()
        ]

        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_sellers = filtered_sellers[start_index:end_index]

        return {"sellers_status": True, "sellers": paginated_sellers}

    def show_seller(self, seller_id: int) -> Dict[str, Union[bool, Dict]]:
        """
        Shows the details of a specific seller.

        Args:
            seller_id (int): The ID of the seller.

        Returns:
            Dict: A dictionary containing 'seller_status' (bool) and 'seller' (Dict) if successful.
        """
        seller = self.sellers.get(seller_id)
        if seller:
            return {"seller_status": True, "seller": seller}
        return {"seller_status": False, "seller": {}}

    def search_product_types(self, query: str = "", page_index: int = 1, page_limit: int = 10) -> Dict[str, Union[bool, List[str]]]:
        """
        Searches for product types, optionally filtered by a query.

        Args:
            query (str): Optional search query to filter product types.
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.

        Returns:
            Dict: A dictionary containing 'product_types_status' (bool) and 'product_types' (List[str]) if successful.
        """
        all_product_types = sorted(list(set(product["product_type"] for product in self.products.values())))
        filtered_product_types = [
            pt for pt in all_product_types
            if query.lower() in pt.lower()
        ]

        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_product_types = filtered_product_types[start_index:end_index]

        return {"product_types_status": True, "product_types": paginated_product_types}

    def show_product_feature_choices(self, product_type: str | None) -> Dict[str, Union[bool, Dict]]:
        """
        Shows available feature choices for a given product type (e.g., colors, sizes).

        Args:
            product_type (str | None): The product type to get feature choices for. If None, shows all.

        Returns:
            Dict: A dictionary containing 'feature_choices_status' (bool) and 'feature_choices' (Dict).
        """
        feature_choices = {
            "colors": [],
            "relative_sizes": ["extra-small", "small", "medium", "large", "extra-large"]
        }
        
        products_to_consider = []
        if product_type:
            products_to_consider = [p for p in self.products.values() if p["product_type"] == product_type]
        else:
            products_to_consider = list(self.products.values())

        for product in products_to_consider:
            if "color" in product and product["color"] not in feature_choices["colors"]:
                feature_choices["colors"].append(product["color"])
        
        feature_choices["colors"].sort()
        
        return {"feature_choices_status": True, "feature_choices": feature_choices}

    def search_products(
        self,
        query: str = "",
        page_index: int = 1,
        page_limit: int = 10,
        product_type: str = None,
        color: str = None,
        relative_size: Literal["extra-small", "small", "medium", "large", "extra-large"] = None,
        min_price: float = 0.0,
        max_price: float = float('inf'),
        min_product_rating: float = 0.0,
        max_product_rating: float = 5.0,
        min_seller_rating: float = 0.0,
        max_seller_rating: float = 5.0,
        seller_id: int | None = None,
        sort_by: str | None = None,
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Searches for products with various filtering and sorting options.

        Args:
            query (str): Optional search query for product name or description.
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.
            product_type (str): Filter by product type.
            color (str): Filter by product color.
            relative_size (Literal): Filter by product relative size.
            min_price (float): Minimum price.
            max_price (float): Maximum price.
            min_product_rating (float): Minimum product rating.
            max_product_rating (float): Maximum product rating.
            min_seller_rating (float): Minimum seller rating.
            max_seller_rating (float): Maximum seller rating.
            seller_id (int | None): Filter by specific seller ID.
            sort_by (str | None): Field to sort by (e.g., 'price_asc', 'price_desc', 'rating_asc', 'rating_desc').

        Returns:
            Dict: A dictionary containing 'products_status' (bool) and 'products' (List[Dict]) if successful.
        """
        filtered_products = []
        for product in self.products.values():
            if query and not (query.lower() in product["name"].lower() or query.lower() in product["description"].lower()):
                continue
            if product_type and product["product_type"] != product_type:
                continue
            if color and product.get("color") != color:
                continue
            if relative_size and product.get("relative_size") != relative_size:
                continue
            if not (min_price <= product["price"] <= max_price):
                continue
            if not (min_product_rating <= product["product_rating"] <= max_product_rating):
                continue
            
            seller = self.sellers.get(product["seller_id"])
            if seller and not (min_seller_rating <= seller["rating"] <= max_seller_rating):
                continue
            
            if seller_id and product["seller_id"] != seller_id:
                continue
            
            filtered_products.append(product)

        if sort_by:
            if sort_by == 'price_asc':
                filtered_products.sort(key=lambda p: p['price'])
            elif sort_by == 'price_desc':
                filtered_products.sort(key=lambda p: p['price'], reverse=True)
            elif sort_by == 'rating_asc':
                filtered_products.sort(key=lambda p: p['product_rating'])
            elif sort_by == 'rating_desc':
                filtered_products.sort(key=lambda p: p['product_rating'], reverse=True)

        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_products = filtered_products[start_index:end_index]

        return {"products_status": True, "products": paginated_products}

    def show_cart(self, user: User) -> Dict[str, Union[bool, List[Dict], float]]:
        """
        Shows the contents of the current user's shopping cart.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'cart_status' (bool), 'cart_items' (List[Dict]), and 'total_price' (float).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"cart_status": False, "cart_items": [], "total_price": 0.0}

        cart_items = []
        total_price = 0.0
        for product_id, quantity in user_data.get("cart", {}).items():
            product = self.products.get(product_id)
            if product:
                item_price = product["price"] * quantity
                cart_items.append({
                    "product_id": product_id,
                    "name": product["name"],
                    "quantity": quantity,
                    "price_per_unit": product["price"],
                    "total_item_price": item_price
                })
                total_price += item_price
        
        return {"cart_status": True, "cart_items": cart_items, "total_price": total_price}

    def add_product_to_cart(
        self, product_id: int, quantity: int, clear_cart_first: bool, user: User
    ) -> Dict[str, Union[bool, str]]:
        """
        Adds a product to the current user's cart.

        Args:
            product_id (int): The ID of the product to add.
            quantity (int): The quantity to add.
            clear_cart_first (bool): If True, clears the cart before adding the product.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'add_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"add_status": False, "message": "User not found."}

        product = self.products.get(product_id)
        if not product:
            return {"add_status": False, "message": f"Product with ID {product_id} not found."}
        if product["stock"] < quantity:
            return {"add_status": False, "message": f"Not enough stock for product {product['name']} (available: {product['stock']})."}

        cart = user_data.get("cart", {})
        if clear_cart_first:
            cart = {}
        
        cart[product_id] = cart.get(product_id, 0) + quantity
        self._update_user_data(user, "cart", cart)
        return {"add_status": True, "message": f"{quantity} of {product['name']} added to cart."}

    def update_product_quantity_in_cart(
        self, product_id: int, quantity: int, user: User
    ) -> Dict[str, Union[bool, str]]:
        """
        Updates the quantity of a product in the current user's cart.

        Args:
            product_id (int): The ID of the product to update.
            quantity (int): The new quantity.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'update_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"update_status": False, "message": "User not found."}

        cart = user_data.get("cart", {})
        if product_id not in cart:
            return {"update_status": False, "message": f"Product with ID {product_id} not in cart."}
        
        product = self.products.get(product_id)
        if not product:
            return {"update_status": False, "message": f"Product with ID {product_id} not found."}
        if product["stock"] < quantity:
            return {"update_status": False, "message": f"Not enough stock for product {product['name']} (available: {product['stock']})."}

        if quantity <= 0:
            del cart[product_id]
            message = f"Product {product['name']} removed from cart."
        else:
            cart[product_id] = quantity
            message = f"Quantity of {product['name']} updated to {quantity} in cart."
            
        self._update_user_data(user, "cart", cart)
        return {"update_status": True, "message": message}

    def delete_product_from_cart(
        self, product_id: int, user: User
    ) -> Dict[str, Union[bool, str]]:
        """
        Deletes a product from the current user's cart.

        Args:
            product_id (int): The ID of the product to delete.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'delete_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"delete_status": False, "message": "User not found."}

        cart = user_data.get("cart", {})
        if product_id in cart:
            del cart[product_id]
            self._update_user_data(user, "cart", cart)
            return {"delete_status": True, "message": f"Product with ID {product_id} removed from cart."}
        return {"delete_status": False, "message": f"Product with ID {product_id} not found in cart."}

    def apply_promo_code_to_cart(self, promo_code: str, user: User) -> Dict[str, Union[bool, str]]:
        """
        Applies a promo code to the current user's cart. (Dummy implementation)

        Args:
            promo_code (str): The promo code to apply.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'promo_status' (bool) and 'message' (str).
        """
        if user.email not in self.users:
            return {"promo_status": False, "message": "User not found."}
        
        if promo_code == "DISCOUNT10":
            return {"promo_status": True, "message": f"Promo code '{promo_code}' applied successfully. 10% discount added."}
        return {"promo_status": False, "message": f"Invalid promo code: {promo_code}."}

    def remove_promo_code_from_cart(self, user: User) -> Dict[str, Union[bool, str]]:
        """
        Removes any applied promo code from the current user's cart. (Dummy implementation)

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'promo_status' (bool) and 'message' (str).
        """
        if user.email not in self.users:
            return {"promo_status": False, "message": "User not found."}
        
        return {"promo_status": True, "message": "Promo code removed from cart."}

    def show_wish_list(self, user: User) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows the contents of the current user's wish list.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'wish_list_status' (bool) and 'wish_list_items' (List[Dict]) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"wish_list_status": False, "wish_list_items": []}

        wish_list_items = []
        for product_id, quantity in user_data.get("wish_list", {}).items():
            product = self.products.get(product_id)
            if product:
                wish_list_items.append({
                    "product_id": product_id,
                    "name": product["name"],
                    "quantity": quantity,
                    "price": product["price"]
                })
        
        return {"wish_list_status": True, "wish_list_items": wish_list_items}

    def add_product_to_wish_list(
        self, product_id: int, quantity: int, clear_wish_list_first: bool, user: User
    ) -> Dict[str, Union[bool, str]]:
        """
        Adds a product to the current user's wish list.

        Args:
            product_id (int): The ID of the product to add.
            quantity (int): The quantity to add.
            clear_wish_list_first (bool): If True, clears the wish list before adding the product.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'add_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"add_status": False, "message": "User not found."}

        product = self.products.get(product_id)
        if not product:
            return {"add_status": False, "message": f"Product with ID {product_id} not found."}

        wish_list = user_data.get("wish_list", {})
        if clear_wish_list_first:
            wish_list = {}
        
        wish_list[product_id] = wish_list.get(product_id, 0) + quantity
        self._update_user_data(user, "wish_list", wish_list)
        return {"add_status": True, "message": f"{quantity} of {product['name']} added to wish list."}

    def update_product_quantity_in_wish_list(
        self, product_id: int, quantity: int, user: User
    ) -> Dict[str, Union[bool, str]]:
        """
        Updates the quantity of a product in the current user's wish list.

        Args:
            product_id (int): The ID of the product to update.
            quantity (int): The new quantity.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'update_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"update_status": False, "message": "User not found."}

        wish_list = user_data.get("wish_list", {})
        if product_id not in wish_list:
            return {"update_status": False, "message": f"Product with ID {product_id} not in wish list."}
        
        product = self.products.get(product_id)
        if not product:
            return {"update_status": False, "message": f"Product with ID {product_id} not found."}

        if quantity <= 0:
            del wish_list[product_id]
            message = f"Product {product['name']} removed from wish list."
        else:
            wish_list[product_id] = quantity
            message = f"Quantity of {product['name']} updated to {quantity} in wish list."
            
        self._update_user_data(user, "wish_list", wish_list)
        return {"update_status": True, "message": message}

    def delete_product_from_wish_list(
        self, product_id: int, user: User
    ) -> Dict[str, Union[bool, str]]:
        """
        Deletes a product from the current user's wish list.

        Args:
            product_id (int): The ID of the product to delete.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'delete_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"delete_status": False, "message": "User not found."}

        wish_list = user_data.get("wish_list", {})
        if product_id in wish_list:
            del wish_list[product_id]
            self._update_user_data(user, "wish_list", wish_list)
            return {"delete_status": True, "message": f"Product with ID {product_id} removed from wish list."}
        return {"delete_status": False, "message": f"Product with ID {product_id} not found in wish list."}

    def move_product_from_cart_to_wish_list(
        self, product_id: int, quantity: int, user: User
    ) -> Dict[str, Union[bool, str]]:
        """
        Moves a product from the cart to the wish list.

        Args:
            product_id (int): The ID of the product to move.
            quantity (int): The quantity to move.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'move_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"move_status": False, "message": "User not found."}

        cart = user_data.get("cart", {})
        wish_list = user_data.get("wish_list", {})

        if product_id not in cart or cart[product_id] < quantity:
            return {"move_status": False, "message": f"Product with ID {product_id} not in cart or insufficient quantity."}
        
        cart[product_id] -= quantity
        if cart[product_id] == 0:
            del cart[product_id]

        wish_list[product_id] = wish_list.get(product_id, 0) + quantity

        self._update_user_data(user, "cart", cart)
        self._update_user_data(user, "wish_list", wish_list)
        return {"move_status": True, "message": f"{quantity} of product {product_id} moved from cart to wish list."}

    def move_product_from_wish_list_to_cart(
        self, product_id: int, quantity: int, user: User
    ) -> Dict[str, Union[bool, str]]:
        """
        Moves a product from the wish list to the cart.

        Args:
            product_id (int): The ID of the product to move.
            quantity (int): The quantity to move.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'move_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"move_status": False, "message": "User not found."}

        cart = user_data.get("cart", {})
        wish_list = user_data.get("wish_list", {})

        if product_id not in wish_list or wish_list[product_id] < quantity:
            return {"move_status": False, "message": f"Product with ID {product_id} not in wish list or insufficient quantity."}
        
        wish_list[product_id] -= quantity
        if wish_list[product_id] == 0:
            del wish_list[product_id]

        product = self.products.get(product_id)
        if not product:
            return {"move_status": False, "message": f"Product with ID {product_id} not found."}
        if product["stock"] < quantity:
            return {"move_status": False, "message": f"Not enough stock for product {product['name']} (available: {product['stock']})."}


        cart[product_id] = cart.get(product_id, 0) + quantity

        self._update_user_data(user, "cart", cart)
        self._update_user_data(user, "wish_list", wish_list)
        return {"move_status": True, "message": f"{quantity} of product {product_id} moved from wish list to cart."}

    def clear_cart(self, user: User) -> Dict[str, Union[bool, str]]:
        """
        Clears the current user's shopping cart.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'clear_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"clear_status": False, "message": "User not found."}

        self._update_user_data(user, "cart", {})
        return {"clear_status": True, "message": "Cart cleared successfully."}

    def add_gift_wrapping_to_product(
        self, product_id: int, quantity: int, user: User
    ) -> Dict[str, Union[bool, str]]:
        """
        Adds gift wrapping to a product in the cart. (Dummy implementation)

        Args:
            product_id (int): The ID of the product.
            quantity (int): The quantity to apply gift wrapping to.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'gift_wrapping_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"gift_wrapping_status": False, "message": "User not found."}
        
        cart = user_data.get("cart", {})
        if product_id not in cart or cart[product_id] < quantity:
            return {"gift_wrapping_status": False, "message": f"Product {product_id} not in cart or insufficient quantity."}
        
        product = self.products.get(product_id)
        if not product:
            return {"gift_wrapping_status": False, "message": f"Product with ID {product_id} not found."}
            
        return {"gift_wrapping_status": True, "message": f"Gift wrapping added for {quantity} of {product['name']}."}

    def remove_gift_wrapping_from_product(
        self, product_id: int, user: User
    ) -> Dict[str, Union[bool, str]]:
        """
        Removes gift wrapping from a product in the cart. (Dummy implementation)

        Args:
            product_id (int): The ID of the product.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'gift_wrapping_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"gift_wrapping_status": False, "message": "User not found."}
        
        cart = user_data.get("cart", {})
        if product_id not in cart:
            return {"gift_wrapping_status": False, "message": f"Product {product_id} not in cart."}
            
        product = self.products.get(product_id)
        if not product:
            return {"gift_wrapping_status": False, "message": f"Product with ID {product_id} not found."}

        return {"gift_wrapping_status": True, "message": f"Gift wrapping removed for {product['name']}."}

    def clear_wish_list(self, user: User) -> Dict[str, Union[bool, str]]:
        """
        Clears the current user's wish list.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'clear_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"clear_status": False, "message": "User not found."}

        self._update_user_data(user, "wish_list", {})
        return {"clear_status": True, "message": "Wish list cleared successfully."}

    def show_orders(
        self, user: User, query: str = "", page_index: int = 1, page_limit: int = 10, sort_by: str | None = None
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows the current user's past orders, optionally filtered and sorted.

        Args:
            query (str): Optional search query to filter orders.
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.
            sort_by (str | None): Field to sort by (e.g., 'date_asc', 'date_desc', 'total_asc', 'total_desc').
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'orders_status' (bool) and 'orders' (List[Dict]) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"orders_status": False, "orders": []}

        all_orders = list(user_data.get("orders", {}).values())
        filtered_orders = [
            order for order in all_orders
            if query.lower() in str(order["order_id"]).lower() or
               query.lower() in order["status"].lower() or
               any(query.lower() in p["name"].lower() for p in order["products"].values())
        ]

        if sort_by:
            if sort_by == 'date_asc':
                filtered_orders.sort(key=lambda o: o['order_date'])
            elif sort_by == 'date_desc':
                filtered_orders.sort(key=lambda o: o['order_date'], reverse=True)
            elif sort_by == 'total_asc':
                filtered_orders.sort(key=lambda o: o['total_amount'])
            elif sort_by == 'total_desc':
                filtered_orders.sort(key=lambda o: o['total_amount'], reverse=True)

        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_orders = filtered_orders[start_index:end_index]

        return {"orders_status": True, "orders": paginated_orders}

    def show_order(self, order_id: int, user: User) -> Dict[str, Union[bool, Dict]]:
        """
        Shows the details of a specific order for the current user.

        Args:
            order_id (int): The ID of the order.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'order_status' (bool) and 'order' (Dict) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"order_status": False, "order": {}}

        order = user_data.get("orders", {}).get(order_id)
        if order:
            return {"order_status": True, "order": order}
        return {"order_status": False, "order": {}}

    def place_order(
        self, payment_card_id: int, address_id: int, user: User
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Places an order using the items in the current user's cart.

        Args:
            payment_card_id (int): The ID of the payment card to use.
            address_id (int): The ID of the address to ship to.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'order_status' (bool), 'message' (str), and 'order_id' (int) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"order_status": False, "message": "User not found."}

        cart = user_data.get("cart", {})
        if not cart:
            return {"order_status": False, "message": "Cart is empty. Cannot place an order."}

        payment_card = user_data.get("payment_cards", {}).get(payment_card_id)
        if not payment_card:
            return {"order_status": False, "message": f"Payment card with ID {payment_card_id} not found."}

        address = user_data.get("addresses", {}).get(address_id)
        if not address:
            return {"order_status": False, "message": f"Address with ID {address_id} not found."}

        new_order_id = self.order_counter + 1
        self.order_counter = new_order_id

        order_products = {}
        total_amount = 0.0
        for product_id, quantity in cart.items():
            product = self.products.get(product_id)
            if product and product["stock"] >= quantity:
                order_products[product_id] = {
                    "product_id": product_id,
                    "name": product["name"],
                    "quantity": quantity,
                    "price": product["price"]
                }
                total_amount += product["price"] * quantity
                # Deduct from stock
                self.products[product_id]["stock"] -= quantity
            else:
                return {"order_status": False, "message": f"Insufficient stock for product {product_id} or product not found."}

        new_order = {
            "order_id": new_order_id,
            "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_amount": total_amount,
            "status": "pending",
            "products": order_products,
            "payment_card_used": payment_card,
            "shipping_address": address
        }
        
        user_orders = user_data.get("orders", {})
        user_orders[new_order_id] = new_order
        self._update_user_data(user, "orders", user_orders)
        self._update_user_data(user, "cart", {}) # Clear cart after order

        return {"order_status": True, "message": f"Order {new_order_id} placed successfully!", "order_id": new_order_id}

    def show_payment_cards(self, user: User) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows the current user's registered payment cards.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'cards_status' (bool) and 'payment_cards' (List[Dict]) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"cards_status": False, "payment_cards": []}
        
        return {"cards_status": True, "payment_cards": list(user_data.get("payment_cards", {}).values())}

    def add_payment_card(
        self,
        card_name: str,
        owner_name: str,
        card_number: int,
        expiry_year: int,
        expiry_month: int,
        cvv_number: int,
        user: User,
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Adds a new payment card for the current user.

        Args:
            card_name (str): A name for the card (e.g., "My Visa").
            owner_name (str): The name of the card owner.
            card_number (int): The card number.
            expiry_year (int): The expiry year of the card.
            expiry_month (int): The expiry month of the card.
            cvv_number (int): The CVV number of the card.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'add_status' (bool), 'message' (str), and 'payment_card_id' (int) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"add_status": False, "message": "User not found."}

        new_card_id = self.payment_card_counter + 1
        self.payment_card_counter = new_card_id

        new_card = {
            "card_name": card_name,
            "owner_name": owner_name,
            "card_number": card_number,
            "expiry_year": expiry_year,
            "expiry_month": expiry_month,
            "cvv_number": cvv_number,
            "card_id": new_card_id # Add card_id to the card details
        }
        
        user_payment_cards = user_data.get("payment_cards", {})
        user_payment_cards[new_card_id] = new_card
        self._update_user_data(user, "payment_cards", user_payment_cards)
        
        return {"add_status": True, "message": f"Payment card '{card_name}' added successfully.", "payment_card_id": new_card_id}

    def delete_payment_card(self, payment_card_id: int, user: User) -> Dict[str, Union[bool, str]]:
        """
        Deletes a payment card for the current user.

        Args:
            payment_card_id (int): The ID of the payment card to delete.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'delete_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"delete_status": False, "message": "User not found."}

        user_payment_cards = user_data.get("payment_cards", {})
        if payment_card_id in user_payment_cards:
            del user_payment_cards[payment_card_id]
            self._update_user_data(user, "payment_cards", user_payment_cards)
            return {"delete_status": True, "message": f"Payment card with ID {payment_card_id} deleted successfully."}
        return {"delete_status": False, "message": f"Payment card with ID {payment_card_id} not found."}

    def show_addresses(self, user: User) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows the current user's registered addresses.

        Args:
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'addresses_status' (bool) and 'addresses' (List[Dict]) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"addresses_status": False, "addresses": []}
        
        return {"addresses_status": True, "addresses": list(user_data.get("addresses", {}).values())}

    def add_address(
        self,
        name: str,
        street_address: str,
        city: str,
        state: str,
        country: str,
        zip_code: int,
        user: User,
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Adds a new address for the current user.

        Args:
            name (str): A name for the address (e.g., "Home", "Work").
            street_address (str): The street address.
            city (str): The city.
            state (str): The state.
            country (str): The country.
            zip_code (int): The zip code.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'add_status' (bool), 'message' (str), and 'address_id' (int) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"add_status": False, "message": "User not found."}

        new_address_id = self.address_counter + 1
        self.address_counter = new_address_id

        new_address = {
            "name": name,
            "street_address": street_address,
            "city": city,
            "state": state,
            "country": country,
            "zip_code": zip_code,
            "address_id": new_address_id # Add address_id to the address details
        }
        
        user_addresses = user_data.get("addresses", {})
        user_addresses[new_address_id] = new_address
        self._update_user_data(user, "addresses", user_addresses)
        
        return {"add_status": True, "message": f"Address '{name}' added successfully.", "address_id": new_address_id}

    def delete_address(self, address_id: int, user: User) -> Dict[str, Union[bool, str]]:
        """
        Deletes an address for the current user.

        Args:
            address_id (int): The ID of the address to delete.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'delete_status' (bool) and 'message' (str).
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"delete_status": False, "message": "User not found."}

        user_addresses = user_data.get("addresses", {})
        if address_id in user_addresses:
            del user_addresses[address_id]
            self._update_user_data(user, "addresses", user_addresses)
            return {"delete_status": True, "message": f"Address with ID {address_id} deleted successfully."}
        return {"delete_status": False, "message": f"Address with ID {address_id} not found."}

    def show_product_reviews(
        self,
        product_id: int,
        query: str = "",
        user_email: EmailStr | None = None,
        page_index: int = 1,
        page_limit: int = 10,
        min_rating: int = 1,
        max_rating: int = 5,
        is_verified: bool | None = None,
        sort_by: str | None = None,
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows reviews for a specific product, with filtering and sorting options.

        Args:
            product_id (int): The ID of the product.
            query (str): Optional search query for review comments.
            user_email (EmailStr | None): Filter by the email of the reviewer.
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.
            min_rating (int): Minimum rating for reviews.
            max_rating (int): Maximum rating for reviews.
            is_verified (bool | None): Filter by verified purchase status.
            sort_by (str | None): Field to sort by (e.g., 'rating_asc', 'rating_desc').

        Returns:
            Dict: A dictionary containing 'reviews_status' (bool) and 'reviews' (List[Dict]) if successful.
        """
        product_reviews = self.product_reviews.get(product_id, [])
        filtered_reviews = []
        for review in product_reviews:
            if query and query.lower() not in review["comment"].lower():
                continue
            if user_email and review["user_email"] != str(user_email):
                continue
            if not (min_rating <= review["rating"] <= max_rating):
                continue
            if is_verified is not None and review["is_verified"] != is_verified:
                continue
            filtered_reviews.append(review)

        if sort_by:
            if sort_by == 'rating_asc':
                filtered_reviews.sort(key=lambda r: r['rating'])
            elif sort_by == 'rating_desc':
                filtered_reviews.sort(key=lambda r: r['rating'], reverse=True)

        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_reviews = filtered_reviews[start_index:end_index]

        return {"reviews_status": True, "reviews": paginated_reviews}

    def show_product_questions(
        self,
        product_id: int,
        query: str = "",
        user_email: EmailStr | None = None,
        page_index: int = 1,
        page_limit: int = 10,
        sort_by: str | None = None,
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows questions for a specific product, with filtering and sorting options.

        Args:
            product_id (int): The ID of the product.
            query (str): Optional search query for question text.
            user_email (EmailStr | None): Filter by the email of the questioner.
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.
            sort_by (str | None): Field to sort by (e.g., 'date_asc', 'date_desc').

        Returns:
            Dict: A dictionary containing 'questions_status' (bool) and 'questions' (List[Dict]) if successful.
        """
        product_questions = self.product_questions.get(product_id, [])
        filtered_questions = []
        for question in product_questions:
            if query and query.lower() not in question["question"].lower():
                continue
            if user_email and question["user_email"] != str(user_email):
                continue
            filtered_questions.append(question)

        # Dummy sorting as no date/time for questions in default state
        if sort_by:
            pass 

        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_questions = filtered_questions[start_index:end_index]

        return {"questions_status": True, "questions": paginated_questions}

    def show_product_Youtubes( # Renamed from show_product_answers to show_product_Youtubes as per the prompt
        self,
        question_id: int,
        query: str = "",
        user_email: EmailStr | None = None,
        is_verified: bool | None = None,
        page_index: int = 1,
        page_limit: int = 10,
        sort_by: str | None = None,
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows answers (Youtubes) for a specific product question, with filtering and sorting options.
        NOTE: This is a dummy implementation and "Youtubes" are treated as answers here.

        Args:
            question_id (int): The ID of the product question.
            query (str): Optional search query for answer text.
            user_email (EmailStr | None): Filter by the email of the answerer.
            is_verified (bool | None): Filter by verified status of the answerer (dummy).
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.
            sort_by (str | None): Field to sort by (dummy).

        Returns:
            Dict: A dictionary containing 'youtubes_status' (bool) and 'youtubes' (List[Dict]) if successful.
        """
        all_answers = []
        for product_id, questions in self.product_questions.items():
            for question in questions:
                if question["question_id"] == question_id:
                    # In a real scenario, answers would be stored separately or within the question
                    # For dummy purposes, let's create a dummy answer if none exist
                    if not question["answers"]:
                        question["answers"].append({
                            "answer_id": 1,
                            "user_email": "seller@example.com",
                            "answer": "Yes, it comes with Windows 11.",
                            "is_verified": True
                        })
                    all_answers = question["answers"]
                    break
            if all_answers:
                break

        filtered_answers = []
        for answer in all_answers:
            if query and query.lower() not in answer["answer"].lower():
                continue
            if user_email and answer["user_email"] != str(user_email):
                continue
            if is_verified is not None and answer.get("is_verified", False) != is_verified:
                continue
            filtered_answers.append(answer)

        # Dummy sorting as no date/time for answers in default state
        if sort_by:
            pass

        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_answers = filtered_answers[start_index:end_index]

        return {"youtubes_status": True, "youtubes": paginated_answers}


    def show_returns(
        self,
        user: User,
        order_id: int | None = None,
        page_index: int = 1,
        page_limit: int = 10,
        sort_by: str = "date_desc",
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows the current user's product returns, optionally filtered by order and sorted.

        Args:
            order_id (int | None): Optional order ID to filter returns.
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.
            sort_by (str): Field to sort by (e.g., 'date_asc', 'date_desc').
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'returns_status' (bool) and 'returns' (List[Dict]) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"returns_status": False, "returns": []}

        all_returns = list(user_data.get("returns", {}).values())
        filtered_returns = [
            ret for ret in all_returns
            if order_id is None or ret["order_id"] == order_id
        ]

        if sort_by == 'date_asc':
            filtered_returns.sort(key=lambda r: r['return_date'])
        elif sort_by == 'date_desc':
            filtered_returns.sort(key=lambda r: r['return_date'], reverse=True)

        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_returns = filtered_returns[start_index:end_index]

        return {"returns_status": True, "returns": paginated_returns}

    def show_return(self, return_id: int, user: User) -> Dict[str, Union[bool, Dict]]:
        """
        Shows the details of a specific product return for the current user.

        Args:
            return_id (int): The ID of the return.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'return_status' (bool) and 'return_details' (Dict) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"return_status": False, "return_details": {}}
        
        return_details = user_data.get("returns", {}).get(return_id)
        if return_details:
            return {"return_status": True, "return_details": return_details}
        return {"return_status": False, "return_details": {}}

    def show_return_deliverers(self) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows available deliverers for product returns.

        Returns:
            Dict: A dictionary containing 'deliverers_status' (bool) and 'deliverers' (List[Dict]) if successful.
        """
        return {"deliverers_status": True, "deliverers": list(self.deliverers.values())}

    def initiate_return(
        self,
        order_id: int,
        product_id: int,
        deliverer_id: int,
        quantity: int,
        user: User,
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Initiates a product return for the current user.

        Args:
            order_id (int): The ID of the original order.
            product_id (int): The ID of the product to return.
            deliverer_id (int): The ID of the selected deliverer.
            quantity (int): The quantity to return.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'initiate_status' (bool), 'message' (str), and 'return_id' (int) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"initiate_status": False, "message": "User not found."}

        order = user_data.get("orders", {}).get(order_id)
        if not order:
            return {"initiate_status": False, "message": f"Order with ID {order_id} not found."}

        product_in_order = order["products"].get(product_id)
        if not product_in_order or product_in_order["quantity"] < quantity:
            return {"initiate_status": False, "message": f"Product {product_id} not found in order {order_id} or insufficient quantity."}

        deliverer = self.deliverers.get(deliverer_id)
        if not deliverer:
            return {"initiate_status": False, "message": f"Deliverer with ID {deliverer_id} not found."}

        new_return_id = self.return_counter + 1
        self.return_counter = new_return_id

        new_return = {
            "return_id": new_return_id,
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "return_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending",
            "deliverer": deliverer
        }

        user_returns = user_data.get("returns", {})
        user_returns[new_return_id] = new_return
        self._update_user_data(user, "returns", user_returns)

        return {"initiate_status": True, "message": f"Return {new_return_id} initiated successfully.", "return_id": new_return_id}

    def show_prime_plans(self) -> Dict[str, Union[bool, Dict]]:
        """
        Shows available Amazon Prime subscription plans.

        Returns:
            Dict: A dictionary containing 'prime_plans_status' (bool) and 'prime_plans' (Dict) if successful.
        """
        return {"prime_plans_status": True, "prime_plans": self.prime_plans}

    def subscribe_prime(
        self, payment_card_id: int, duration: Literal["monthly", "yearly"], user: User
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Subscribes the current user to an Amazon Prime plan.

        Args:
            payment_card_id (int): The ID of the payment card to use.
            duration (Literal["monthly", "yearly"]): The duration of the subscription.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'subscribe_status' (bool), 'message' (str), and 'prime_subscription_id' (int) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"subscribe_status": False, "message": "User not found."}

        payment_card = user_data.get("payment_cards", {}).get(payment_card_id)
        if not payment_card:
            return {"subscribe_status": False, "message": f"Payment card with ID {payment_card_id} not found."}

        if duration not in self.prime_plans:
            return {"subscribe_status": False, "message": f"Invalid Prime plan duration: {duration}."}

        new_subscription_id = self.prime_subscription_counter + 1
        self.prime_subscription_counter = new_subscription_id

        start_date = datetime.now()
        if duration == "monthly":
            end_date = start_date + timedelta(days=30)
        elif duration == "yearly":
            end_date = start_date + timedelta(days=365)

        new_subscription = {
            "subscription_id": new_subscription_id,
            "plan": duration,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "status": "active",
            "payment_card_used": payment_card["card_name"]
        }

        user_prime_subscriptions = user_data.get("prime_subscriptions", {})
        user_prime_subscriptions[new_subscription_id] = new_subscription
        self._update_user_data(user, "prime_subscriptions", user_prime_subscriptions)

        return {"subscribe_status": True, "message": f"Successfully subscribed to {duration} Prime plan.", "prime_subscription_id": new_subscription_id}

    def show_prime_subscriptions(
        self, user: User, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows the current user's Amazon Prime subscriptions.

        Args:
            page_index (int): Page index for pagination.
            page_limit (int): Number of results per page.
            user (User): The current user object.

        Returns:
            Dict: A dictionary containing 'subscriptions_status' (bool) and 'prime_subscriptions' (List[Dict]) if successful.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"subscriptions_status": False, "prime_subscriptions": []}

        all_subscriptions = list(user_data.get("prime_subscriptions", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_subscriptions = all_subscriptions[start_index:end_index]

        return {"subscriptions_status": True, "prime_subscriptions": paginated_subscriptions}