import uuid
from typing import Dict, List, Union, Literal, Any
from datetime import datetime, timedelta
from copy import deepcopy

class User:
    def __init__(self, user_id: str, email: str = None):
        self.user_id = user_id
        self.email = email

class AmazonAPI:
    def __init__(self):
        self.state = deepcopy(DEFAULT_STATE)

    def _get_user_data(self, user: User) -> Union[Dict, None]:
        """
        Retrieves user data using user_id.
        """
        return self.state["users"].get(user.user_id)

    def _update_user_data(self, user: User, key: str, value: Any):
        """
        Updates a specific key in user data using user_id.
        """
        if user.user_id in self.state["users"]:
            self.state["users"][user.user_id][key] = value

    def register_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str
    ) -> Dict[str, Union[bool, str]]:
        """
        Registers a new user with a unique user_id.
        """
        for user_id, user_data in self.state["users"].items():
            if user_data["email"] == email:
                return {"register_status": False, "message": "User with this email already exists."}

        new_user_id = str(uuid.uuid4())
        self.state["users"][new_user_id] = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "balance": 0.0,
            "friends": [],
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
        Logs in a user and sets current_user to their user_id.
        In a real app, password verification would happen here.
        """
        for user_id, user_data in self.state["users"].items():
            if user_data["email"] == email:
                self.state["current_user"] = user_id
                return {"login_status": True, "message": f"User {email} logged in successfully."}
        return {"login_status": False, "message": "Invalid email or password."}

    def show_profile(self, user: User) -> Dict[str, Union[bool, Dict]]:
        """
        Shows the profile of the specified user using their user_id.
        Function signature updated to take User object which holds user_id.
        """
        user_data = self._get_user_data(user)
        if user_data:
            return {"profile_status": True, "profile": user_data}
        return {"profile_status": False, "profile": {}}

    def show_account(self, user: User) -> Dict[str, Union[bool, str, Dict]]:
        """
        Shows account details for the current user, using user_id.
        Function signature remains the same, but now `user` object internally holds `user_id`.
        """
        user_data = self._get_user_data(user)
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

    def delete_account(self, user: User) -> Dict[str, Union[bool, str]]:
        """
        Deletes the user's account using user_id.
        """
        if user.user_id in self.state["users"]:
            del self.state["users"][user.user_id]
            if self.state["current_user"] == user.user_id:
                self.state["current_user"] = None
            return {"delete_status": True, "message": f"Account for user ID {user.user_id} deleted successfully."}
        return {"delete_status": False, "message": "User not found."}

    def add_friend(self, user: User, friend_email: str) -> Dict[str, Union[bool, str]]:
        """
        Adds a friend by their email, converting it to user_id.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"add_friend_status": False, "message": "User not found."}

        friend_user_id = None
        for u_id, u_data in self.state["users"].items():
            if u_data["email"] == friend_email:
                friend_user_id = u_id
                break

        if not friend_user_id:
            return {"add_friend_status": False, "message": f"Friend with email {friend_email} not found."}

        if friend_user_id == user.user_id:
            return {"add_friend_status": False, "message": "Cannot add yourself as a friend."}

        if friend_user_id in user_data["friends"]:
            return {"add_friend_status": False, "message": f"{friend_email} is already your friend."}

        user_data["friends"].append(friend_user_id)
        self._update_user_data(user, "friends", user_data["friends"])
        return {"add_friend_status": True, "message": f"Successfully added {friend_email} as a friend."}

    def remove_friend(self, user: User, friend_email: str) -> Dict[str, Union[bool, str]]:
        """
        Removes a friend by their email, converting it to user_id.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"remove_friend_status": False, "message": "User not found."}

        friend_user_id = None
        for u_id, u_data in self.state["users"].items():
            if u_data["email"] == friend_email:
                friend_user_id = u_id
                break

        if not friend_user_id:
            return {"remove_friend_status": False, "message": f"Friend with email {friend_email} not found."}

        if friend_user_id not in user_data["friends"]:
            return {"remove_friend_status": False, "message": f"{friend_email} is not in your friends list."}

        user_data["friends"].remove(friend_user_id)
        self._update_user_data(user, "friends", user_data["friends"])
        return {"remove_friend_status": True, "message": f"Successfully removed {friend_email} from friends."}

    def show_friends(self, user: User) -> Dict[str, Union[bool, List[str]]]:
        """
        Shows the list of friends (emails) for the current user.
        Converts friend user_ids back to emails for display.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"friends_status": False, "friends": []}

        friend_emails = []
        for friend_user_id in user_data["friends"]:
            for u_id, u_data in self.state["users"].items():
                if u_id == friend_user_id:
                    friend_emails.append(u_data["email"])
                    break
        return {"friends_status": True, "friends": friend_emails}

    def add_payment_card(
        self,
        user: User,
        card_name: str,
        owner_name: str,
        card_number: int,
        expiry_year: int,
        expiry_month: int,
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Adds a new payment card with a UUID as ID.
        CVV is not stored for realism.
        Card number stored as last 4 digits.
        """
        user_data = self._get_user_data(user)
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
        self._update_user_data(user, "payment_cards", user_payment_cards)
        return {"add_card_status": True, "message": "Payment card added successfully.", "card_id": new_card_id}

    def remove_payment_card(self, user: User, card_id: str) -> Dict[str, Union[bool, str]]:
        """
        Removes a payment card using its UUID.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"remove_card_status": False, "message": "User not found."}

        user_payment_cards = user_data.get("payment_cards", {})
        if card_id in user_payment_cards:
            del user_payment_cards[card_id]
            self._update_user_data(user, "payment_cards", user_payment_cards)
            return {"remove_card_status": True, "message": f"Payment card {card_id} removed successfully."}
        return {"remove_card_status": False, "message": "Payment card not found."}

    def show_payment_cards(
        self, user: User, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows the current user's payment cards.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"cards_status": False, "payment_cards": []}

        all_cards = list(user_data.get("payment_cards", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_cards = all_cards[start_index:end_index]

        return {"cards_status": True, "payment_cards": paginated_cards}

    def add_address(
        self,
        user: User,
        name: str,
        street_address: str,
        city: str,
        state: str,
        country: str,
        zip_code: int,
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Adds a new address with a UUID as ID.
        """
        user_data = self._get_user_data(user)
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
        self._update_user_data(user, "addresses", user_addresses)
        return {"add_address_status": True, "message": "Address added successfully.", "address_id": new_address_id}

    def remove_address(self, user: User, address_id: str) -> Dict[str, Union[bool, str]]:
        """
        Removes an address using its UUID.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"remove_address_status": False, "message": "User not found."}

        user_addresses = user_data.get("addresses", {})
        if address_id in user_addresses:
            del user_addresses[address_id]
            self._update_user_data(user, "addresses", user_addresses)
            return {"remove_address_status": True, "message": f"Address {address_id} removed successfully."}
        return {"remove_address_status": False, "message": "Address not found."}

    def show_addresses(
        self, user: User, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows the current user's addresses.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"addresses_status": False, "addresses": []}

        all_addresses = list(user_data.get("addresses", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_addresses = all_addresses[start_index:end_index]

        return {"addresses_status": True, "addresses": paginated_addresses}

    def add_to_cart(self, user: User, product_id: int, quantity: int) -> Dict[str, Union[bool, str]]:
        """
        Adds a product to the user's cart.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"add_to_cart_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"add_to_cart_status": False, "message": "Product not found."}
        if self.state["products"][product_id]["stock"] < quantity:
            return {"add_to_cart_status": False, "message": "Not enough stock."}

        user_cart = user_data.get("cart", {})
        user_cart[product_id] = user_cart.get(product_id, 0) + quantity
        self._update_user_data(user, "cart", user_cart)
        return {"add_to_cart_status": True, "message": "Product added to cart."}

    def remove_from_cart(self, user: User, product_id: int) -> Dict[str, Union[bool, str]]:
        """
        Removes a product from the user's cart.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"remove_from_cart_status": False, "message": "User not found."}

        user_cart = user_data.get("cart", {})
        if product_id in user_cart:
            del user_cart[product_id]
            self._update_user_data(user, "cart", user_cart)
            return {"remove_from_cart_status": True, "message": "Product removed from cart."}
        return {"remove_from_cart_status": False, "message": "Product not found in cart."}

    def update_cart_item_quantity(self, user: User, product_id: int, quantity: int) -> Dict[str, Union[bool, str]]:
        """
        Updates the quantity of a product in the user's cart.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"update_cart_status": False, "message": "User not found."}

        user_cart = user_data.get("cart", {})
        if product_id not in user_cart:
            return {"update_cart_status": False, "message": "Product not in cart."}
        if self.state["products"][product_id]["stock"] < quantity:
            return {"update_cart_status": False, "message": "Not enough stock."}

        if quantity <= 0:
            del user_cart[product_id]
        else:
            user_cart[product_id] = quantity
        self._update_user_data(user, "cart", user_cart)
        return {"update_cart_status": True, "message": "Cart updated."}

    def show_cart(self, user: User) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows the current user's cart content.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"cart_status": False, "cart_items": []}

        cart_items = []
        for product_id, quantity in user_data.get("cart", {}).items():
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
        return {"cart_status": True, "cart_items": cart_items}

    def apply_promo_code_to_cart(self, promo_code: str, user: User) -> Dict[str, Union[bool, str, float]]:
        """
        Applies a promo code to the current user's cart.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"promo_status": False, "message": "User not found."}

        if promo_code == "WELCOME10":
            discount_percentage = 0.10
        elif promo_code == "FREESHIP":
            discount_percentage = 0.0
        else:
            return {"promo_status": False, "message": "Invalid promo code."}

        cart_total = 0.0
        for product_id, quantity in user_data.get("cart", {}).items():
            product_info = self.state["products"].get(product_id)
            if product_info:
                cart_total += product_info["price"] * quantity
        
        discount_amount = cart_total * discount_percentage
        new_total = cart_total - discount_amount

        return {"promo_status": True, "message": f"Promo code {promo_code} applied. Discount: ${discount_amount:.2f}", "discount_amount": discount_amount, "new_total": new_total}

    def remove_promo_code_from_cart(self, user: User) -> Dict[str, Union[bool, str]]:
        """
        Removes any applied promo code from the user's cart.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"promo_status": False, "message": "User not found."}

        return {"promo_status": True, "message": "Promo code removed from cart."}

    def checkout(
        self, user: User, delivery_address_id: str, payment_card_id: str, promo_code: Union[str, None] = None
    ) -> Dict[str, Union[bool, str, Dict]]:
        """
        Processes the checkout, creates an order with a UUID, updates stock and balance.
        """
        user_data = self._get_user_data(user)
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
        self._update_user_data(user, "orders", user_orders)
        self._update_user_data(user, "balance", user_data["balance"])
        self._update_user_data(user, "cart", {})

        return {
            "checkout_status": True,
            "message": "Checkout successful. Order placed.",
            "order": user_orders[new_order_id],
        }

    def show_orders(
        self, user: User, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows the current user's orders.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"orders_status": False, "orders": []}

        all_orders = list(user_data.get("orders", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_orders = all_orders[start_index:end_index]

        return {"orders_status": True, "orders": paginated_orders}

    def add_to_wish_list(self, user: User, product_id: int) -> Dict[str, Union[bool, str]]:
        """
        Adds a product to the user's wish list.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"add_to_wish_list_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"add_to_wish_list_status": False, "message": "Product not found."}

        user_wish_list = user_data.get("wish_list", {})
        if product_id in user_wish_list:
            return {"add_to_wish_list_status": False, "message": "Product already in wish list."}

        user_wish_list[product_id] = {"added_date": datetime.now().strftime("%Y-%m-%d")}
        self._update_user_data(user, "wish_list", user_wish_list)
        return {"add_to_wish_list_status": True, "message": "Product added to wish list."}

    def remove_from_wish_list(self, user: User, product_id: int) -> Dict[str, Union[bool, str]]:
        """
        Removes a product from the user's wish list.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"remove_from_wish_list_status": False, "message": "User not found."}

        user_wish_list = user_data.get("wish_list", {})
        if product_id in user_wish_list:
            del user_wish_list[product_id]
            self._update_user_data(user, "wish_list", user_wish_list)
            return {"remove_from_wish_list_status": True, "message": "Product removed from wish list."}
        return {"remove_from_wish_list_status": False, "message": "Product not found in wish list."}

    def show_wish_list(self, user: User) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows the current user's wish list content.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"wish_list_status": False, "wish_list_items": []}

        wish_list_items = []
        for product_id, details in user_data.get("wish_list", {}).items():
            product_info = self.state["products"].get(product_id)
            if product_info:
                wish_list_items.append(
                    {
                        "product_id": product_id,
                        "name": product_info["name"],
                        "price": product_info["price"],
                        "added_date": details["added_date"],
                    }
                )
        return {"wish_list_status": True, "wish_list_items": wish_list_items}

    def search_products(
        self, query: str, category: Union[str, None] = None, min_price: float = 0.0, max_price: float = float('inf')
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Searches for products based on query, category, and price range.
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

    def show_product_details(self, product_id: int) -> Dict[str, Union[bool, Dict]]:
        """
        Shows details of a specific product.
        """
        product_info = self.state["products"].get(product_id)
        if product_info:
            return {"product_status": True, "product": product_info}
        return {"product_status": False, "product": {}}

    def submit_product_review(
        self, user: User, product_id: int, rating: int, comment: str
    ) -> Dict[str, Union[bool, str]]:
        """
        Submits a product review with a UUID for the review ID and user ID.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"submit_review_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"submit_review_status": False, "message": "Product not found."}

        new_review_id = str(uuid.uuid4())
        product_reviews = self.state["product_reviews"].get(product_id, [])
        product_reviews.append(
            {
                "review_id": new_review_id,
                "user_id": user.user_id,
                "rating": rating,
                "comment": comment,
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
        )
        self.state["product_reviews"][product_id] = product_reviews
        return {"submit_review_status": True, "message": "Review submitted successfully.", "review_id": new_review_id}

    def show_product_reviews(
        self, product_id: int, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows reviews for a specific product.
        Converts user_id back to email for display in reviews.
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
        self, user: User, product_id: int, question: str
    ) -> Dict[str, Union[bool, str]]:
        """
        Asks a question about a product with a UUID for the question ID and user ID.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"ask_question_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"ask_question_status": False, "message": "Product not found."}

        new_question_id = str(uuid.uuid4())
        product_questions = self.state["product_questions"].get(product_id, [])
        product_questions.append(
            {
                "question_id": new_question_id,
                "user_id": user.user_id,
                "question": question,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "answers": [],
            }
        )
        self.state["product_questions"][product_id] = product_questions
        return {"ask_question_status": True, "message": "Question submitted successfully.", "question_id": new_question_id}

    def answer_product_question(
        self, user: User, product_id: int, question_id: str, answer: str
    ) -> Dict[str, Union[bool, str]]:
        """
        Answers a product question with a UUID for the answer ID and user ID.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"answer_question_status": False, "message": "User not found."}

        if product_id not in self.state["products"]:
            return {"answer_question_status": False, "message": "Product not found."}

        product_questions = self.state["product_questions"].get(product_id, [])
        for question_data in product_questions:
            if question_data["question_id"] == question_id:
                new_answer_id = str(uuid.uuid4())
                question_data["answers"].append(
                    {
                        "answer_id": new_answer_id,
                        "user_id": user.user_id,
                        "answer": answer,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                    }
                )
                return {"answer_question_status": True, "message": "Answer submitted successfully.", "answer_id": new_answer_id}
        return {"answer_question_status": False, "message": "Question not found."}

    def show_product_questions(
        self, product_id: int, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows questions and answers for a specific product.
        Converts user_ids back to emails for display.
        """
        questions = self.state["product_questions"].get(product_id, [])
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_questions = questions[start_index:end_index]

        display_questions = []
        for question in paginated_questions:
            question_copy = question.copy()
            for u_id, u_data in self.state["users"].items():
                if u_id == question_copy["user_id"]:
                    question_copy["user_email"] = u_data["email"]
                    break
            
            display_answers = []
            for answer in question_copy.get("answers", []):
                answer_copy = answer.copy()
                for u_id, u_data in self.state["users"].items():
                    if u_id == answer_copy["user_id"]:
                        answer_copy["user_email"] = u_data["email"]
                        break
                display_answers.append(answer_copy)
            question_copy["answers"] = display_answers
            display_questions.append(question_copy)

        return {"questions_status": True, "questions": display_questions}

    def subscribe_prime(
        self, user: User, duration: Literal["monthly", "yearly"]
    ) -> Dict[str, Union[bool, str, str]]:
        """
        Subscribes the user to Amazon Prime with a UUID for the subscription ID.
        """
        user_data = self._get_user_data(user)
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
        self._update_user_data(user, "prime_subscriptions", user_prime_subscriptions)

        return {"subscribe_status": True, "message": f"Successfully subscribed to {duration} Prime plan.", "prime_subscription_id": new_subscription_id}

    def show_prime_subscriptions(
        self, user: User, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows the current user's Amazon Prime subscriptions.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"subscriptions_status": False, "prime_subscriptions": []}

        all_subscriptions = list(user_data.get("prime_subscriptions", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_subscriptions = all_subscriptions[start_index:end_index]

        return {"subscriptions_status": True, "prime_subscriptions": paginated_subscriptions}

    def request_return(
        self, user: User, order_id: str, product_id: int, reason: str
    ) -> Dict[str, Union[bool, str, str]]:
        """
        Initiates a return request with a UUID for the return ID.
        """
        user_data = self._get_user_data(user)
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
        self._update_user_data(user, "returns", user_returns)
        return {"return_status": True, "message": "Return request submitted.", "return_id": new_return_id}

    def show_returns(
        self, user: User, page_index: int = 1, page_limit: int = 10
    ) -> Dict[str, Union[bool, List[Dict]]]:
        """
        Shows the current user's return requests.
        """
        user_data = self._get_user_data(user)
        if not user_data:
            return {"returns_status": False, "returns": []}

        all_returns = list(user_data.get("returns", {}).values())
        
        start_index = (page_index - 1) * page_limit
        end_index = start_index + page_limit
        paginated_returns = all_returns[start_index:end_index]

        return {"returns_status": True, "returns": paginated_returns}

    def get_seller_info(self, seller_id: int) -> Dict[str, Union[bool, Dict]]:
        """
        Retrieves information about a specific seller.
        """
        seller_info = self.state["sellers"].get(seller_id)
        if seller_info:
            return {"seller_status": True, "seller_info": seller_info}
        return {"seller_status": False, "seller_info": {}}