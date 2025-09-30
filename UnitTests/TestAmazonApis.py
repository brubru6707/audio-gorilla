import sys
import os

# Add the parent directory (audio_gorilla) to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Add the Backends directory to the Python path for fake_data import
backends_dir = os.path.join(parent_dir, 'Backends')
sys.path.insert(0, backends_dir)

from AmazonApis import AmazonApis
import unittest
from copy import deepcopy

# Import DEFAULT_STATE directly from the backend
from createAmazonBackend import DEFAULT_STATE

# Real users from backend diverse_amazon_state.json
REAL_USER_ID_1 = "b462da43-c54d-4fc5-b312-e348d363b961"  # Leah Sanchez
REAL_EMAIL_1 = "leah.sanchez@astronomy-club.net"
REAL_USER_ID_2 = "c1a91647-9b96-426b-af7c-5ba66f27002f"  # Grace Ford  
REAL_EMAIL_2 = "grace.ford@cat-boarding.services"
REAL_USER_ID_3 = "f9874864-b1ac-4887-8fef-2acaa3a0ea82"  # Adrian Vasquez
REAL_EMAIL_3 = "adrian.vasquez@poetry-journal.com"

# Real product IDs from backend (based on order data seen)
REAL_PRODUCT_ID_1 = "2"
REAL_PRODUCT_ID_2 = "4" 
REAL_PRODUCT_ID_3 = "9"

class TestAmazonApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh AmazonApis instance for each test."""
        self.amazon_api = AmazonApis()
        # The AmazonApis automatically loads DEFAULT_STATE in its __init__ method
    def test_register_user_success(self):
        """Test registering a new user successfully."""
        result = self.amazon_api.register_user(
            first_name="John",
            last_name="Doe", 
            email="john.doe@test.com",
            password="securepassword"
        )
        self.assertTrue(result["register_status"])
        self.assertIn("User john.doe@test.com registered successfully", result["message"])
        
        # Verify user was added to the system by finding them by email
        found_user = None
        for user_id, user_data in self.amazon_api.state["users"].items():
            if user_data["email"] == "john.doe@test.com":
                found_user = user_data
                break
        
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user["email"], "john.doe@test.com")
        self.assertEqual(found_user["first_name"], "John")

    def test_register_user_duplicate_email(self):
        """Test registering a user with an already existing email."""
        # Try to register with an existing email from backend
        result = self.amazon_api.register_user(
            first_name="Test",
            last_name="User", 
            email=REAL_EMAIL_1,
            password="password"
        )
        self.assertFalse(result["register_status"])
        self.assertIn("User with this email already exists", result.get("message", ""))

    def test_login_user_success(self):
        """Test logging in with correct credentials."""
        # First register a user
        register_result = self.amazon_api.register_user(
            first_name="Login",
            last_name="Test",
            email="login.test@example.com",
            password="testpass123"
        )
        self.assertTrue(register_result["register_status"])
        
        # Now login (the API only checks email, not password in current implementation)
        result = self.amazon_api.login_user("login.test@example.com", "testpass123")
        self.assertTrue(result["login_status"])
        self.assertIn("logged in successfully", result["message"])

    def test_login_user_invalid_credentials(self):
        """Test logging in with invalid credentials."""
        result = self.amazon_api.login_user("nonexistent@example.com", "wrongpassword")
        self.assertFalse(result["login_status"])

    def test_show_profile_success(self):
        """Test showing the profile of an existing user."""
        result = self.amazon_api.show_profile(REAL_USER_ID_1)
        self.assertTrue(result["profile_status"])
        self.assertEqual(result["profile"]["first_name"], "Leah")
        self.assertEqual(result["profile"]["last_name"], "Sanchez")
        self.assertEqual(result["profile"]["email"], REAL_EMAIL_1)

    def test_show_profile_not_found(self):
        """Test showing the profile of a non-existent user."""
        result = self.amazon_api.show_profile("nonexistent-user-id")
        self.assertFalse(result["profile_status"])
        self.assertEqual(result["profile"], {})

    def test_show_account_success(self):
        """Test showing full account details for an existing user."""
        result = self.amazon_api.show_account(REAL_USER_ID_1)
        self.assertTrue(result["account_status"])
        self.assertIn("Account details for", result["message"])
        self.assertIn("balance", result["account"])
        self.assertIn("payment_cards", result["account"])
        self.assertIn("addresses", result["account"])

    def test_show_account_user_not_found(self):
        """Test showing account details when user is not found."""
        result = self.amazon_api.show_account("nonexistent-user-id")
        self.assertFalse(result["account_status"])
        self.assertEqual(result["message"], "User not found.")

    def test_delete_account_success(self):
        """Test deleting an existing user account."""
        initial_user_count = len(self.amazon_api.users)
        result = self.amazon_api.delete_account(self.user1)
        self.assertTrue(result["delete_status"])
        self.assertNotIn(REAL_USER_ID_1, self.amazon_api.users)
        self.assertEqual(len(self.amazon_api.users), initial_user_count - 1)
        self.assertIsNone(self.amazon_api.current_user) # Current user should be cleared if deleted

    def test_delete_account_not_found(self):
        """Test deleting a non-existent user account."""
        initial_user_count = len(self.amazon_api.users)
        non_existent_user = User(email="unknown@example.com")
        result = self.amazon_api.delete_account(non_existent_user)
        self.assertFalse(result["delete_status"])
        self.assertEqual(len(self.amazon_api.users), initial_user_count) # User count should be unchanged

    def test_show_product_success(self):
        """Test showing details of an existing product."""
        result = self.amazon_api.show_product(1)
        self.assertTrue(result["product_status"])
        self.assertEqual(result["product"]["name"], "Laptop")
        self.assertEqual(result["product"]["price"], 75.00)

    def test_show_product_not_found(self):
        """Test showing details of a non-existent product."""
        result = self.amazon_api.show_product(999)
        self.assertFalse(result["product_status"])
        self.assertEqual(result["product"], {})

    def test_search_products_by_query(self):
        """Test searching products by a query string."""
        result = self.amazon_api.search_products(query="mouse")
        self.assertTrue(result["products_status"])
        self.assertEqual(len(result["products"]), 1)
        self.assertEqual(result["products"][0]["name"], "Wireless Mouse")

    def test_search_products_by_product_type(self):
        """Test searching products by product type."""
        result = self.amazon_api.search_products(product_type="apparel")
        self.assertTrue(result["products_status"])
        self.assertEqual(len(result["products"]), 1)
        self.assertEqual(result["products"][0]["name"], "T-Shirt")

    def test_search_products_by_price_range(self):
        """Test searching products by price range."""
        result = self.amazon_api.search_products(min_price=20.0, max_price=30.0)
        self.assertTrue(result["products_status"])
        self.assertEqual(len(result["products"]), 2) # Wireless Mouse (25) and T-Shirt (20)

    def test_add_product_to_cart_success(self):
        """Test adding a product to the cart successfully."""
        result = self.amazon_api.add_product_to_cart(product_id=2, quantity=1, clear_cart_first=False, user=self.user1)
        self.assertTrue(result["add_status"])
        self.assertEqual(self.amazon_api.users[fake_email_1]["cart"][2], 1)

    def test_add_product_to_cart_insufficient_stock(self):
        """Test adding a product to cart with insufficient stock."""
        # Laptop has stock 10, try to add 11
        result = self.amazon_api.add_product_to_cart(product_id=1, quantity=11, clear_cart_first=False, user=self.user1)
        self.assertFalse(result["add_status"])
        self.assertNotIn(1, self.amazon_api.users[fake_email_1]["cart"])

    def test_update_product_quantity_in_cart_success(self):
        """Test updating product quantity in cart successfully."""
        self.amazon_api.add_product_to_cart(product_id=2, quantity=1, clear_cart_first=False, user=self.user1)
        result = self.amazon_api.update_product_quantity_in_cart(product_id=2, quantity=3, user=self.user1)
        self.assertTrue(result["update_status"])
        self.assertEqual(self.amazon_api.users[fake_email_1]["cart"][2], 3)

    def test_delete_product_from_cart_success(self):
        """Test deleting a product from the cart successfully."""
        self.amazon_api.add_product_to_cart(product_id=2, quantity=1, clear_cart_first=False, user=self.user1)
        result = self.amazon_api.delete_product_from_cart(product_id=2, user=self.user1)
        self.assertTrue(result["delete_status"])
        self.assertNotIn(2, self.amazon_api.users[fake_email_1]["cart"])

    def test_place_order_success(self):
        """Test placing an order successfully."""
        # Add products to cart
        self.amazon_api.add_product_to_cart(product_id=1, quantity=1, clear_cart_first=True, user=self.user1)
        self.amazon_api.add_product_to_cart(product_id=2, quantity=1, clear_cart_first=False, user=self.user1)
        
        initial_order_count = len(self.amazon_api.users[fake_email_1]["orders"])
        initial_laptop_stock = self.amazon_api.products[1]["stock"]
        initial_mouse_stock = self.amazon_api.products[2]["stock"]

        result = self.amazon_api.place_order(payment_card_id=1, address_id=1, user=self.user1)
        self.assertTrue(result["order_status"])
        self.assertIn("order_id", result)
        self.assertEqual(len(self.amazon_api.users[fake_email_1]["orders"]), initial_order_count + 1)
        self.assertEqual(self.amazon_api.users[fake_email_1]["cart"], {}) # Cart should be empty
        self.assertEqual(self.amazon_api.products[1]["stock"], initial_laptop_stock - 1)
        self.assertEqual(self.amazon_api.products[2]["stock"], initial_mouse_stock - 1)

    def test_place_order_empty_cart(self):
        """Test placing an order with an empty cart."""
        self.amazon_api.clear_cart(self.user1) # Ensure cart is empty
        result = self.amazon_api.place_order(payment_card_id=1, address_id=1, user=self.user1)
        self.assertFalse(result["order_status"])
        self.assertEqual(result["message"], "Cart is empty. Cannot place an order.")

    def test_place_order_invalid_payment_card(self):
        """Test placing an order with an invalid payment card."""
        self.amazon_api.add_product_to_cart(product_id=1, quantity=1, clear_cart_first=True, user=self.user1)
        result = self.amazon_api.place_order(payment_card_id=999, address_id=1, user=self.user1)
        self.assertFalse(result["order_status"])
        self.assertIn("Payment card with ID 999 not found.", result["message"])

    def test_show_orders_success(self):
        """Test showing past orders for the current user."""
        # A default order exists in DEFAULT_STATE
        result = self.amazon_api.show_orders(self.user1)
        self.assertTrue(result["orders_status"])
        self.assertGreater(len(result["orders"]), 0)
        self.assertEqual(result["orders"][0]["order_id"], 101)

    def test_show_orders_no_orders(self):
        """Test showing orders for a user with no orders."""
        # Create a new user with no orders
        self.amazon_api.users["newuser@example.com"] = deepcopy(DEFAULT_STATE["users"][fake_email_1])
        self.amazon_api.users["newuser@example.com"]["orders"] = {}
        new_user = User(email="newuser@example.com")
        result = self.amazon_api.show_orders(new_user)
        self.assertTrue(result["orders_status"])
        self.assertEqual(len(result["orders"]), 0)

    def test_show_payment_cards_success(self):
        """Test showing payment cards for the current user."""
        result = self.amazon_api.show_payment_cards(self.user1)
        self.assertTrue(result["cards_status"])
        self.assertGreater(len(result["payment_cards"]), 0)
        self.assertEqual(result["payment_cards"][0]["card_name"], "My Debit Card")

    def test_add_payment_card_success(self):
        """Test adding a new payment card successfully."""
        initial_card_count = len(self.amazon_api.users[fake_email_1]["payment_cards"])
        result = self.amazon_api.add_payment_card(
            card_name="New Credit Card",
            owner_name="Alice Smith",
            card_number=5555,
            expiry_year=2030,
            expiry_month=10,
            cvv_number=456,
            user=self.user1
        )
        self.assertTrue(result["add_status"])
        self.assertEqual(len(self.amazon_api.users[fake_email_1]["payment_cards"]), initial_card_count + 1)
        self.assertIn("payment_card_id", result)

    def test_delete_payment_card_success(self):
        """Test deleting an existing payment card."""
        initial_card_count = len(self.amazon_api.users[fake_email_1]["payment_cards"])
        result = self.amazon_api.delete_payment_card(payment_card_id=1, user=self.user1)
        self.assertTrue(result["delete_status"])
        self.assertEqual(len(self.amazon_api.users[fake_email_1]["payment_cards"]), initial_card_count - 1)
        self.assertNotIn(1, self.amazon_api.users[fake_email_1]["payment_cards"])

    def test_show_addresses_success(self):
        """Test showing addresses for the current user."""
        result = self.amazon_api.show_addresses(self.user1)
        self.assertTrue(result["addresses_status"])
        self.assertGreater(len(result["addresses"]), 0)
        self.assertEqual(result["addresses"][0]["name"], "Home Address")

    def test_add_address_success(self):
        """Test adding a new address successfully."""
        initial_address_count = len(self.amazon_api.users[fake_email_1]["addresses"])
        result = self.amazon_api.add_address(
            name="Work Address",
            street_address="456 Office Rd",
            city="Workville",
            state="NY",
            country="USA",
            zip_code=67890,
            user=self.user1
        )
        self.assertTrue(result["add_status"])
        self.assertEqual(len(self.amazon_api.users[fake_email_1]["addresses"]), initial_address_count + 1)
        self.assertIn("address_id", result)

    def test_delete_address_success(self):
        """Test deleting an existing address."""
        initial_address_count = len(self.amazon_api.users[fake_email_1]["addresses"])
        result = self.amazon_api.delete_address(address_id=1, user=self.user1)
        self.assertTrue(result["delete_status"])
        self.assertEqual(len(self.amazon_api.users[fake_email_1]["addresses"]), initial_address_count - 1)
        self.assertNotIn(1, self.amazon_api.users[fake_email_1]["addresses"])

    def test_show_prime_plans_success(self):
        """Test showing available Prime plans."""
        result = self.amazon_api.show_prime_plans()
        self.assertTrue(result["prime_plans_status"])
        self.assertIn("monthly", result["prime_plans"])
        self.assertIn("yearly", result["prime_plans"])

    def test_subscribe_prime_monthly_success(self):
        """Test subscribing to a monthly Prime plan."""
        initial_prime_sub_count = len(self.amazon_api.users[fake_email_1]["prime_subscriptions"])
        result = self.amazon_api.subscribe_prime(payment_card_id=1, duration="monthly", user=self.user1)
        self.assertTrue(result["subscribe_status"])
        self.assertEqual(len(self.amazon_api.users[fake_email_1]["prime_subscriptions"]), initial_prime_sub_count + 1)
        self.assertIn("prime_subscription_id", result)
        new_sub_id = result["prime_subscription_id"]
        self.assertEqual(self.amazon_api.users[fake_email_1]["prime_subscriptions"][new_sub_id]["plan"], "monthly")

    def test_subscribe_prime_invalid_card(self):
        """Test subscribing to Prime with an invalid payment card."""
        result = self.amazon_api.subscribe_prime(payment_card_id=999, duration="monthly", user=self.user1)
        self.assertFalse(result["subscribe_status"])
        self.assertIn("Payment card with ID 999 not found.", result["message"])

    def test_show_prime_subscriptions_success(self):
        """Test showing current user's Prime subscriptions."""
        # A default subscription exists in DEFAULT_STATE
        result = self.amazon_api.show_prime_subscriptions(self.user1)
        self.assertTrue(result["subscriptions_status"])
        self.assertGreater(len(result["prime_subscriptions"]), 0)
        self.assertEqual(result["prime_subscriptions"][0]["plan"], "monthly")

    # --- Unit Tests for Combined Functionality (Audio Calling Scenarios) ---

    def test_search_add_to_cart_and_checkout(self):
        """
        Scenario: Search for a product, add it to the cart, and then place an order.
        Functions: search_products, add_product_to_cart, place_order
        """
        # 1. Search for a product (e.g., "Wireless Mouse")
        search_result = self.amazon_api.search_products(query="mouse")
        self.assertTrue(search_result["products_status"])
        self.assertGreater(len(search_result["products"]), 0)
        mouse_product_id = search_result["products"][0]["product_id"]
        initial_mouse_stock = self.amazon_api.products[mouse_product_id]["stock"]

        # 2. Add the product to the cart
        add_to_cart_result = self.amazon_api.add_product_to_cart(
            product_id=mouse_product_id, quantity=1, clear_cart_first=True, user=self.user1
        )
        self.assertTrue(add_to_cart_result["add_status"])
        self.assertEqual(self.amazon_api.users[fake_email_1]["cart"][mouse_product_id], 1)

        # 3. Place the order
        place_order_result = self.amazon_api.place_order(payment_card_id=1, address_id=1, user=self.user1)
        self.assertTrue(place_order_result["order_status"])
        self.assertIn("order_id", place_order_result)
        self.assertEqual(self.amazon_api.users[fake_email_1]["cart"], {}) # Cart should be empty
        self.assertEqual(self.amazon_api.products[mouse_product_id]["stock"], initial_mouse_stock - 1)

    def test_add_address_and_place_order(self):
        """
        Scenario: Add a new shipping address, then place an order using that new address.
        Functions: add_address, add_product_to_cart, place_order
        """
        # 1. Add a new address
        add_address_result = self.amazon_api.add_address(
            name="Vacation Home",
            street_address="789 Beach Blvd",
            city="Seaside",
            state="CA",
            country="USA",
            zip_code=90210,
            user=self.user1
        )
        self.assertTrue(add_address_result["add_status"])
        new_address_id = add_address_result["address_id"]

        # 2. Add a product to cart
        self.amazon_api.add_product_to_cart(product_id=3, quantity=1, clear_cart_first=True, user=self.user1)

        # 3. Place the order using the new address
        place_order_result = self.amazon_api.place_order(payment_card_id=1, address_id=new_address_id, user=self.user1)
        self.assertTrue(place_order_result["order_status"])
        order_id = place_order_result["order_id"]

        # Verify the order used the correct address
        order_details = self.amazon_api.users[fake_email_1]["orders"][order_id]
        self.assertEqual(order_details["shipping_address"]["address_id"], new_address_id)
        self.assertEqual(order_details["shipping_address"]["name"], "Vacation Home")

    def test_add_to_wishlist_then_move_to_cart_and_checkout(self):
        """
        Scenario: Add a product to wishlist, move it to cart, then checkout.
        Functions: add_product_to_wish_list, move_product_from_wish_list_to_cart, place_order
        """
        # 1. Add a product to wishlist
        add_wishlist_result = self.amazon_api.add_product_to_wish_list(
            product_id=1, quantity=1, clear_wish_list_first=True, user=self.user1
        )
        self.assertTrue(add_wishlist_result["add_status"])
        self.assertEqual(self.amazon_api.users[fake_email_1]["wish_list"][1], 1)
        initial_laptop_stock = self.amazon_api.products[1]["stock"]

        # 2. Move product from wishlist to cart
        move_to_cart_result = self.amazon_api.move_product_from_wish_list_to_cart(
            product_id=1, quantity=1, user=self.user1
        )
        self.assertTrue(move_to_cart_result["move_status"])
        self.assertNotIn(1, self.amazon_api.users[fake_email_1]["wish_list"]) # Should be removed from wishlist
        self.assertEqual(self.amazon_api.users[fake_email_1]["cart"][1], 1) # Should be in cart

        # 3. Place the order
        place_order_result = self.amazon_api.place_order(payment_card_id=1, address_id=1, user=self.user1)
        self.assertTrue(place_order_result["order_status"])
        self.assertEqual(self.amazon_api.users[fake_email_1]["cart"], {})
        self.assertEqual(self.amazon_api.products[1]["stock"], initial_laptop_stock - 1)

    def test_initiate_return_and_show_returns(self):
        """
        Scenario: Place an order, then initiate a return for a product in that order, and finally show returns.
        Functions: place_order, initiate_return, show_returns
        """
        # Ensure a product is in stock for the order
        self.amazon_api.products[1]["stock"] = 5 # Ensure enough stock for laptop
        
        # 1. Place an order
        self.amazon_api.add_product_to_cart(product_id=1, quantity=1, clear_cart_first=True, user=self.user1)
        place_order_result = self.amazon_api.place_order(payment_card_id=1, address_id=1, user=self.user1)
        self.assertTrue(place_order_result["order_status"])
        order_id = place_order_result["order_id"]
        
        initial_return_count = len(self.amazon_api.users[fake_email_1].get("returns", {}))

        # 2. Initiate a return for a product from that order
        initiate_return_result = self.amazon_api.initiate_return(
            order_id=order_id, product_id=1, deliverer_id=1, quantity=1, user=self.user1
        )
        self.assertTrue(initiate_return_result["initiate_status"])
        self.assertIn("return_id", initiate_return_result)
        self.assertEqual(len(self.amazon_api.users[fake_email_1]["returns"]), initial_return_count + 1)

        # 3. Show returns to verify
        show_returns_result = self.amazon_api.show_returns(self.user1)
        self.assertTrue(show_returns_result["returns_status"])
        self.assertGreater(len(show_returns_result["returns"]), 0)
        self.assertEqual(show_returns_result["returns"][0]["order_id"], order_id)
        self.assertEqual(show_returns_result["returns"][0]["product_id"], 1)

    # ================== COMPREHENSIVE TEST COVERAGE FOR MISSING METHODS ==================
    
    def test_register_user_success(self):
        """Test successful user registration with all required fields."""
        email = "newuser@test.com"
        password = "securepassword123"
        first_name = "John"
        last_name = "Doe"
        phone = "555-1234"
        
        result = self.amazon_api.register_user(
            email=email,
            password=password, 
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        
        self.assertTrue(result["registration_status"])
        self.assertIn(email, self.amazon_api.state["users"])
        self.assertEqual(self.amazon_api.state["users"][email]["email"], email)
        self.assertEqual(self.amazon_api.state["users"][email]["first_name"], first_name)
        self.assertEqual(self.amazon_api.state["users"][email]["last_name"], last_name)
        self.assertEqual(self.amazon_api.state["users"][email]["phone"], phone)

    def test_register_user_duplicate_email(self):
        """Test registration with existing email."""
        result = self.amazon_api.register_user(
            email=fake_email_1,
            password="password123",
            first_name="Test",
            last_name="User",
            phone="555-0000"
        )
        
        self.assertFalse(result["registration_status"])
        self.assertIn("already registered", result["registration_message"])

    def test_login_user_success(self):
        """Test successful user login with correct credentials."""
        # Use existing user from DEFAULT_STATE
        user_data = list(DEFAULT_STATE["users"].values())[0]
        email = user_data["email"]
        password = user_data["password"]
        
        result = self.amazon_api.login_user(email=email, password=password)
        
        self.assertTrue(result["login_status"])
        self.assertEqual(result["user_id"], email)

    def test_login_user_invalid_credentials(self):
        """Test login with invalid password."""
        user_data = list(DEFAULT_STATE["users"].values())[0]
        email = user_data["email"]
        
        result = self.amazon_api.login_user(email=email, password="wrongpassword")
        
        self.assertFalse(result["login_status"])
        self.assertIn("Invalid email or password", result["login_message"])

    def test_login_user_nonexistent_email(self):
        """Test login with non-existent email."""
        result = self.amazon_api.login_user(email="nonexistent@test.com", password="password")
        
        self.assertFalse(result["login_status"])
        self.assertIn("Invalid email or password", result["login_message"])

    def test_submit_product_review_success(self):
        """Test submitting a product review successfully."""
        # Get a product from DEFAULT_STATE
        product_id = list(DEFAULT_STATE["products"].keys())[0]
        
        result = self.amazon_api.submit_product_review(
            user_id=fake_email_1,
            product_id=product_id,
            rating=5,
            review_text="Excellent product! Highly recommend."
        )
        
        self.assertTrue(result["review_status"])
        self.assertIn("review_id", result)

    def test_submit_product_review_invalid_rating(self):
        """Test submitting review with invalid rating."""
        product_id = list(DEFAULT_STATE["products"].keys())[0]
        
        result = self.amazon_api.submit_product_review(
            user_id=fake_email_1,
            product_id=product_id,
            rating=6,  # Invalid rating > 5
            review_text="Test review"
        )
        
        self.assertFalse(result["review_status"])
        self.assertIn("Rating must be between 1 and 5", result["review_message"])

    def test_show_product_reviews_success(self):
        """Test showing product reviews."""
        # Use a product that has reviews in DEFAULT_STATE
        product_id = list(DEFAULT_STATE["product_reviews"].keys())[0]
        
        result = self.amazon_api.show_product_reviews(product_id=product_id)
        
        self.assertTrue(result["reviews_status"])
        self.assertIn("reviews", result)
        self.assertIsInstance(result["reviews"], list)

    def test_show_product_reviews_no_reviews(self):
        """Test showing reviews for product with no reviews."""
        # Use a product ID that doesn't exist in reviews
        result = self.amazon_api.show_product_reviews(product_id="nonexistent_product")
        
        self.assertTrue(result["reviews_status"])
        self.assertEqual(len(result["reviews"]), 0)

    def test_ask_product_question_success(self):
        """Test asking a product question."""
        product_id = list(DEFAULT_STATE["products"].keys())[0]
        
        result = self.amazon_api.ask_product_question(
            user_id=fake_email_1,
            product_id=product_id,
            question="What is the warranty period for this product?"
        )
        
        self.assertTrue(result["question_status"])
        self.assertIn("question_id", result)

    def test_ask_product_question_invalid_user(self):
        """Test asking question with invalid user."""
        product_id = list(DEFAULT_STATE["products"].keys())[0]
        
        result = self.amazon_api.ask_product_question(
            user_id="nonexistent@test.com",
            product_id=product_id,
            question="Test question?"
        )
        
        self.assertFalse(result["question_status"])
        self.assertIn("User not found", result["question_message"])

    def test_answer_product_question_success(self):
        """Test answering a product question."""
        # First ask a question
        product_id = list(DEFAULT_STATE["products"].keys())[0]
        ask_result = self.amazon_api.ask_product_question(
            user_id=fake_email_1,
            product_id=product_id,
            question="Test question?"
        )
        question_id = ask_result["question_id"]
        
        # Then answer it
        result = self.amazon_api.answer_product_question(
            user_id=fake_email_1,
            question_id=question_id,
            answer="This is a test answer."
        )
        
        self.assertTrue(result["answer_status"])

    def test_show_product_questions_success(self):
        """Test showing product questions."""
        # Use a product that has questions in DEFAULT_STATE
        if DEFAULT_STATE["product_questions"]:
            product_id = list(DEFAULT_STATE["product_questions"].keys())[0]
            
            result = self.amazon_api.show_product_questions(product_id=product_id)
            
            self.assertTrue(result["questions_status"])
            self.assertIn("questions", result)
            self.assertIsInstance(result["questions"], list)

    def test_comprehensive_wishlist_operations(self):
        """Test complete wishlist functionality."""
        product_id = list(DEFAULT_STATE["products"].keys())[0]
        
        # 1. Add to wishlist
        add_result = self.amazon_api.add_to_wish_list(
            user_id=fake_email_1,
            product_id=product_id
        )
        self.assertTrue(add_result["wishlist_status"])
        
        # 2. Show wishlist
        show_result = self.amazon_api.show_wish_list(user_id=fake_email_1)
        self.assertTrue(show_result["wishlist_status"])
        self.assertGreater(len(show_result["wishlist"]), 0)
        
        # 3. Remove from wishlist
        remove_result = self.amazon_api.remove_from_wish_list(
            user_id=fake_email_1,
            product_id=product_id
        )
        self.assertTrue(remove_result["wishlist_status"])

    def test_apply_promo_code_success(self):
        """Test applying valid promo code to cart."""
        # First add item to cart
        product_id = list(DEFAULT_STATE["products"].keys())[0]
        self.amazon_api.add_to_cart(fake_email_1, product_id, 1)
        
        # Get a valid promo code from DEFAULT_STATE
        promo_code = "SUMMERFUN"
        
        result = self.amazon_api.apply_promo_code_to_cart(
            promo_code=promo_code,
            user_id=fake_email_1
        )
        
        self.assertTrue(result["promo_status"])
        self.assertIn("discount_applied", result)

    def test_apply_promo_code_invalid(self):
        """Test applying invalid promo code."""
        # First add item to cart
        product_id = list(DEFAULT_STATE["products"].keys())[0]
        self.amazon_api.add_to_cart(fake_email_1, product_id, 1)
        
        result = self.amazon_api.apply_promo_code_to_cart(
            promo_code="INVALID_CODE",
            user_id=fake_email_1
        )
        
        self.assertFalse(result["promo_status"])
        self.assertIn("Invalid promo code", result["promo_message"])

    def test_remove_promo_code_success(self):
        """Test removing promo code from cart."""
        # First add item and apply promo code
        product_id = list(DEFAULT_STATE["products"].keys())[0]
        self.amazon_api.add_to_cart(fake_email_1, product_id, 1)
        self.amazon_api.apply_promo_code_to_cart("SUMMERFUN", fake_email_1)
        
        result = self.amazon_api.remove_promo_code_from_cart(user_id=fake_email_1)
        
        self.assertTrue(result["promo_status"])

    def test_get_seller_info_success(self):
        """Test getting seller information."""
        # Get a seller ID from DEFAULT_STATE
        if DEFAULT_STATE["sellers"]:
            seller_id = 1  # Use first seller ID
            
            result = self.amazon_api.get_seller_info(seller_id=seller_id)
            
            self.assertTrue(result["seller_status"])
            self.assertIn("seller", result)

    def test_get_seller_info_not_found(self):
        """Test getting info for non-existent seller."""
        result = self.amazon_api.get_seller_info(seller_id=99999)
        
        self.assertFalse(result["seller_status"])
        self.assertIn("Seller not found", result["seller_message"])

    def test_comprehensive_cart_operations(self):
        """Test comprehensive cart operations with detailed verification."""
        product_id = list(DEFAULT_STATE["products"].keys())[0]
        
        # 1. Add to cart
        add_result = self.amazon_api.add_to_cart(fake_email_1, product_id, 2)
        self.assertTrue(add_result["cart_status"])
        
        # 2. Show cart
        show_result = self.amazon_api.show_cart(user_id=fake_email_1)
        self.assertTrue(show_result["cart_status"])
        self.assertGreater(len(show_result["cart"]), 0)
        
        # 3. Update quantity
        update_result = self.amazon_api.update_cart_item_quantity(fake_email_1, product_id, 3)
        self.assertTrue(update_result["cart_status"])
        
        # 4. Apply promo code
        promo_result = self.amazon_api.apply_promo_code_to_cart("SUMMERFUN", fake_email_1)
        if promo_result["promo_status"]:
            self.assertIn("discount_applied", promo_result)
        
        # 5. Remove from cart
        remove_result = self.amazon_api.remove_from_cart(fake_email_1, product_id)
        self.assertTrue(remove_result["cart_status"])

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
