import unittest
from copy import deepcopy
from AmazonApis import AmazonApis

class TestAmazonApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh AmazonApis instance for each test"""
        self.api = AmazonApis()
        # Load a basic scenario with one user, one product, and logged in user
        self.basic_scenario = {
            "users": {
                "user1": {"name": "Test User", "email": "test@example.com"}
            },
            "current_user": "user1",
            "products": {
                1: {"name": "Test Product", "price": 9.99, "stock": 10}
            },
            "next_id_counters": {
                "product": 2,
                "order": 1,
                "payment_card": 1,
                "address": 1
            }
        }
        self.api._load_scenario(self.basic_scenario)

    # Test helper functions
    def test_load_scenario(self):
        """Test that scenario loading works correctly"""
        self.assertEqual(self.api.current_user, "user1")
        self.assertEqual(len(self.api.products), 1)
        self.assertEqual(self.api.products[1]["name"], "Test Product")

    def test_get_next_id(self):
        """Test ID generation"""
        self.assertEqual(self.api._get_next_id("product"), 2)
        self.assertEqual(self.api._get_next_id("product"), 3)
        self.assertEqual(self.api._get_next_id("order"), 1)
        self.assertEqual(self.api._get_next_id("order"), 2)

    # Test product-related functions
    def test_show_product(self):
        """Test showing a product"""
        self.assertEqual(self.api.show_product(1), {"product_status": True})
        self.assertEqual(self.api.show_product(999), {"product_status": False})

    def test_search_products(self):
        """Test product search"""
        self.assertEqual(self.api.search_products("test", 1, 10), {"search_status": True})

    # Test cart-related functions
    def test_show_cart(self):
        """Test showing cart"""
        self.assertEqual(self.api.show_cart(), {"cart_status": True})
        
        # Test with no user logged in
        self.api.current_user = None
        self.assertEqual(self.api.show_cart(), {"cart_status": False})

    def test_add_product_to_cart(self):
        """Test adding product to cart"""
        # Successful add
        self.assertEqual(self.api.add_product_to_cart(1, 2), {"add_status": True})
        self.assertEqual(self.api.carts["user1"][1]["quantity"], 2)
        
        # Add same product again
        self.assertEqual(self.api.add_product_to_cart(1, 3), {"add_status": True})
        self.assertEqual(self.api.carts["user1"][1]["quantity"], 5)
        
        # Add new product
        self.api.products[2] = {"name": "Another Product", "price": 5.99, "stock": 5}
        self.assertEqual(self.api.add_product_to_cart(2, 1), {"add_status": True})
        self.assertEqual(len(self.api.carts["user1"]), 2)
        
        # Test failures
        self.assertEqual(self.api.add_product_to_cart(999, 1), {"add_status": False})  # Invalid product
        self.api.current_user = None
        self.assertEqual(self.api.add_product_to_cart(1, 1), {"add_status": False})  # No user

    def test_update_product_quantity_in_cart(self):
        """Test updating product quantity in cart"""
        # Setup cart first
        self.api.add_product_to_cart(1, 2)
        
        # Successful update
        self.assertEqual(self.api.update_product_quantity_in_cart(1, 5), {"update_status": True})
        self.assertEqual(self.api.carts["user1"][1]["quantity"], 5)
        
        # Test failures
        self.assertEqual(self.api.update_product_quantity_in_cart(999, 1), {"update_status": False})  # Invalid product
        self.api.current_user = None
        self.assertEqual(self.api.update_product_quantity_in_cart(1, 1), {"update_status": False})  # No user

    def test_delete_product_from_cart(self):
        """Test deleting product from cart"""
        # Setup cart first
        self.api.add_product_to_cart(1, 2)
        
        # Successful delete
        self.assertEqual(self.api.delete_product_from_cart(1), {"delete_status": True})
        self.assertEqual(len(self.api.carts["user1"]), 0)
        
        # Test failures
        self.assertEqual(self.api.delete_product_from_cart(999), {"delete_status": False})  # Invalid product
        self.api.current_user = None
        self.assertEqual(self.api.delete_product_from_cart(1), {"delete_status": False})  # No user

    def test_clear_cart(self):
        """Test clearing cart"""
        # Setup cart first
        self.api.add_product_to_cart(1, 2)
        self.api.add_product_to_cart(2, 1) if 2 in self.api.products else None
        
        # Successful clear
        self.assertEqual(self.api.clear_cart(), {"clear_status": True})
        self.assertEqual(len(self.api.carts["user1"]), 0)
        
        # Test failures
        self.api.current_user = None
        self.assertEqual(self.api.clear_cart(), {"clear_status": False})  # No user

    # Test wishlist-related functions
    def test_show_wish_list(self):
        """Test showing wishlist"""
        self.assertEqual(self.api.show_wish_list(), {"wishlist_status": True})
        
        # Test with no user logged in
        self.api.current_user = None
        self.assertEqual(self.api.show_wish_list(), {"wishlist_status": False})

    def test_add_product_to_wish_list(self):
        """Test adding product to wishlist"""
        # Successful add
        self.assertEqual(self.api.add_product_to_wish_list(1, 2), {"add_status": True})
        self.assertEqual(self.api.wishlists["user1"][1]["quantity"], 2)
        
        # Add same product again
        self.assertEqual(self.api.add_product_to_wish_list(1, 3), {"add_status": True})
        self.assertEqual(self.api.wishlists["user1"][1]["quantity"], 5)
        
        # Add new product
        self.api.products[2] = {"name": "Another Product", "price": 5.99, "stock": 5}
        self.assertEqual(self.api.add_product_to_wish_list(2, 1), {"add_status": True})
        self.assertEqual(len(self.api.wishlists["user1"]), 2)
        
        # Test failures
        self.assertEqual(self.api.add_product_to_wish_list(999, 1), {"add_status": False})  # Invalid product
        self.api.current_user = None
        self.assertEqual(self.api.add_product_to_wish_list(1, 1), {"add_status": False})  # No user

    def test_delete_product_from_wish_list(self):
        """Test deleting product from wishlist"""
        # Setup wishlist first
        self.api.add_product_to_wish_list(1, 2)
        
        # Successful delete
        self.assertEqual(self.api.delete_product_from_wish_list(1), {"delete_status": True})
        self.assertEqual(len(self.api.wishlists["user1"]), 0)
        
        # Test failures
        self.assertEqual(self.api.delete_product_from_wish_list(999), {"delete_status": False})  # Invalid product
        self.api.current_user = None
        self.assertEqual(self.api.delete_product_from_wish_list(1), {"delete_status": False})  # No user

    def test_clear_wish_list(self):
        """Test clearing wishlist"""
        # Setup wishlist first
        self.api.add_product_to_wish_list(1, 2)
        self.api.add_product_to_wish_list(2, 1) if 2 in self.api.products else None
        
        # Successful clear
        self.assertEqual(self.api.clear_wish_list(), {"clear_status": True})
        self.assertEqual(len(self.api.wishlists["user1"]), 0)
        
        # Test failures
        self.api.current_user = None
        self.assertEqual(self.api.clear_wish_list(), {"clear_status": False})  # No user

    # Test order-related functions
    def test_show_orders(self):
        """Test showing orders"""
        self.assertEqual(self.api.show_orders("", 1, 10), {"orders_status": True})
        
        # Test with no user logged in
        self.api.current_user = None
        self.assertEqual(self.api.show_orders("", 1, 10), {"orders_status": False})

    def test_show_order(self):
        """Test showing specific order"""
        # Setup an order first
        self.api.orders[1] = {"user": "user1", "items": {}, "status": "placed"}
        
        self.assertEqual(self.api.show_order(1), {"order_status": True})
        self.assertEqual(self.api.show_order(999), {"order_status": False})  # Invalid order
        
        # Test with no user logged in
        self.api.current_user = None
        self.assertEqual(self.api.show_order(1), {"order_status": False})

    def test_place_order(self):
        """Test placing an order"""
        # Setup required data
        self.api.add_product_to_cart(1, 2)
        payment_card_id = self.api._get_next_id("payment_card")
        self.api.payment_cards[payment_card_id] = {
            "user": "user1",
            "card_name": "Test Card",
            "card_number": "4111111111111111",
            "expiry_date": "12/25",
            "cvv": "123"
        }
        address_id = self.api._get_next_id("address")
        self.api.addresses[address_id] = {
            "user": "user1",
            "name": "Home",
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip_code": "12345",
            "country": "USA"
        }
        
        # Successful order
        result = self.api.place_order(payment_card_id, address_id)
        self.assertEqual(result, {"order_status": True})
        self.assertEqual(len(self.api.orders), 1)
        self.assertEqual(len(self.api.carts["user1"]), 0)  # Cart should be cleared
        
        # Test failures
        self.assertEqual(self.api.place_order(999, address_id), {"order_status": False})  # Invalid payment card
        self.assertEqual(self.api.place_order(payment_card_id, 999), {"order_status": False})  # Invalid address
        self.api.current_user = None
        self.assertEqual(self.api.place_order(payment_card_id, address_id), {"order_status": False})  # No user

    # Test payment card functions
    def test_show_payment_cards(self):
        """Test showing payment cards"""
        self.assertEqual(self.api.show_payment_cards(), {"cards_status": True})
        
        # Test with no user logged in
        self.api.current_user = None
        self.assertEqual(self.api.show_payment_cards(), {"cards_status": False})

    def test_add_payment_card(self):
        """Test adding a payment card"""
        result = self.api.add_payment_card("Test Card", "4111111111111111", "12/25", "123")
        self.assertEqual(result, {"add_status": True})
        self.assertEqual(len(self.api.payment_cards), 1)
        
        # Test with no user logged in
        self.api.current_user = None
        self.assertEqual(self.api.add_payment_card("Test Card", "4111111111111111", "12/25", "123"), 
                         {"add_status": False})

    def test_delete_payment_card(self):
        """Test deleting a payment card"""
        # Add a card first
        self.api.add_payment_card("Test Card", "4111111111111111", "12/25", "123")
        card_id = next(iter(self.api.payment_cards.keys()))
        
        # Successful delete
        self.assertEqual(self.api.delete_payment_card(card_id), {"delete_status": True})
        self.assertEqual(len(self.api.payment_cards), 0)
        
        # Test failures
        self.assertEqual(self.api.delete_payment_card(999), {"delete_status": False})  # Invalid card
        self.api.current_user = None
        self.assertEqual(self.api.delete_payment_card(card_id), {"delete_status": False})  # No user

    # Test address functions
    def test_show_addresses(self):
        """Test showing addresses"""
        self.assertEqual(self.api.show_addresses(), {"addresses_status": True})
        
        # Test with no user logged in
        self.api.current_user = None
        self.assertEqual(self.api.show_addresses(), {"addresses_status": False})

    def test_add_address(self):
        """Test adding an address"""
        result = self.api.add_address("Home", "123 Main St", "Anytown", "CA", "12345", "USA")
        self.assertEqual(result, {"add_status": True})
        self.assertEqual(len(self.api.addresses), 1)
        
        # Test with no user logged in
        self.api.current_user = None
        self.assertEqual(self.api.add_address("Home", "123 Main St", "Anytown", "CA", "12345", "USA"), 
                         {"add_status": False})

    def test_delete_address(self):
        """Test deleting an address"""
        # Add an address first
        self.api.add_address("Home", "123 Main St", "Anytown", "CA", "12345", "USA")
        address_id = next(iter(self.api.addresses.keys()))
        
        # Successful delete
        self.assertEqual(self.api.delete_address(address_id), {"delete_status": True})
        self.assertEqual(len(self.api.addresses), 0)
        
        # Test failures
        self.assertEqual(self.api.delete_address(999), {"delete_status": False})  # Invalid address
        self.api.current_user = None
        self.assertEqual(self.api.delete_address(address_id), {"delete_status": False})  # No user

    # Test multi-function workflows
    def test_cart_to_order_workflow(self):
        """Test complete workflow from adding to cart to placing order"""
        # 1. Add product to cart
        self.assertEqual(self.api.add_product_to_cart(1, 2), {"add_status": True})
        
        # 2. Add payment method
        payment_result = self.api.add_payment_card("Test Card", "4111111111111111", "12/25", "123")
        self.assertEqual(payment_result, {"add_status": True})
        payment_card_id = next(iter(self.api.payment_cards.keys()))
        
        # 3. Add address
        address_result = self.api.add_address("Home", "123 Main St", "Anytown", "CA", "12345", "USA")
        self.assertEqual(address_result, {"add_status": True})
        address_id = next(iter(self.api.addresses.keys()))
        
        # 4. Place order
        order_result = self.api.place_order(payment_card_id, address_id)
        self.assertEqual(order_result, {"order_status": True})
        
        # Verify results
        self.assertEqual(len(self.api.orders), 1)
        self.assertEqual(len(self.api.carts["user1"]), 0)  # Cart should be empty
        order = next(iter(self.api.orders.values()))
        self.assertEqual(order["user"], "user1")
        self.assertEqual(order["items"][1]["quantity"], 2)

    def test_wishlist_to_cart_workflow(self):
        """Test workflow from adding to wishlist to moving to cart"""
        # 1. Add product to wishlist
        self.assertEqual(self.api.add_product_to_wish_list(1, 1), {"add_status": True})
        
        # 2. Delete from wishlist and add to cart
        self.assertEqual(self.api.delete_product_from_wish_list(1), {"delete_status": True})
        self.assertEqual(self.api.add_product_to_cart(1, 1), {"add_status": True})
        
        # Verify results
        self.assertEqual(len(self.api.wishlists["user1"]), 0)
        self.assertEqual(len(self.api.carts["user1"]), 1)
        self.assertEqual(self.api.carts["user1"][1]["quantity"], 1)

    def test_user_registration_workflow(self):
        """Test a new user registration and setup workflow"""
        # 1. Create a new user (simulate registration)
        new_api = AmazonApis()
        scenario = {
            "users": {
                "new_user": {"name": "New User", "email": "new@example.com"}
            },
            "current_user": "new_user",
            "products": {
                1: {"name": "Test Product", "price": 9.99, "stock": 10}
            }
        }
        new_api._load_scenario(scenario)
        
        # 2. Add payment method
        payment_result = new_api.add_payment_card("New Card", "4222222222222222", "06/26", "456")
        self.assertEqual(payment_result, {"add_status": True})
        
        # 3. Add address
        address_result = new_api.add_address("Work", "456 Office Blvd", "Businesstown", "NY", "54321", "USA")
        self.assertEqual(address_result, {"add_status": True})
        
        # 4. Add product to cart
        cart_result = new_api.add_product_to_cart(1, 1)
        self.assertEqual(cart_result, {"add_status": True})
        
        # 5. Place order
        payment_card_id = next(iter(new_api.payment_cards.keys()))
        address_id = next(iter(new_api.addresses.keys()))
        order_result = new_api.place_order(payment_card_id, address_id)
        self.assertEqual(order_result, {"order_status": True})
        
        # Verify results
        self.assertEqual(len(new_api.orders), 1)
        self.assertEqual(len(new_api.carts["new_user"]), 0)

if __name__ == "__main__":
    unittest.main()