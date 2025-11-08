import uuid
from typing import Dict, List, Union, Literal, Any
from datetime import datetime, timedelta
from copy import deepcopy
from state_loader import load_default_state

DEFAULT_STATE = load_default_state("AmazonApis")

class AmazonApis:
    def __init__(self):
        self.state = deepcopy(DEFAULT_STATE)

    def _get_user_data(self, user_id: str) -> Union[Dict, None]:
        """
        Retrieves user data using user_id.
        """
        return self.state["users"].get(user_id)

    def _update_user_data(self, user_id: str, key: str, value: Any):
        """
        Updates a specific key in user data using user_id.
        """
        if user_id in self.state["users"]:
            self.state["users"][user_id][key] = value

    def register_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        phone_number: str) -> Dict[str, Union[bool, str]]:
        """
        Registers a new user with the system by creating a unique user ID and storing their information.
        Args:
            first_name (str): The user's first name.
            last_name (str): The user's last name.
            email (str): The user's email address (must be unique).
            password (str): The user's password (not securely stored in this implementation).
        Returns:
            Dict: A dictionary containing registration status and message. If successful,
                  includes the new user ID. If failed, indicates the reason for failure.
        """
        for user_id, user_data in self.state["users"].items():
            if user_data["email"] == email:
                return {"register_status": False, "message": "User with this email already exists."}

        new_user_id = str(uuid.uuid4())
        self.state["users"][new_user_id] = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "phone_number": phone_number,
            "balance": 0.0,
            "payment_cards": {},
            "addresses": {},
            "cart": {},
            "wish_list": {},
            "orders": {},
            "prime_subscriptions": {},
            "returns": {},
        }
        return {"register_status": True, "message": f"User {email} registered successfully with ID {new_user_id}."}

    def login_user(self, email: str, password: str) -> Dict[str, Union[bool, str]]:
        """
        Authenticates a user and sets them as the current active user in the system.
        Args:
            email (str): The email address of the user attempting to login.
            password (str): The password for authentication (basic implementation).
        Returns:
            Dict: A dictionary containing login status and message. If successful,
                  sets the current user session.
        """
        for user_id, user_data in self.state["users"].items():
            if user_data["email"] == email:
                self.state["current_user"] = user_id
                return {"login_status": True, "message": f"User {email} logged in successfully."}
        return {"login_status": False, "message": "Invalid email or password."}

    def show_profile(self, user_id: str) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves the complete profile information for a specified user.
        Args:
            user_id (str): The unique identifier of the user whose profile to retrieve.
        Returns:
            Dict: A dictionary containing profile status and the user's profile data if found.
                  Returns an empty profile if user is not found.
        """
        user_data = self._get_user_data(user_id)
        if user_data:
            return {"profile_status": True, "profile": user_data}
        return {"profile_status": False, "profile": {}}

    def show_account(self, user_id: str) -> Dict[str, Union[bool, str, Dict]]:
        """
        Retrieves account-specific information including balance, payment cards, and addresses.
        Args:
            user_id (str): The unique identifier of the user whose account details to retrieve.
        Returns:
            Dict: A dictionary containing account status, message, and account details including
                  balance, payment cards, and addresses if the user is found.
        """
        user_data = self._get_user_data(user_id)
        if user_data:
            return {
                "account_status": True,
                "message": f"Account details for {user_data.get('email', 'N/A')}",
                "account": {
                    "balance": user_data["balance"],
                    "payment_cards": list(user_data["payment_cards"].values()),
                    "addresses": list(user_data["addresses"].values()),
                },
            }
        return {"account_status": False, "message": "User not found."}

    def delete_account(self, user_id: str) -> Dict[str, Union[bool, str]]:
        """
        Permanently removes a user account from the system.
        Args:
            user_id (str): The unique identifier of the user account to delete.
        Returns:
            Dict: A dictionary containing deletion status and message. Also clears the current
                  user session if the deleted user was currently logged in.
        """
        if user_id in self.state["users"]:
            del self.state["users"][user_id]
            if self.state["current_user"] == user_id:
                self.state["current_user"] = None
            return {"delete_status": True, "message": f"Account for user ID {user_id} deleted successfully."}
        return {"delete_status": False, "message": "User not found."}

    def add_payment_card(
        self,
        user_id: str,
        card_name: str,
        owner_name: str,
        card_number: int,
        expiry_year: int,
        expiry_month: int,
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Adds a new payment card to the user's account with secure storage practices.
        Args:
            user_id (str): The unique identifier of the user adding the payment card.
            card_name (str): A descriptive name for the card (e.g., "Personal Visa").
            owner_name (str): The name of the card owner as it appears on the card.
            card_number (int): The full card number (only last 4 digits are stored).
            expiry_year (int): The expiration year of the card.
            expiry_month (int): The expiration month of the card.
        Returns:
            Dict: A dictionary containing add card status, message, and the newly generated
                  card ID if successful.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"add_card_status": False, "message": "User not found."}

        new_card_id = str(uuid.uuid4())
        user_payment_cards = user_data.get("payment_cards", {})
        user_payment_cards[new_card_id] = {
            "card_name": card_name,
            "owner_name": owner_name,
            "card_number_last4": str(card_number)[-4:],
            "expiry_year": expiry_year,
            "expiry_month": expiry_month,
        }
        self._update_user_data(user_id, "payment_cards", user_payment_cards)
        return {"add_card_status": True, "message": "Payment card added successfully.", "card_id": new_card_id}

    def remove_payment_card(self, user_id: str, card_id: str) -> Dict[str, Union[bool, str]]:
        """
        Removes a payment card from the user's account.
        Args:
            user_id (str): The unique identifier of the user removing the payment card.
            card_id (str): The unique identifier of the payment card to remove.
        Returns:
            Dict: A dictionary containing removal status and message indicating whether
                  the card was successfully removed or not found.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"remove_card_status": False, "message": "User not found."}

        user_payment_cards = user_data.get("payment_cards", {})
        if card_id in user_payment_cards:
            del user_payment_cards[card_id]
            self._update_user_data(user_id, "payment_cards", user_payment_cards)
            return {"remove_card_status": True, "message": f"Payment card {card_id} removed successfully."}
        return {"remove_card_status": False, "message": "Payment card not found."}

    def show_payment_cards(
        self, user_id: str, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves a paginated list of the user's payment cards.
        Args:
            user_id (str): The unique identifier of the user whose payment cards to retrieve.
            page_index (int, optional): The page number for pagination (default: 1).
            page_limit (int, optional): The number of items per page (default: 10).
        Returns:
            Dict: A dictionary containing cards status and a list of payment card objects
                  with pagination applied.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"cards_status": False, "payment_cards": []}

        all_cards = list(user_data.get("payment_cards", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_cards = all_cards[start_index:end_index]

        return {"cards_status": True, "payment_cards": paginated_cards}

    def add_address(
        self,
        user_id: str,
        name: str,
        street_address: str,
        city: str,
        state: str,
        country: str,
        zip_code: int,
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Adds a new shipping address to the user's account.
        Args:
            user_id (str): The unique identifier of the user adding the address.
            name (str): A descriptive name for the address (e.g., "Home", "Work").
            street_address (str): The street address including house number and street name.
            city (str): The city name.
            state (str): The state or province.
            country (str): The country name.
            zip_code (int): The postal or zip code.
        Returns:
            Dict: A dictionary containing add address status, message, and the newly generated
                  address ID if successful.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"add_address_status": False, "message": "User not found."}

        new_address_id = str(uuid.uuid4())
        user_addresses = user_data.get("addresses", {})
        user_addresses[new_address_id] = {
            "name": name,
            "street_address": street_address,
            "city": city,
            "state": state,
            "country": country,
            "zip_code": zip_code,
        }
        self._update_user_data(user_id, "addresses", user_addresses)
        return {"add_address_status": True, "message": "Address added successfully.", "address_id": new_address_id}

    def remove_address(self, user_id: str, address_id: str) -> Dict[str, Union[bool, str]]:
        """
        Removes a shipping address from the user's account.
        Args:
            user_id (str): The unique identifier of the user removing the address.
            address_id (str): The unique identifier of the address to remove.
        Returns:
            Dict: A dictionary containing removal status and message indicating whether
                  the address was successfully removed or not found.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"remove_address_status": False, "message": "User not found."}

        user_addresses = user_data.get("addresses", {})
        if address_id in user_addresses:
            del user_addresses[address_id]
            self._update_user_data(user_id, "addresses", user_addresses)
            return {"remove_address_status": True, "message": f"Address {address_id} removed successfully."}
        return {"remove_address_status": False, "message": "Address not found."}

    def show_addresses(
        self, user_id: str, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves a paginated list of the user's shipping addresses.
        Args:
            user_id (str): The unique identifier of the user whose addresses to retrieve.
            page_index (int, optional): The page number for pagination (default: 1).
            page_limit (int, optional): The number of items per page (default: 10).
        Returns:
            Dict: A dictionary containing addresses status and a list of address objects
                  with pagination applied.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"addresses_status": False, "addresses": []}

        all_addresses = list(user_data.get("addresses", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_addresses = all_addresses[start_index:end_index]

        return {"addresses_status": True, "addresses": paginated_addresses}

    def add_to_cart(self, user_id: str, product_id: str, quantity: int) -> Dict[str, Union[bool, str]]:
        """
        Adds a product to the user's shopping cart with specified quantity.
        Args:
            user_id (str): The unique identifier of the user adding to cart.
            product_id (str): The unique identifier of the product to add.
            quantity (int): The quantity of the product to add.
        Returns:
            Dict: A dictionary containing add to cart status and message. Validates product
                  existence and available stock before adding.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"cart_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"cart_status": False, "message": "Product not found."}
        if self.state["products"][product_id]["stock"] < quantity:
            return {"cart_status": False, "message": "Not enough stock."}

        user_cart = user_data.get("cart", {})
        user_cart[product_id] = user_cart.get(product_id, 0) + quantity
        self._update_user_data(user_id, "cart", user_cart)
        return {"cart_status": True, "message": "Product added to cart."}

    def remove_from_cart(self, user_id: str, product_id: str) -> Dict[str, Union[bool, str]]:
        """
        Removes a product completely from the user's shopping cart.
        Args:
            user_id (str): The unique identifier of the user removing from cart.
            product_id (str): The unique identifier of the product to remove.
        Returns:
            Dict: A dictionary containing removal status and message indicating whether
                  the product was successfully removed from the cart.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"cart_status": False, "message": "User not found."}

        user_cart = user_data.get("cart", {})
        if product_id in user_cart:
            del user_cart[product_id]
            self._update_user_data(user_id, "cart", user_cart)
            return {"cart_status": True, "message": "Product removed from cart."}
        return {"cart_status": False, "message": "Product not found in cart."}

    def update_cart_item_quantity(self, user_id: str, product_id: str, quantity: int) -> Dict[str, Union[bool, str]]:
        """
        Updates the quantity of a specific product in the user's shopping cart.
        Args:
            user_id (str): The unique identifier of the user updating cart quantity.
            product_id (str): The unique identifier of the product to update.
            quantity (int): The new quantity for the product (removes if quantity <= 0).
        Returns:
            Dict: A dictionary containing update status and message. Validates product
                  existence and available stock before updating.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"cart_status": False, "message": "User not found."}

        user_cart = user_data.get("cart", {})
        if product_id not in user_cart:
            return {"cart_status": False, "message": "Product not in cart."}
        if self.state["products"][product_id]["stock"] < quantity:
            return {"cart_status": False, "message": "Not enough stock."}

        if quantity <= 0:
            del user_cart[product_id]
        else:
            user_cart[product_id] = quantity
        self._update_user_data(user_id, "cart", user_cart)
        return {"cart_status": True, "message": "Cart updated."}

    def show_cart(self, user_id: str) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves the complete contents of the user's shopping cart with product details.
        Args:
            user_id (str): The unique identifier of the user whose cart to retrieve.
        Returns:
            Dict: A dictionary containing cart status and a list of cart items with
                  product information, quantities, and total prices.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"cart_status": False, "cart": []}

        cart_items = []
        for product_id, quantity in user_data.get("cart", {}).items():
            if product_id == "promo_code":
                continue
            product_info = self.state["products"].get(product_id)
            if product_info:
                cart_items.append(
                    {
                        "product_id": product_id,
                        "name": product_info["name"],
                        "price": product_info["price"],
                        "quantity": quantity,
                        "total": product_info["price"] * quantity,
                    }
                )
        return {"cart_status": True, "cart": cart_items}

    def apply_promo_code_to_cart(self, promo_code: str, user_id: str) -> Dict[str, Union[bool, str, float]]:
        """
        Applies a promotional code to the user's shopping cart, validating eligibility and calculating discounts.
        Args:
            promo_code (str): The promotional code to apply.
            user_id (str): The unique identifier of the user applying the promo code.
        Returns:
            Dict: A dictionary containing promo status, message, discount amount, and new total.
                  Validates code existence, activation status, expiration, and minimum purchase requirements.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"promo_status": False, "message": "User not found."}
        
        cart_total = 0.0
        if not user_data.get("cart"):
            return {"promo_status": False, "message": "Your cart is empty."}

        if user_data.get("cart").get("promo_code"):
            return {"promo_status": True, "message": "Prompo code already applied to cart."}

        for product_id, quantity in user_data.get("cart", {}).items():
            product_info = self.state["products"].get(product_id)
            if product_info:
                cart_total += product_info["price"] * quantity

        found_promo = None
        for promo_details in self.state.get("promotions", {}).values():
            if promo_details.get("code") == promo_code:
                found_promo = promo_details
                break

        if not found_promo:
            return {"promo_status": False, "message": "Invalid promo code."}

        if not found_promo.get("is_active", False):
            return {"promo_status": False, "message": "This promo code is not currently active."}

        expiry_date = datetime.strptime(found_promo["expiry_date"], "%Y-%m-%d")
        if datetime.now() > expiry_date:
            return {"promo_status": False, "message": "This promo code has expired."}

        min_purchase = found_promo.get("min_purchase_amount", 0.0)
        if cart_total < min_purchase:
            return {"promo_status": False, "message": f"A minimum purchase of ${min_purchase:.2f} is required for this code."}

        discount_percentage = found_promo.get("discount_percentage", 0) / 100.0
        
        discount_amount = cart_total * discount_percentage
        new_total = cart_total - discount_amount

        user_cart = user_data.get("cart", {})
        user_cart["promo_code"] = promo_code
        self._update_user_data(user_id, "cart", user_cart)

        return {
            "promo_status": True,
            "message": f"Promo code '{promo_code}' applied. Discount: ${discount_amount:.2f}",
            "discount_amount": discount_amount,
            "new_total": new_total,
        }

    def remove_promo_code_from_cart(self, user_id: str) -> Dict[str, Union[bool, str]]:
        """
        Removes any applied promotional code from the user's shopping cart.
        Args:
            user_id (str): The unique identifier of the user removing the promo code.
        Returns:
            Dict: A dictionary containing promo status and message indicating successful removal.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"promo_status": False, "message": "User not found."}

        return {"promo_status": True, "message": "Promo code removed from cart."}

    def checkout(
        self, user_id: str, delivery_address_id: str, payment_card_id: str, promo_code: Union[str, None] = None
    ) -> Dict[str, Union[bool, str, Dict]]:
        """
        Processes the checkout operation, creating an order, updating inventory, and processing payment.
        Args:
            user_id (str): The unique identifier of the user checking out.
            delivery_address_id (str): The unique identifier of the delivery address to use.
            payment_card_id (str): The unique identifier of the payment card to use.
            promo_code (Union[str, None], optional): An optional promotional code to apply (default: None).
        Returns:
            Dict: A dictionary containing checkout status, message, and order details if successful.
                  Validates cart contents, address, payment method, stock availability, and user balance.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"checkout_status": False, "message": "User not found."}

        user_cart = user_data.get("cart", {})
        if not user_cart:
            return {"checkout_status": False, "message": "Cart is empty."}

        if delivery_address_id not in user_data.get("addresses", {}):
            return {"checkout_status": False, "message": "Delivery address not found."}
        if payment_card_id not in user_data.get("payment_cards", {}):
            return {"checkout_status": False, "message": "Payment card not found."}

        total_amount = 0.0
        products_in_order = {}
        for product_id, quantity in user_cart.items():
            if product_id == "promo_code":
                continue
            product_info = self.state["products"].get(product_id)
            if not product_info or product_info["stock"] < quantity:
                return {"checkout_status": False, "message": f"Not enough stock for product ID {product_id}."}
            total_amount += product_info["price"] * quantity
            products_in_order[product_id] = quantity

        if promo_code == "WELCOME10":
            total_amount *= 0.90

        if user_data["balance"] < total_amount:
            return {"checkout_status": False, "message": "Insufficient balance."}

        for product_id, quantity in products_in_order.items():
            self.state["products"][product_id]["stock"] -= quantity
        user_data["balance"] -= total_amount

        new_order_id = str(uuid.uuid4())
        user_orders = user_data.get("orders", {})
        user_orders[new_order_id] = {
            "order_date": datetime.now().strftime("%Y-%m-%d"),
            "total_amount": total_amount,
            "products": products_in_order,
            "delivery_address_id": delivery_address_id,
            "payment_card_id": payment_card_id,
            "status": "pending",
            "promo_code_applied": promo_code,
            "tracking_number": f"TRK{str(uuid.uuid4())[:8].upper()}"
        }
        self._update_user_data(user_id, "orders", user_orders)
        self._update_user_data(user_id, "balance", user_data["balance"])
        self._update_user_data(user_id, "cart", {})

        return {
            "checkout_status": True,
            "message": "Checkout successful. Order placed.",
            "order": user_orders[new_order_id],
        }

    def show_orders(
        self, user_id: str, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves a paginated list of the user's order history.
        Args:
            user_id (str): The unique identifier of the user whose orders to retrieve.
            page_index (int, optional): The page number for pagination (default: 1).
            page_limit (int, optional): The number of items per page (default: 10).
        Returns:
            Dict: A dictionary containing orders status and a list of order objects
                  with pagination applied.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"orders_status": False, "orders": []}

        all_orders = list(user_data.get("orders", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_orders = all_orders[start_index:end_index]

        return {"orders_status": True, "orders": paginated_orders}

    def add_to_wish_list(self, user_id: str, product_id: str) -> Dict[str, Union[bool, str]]:
        """
        Adds a product to the user's wish list for future reference.
        Args:
            user_id (str): The unique identifier of the user adding to wish list.
            product_id (str): The unique identifier of the product to add.
        Returns:
            Dict: A dictionary containing add status and message. Validates product
                  existence and prevents duplicate entries.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"wishlist_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"wishlist_status": False, "message": "Product not found."}

        user_wish_list = user_data.get("wish_list", [])
        # Check if already in wish list
        for item in user_wish_list:
            if item.get("product_id") == product_id:
                return {"wishlist_status": False, "message": "Product already in wish list."}

        user_wish_list.append({"product_id": product_id, "added_date": datetime.now().strftime("%Y-%m-%d")})
        self._update_user_data(user_id, "wish_list", user_wish_list)
        return {"wishlist_status": True, "message": "Product added to wish list."}

    def remove_from_wish_list(self, user_id: str, product_id: str) -> Dict[str, Union[bool, str]]:
        """
        Removes a product from the user's wish list.
        Args:
            user_id (str): The unique identifier of the user removing from wish list.
            product_id (str): The unique identifier of the product to remove.
        Returns:
            Dict: A dictionary containing removal status and message indicating whether
                  the product was successfully removed from the wish list.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"wishlist_status": False, "message": "User not found."}

        user_wish_list = user_data.get("wish_list", [])
        for i, item in enumerate(user_wish_list):
            if item.get("product_id") == product_id:
                user_wish_list.pop(i)
                self._update_user_data(user_id, "wish_list", user_wish_list)
                return {"wishlist_status": True, "message": "Product removed from wish list."}
        return {"wishlist_status": False, "message": "Product not found in wish list."}

    def show_wish_list(self, user_id: str) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves the complete contents of the user's wish list with product details.
        Args:
            user_id (str): The unique identifier of the user whose wish list to retrieve.
        Returns:
            Dict: A dictionary containing wish list status and a list of wish list items
                  with product information and addition dates.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"wishlist_status": False, "wishlist": []}

        wish_list_items = []
        for item in user_data.get("wish_list", []):
            product_id = item.get("product_id")
            product_info = self.state["products"].get(product_id)
            if product_info:
                wish_list_items.append(
                    {
                        "product_id": product_id,
                        "name": product_info["name"],
                        "price": product_info["price"],
                        "added_date": item["added_date"],
                    }
                )
        return {"wishlist_status": True, "wishlist": wish_list_items}

    def search_products(
        self, query: str, category: Union[str, None] = None, min_price: float = 0.0, max_price: float = float('inf')
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Searches for products based on various criteria including text query, category, and price range.
        Args:
            query (str): The search query text to match against product names and descriptions.
            category (Union[str, None], optional): Filter by specific product category (default: None).
            min_price (float, optional): Minimum price filter (default: 0.0).
            max_price (float, optional): Maximum price filter (default: infinity).
        Returns:
            Dict: A dictionary containing search status and a list of matching product objects
                  with their complete details.
        """
        results = []
        for product_id, product_info in self.state["products"].items():
            if (
                query.lower() in product_info["name"].lower()
                or query.lower() in product_info["description"].lower()
            ) and (category is None or product_info["category"].lower() == category.lower()) and (
                min_price <= product_info["price"] <= max_price
            ):
                results.append({"product_id": product_id, **product_info})
        return {"search_status": True, "products": results}

    def show_product_details(self, product_id: str) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves detailed information about a specific product.
        Args:
            product_id (str): The unique identifier of the product to retrieve details for.
        Returns:
            Dict: A dictionary containing product status and the complete product information
                  if the product is found.
        """
        product_info = self.state["products"].get(product_id)
        if product_info:
            return {"product_status": True, "product": product_info}
        return {"product_status": False, "product": {}}

    def submit_product_review(
        self, user_id: str, product_id: str, rating: int, comment: str
    ) -> Dict[str, Union[bool, str]]:
        """
        Submits a product review with rating and comment from an authenticated user.
        Args:
            user_id (str): The unique identifier of the user submitting the review.
            product_id (str): The unique identifier of the product being reviewed.
            rating (int): The rating score (typically 1-5 stars).
            comment (str): The detailed review comment text.
        Returns:
            Dict: A dictionary containing submission status, message, and the newly generated
                  review ID if successful.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"submit_review_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"submit_review_status": False, "message": "Product not found."}

        new_review_id = str(uuid.uuid4())
        product_reviews = self.state["product_reviews"].get(product_id, [])
        product_reviews.append(
            {
                "review_id": new_review_id,
                "user_id": user_id,
                "rating": rating,
                "comment": comment,
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
        )
        self.state["product_reviews"][product_id] = product_reviews
        return {"submit_review_status": True, "message": "Review submitted successfully.", "review_id": new_review_id}

    def show_product_reviews(
        self, product_id: str, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves a paginated list of reviews for a specific product with user information.
        Args:
            product_id (str): The unique identifier of the product whose reviews to retrieve.
            page_index (int, optional): The page number for pagination (default: 1).
            page_limit (int, optional): The number of items per page (default: 10).
        Returns:
            Dict: A dictionary containing reviews status and a list of review objects
                  with user email information and pagination applied.
        """
        reviews = self.state["product_reviews"].get(product_id, [])
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_reviews = reviews[start_index:end_index]

        display_reviews = []
        for review in paginated_reviews:
            review_copy = review.copy()
            for u_id, u_data in self.state["users"].items():
                if u_id == review_copy["user_id"]:
                    review_copy["user_email"] = u_data["email"]
                    break
            display_reviews.append(review_copy)

        return {"reviews_status": True, "reviews": display_reviews}

    def ask_product_question(
        self, user_id: str, product_id: str, question: str
    ) -> Dict[str, Union[bool, str]]:
        """
        Submits a question about a specific product from an authenticated user.
        Args:
            user_id (str): The unique identifier of the user asking the question.
            product_id (str): The unique identifier of the product being questioned.
            question (str): The question text to submit.
        Returns:
            Dict: A dictionary containing question submission status, message, and the newly
                  generated question ID if successful.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"ask_question_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"ask_question_status": False, "message": "Product not found."}

        if product_id not in self.state["product_questions"]:
            self.state["product_questions"][product_id] = {"product_id": product_id, "q_and_as": []}

        qa_list = self.state["product_questions"][product_id]["q_and_as"]
        new_question_id = str(uuid.uuid4())
        qa_list.append({
            "id": new_question_id,
            "user_id": user_id,
            "question": question,
            "answer": "...",
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        return {"ask_question_status": True, "message": "Question submitted successfully.", "question_id": new_question_id}

    def answer_product_question(
            self, user_id: str, product_id: str, question_id: str, answer: str
        ) -> Dict[str, Union[bool, str]]:
        """
        Answers a previously asked product question from an authenticated user.
        Args:
            user_id (str): The unique identifier of the user answering the question.
            product_id (str): The unique identifier of the product the question is about.
            question_id (str): The unique identifier of the question to answer.
            answer (str): The answer text to submit.
        Returns:
            Dict: A dictionary containing answer submission status, message, and the question ID
                  if successfully answered.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"answer_question_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"answer_question_status": False, "message": "Product not found."}

        container = self.state["product_questions"].get(product_id)

        if container:
            for qa_pair in container.get("q_and_as", []):
                if qa_pair.get("id") == question_id:
                    qa_pair["answer"] = answer
                    qa_pair["answer_user_id"] = user_id
                    qa_pair["answer_date"] = datetime.now().strftime("%Y-%m-%d")

                    return {
                        "answer_question_status": True,
                        "message": "Answer submitted successfully.",
                        "qa_id": question_id
                    }
        return {"answer_question_status": False, "message": "Question not found."}

    def show_product_questions(
        self, product_id: str, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves a paginated list of questions and answers for a specific product.
        Args:
            product_id (str): The unique identifier of the product whose questions to retrieve.
            page_index (int, optional): The page number for pagination (default: 1).
            page_limit (int, optional): The number of items per page (default: 10).
        Returns:
            Dict: A dictionary containing questions status and a list of question objects
                  with user email information and pagination applied.
        """
        container = self.state["product_questions"].get(product_id)
        if not container:
            return {"questions_status": True, "questions": []}
        
        qa_list = container.get("q_and_as", [])
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_qa = qa_list[start_index:end_index]

        display_questions = []
        for qa in paginated_qa:
            qa_copy = qa.copy()
            # Add user email for asker
            for u_id, u_data in self.state["users"].items():
                if u_id == qa_copy.get("user_id"):
                    qa_copy["user_email"] = u_data["email"]
                    break
            # If answered, add answer user email
            if qa_copy.get("answer_user_id"):
                for u_id, u_data in self.state["users"].items():
                    if u_id == qa_copy["answer_user_id"]:
                        qa_copy["answer_user_email"] = u_data["email"]
                        break
            display_questions.append(qa_copy)

        return {"questions_status": True, "questions": display_questions}

    def subscribe_prime(
        self, user_id: str, duration: Literal["monthly", "yearly"]
    ) -> Dict[str, Union[bool, str, str]]:
        """
        Subscribes the user to an Amazon Prime membership with the specified duration.
        Args:
            user_id (str): The unique identifier of the user subscribing to Prime.
            duration (Literal["monthly", "yearly"]): The subscription duration period.
        Returns:
            Dict: A dictionary containing subscription status, message, and the newly generated
                  subscription ID if successful. Validates against existing active subscriptions.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"subscribe_status": False, "message": "User not found."}

        for sub_id, sub_data in user_data.get("prime_subscriptions", {}).items():
            if sub_data["status"] == "active" and datetime.strptime(sub_data["end_date"], "%Y-%m-%d") > datetime.now():
                return {"subscribe_status": False, "message": "You already have an active Prime subscription."}

        new_subscription_id = str(uuid.uuid4())
        start_date = datetime.now()
        if duration == "monthly":
            end_date = start_date + timedelta(days=30)
        else:
            end_date = start_date + timedelta(days=365)

        new_subscription = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "plan_type": duration,
            "status": "active",
        }

        user_prime_subscriptions = user_data.get("prime_subscriptions", {})
        user_prime_subscriptions[new_subscription_id] = new_subscription
        self._update_user_data(user_id, "prime_subscriptions", user_prime_subscriptions)

        return {"subscribe_status": True, "message": f"Successfully subscribed to {duration} Prime plan.", "prime_subscription_id": new_subscription_id}

    def show_prime_subscriptions(
        self, user_id: str, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves a paginated list of the user's Amazon Prime subscription history.
        Args:
            user_id (str): The unique identifier of the user whose Prime subscriptions to retrieve.
            page_index (int, optional): The page number for pagination (default: 1).
            page_limit (int, optional): The number of items per page (default: 10).
        Returns:
            Dict: A dictionary containing subscriptions status and a list of Prime subscription
                  objects with pagination applied.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"subscriptions_status": False, "prime_subscriptions": []}

        all_subscriptions = list(user_data.get("prime_subscriptions", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_subscriptions = all_subscriptions[start_index:end_index]

        return {"subscriptions_status": True, "prime_subscriptions": paginated_subscriptions}

    def request_return(
        self, user_id: str, order_id: str, product_id: str, reason: str
    ) -> Dict[str, Union[bool, str, str]]:
        """
        Initiates a return request for a product from a specific order.
        Args:
            user_id (str): The unique identifier of the user requesting the return.
            order_id (str): The unique identifier of the order containing the product.
            product_id (str): The unique identifier of the product to return.
            reason (str): The reason for the return request.
        Returns:
            Dict: A dictionary containing return status, message, and the newly generated
                  return ID if successful. Validates order and product existence.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"return_status": False, "message": "User not found."}

        user_orders = user_data.get("orders", {})
        if order_id not in user_orders:
            return {"return_status": False, "message": "Order not found."}

        order_products = user_orders[order_id]["products"]
        if product_id not in order_products:
            return {"return_status": False, "message": "Product not found in this order."}

        new_return_id = str(uuid.uuid4())
        user_returns = user_data.get("returns", {})
        user_returns[new_return_id] = {
            "order_id": order_id,
            "product_id": product_id,
            "return_date": datetime.now().strftime("%Y-%m-%d"),
            "reason": reason,
            "status": "pending",
        }
        self._update_user_data(user_id, "returns", user_returns)
        return {"return_status": True, "message": "Return request submitted.", "return_id": new_return_id}

    def show_returns(
        self, user_id: str, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Retrieves a paginated list of the user's return request history.
        Args:
            user_id (str): The unique identifier of the user whose returns to retrieve.
            page_index (int, optional): The page number for pagination (default: 1).
            page_limit (int, optional): The number of items per page (default: 10).
        Returns:
            Dict: A dictionary containing returns status and a list of return request objects
                  with pagination applied.
        """
        user_data = self._get_user_data(user_id)
        if not user_data:
            return {"returns_status": False, "returns": []}

        all_returns = list(user_data.get("returns", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_returns = all_returns[start_index:end_index]

        return {"returns_status": True, "returns": paginated_returns}

    def get_seller_info(self, seller_id: int) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves information about a specific seller registered in the system.
        Args:
            seller_id (int): The unique identifier of the seller to retrieve information for.
        Returns:
            Dict: A dictionary containing seller status and the seller's information if found.
        """
        seller_info = self.state["sellers"].get(seller_id)
        if seller_info:
            return {"seller_status": True, "seller_info": seller_info}
        return {"seller_status": False, "seller_info": {}}
        """
        Retrieves the current status of a previously sent SMS message.
        Args:
            message_id (str): The unique ID of the SMS message to check.
        Returns:
            Dict: A dictionary representing the SMS message object if found,
                  or an error dictionary if not found.
        """
        time.sleep(0.05)
        sms = None
        for user_data in self.users.values():
            sms = next((msg for msg in user_data["sms_history"] if msg["sms_id"] == message_id), None)
            if sms:
                break

        if not sms:
            return {"code": "SMS_NOT_FOUND", "message": f"SMS message with ID '{message_id}' not found."}

        print(f"Dummy SMS status retrieved for ID={message_id}: {sms['status']}")
        return {
            "id": sms["sms_id"],
            "from": sms["sender"],
            "to": sms["receiver"],
            "message": sms["message"],
            "status": sms["status"],
            "timestamp": sms["timestamp"]
        }
