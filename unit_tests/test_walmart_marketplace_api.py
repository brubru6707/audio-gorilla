import unittest
from WalmartMarketplaceApis import WalmartMarketplaceAPI

class TestWalmartMarketplaceAPI(unittest.TestCase):
    def setUp(self):
        self.api = WalmartMarketplaceAPI()

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - ITEMS METHODS
    # ============================================================================

    def test_get_items_basic(self):
        """Test basic get_items functionality"""
        resp = self.api.get_items()
        self.assertIn("items", resp)
        self.assertIn("pagination", resp)
        self.assertIsInstance(resp["items"], list)

    def test_get_items_with_limit(self):
        """Test get_items with limit parameter"""
        resp = self.api.get_items(limit=1)
        self.assertLessEqual(len(resp["items"]), 1)
        self.assertEqual(resp["pagination"]["limit"], 1)

    def test_get_items_with_offset(self):
        """Test get_items with offset parameter"""
        resp = self.api.get_items(offset=1)
        self.assertEqual(resp["pagination"]["offset"], 1)

    def test_get_item_basic(self):
        """Test basic get_item functionality"""
        resp = self.api.get_item("SKU001")
        self.assertEqual(resp["sku"], "SKU001")
        self.assertIn("product_name", resp)

    def test_get_item_nonexistent(self):
        """Test get_item with nonexistent SKU"""
        resp = self.api.get_item("NONEXISTENT_SKU")
        self.assertIn("error", resp)
        self.assertEqual(resp["sku"], "NONEXISTENT_SKU")

    def test_update_item_basic(self):
        """Test basic update_item functionality"""
        update_data = {"product_name": "Updated Name", "price": 99.99}
        resp = self.api.update_item("SKU001", update_data)
        self.assertEqual(resp["status"], "success")
        
        # Verify the update
        item = self.api.get_item("SKU001")
        self.assertEqual(item["product_name"], "Updated Name")
        self.assertEqual(item["price"], 99.99)

    def test_update_item_nonexistent(self):
        """Test update_item with nonexistent SKU"""
        resp = self.api.update_item("NONEXISTENT_SKU", {"product_name": "Test"})
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_retire_item_basic(self):
        """Test basic retire_item functionality"""
        resp = self.api.retire_item("SKU001")
        self.assertEqual(resp["status"], "success")
        
        # Verify the item is retired
        item = self.api.get_item("SKU001")
        self.assertEqual(item["status"], "Retired")

    def test_retire_item_nonexistent(self):
        """Test retire_item with nonexistent SKU"""
        resp = self.api.retire_item("NONEXISTENT_SKU")
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_bulk_item_upload_basic(self):
        """Test basic bulk_item_upload functionality"""
        file_content = b"<xml>bulk item data</xml>"
        resp = self.api.bulk_item_upload(file_content, "xml")
        self.assertIn("feed_id", resp)
        self.assertEqual(resp["status"], "Submitted")

    def test_bulk_item_upload_xlsx(self):
        """Test bulk_item_upload with xlsx file type"""
        file_content = b"xlsx content"
        resp = self.api.bulk_item_upload(file_content, "xlsx")
        self.assertIn("feed_id", resp)
        self.assertEqual(resp["status"], "Submitted")

    def test_get_bulk_item_status_basic(self):
        """Test basic get_bulk_item_status functionality"""
        # First create a feed
        file_content = b"<xml>test</xml>"
        upload_resp = self.api.bulk_item_upload(file_content, "xml")
        feed_id = upload_resp["feed_id"]
        
        # Get status
        resp = self.api.get_bulk_item_status(feed_id)
        self.assertEqual(resp["status"], "Completed")
        self.assertEqual(resp["feed_id"], feed_id)

    def test_get_bulk_item_status_nonexistent(self):
        """Test get_bulk_item_status with nonexistent feed"""
        resp = self.api.get_bulk_item_status("NONEXISTENT_FEED")
        self.assertIn("error", resp)
        self.assertEqual(resp["feed_id"], "NONEXISTENT_FEED")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - INVENTORY METHODS
    # ============================================================================

    def test_get_inventory_basic(self):
        """Test basic get_inventory functionality"""
        resp = self.api.get_inventory("SKU001")
        self.assertIn("quantity", resp)
        self.assertIn("fulfillment_center_id", resp)

    def test_get_inventory_nonexistent(self):
        """Test get_inventory with nonexistent SKU"""
        resp = self.api.get_inventory("NONEXISTENT_SKU")
        self.assertIn("error", resp)
        self.assertEqual(resp["sku"], "NONEXISTENT_SKU")

    def test_update_inventory_basic(self):
        """Test basic update_inventory functionality"""
        resp = self.api.update_inventory("SKU001", 50)
        self.assertEqual(resp["status"], "success")
        
        # Verify the update
        inv = self.api.get_inventory("SKU001")
        self.assertEqual(inv["quantity"], 50)

    def test_update_inventory_with_fulfillment_center(self):
        """Test update_inventory with fulfillment_center_id parameter"""
        resp = self.api.update_inventory("SKU001", 100, "FC003")
        self.assertEqual(resp["status"], "success")
        
        # Verify the update
        inv = self.api.get_inventory("SKU001")
        self.assertEqual(inv["quantity"], 100)
        self.assertEqual(inv["fulfillment_center_id"], "FC003")

    def test_update_inventory_nonexistent(self):
        """Test update_inventory with nonexistent SKU"""
        resp = self.api.update_inventory("NONEXISTENT_SKU", 100)
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_bulk_inventory_update_basic(self):
        """Test basic bulk_inventory_update functionality"""
        file_content = b"<xml>inventory data</xml>"
        resp = self.api.bulk_inventory_update(file_content, "xml")
        self.assertIn("feed_id", resp)
        self.assertEqual(resp["status"], "Submitted")

    def test_bulk_inventory_update_xlsx(self):
        """Test bulk_inventory_update with xlsx file type"""
        file_content = b"xlsx inventory content"
        resp = self.api.bulk_inventory_update(file_content, "xlsx")
        self.assertIn("feed_id", resp)
        self.assertEqual(resp["status"], "Submitted")

    def test_get_bulk_inventory_status_basic(self):
        """Test basic get_bulk_inventory_status functionality"""
        # First create a feed
        file_content = b"<xml>test</xml>"
        upload_resp = self.api.bulk_inventory_update(file_content, "xml")
        feed_id = upload_resp["feed_id"]
        
        # Get status
        resp = self.api.get_bulk_inventory_status(feed_id)
        self.assertEqual(resp["status"], "Completed")
        self.assertEqual(resp["feed_id"], feed_id)

    def test_get_bulk_inventory_status_nonexistent(self):
        """Test get_bulk_inventory_status with nonexistent feed"""
        resp = self.api.get_bulk_inventory_status("NONEXISTENT_FEED")
        self.assertIn("error", resp)
        self.assertEqual(resp["feed_id"], "NONEXISTENT_FEED")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - ORDERS METHODS
    # ============================================================================

    def test_get_orders_basic(self):
        """Test basic get_orders functionality"""
        resp = self.api.get_orders()
        self.assertIn("orders", resp)
        self.assertIn("pagination", resp)
        self.assertIsInstance(resp["orders"], list)

    def test_get_orders_with_status(self):
        """Test get_orders with status parameter"""
        resp = self.api.get_orders(status="Created")
        self.assertIn("orders", resp)
        for order in resp["orders"]:
            self.assertEqual(order["status"], "Created")

    def test_get_orders_with_limit(self):
        """Test get_orders with limit parameter"""
        resp = self.api.get_orders(limit=1)
        self.assertLessEqual(len(resp["orders"]), 1)
        self.assertEqual(resp["pagination"]["limit"], 1)

    def test_get_orders_with_dates(self):
        """Test get_orders with date parameters"""
        resp = self.api.get_orders(created_start_date="2024-01-01T00:00:00Z", 
                                  created_end_date="2024-12-31T23:59:59Z")
        self.assertIn("orders", resp)

    def test_get_order_basic(self):
        """Test basic get_order functionality"""
        resp = self.api.get_order("PO001")
        self.assertEqual(resp["purchase_order_id"], "PO001")
        self.assertIn("order_date", resp)

    def test_get_order_nonexistent(self):
        """Test get_order with nonexistent order"""
        resp = self.api.get_order("NONEXISTENT_PO")
        self.assertIn("error", resp)
        self.assertEqual(resp["purchase_order_id"], "NONEXISTENT_PO")

    def test_acknowledge_order_basic(self):
        """Test basic acknowledge_order functionality"""
        ack_data = {"ack": True, "acknowledgement_date": "2024-01-15T10:30:00Z"}
        resp = self.api.acknowledge_order("PO001", ack_data)
        self.assertEqual(resp["status"], "success")
        
        # Verify the order is acknowledged
        order = self.api.get_order("PO001")
        self.assertEqual(order["status"], "Acknowledged")

    def test_acknowledge_order_nonexistent(self):
        """Test acknowledge_order with nonexistent order"""
        resp = self.api.acknowledge_order("NONEXISTENT_PO", {"ack": True})
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_ship_order_basic(self):
        """Test basic ship_order functionality"""
        ship_data = {"carrier": "UPS", "tracking_number": "123456789", "ship_date": "2024-01-16T10:30:00Z"}
        resp = self.api.ship_order("PO001", ship_data)
        self.assertEqual(resp["status"], "success")
        
        # Verify the order is shipped
        order = self.api.get_order("PO001")
        self.assertEqual(order["status"], "Shipped")

    def test_ship_order_nonexistent(self):
        """Test ship_order with nonexistent order"""
        resp = self.api.ship_order("NONEXISTENT_PO", {"carrier": "UPS"})
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_cancel_order_basic(self):
        """Test basic cancel_order functionality"""
        cancel_data = {"reason": "Customer request", "cancellation_date": "2024-01-15T10:30:00Z"}
        resp = self.api.cancel_order("PO001", cancel_data)
        self.assertEqual(resp["status"], "success")
        
        # Verify the order is cancelled
        order = self.api.get_order("PO001")
        self.assertEqual(order["status"], "Cancelled")

    def test_cancel_order_nonexistent(self):
        """Test cancel_order with nonexistent order"""
        resp = self.api.cancel_order("NONEXISTENT_PO", {"reason": "Test"})
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_cancel_order_already_shipped(self):
        """Test cancel_order with already shipped order"""
        # First ship the order
        self.api.ship_order("PO001", {"carrier": "UPS", "tracking": "123"})
        
        # Try to cancel it
        resp = self.api.cancel_order("PO001", {"reason": "Customer request"})
        self.assertEqual(resp["status"], "error")
        self.assertIn("cannot be cancelled", resp["errors"][0])

    def test_refund_order_basic(self):
        """Test basic refund_order functionality"""
        # First ship the order
        self.api.ship_order("PO001", {"carrier": "UPS", "tracking": "123"})
        
        # Refund the order
        refund_data = {"amount": 50.00, "reason": "Customer request"}
        resp = self.api.refund_order("PO001", refund_data)
        self.assertEqual(resp["status"], "success")
        self.assertIn("refund_id", resp)

    def test_refund_order_nonexistent(self):
        """Test refund_order with nonexistent order"""
        resp = self.api.refund_order("NONEXISTENT_PO", {"amount": 50.00})
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_refund_order_unshipped(self):
        """Test refund_order with unshipped order"""
        resp = self.api.refund_order("PO001", {"amount": 50.00})
        self.assertEqual(resp["status"], "error")
        self.assertIn("cannot be refunded", resp["errors"][0])

    def test_get_order_shipment_basic(self):
        """Test basic get_order_shipment functionality"""
        # First ship the order
        ship_data = {"carrier": "FedEx", "tracking": "987654321"}
        self.api.ship_order("PO001", ship_data)
        
        # Get shipment details
        resp = self.api.get_order_shipment("PO001")
        self.assertEqual(resp["carrier"], "FedEx")
        self.assertEqual(resp["tracking"], "987654321")

    def test_get_order_shipment_nonexistent(self):
        """Test get_order_shipment with nonexistent order"""
        resp = self.api.get_order_shipment("NONEXISTENT_PO")
        self.assertIn("error", resp)
        self.assertEqual(resp["purchase_order_id"], "NONEXISTENT_PO")

    def test_get_order_shipment_no_shipment(self):
        """Test get_order_shipment with order that has no shipment"""
        resp = self.api.get_order_shipment("PO001")
        self.assertIn("error", resp)
        self.assertIn("No shipment details found", resp["error"])

    def test_get_order_advance_shipment_notice_basic(self):
        """Test basic get_order_advance_shipment_notice functionality"""
        resp = self.api.get_order_advance_shipment_notice("PO001")
        self.assertIn("asn_id", resp)
        self.assertEqual(resp["purchase_order_id"], "PO001")
        self.assertIn("carrier", resp)
        self.assertIn("tracking_number", resp)

    def test_get_order_advance_shipment_notice_nonexistent(self):
        """Test get_order_advance_shipment_notice with nonexistent order"""
        resp = self.api.get_order_advance_shipment_notice("NONEXISTENT_PO")
        self.assertIn("error", resp)
        self.assertEqual(resp["purchase_order_id"], "NONEXISTENT_PO")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - PRICE METHODS
    # ============================================================================

    def test_get_price_basic(self):
        """Test basic get_price functionality"""
        resp = self.api.get_price("SKU001")
        self.assertIn("price", resp)

    def test_get_price_nonexistent(self):
        """Test get_price with nonexistent SKU"""
        resp = self.api.get_price("NONEXISTENT_SKU")
        self.assertIn("error", resp)
        self.assertEqual(resp["sku"], "NONEXISTENT_SKU")

    def test_update_price_basic(self):
        """Test basic update_price functionality"""
        price_data = {"price": 79.99}
        resp = self.api.update_price("SKU001", price_data)
        self.assertEqual(resp["status"], "success")
        
        # Verify the update
        price_info = self.api.get_price("SKU001")
        self.assertEqual(price_info["price"], 79.99)

    def test_update_price_nonexistent(self):
        """Test update_price with nonexistent SKU"""
        resp = self.api.update_price("NONEXISTENT_SKU", {"price": 50.00})
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_bulk_price_update_basic(self):
        """Test basic bulk_price_update functionality"""
        file_content = b"<xml>price data</xml>"
        resp = self.api.bulk_price_update(file_content, "xml")
        self.assertIn("feed_id", resp)
        self.assertEqual(resp["status"], "Submitted")

    def test_bulk_price_update_xlsx(self):
        """Test bulk_price_update with xlsx file type"""
        file_content = b"xlsx price content"
        resp = self.api.bulk_price_update(file_content, "xlsx")
        self.assertIn("feed_id", resp)
        self.assertEqual(resp["status"], "Submitted")

    def test_get_bulk_price_status_basic(self):
        """Test basic get_bulk_price_status functionality"""
        # First create a feed
        file_content = b"<xml>test</xml>"
        upload_resp = self.api.bulk_price_update(file_content, "xml")
        feed_id = upload_resp["feed_id"]
        
        # Get status
        resp = self.api.get_bulk_price_status(feed_id)
        self.assertEqual(resp["status"], "Completed")
        self.assertEqual(resp["feed_id"], feed_id)

    def test_get_bulk_price_status_nonexistent(self):
        """Test get_bulk_price_status with nonexistent feed"""
        resp = self.api.get_bulk_price_status("NONEXISTENT_FEED")
        self.assertIn("error", resp)
        self.assertEqual(resp["feed_id"], "NONEXISTENT_FEED")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - PROMOTIONS METHODS
    # ============================================================================

    def test_get_promotions_basic(self):
        """Test basic get_promotions functionality"""
        resp = self.api.get_promotions()
        self.assertIn("promotions", resp)
        self.assertIn("pagination", resp)
        self.assertIsInstance(resp["promotions"], list)

    def test_get_promotions_with_limit(self):
        """Test get_promotions with limit parameter"""
        resp = self.api.get_promotions(limit=1)
        self.assertLessEqual(len(resp["promotions"]), 1)
        self.assertEqual(resp["pagination"]["limit"], 1)

    def test_get_promotions_with_offset(self):
        """Test get_promotions with offset parameter"""
        resp = self.api.get_promotions(offset=1)
        self.assertEqual(resp["pagination"]["offset"], 1)

    def test_create_promotion_basic(self):
        """Test basic create_promotion functionality"""
        promo_data = {
            "name": "Test Promotion",
            "discount_percent": 15,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        resp = self.api.create_promotion(promo_data)
        self.assertEqual(resp["status"], "success")
        self.assertIn("promo_id", resp)

    def test_update_promotion_basic(self):
        """Test basic update_promotion functionality"""
        # First create a promotion
        promo_data = {"name": "Test Promo", "discount_percent": 10}
        create_resp = self.api.create_promotion(promo_data)
        promo_id = create_resp["promo_id"]
        
        # Update the promotion
        update_data = {"discount_percent": 20}
        resp = self.api.update_promotion(promo_id, update_data)
        self.assertEqual(resp["status"], "success")
        
        # Verify the update
        promo = self.api.get_promotion(promo_id)
        self.assertEqual(promo["discount_percent"], 20)

    def test_update_promotion_nonexistent(self):
        """Test update_promotion with nonexistent promotion"""
        resp = self.api.update_promotion("NONEXISTENT_PROMO", {"discount_percent": 25})
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_get_promotion_basic(self):
        """Test basic get_promotion functionality"""
        resp = self.api.get_promotion("PROMO001")
        self.assertEqual(resp["promo_id"], "PROMO001")
        self.assertIn("name", resp)

    def test_get_promotion_nonexistent(self):
        """Test get_promotion with nonexistent promotion"""
        resp = self.api.get_promotion("NONEXISTENT_PROMO")
        self.assertIn("error", resp)
        self.assertEqual(resp["promo_id"], "NONEXISTENT_PROMO")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - REPORTS METHODS
    # ============================================================================

    def test_get_reports_basic(self):
        """Test basic get_reports functionality"""
        resp = self.api.get_reports("item")
        self.assertIn("reports", resp)
        self.assertIn("pagination", resp)
        self.assertIsInstance(resp["reports"], list)

    def test_get_reports_with_limit(self):
        """Test get_reports with limit parameter"""
        resp = self.api.get_reports("item", limit=1)
        self.assertLessEqual(len(resp["reports"]), 1)
        self.assertEqual(resp["pagination"]["limit"], 1)

    def test_get_reports_with_offset(self):
        """Test get_reports with offset parameter"""
        resp = self.api.get_reports("item", offset=1)
        self.assertEqual(resp["pagination"]["offset"], 1)

    def test_request_report_basic(self):
        """Test basic request_report functionality"""
        report_params = {"start_date": "2024-01-01", "end_date": "2024-01-31"}
        resp = self.api.request_report("item", report_params)
        self.assertEqual(resp["status"], "success")
        self.assertIn("report_id", resp)

    def test_request_report_no_params(self):
        """Test request_report without parameters"""
        resp = self.api.request_report("inventory")
        self.assertEqual(resp["status"], "success")
        self.assertIn("report_id", resp)

    def test_download_report_basic(self):
        """Test basic download_report functionality"""
        # First request a report
        report_resp = self.api.request_report("item")
        report_id = report_resp["report_id"]
        
        # Download the report
        resp = self.api.download_report(report_id)
        self.assertIsInstance(resp, bytes)
        self.assertGreater(len(resp), 0)

    def test_download_report_nonexistent(self):
        """Test download_report with nonexistent report"""
        resp = self.api.download_report("NONEXISTENT_REPORT")
        self.assertEqual(resp, b"Report not found")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - FEEDS METHODS
    # ============================================================================

    def test_get_feeds_basic(self):
        """Test basic get_feeds functionality"""
        resp = self.api.get_feeds()
        self.assertIn("feeds", resp)
        self.assertIn("pagination", resp)
        self.assertIsInstance(resp["feeds"], list)

    def test_get_feeds_with_feed_type(self):
        """Test get_feeds with feed_type parameter"""
        resp = self.api.get_feeds(feed_type="item")
        self.assertIn("feeds", resp)

    def test_get_feeds_with_limit(self):
        """Test get_feeds with limit parameter"""
        resp = self.api.get_feeds(limit=1)
        self.assertLessEqual(len(resp["feeds"]), 1)
        self.assertEqual(resp["pagination"]["limit"], 1)

    def test_get_feeds_with_offset(self):
        """Test get_feeds with offset parameter"""
        resp = self.api.get_feeds(offset=1)
        self.assertEqual(resp["pagination"]["offset"], 1)

    def test_get_feed_status_basic(self):
        """Test basic get_feed_status functionality"""
        # First create a feed
        file_content = b"<xml>test</xml>"
        upload_resp = self.api.bulk_item_upload(file_content, "xml")
        feed_id = upload_resp["feed_id"]
        
        # Get feed status
        resp = self.api.get_feed_status(feed_id)
        self.assertEqual(resp["feed_id"], feed_id)
        self.assertIn("status", resp)

    def test_get_feed_status_nonexistent(self):
        """Test get_feed_status with nonexistent feed"""
        resp = self.api.get_feed_status("NONEXISTENT_FEED")
        self.assertIn("error", resp)
        self.assertEqual(resp["feed_id"], "NONEXISTENT_FEED")

    # ============================================================================
    # INDIVIDUAL FUNCTION TESTS - RETURNS METHODS
    # ============================================================================

    def test_get_returns_basic(self):
        """Test basic get_returns functionality"""
        resp = self.api.get_returns()
        self.assertIn("returns", resp)
        self.assertIn("pagination", resp)
        self.assertIsInstance(resp["returns"], list)

    def test_get_returns_with_status(self):
        """Test get_returns with status parameter"""
        resp = self.api.get_returns(status="Pending")
        self.assertIn("returns", resp)

    def test_get_returns_with_limit(self):
        """Test get_returns with limit parameter"""
        resp = self.api.get_returns(limit=1)
        self.assertLessEqual(len(resp["returns"]), 1)
        self.assertEqual(resp["pagination"]["limit"], 1)

    def test_get_returns_with_dates(self):
        """Test get_returns with date parameters"""
        resp = self.api.get_returns(created_start_date="2024-01-01T00:00:00Z",
                                   created_end_date="2024-12-31T23:59:59Z")
        self.assertIn("returns", resp)

    def test_get_return_basic(self):
        """Test basic get_return functionality"""
        resp = self.api.get_return("RETURN001")
        self.assertEqual(resp["return_id"], "RETURN001")

    def test_get_return_nonexistent(self):
        """Test get_return with nonexistent return"""
        resp = self.api.get_return("NONEXISTENT_RETURN")
        self.assertIn("error", resp)
        self.assertEqual(resp["return_id"], "NONEXISTENT_RETURN")

    def test_approve_return_basic(self):
        """Test basic approve_return functionality"""
        approval_data = {"approved_by": "admin", "approval_notes": "Approved"}
        resp = self.api.approve_return("RETURN001", approval_data)
        self.assertEqual(resp["status"], "success")
        
        # Verify the return is approved
        return_info = self.api.get_return("RETURN001")
        self.assertEqual(return_info["status"], "Approved")

    def test_approve_return_nonexistent(self):
        """Test approve_return with nonexistent return"""
        resp = self.api.approve_return("NONEXISTENT_RETURN", {})
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_approve_return_wrong_status(self):
        """Test approve_return with return in wrong status"""
        # First approve the return
        self.api.approve_return("RETURN001", {})
        
        # Try to approve it again
        resp = self.api.approve_return("RETURN001", {})
        self.assertEqual(resp["status"], "error")
        self.assertIn("cannot be approved", resp["errors"][0])

    def test_reject_return_basic(self):
        """Test basic reject_return functionality"""
        rejection_data = {"rejected_by": "admin", "rejection_reason": "Invalid return"}
        resp = self.api.reject_return("RETURN001", rejection_data)
        self.assertEqual(resp["status"], "success")
        
        # Verify the return is rejected
        return_info = self.api.get_return("RETURN001")
        self.assertEqual(return_info["status"], "Rejected")

    def test_reject_return_nonexistent(self):
        """Test reject_return with nonexistent return"""
        resp = self.api.reject_return("NONEXISTENT_RETURN", {})
        self.assertEqual(resp["status"], "error")
        self.assertIn("not found", resp["errors"][0])

    def test_reject_return_wrong_status(self):
        """Test reject_return with return in wrong status"""
        # First reject the return
        self.api.reject_return("RETURN001", {})
        
        # Try to reject it again
        resp = self.api.reject_return("RETURN001", {})
        self.assertEqual(resp["status"], "error")
        self.assertIn("cannot be rejected", resp["errors"][0])

    # ============================================================================
    # EDGE CASE TESTS
    # ============================================================================

    def test_zero_quantity_inventory(self):
        """Test setting inventory quantity to zero"""
        resp = self.api.update_inventory("SKU001", 0)
        self.assertEqual(resp["status"], "success")
        inv = self.api.get_inventory("SKU001")
        self.assertEqual(inv["quantity"], 0)

    def test_negative_quantity_inventory(self):
        """Test setting negative inventory quantity"""
        resp = self.api.update_inventory("SKU001", -10)
        self.assertEqual(resp["status"], "success")  # API allows negative quantities
        inv = self.api.get_inventory("SKU001")
        self.assertEqual(inv["quantity"], -10)

    def test_very_high_price(self):
        """Test setting a very high price"""
        high_price = 999999.99
        resp = self.api.update_price("SKU001", {"price": high_price})
        self.assertEqual(resp["status"], "success")
        price_info = self.api.get_price("SKU001")
        self.assertEqual(price_info["price"], high_price)

    def test_zero_price(self):
        """Test setting price to zero"""
        resp = self.api.update_price("SKU001", {"price": 0})
        self.assertEqual(resp["status"], "success")
        price_info = self.api.get_price("SKU001")
        self.assertEqual(price_info["price"], 0)

    def test_empty_file_upload(self):
        """Test uploading an empty file"""
        resp = self.api.bulk_item_upload(b"", "xml")
        self.assertIn("feed_id", resp)
        self.assertEqual(resp["status"], "Submitted")

    def test_large_file_upload(self):
        """Test uploading a large file"""
        large_content = b"x" * 1000000  # 1MB
        resp = self.api.bulk_item_upload(large_content, "xml")
        self.assertIn("feed_id", resp)
        self.assertEqual(resp["status"], "Submitted")

if __name__ == "__main__":
    unittest.main() 