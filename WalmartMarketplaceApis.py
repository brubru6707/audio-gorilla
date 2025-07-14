import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
import json

# Api Reference Docs
# https://www.npmjs.com/package/@mediocre/walmart-marketplace

class WalmartMarketplaceAPI:
    def __init__(self, client_id: str = None, client_secret: str = None, seller_id: str = None):
        """
        Initialize the Walmart Marketplace API client.
        
        Args:
            client_id (str, optional): Walmart API client ID
            client_secret (str, optional): Walmart API client secret
            seller_id (str, optional): Walmart seller ID
        """
        # Authentication state
        self.client_id = client_id
        self.client_secret = client_secret
        self.seller_id = seller_id
        self.access_token = None
        self.token_expires_at = None
        
        # Data storage
        self.items: Dict[str, Dict[str, Any]] = {}
        self.inventory: Dict[str, Dict[str, Any]] = {}
        self.prices: Dict[str, Dict[str, Any]] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.promotions: Dict[str, Dict[str, Any]] = {}
        self.returns: Dict[str, Dict[str, Any]] = {}
        
        # Feed tracking
        self.feeds: Dict[str, Dict[str, Any]] = {}
        
        # Report tracking
        self.reports: Dict[str, Dict[str, Any]] = {}
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize the API with sample data for testing."""
        # Sample items
        sample_items = {
            "SKU001": {
                "sku": "SKU001",
                "product_name": "Sample Product 1",
                "price": 29.99,
                "description": "A sample product for testing",
                "category": "Electronics",
                "status": "Active"
            },
            "SKU002": {
                "sku": "SKU002", 
                "product_name": "Sample Product 2",
                "price": 49.99,
                "description": "Another sample product",
                "category": "Home & Garden",
                "status": "Active"
            }
        }
        
        # Sample inventory
        sample_inventory = {
            "SKU001": {"quantity": 100, "fulfillment_center_id": "FC001"},
            "SKU002": {"quantity": 50, "fulfillment_center_id": "FC002"}
        }
        
        # Sample orders
        sample_orders = {
            "PO001": {
                "purchase_order_id": "PO001",
                "order_date": "2024-01-15T10:30:00Z",
                "status": "Created",
                "items": [{"sku": "SKU001", "quantity": 2, "price": 29.99}],
                "total_amount": 59.98
            },
            "PO002": {
                "purchase_order_id": "PO002", 
                "order_date": "2024-01-16T14:20:00Z",
                "status": "Acknowledged",
                "items": [{"sku": "SKU002", "quantity": 1, "price": 49.99}],
                "total_amount": 49.99
            }
        }
        
        # Sample promotions
        sample_promotions = {
            "PROMO001": {
                "promo_id": "PROMO001",
                "name": "Summer Sale",
                "discount_percent": 15,
                "start_date": "2024-06-01",
                "end_date": "2024-08-31",
                "status": "Active"
            }
        }
        
        self.items.update(sample_items)
        self.inventory.update(sample_inventory)
        self.prices.update({sku: {"price": item["price"]} for sku, item in sample_items.items()})
        self.orders.update(sample_orders)
        self.promotions.update(sample_promotions)

    def get_items(self, limit: int = 50, offset: int = 0) -> Dict[str, Union[List[Dict[str, Any]], Dict[str, int]]]:
        """
        Retrieve a paginated list of all items for the seller.

        Args:
            limit (int, optional): Number of items to return per page.
            offset (int, optional): Number of items to skip.

        Returns:
            Dict[str, Union[List[Dict[str, Any]], Dict[str, int]]]: List of items and pagination info.
        """
        items_list = list(self.items.values())
        total_count = len(items_list)
        
        # Apply pagination
        start_idx = offset
        end_idx = min(offset + limit, total_count)
        paginated_items = items_list[start_idx:end_idx]
        
        return {
            "items": paginated_items,
            "pagination": {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": end_idx < total_count
            }
        }

    def get_item(self, sku: str) -> Dict[str, Any]:
        """
        Retrieve the details of a single item by SKU.

        Args:
            sku (str): The SKU identifier of the item.

        Returns:
            Dict[str, Any]: Details of the item.
        """
        if sku not in self.items:
            return {"error": "Item not found", "sku": sku}
        
        return self.items[sku]

    def update_item(self, sku: str, item_payload: Dict[str, Any]) -> Dict[str, Union[str, List[str]]]:
        """
        Update the details of an item by SKU.

        Args:
            sku (str): The SKU identifier of the item.
            item_payload (Dict[str, Any]): The updated item data.

        Returns:
            Dict[str, Union[str, List[str]]]: Response with status and errors if any.
        """
        if sku not in self.items:
            return {"status": "error", "errors": [f"Item with SKU {sku} not found"]}
        
        # Update the item
        self.items[sku].update(item_payload)
        
        # Update price if included
        if "price" in item_payload:
            self.prices[sku] = {"price": item_payload["price"]}
        
        return {"status": "success", "message": f"Item {sku} updated successfully"}

    def retire_item(self, sku: str) -> Dict[str, Union[str, List[str]]]:
        """
        Retire (remove) an item from the Walmart Marketplace by SKU.

        Args:
            sku (str): The SKU identifier of the item.

        Returns:
            Dict[str, Union[str, List[str]]]: Response with status and errors if any.
        """
        if sku not in self.items:
            return {"status": "error", "errors": [f"Item with SKU {sku} not found"]}
        
        # Mark item as retired
        self.items[sku]["status"] = "Retired"
        
        return {"status": "success", "message": f"Item {sku} retired successfully"}

    def bulk_item_upload(self, file: bytes, file_type: str) -> Dict[str, str]:
        """
        Upload a bulk item file (XML or Excel) to add or update multiple items.

        Args:
            file (bytes): The file contents.
            file_type (str): Type of file ('xml' or 'xlsx').

        Returns:
            Dict[str, str]: Feed ID and upload status.
        """
        feed_id = f"feed_{uuid.uuid4().hex[:8]}"
        
        self.feeds[feed_id] = {
            "feed_id": feed_id,
            "feed_type": "item",
            "file_type": file_type,
            "status": "Submitted",
            "submitted_date": datetime.now().isoformat(),
            "file_size": len(file)
        }
        
        return {"feed_id": feed_id, "status": "Submitted"}

    def get_bulk_item_status(self, feed_id: str) -> Dict[str, Any]:
        """
        Retrieve the status of a bulk item upload feed.

        Args:
            feed_id (str): The feed identifier.

        Returns:
            Dict[str, Any]: Feed processing status and errors if any.
        """
        if feed_id not in self.feeds:
            return {"error": "Feed not found", "feed_id": feed_id}
        
        feed = self.feeds[feed_id]
        
        # Simulate processing completion
        if feed["status"] == "Submitted":
            feed["status"] = "Completed"
            feed["completed_date"] = datetime.now().isoformat()
            feed["processed_items"] = 5  # Simulate processing 5 items
        
        return feed

    def get_inventory(self, sku: str) -> Dict[str, Any]:
        """
        Retrieve the inventory information for a given SKU.

        Args:
            sku (str): The SKU identifier.

        Returns:
            Dict[str, Any]: Inventory details for the SKU.
        """
        if sku not in self.inventory:
            return {"error": "Inventory not found", "sku": sku}
        
        return self.inventory[sku]

    def update_inventory(self, sku: str, quantity: int, fulfillment_center_id: str = None) -> Dict[str, Union[str, List[str]]]:
        """
        Update the inventory quantity for a SKU.

        Args:
            sku (str): The SKU identifier.
            quantity (int): The new inventory quantity.
            fulfillment_center_id (str, optional): Fulfillment center ID if applicable.

        Returns:
            Dict[str, Union[str, List[str]]]: Response with status and errors if any.
        """
        if sku not in self.inventory:
            return {"status": "error", "errors": [f"Inventory for SKU {sku} not found"]}
        
        self.inventory[sku]["quantity"] = quantity
        if fulfillment_center_id:
            self.inventory[sku]["fulfillment_center_id"] = fulfillment_center_id
        
        return {"status": "success", "message": f"Inventory for SKU {sku} updated successfully"}

    def bulk_inventory_update(self, file: bytes, file_type: str) -> Dict[str, str]:
        """
        Upload a bulk inventory file (XML or Excel) to update inventory for multiple SKUs.

        Args:
            file (bytes): The file contents.
            file_type (str): Type of file ('xml' or 'xlsx').

        Returns:
            Dict[str, str]: Feed ID and upload status.
        """
        feed_id = f"inventory_feed_{uuid.uuid4().hex[:8]}"
        
        self.feeds[feed_id] = {
            "feed_id": feed_id,
            "feed_type": "inventory",
            "file_type": file_type,
            "status": "Submitted",
            "submitted_date": datetime.now().isoformat(),
            "file_size": len(file)
        }
        
        return {"feed_id": feed_id, "status": "Submitted"}

    def get_bulk_inventory_status(self, feed_id: str) -> Dict[str, Any]:
        """
        Retrieve the status of a bulk inventory upload feed.

        Args:
            feed_id (str): The feed identifier.

        Returns:
            Dict[str, Any]: Feed processing status and errors if any.
        """
        if feed_id not in self.feeds:
            return {"error": "Feed not found", "feed_id": feed_id}
        
        feed = self.feeds[feed_id]
        
        # Simulate processing completion
        if feed["status"] == "Submitted":
            feed["status"] = "Completed"
            feed["completed_date"] = datetime.now().isoformat()
            feed["processed_items"] = 3  # Simulate processing 3 inventory updates
        
        return feed

    def get_orders(self, status: str = "Created", limit: int = 50, created_start_date: str = None, created_end_date: str = None) -> Dict[str, Union[List[Dict[str, Any]], Dict[str, int]]]:
        """
        Retrieve a list of orders filtered by status and date.

        Args:
            status (str, optional): The order status to filter by (e.g., 'Created', 'Acknowledged', 'Shipped').
            limit (int, optional): Number of orders per page.
            created_start_date (str, optional): ISO date string for start date filter.
            created_end_date (str, optional): ISO date string for end date filter.

        Returns:
            Dict[str, Union[List[Dict[str, Any]], Dict[str, int]]]: List of orders and pagination info.
        """
        # Filter orders by status
        filtered_orders = [order for order in self.orders.values() if order["status"] == status]
        
        # Apply date filtering if provided
        if created_start_date or created_end_date:
            filtered_orders = self._filter_orders_by_date(filtered_orders, created_start_date, created_end_date)
        
        total_count = len(filtered_orders)
        
        # Apply pagination
        start_idx = 0
        end_idx = min(limit, total_count)
        paginated_orders = filtered_orders[start_idx:end_idx]
        
        return {
            "orders": paginated_orders,
            "pagination": {
                "total_count": total_count,
                "limit": limit,
                "has_more": end_idx < total_count
            }
        }

    def _filter_orders_by_date(self, orders: List[Dict[str, Any]], start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Helper method to filter orders by date range."""
        filtered = []
        
        for order in orders:
            order_date = datetime.fromisoformat(order["order_date"].replace("Z", "+00:00"))
            
            if start_date:
                start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                if order_date < start_dt:
                    continue
            
            if end_date:
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                if order_date > end_dt:
                    continue
            
            filtered.append(order)
        
        return filtered

    def get_order(self, purchase_order_id: str) -> Dict[str, Any]:
        """
        Retrieve the details of a specific order by purchase order ID.

        Args:
            purchase_order_id (str): The purchase order ID.

        Returns:
            Dict[str, Any]: Details of the order.
        """
        if purchase_order_id not in self.orders:
            return {"error": "Order not found", "purchase_order_id": purchase_order_id}
        
        return self.orders[purchase_order_id]

    def acknowledge_order(self, purchase_order_id: str, acknowledgment_payload: Dict[str, Any]) -> Dict[str, Union[str, List[str]]]:
        """
        Acknowledge receipt of an order.

        Args:
            purchase_order_id (str): The purchase order ID.
            acknowledgment_payload (Dict[str, Any]): Acknowledgment details.

        Returns:
            Dict[str, Union[str, List[str]]]: Response with status and errors if any.
        """
        if purchase_order_id not in self.orders:
            return {"status": "error", "errors": [f"Order {purchase_order_id} not found"]}
        
        order = self.orders[purchase_order_id]
        if order["status"] != "Created":
            return {"status": "error", "errors": [f"Order {purchase_order_id} cannot be acknowledged in current status"]}
        
        # Update order status
        order["status"] = "Acknowledged"
        order["acknowledgment_date"] = datetime.now().isoformat()
        order["acknowledgment_details"] = acknowledgment_payload
        
        return {"status": "success", "message": f"Order {purchase_order_id} acknowledged successfully"}

    def ship_order(self, purchase_order_id: str, shipment_payload: Dict[str, Any]) -> Dict[str, Union[str, List[str]]]:
        """
        Update an order as shipped and provide tracking information.

        Args:
            purchase_order_id (str): The purchase order ID.
            shipment_payload (Dict[str, Any]): Shipment and tracking details.

        Returns:
            Dict[str, Union[str, List[str]]]: Response with status and errors if any.
        """
        if purchase_order_id not in self.orders:
            return {"status": "error", "errors": [f"Order {purchase_order_id} not found"]}
        
        order = self.orders[purchase_order_id]
        if order["status"] not in ["Created", "Acknowledged"]:
            return {"status": "error", "errors": [f"Order {purchase_order_id} cannot be shipped in current status"]}
        
        # Update order status and add shipment info
        order["status"] = "Shipped"
        order["shipment_date"] = datetime.now().isoformat()
        order["shipment_details"] = shipment_payload
        
        return {"status": "success", "message": f"Order {purchase_order_id} marked as shipped"}

    def cancel_order(self, purchase_order_id: str, cancel_payload: Dict[str, Any]) -> Dict[str, Union[str, List[str]]]:
        """
        Cancel an order or order line.

        Args:
            purchase_order_id (str): The purchase order ID.
            cancel_payload (Dict[str, Any]): Details of the cancellation.

        Returns:
            Dict[str, Union[str, List[str]]]: Response with status and errors if any.
        """
        if purchase_order_id not in self.orders:
            return {"status": "error", "errors": [f"Order {purchase_order_id} not found"]}
        
        order = self.orders[purchase_order_id]
        if order["status"] in ["Shipped", "Delivered"]:
            return {"status": "error", "errors": [f"Order {purchase_order_id} cannot be cancelled in current status"]}
        
        # Update order status
        order["status"] = "Cancelled"
        order["cancellation_date"] = datetime.now().isoformat()
        order["cancellation_details"] = cancel_payload
        
        return {"status": "success", "message": f"Order {purchase_order_id} cancelled successfully"}

    def refund_order(self, purchase_order_id: str, refund_payload: Dict[str, Any]) -> Dict[str, Union[str, List[str]]]:
        """
        Issue a refund for an order or order line.

        Args:
            purchase_order_id (str): The purchase order ID.
            refund_payload (Dict[str, Any]): Refund details.

        Returns:
            Dict[str, Union[str, List[str]]]: Response with status and errors if any.
        """
        if purchase_order_id not in self.orders:
            return {"status": "error", "errors": [f"Order {purchase_order_id} not found"]}
        
        order = self.orders[purchase_order_id]
        if order["status"] not in ["Shipped", "Delivered"]:
            return {"status": "error", "errors": [f"Order {purchase_order_id} cannot be refunded in current status"]}
        
        # Add refund information
        if "refunds" not in order:
            order["refunds"] = []
        
        refund_info = {
            "refund_id": f"refund_{uuid.uuid4().hex[:8]}",
            "refund_date": datetime.now().isoformat(),
            "refund_details": refund_payload
        }
        order["refunds"].append(refund_info)
        
        return {"status": "success", "message": f"Refund issued for order {purchase_order_id}", "refund_id": refund_info["refund_id"]}

    def get_order_shipment(self, purchase_order_id: str) -> Dict[str, Any]:
        """
        Retrieve shipment details for an order.

        Args:
            purchase_order_id (str): The purchase order ID.

        Returns:
            Dict[str, Any]: Shipment details.
        """
        if purchase_order_id not in self.orders:
            return {"error": "Order not found", "purchase_order_id": purchase_order_id}
        
        order = self.orders[purchase_order_id]
        
        if "shipment_details" not in order:
            return {"error": "No shipment details found for this order"}
        
        return order["shipment_details"]

    def get_order_advance_shipment_notice(self, purchase_order_id: str) -> Dict[str, Any]:
        """
        Retrieve ASN (Advance Shipment Notice) for an order.

        Args:
            purchase_order_id (str): The purchase order ID.

        Returns:
            Dict[str, Any]: ASN details.
        """
        if purchase_order_id not in self.orders:
            return {"error": "Order not found", "purchase_order_id": purchase_order_id}
        
        # Simulate ASN data
        return {
            "asn_id": f"ASN_{purchase_order_id}",
            "purchase_order_id": purchase_order_id,
            "shipment_date": datetime.now().isoformat(),
            "carrier": "FedEx",
            "tracking_number": f"TRK{uuid.uuid4().hex[:12].upper()}",
            "estimated_delivery": (datetime.now() + timedelta(days=3)).isoformat()
        }

    def get_price(self, sku: str) -> Dict[str, Any]:
        """
        Retrieve the current price for a SKU.

        Args:
            sku (str): The SKU identifier.

        Returns:
            Dict[str, Any]: Price details for the SKU.
        """
        if sku not in self.prices:
            return {"error": "Price not found", "sku": sku}
        
        return self.prices[sku]

    def update_price(self, sku: str, price_payload: Dict[str, Any]) -> Dict[str, Union[str, List[str]]]:
        """
        Update the price for a SKU.

        Args:
            sku (str): The SKU identifier.
            price_payload (Dict[str, Any]): New price information.

        Returns:
            Dict[str, Union[str, List[str]]]: Response with status and errors if any.
        """
        if sku not in self.prices:
            return {"status": "error", "errors": [f"Price for SKU {sku} not found"]}
        
        self.prices[sku].update(price_payload)
        
        # Also update the item price if the item exists
        if sku in self.items:
            self.items[sku]["price"] = price_payload.get("price", self.items[sku]["price"])
        
        return {"status": "success", "message": f"Price for SKU {sku} updated successfully"}

    def bulk_price_update(self, file: bytes, file_type: str) -> Dict[str, str]:
        """
        Upload a bulk price file (XML or Excel) to update prices for multiple SKUs.

        Args:
            file (bytes): The file contents.
            file_type (str): Type of file ('xml' or 'xlsx').

        Returns:
            Dict[str, str]: Feed ID and upload status.
        """
        feed_id = f"price_feed_{uuid.uuid4().hex[:8]}"
        
        self.feeds[feed_id] = {
            "feed_id": feed_id,
            "feed_type": "price",
            "file_type": file_type,
            "status": "Submitted",
            "submitted_date": datetime.now().isoformat(),
            "file_size": len(file)
        }
        
        return {"feed_id": feed_id, "status": "Submitted"}

    def get_bulk_price_status(self, feed_id: str) -> Dict[str, Any]:
        """
        Retrieve the status of a bulk price upload feed.

        Args:
            feed_id (str): The feed identifier.

        Returns:
            Dict[str, Any]: Feed processing status and errors if any.
        """
        if feed_id not in self.feeds:
            return {"error": "Feed not found", "feed_id": feed_id}
        
        feed = self.feeds[feed_id]
        
        # Simulate processing completion
        if feed["status"] == "Submitted":
            feed["status"] = "Completed"
            feed["completed_date"] = datetime.now().isoformat()
            feed["processed_items"] = 4  # Simulate processing 4 price updates
        
        return feed

    def get_promotions(self, limit: int = 50, offset: int = 0) -> Dict[str, Union[List[Dict[str, Any]], Dict[str, int]]]:
        """
        Retrieve a paginated list of all promotions.

        Args:
            limit (int, optional): Number of promotions to return per page.
            offset (int, optional): Number of promotions to skip.

        Returns:
            Dict[str, Union[List[Dict[str, Any]], Dict[str, int]]]: List of promotions and pagination info.
        """
        promotions_list = list(self.promotions.values())
        total_count = len(promotions_list)
        
        # Apply pagination
        start_idx = offset
        end_idx = min(offset + limit, total_count)
        paginated_promotions = promotions_list[start_idx:end_idx]
        
        return {
            "promotions": paginated_promotions,
            "pagination": {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": end_idx < total_count
            }
        }

    def create_promotion(self, promotion_payload: Dict[str, Any]) -> Dict[str, Union[str, List[str]]]:
        """
        Create a new promotion.

        Args:
            promotion_payload (Dict[str, Any]): Promotion details.

        Returns:
            Dict[str, Union[str, List[str]]]: Response with status and errors if any.
        """
        promo_id = f"PROMO{uuid.uuid4().hex[:8].upper()}"
        
        promotion = {
            "promo_id": promo_id,
            "status": "Active",
            "created_date": datetime.now().isoformat()
        }
        promotion.update(promotion_payload)
        
        self.promotions[promo_id] = promotion
        
        return {"status": "success", "message": "Promotion created successfully", "promo_id": promo_id}

    def update_promotion(self, promo_id: str, promotion_payload: Dict[str, Any]) -> Dict[str, Union[str, List[str]]]:
        """
        Update an existing promotion.

        Args:
            promo_id (str): The promotion identifier.
            promotion_payload (Dict[str, Any]): Promotion details to update.

        Returns:
            Dict[str, Union[str, List[str]]]: Response with status and errors if any.
        """
        if promo_id not in self.promotions:
            return {"status": "error", "errors": [f"Promotion {promo_id} not found"]}
        
        self.promotions[promo_id].update(promotion_payload)
        self.promotions[promo_id]["updated_date"] = datetime.now().isoformat()
        
        return {"status": "success", "message": f"Promotion {promo_id} updated successfully"}

    def get_promotion(self, promo_id: str) -> Dict[str, Any]:
        """
        Retrieve the details of a specific promotion.

        Args:
            promo_id (str): The promotion identifier.

        Returns:
            Dict[str, Any]: Promotion details.
        """
        if promo_id not in self.promotions:
            return {"error": "Promotion not found", "promo_id": promo_id}
        
        return self.promotions[promo_id]

    def get_reports(self, report_type: str, limit: int = 50, offset: int = 0) -> Dict[str, Union[List[Dict[str, Any]], Dict[str, int]]]:
        """
        Retrieve a list of available reports of the specified type.

        Args:
            report_type (str): The type of report (e.g., 'item', 'inventory', 'order', 'performance').
            limit (int, optional): Number of reports per page.
            offset (int, optional): Number of reports to skip.

        Returns:
            Dict[str, Union[List[Dict[str, Any]], Dict[str, int]]]: List of reports and pagination info.
        """
        # Filter reports by type
        filtered_reports = [report for report in self.reports.values() if report["report_type"] == report_type]
        
        total_count = len(filtered_reports)
        
        # Apply pagination
        start_idx = offset
        end_idx = min(offset + limit, total_count)
        paginated_reports = filtered_reports[start_idx:end_idx]
        
        return {
            "reports": paginated_reports,
            "pagination": {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": end_idx < total_count
            }
        }

    def request_report(self, report_type: str, report_params: Dict[str, Any] = None) -> Dict[str, Union[str, List[str]]]:
        """
        Request generation of a new report.

        Args:
            report_type (str): The type of report to generate.
            report_params (Dict[str, Any], optional): Parameters for report generation.

        Returns:
            Dict[str, Union[str, List[str]]]: Report request status.
        """
        report_id = f"report_{uuid.uuid4().hex[:8]}"
        
        report = {
            "report_id": report_id,
            "report_type": report_type,
            "status": "Submitted",
            "requested_date": datetime.now().isoformat(),
            "parameters": report_params or {}
        }
        
        self.reports[report_id] = report
        
        return {"status": "success", "message": "Report requested successfully", "report_id": report_id}

    def download_report(self, report_id: str) -> bytes:
        """
        Download a report file by report ID.

        Args:
            report_id (str): The identifier of the report.

        Returns:
            bytes: The report file contents.
        """
        if report_id not in self.reports:
            return b"Report not found"
        
        report = self.reports[report_id]
        
        # Simulate report generation completion
        if report["status"] == "Submitted":
            report["status"] = "Completed"
            report["completed_date"] = datetime.now().isoformat()
        
        # Generate sample report content
        report_content = {
            "report_id": report_id,
            "report_type": report["report_type"],
            "generated_date": datetime.now().isoformat(),
            "data": f"Sample {report['report_type']} report data"
        }
        
        return json.dumps(report_content, indent=2).encode('utf-8')

    def get_feeds(self, feed_type: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Union[List[Dict[str, Any]], Dict[str, int]]]:
        """
        Retrieve a list of all submitted feeds.

        Args:
            feed_type (str, optional): Filter by feed type.
            limit (int, optional): Number of feeds per page.
            offset (int, optional): Number of feeds to skip.

        Returns:
            Dict[str, Union[List[Dict[str, Any]], Dict[str, int]]]: List of feeds and their statuses.
        """
        feeds_list = list(self.feeds.values())
        
        # Filter by feed type if specified
        if feed_type:
            feeds_list = [feed for feed in feeds_list if feed["feed_type"] == feed_type]
        
        total_count = len(feeds_list)
        
        # Apply pagination
        start_idx = offset
        end_idx = min(offset + limit, total_count)
        paginated_feeds = feeds_list[start_idx:end_idx]
        
        return {
            "feeds": paginated_feeds,
            "pagination": {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": end_idx < total_count
            }
        }

    def get_feed_status(self, feed_id: str) -> Dict[str, Any]:
        """
        Retrieve the processing status and result of a feed.

        Args:
            feed_id (str): The feed identifier.

        Returns:
            Dict[str, Any]: Feed status and errors if any.
        """
        if feed_id not in self.feeds:
            return {"error": "Feed not found", "feed_id": feed_id}
        
        return self.feeds[feed_id]

    def get_returns(self, status: str = None, limit: int = 50, created_start_date: str = None, created_end_date: str = None) -> Dict[str, Union[List[Dict[str, Any]], Dict[str, int]]]:
        """
        Retrieve a list of return requests.

        Args:
            status (str, optional): Filter by return status.
            limit (int, optional): Number of returns per page.
            created_start_date (str, optional): ISO date string for start date filter.
            created_end_date (str, optional): ISO date string for end date filter.

        Returns:
            Dict[str, Union[List[Dict[str, Any]], Dict[str, int]]]: List of returns and pagination info.
        """
        returns_list = list(self.returns.values())
        
        # Filter by status if specified
        if status:
            returns_list = [ret for ret in returns_list if ret["status"] == status]
        
        total_count = len(returns_list)
        
        # Apply pagination
        start_idx = 0
        end_idx = min(limit, total_count)
        paginated_returns = returns_list[start_idx:end_idx]
        
        return {
            "returns": paginated_returns,
            "pagination": {
                "total_count": total_count,
                "limit": limit,
                "has_more": end_idx < total_count
            }
        }

    def get_return(self, return_id: str) -> Dict[str, Any]:
        """
        Retrieve the details of a specific return request.

        Args:
            return_id (str): The return request identifier.

        Returns:
            Dict[str, Any]: Return details.
        """
        if return_id not in self.returns:
            return {"error": "Return not found", "return_id": return_id}
        
        return self.returns[return_id]

    def approve_return(self, return_id: str, approval_payload: Dict[str, Any] = None) -> Dict[str, Union[str, List[str]]]:
        """
        Approve a return request.

        Args:
            return_id (str): The return request identifier.
            approval_payload (Dict[str, Any], optional): Additional approval details.

        Returns:
            Dict[str, Union[str, List[str]]]: Response with status and errors if any.
        """
        if return_id not in self.returns:
            return {"status": "error", "errors": [f"Return {return_id} not found"]}
        
        return_request = self.returns[return_id]
        if return_request["status"] != "Pending":
            return {"status": "error", "errors": [f"Return {return_id} cannot be approved in current status"]}
        
        # Update return status
        return_request["status"] = "Approved"
        return_request["approval_date"] = datetime.now().isoformat()
        if approval_payload:
            return_request["approval_details"] = approval_payload
        
        return {"status": "success", "message": f"Return {return_id} approved successfully"}

    def reject_return(self, return_id: str, rejection_payload: Dict[str, Any] = None) -> Dict[str, Union[str, List[str]]]:
        """
        Reject a return request.

        Args:
            return_id (str): The return request identifier.
            rejection_payload (Dict[str, Any], optional): Reason for rejection.

        Returns:
            Dict[str, Union[str, List[str]]]: Response with status and errors if any.
        """
        if return_id not in self.returns:
            return {"status": "error", "errors": [f"Return {return_id} not found"]}
        
        return_request = self.returns[return_id]
        if return_request["status"] != "Pending":
            return {"status": "error", "errors": [f"Return {return_id} cannot be rejected in current status"]}
        
        # Update return status
        return_request["status"] = "Rejected"
        return_request["rejection_date"] = datetime.now().isoformat()
        if rejection_payload:
            return_request["rejection_details"] = rejection_payload
        
        return {"status": "success", "message": f"Return {return_id} rejected successfully"}

    def issue_return_refund(self, return_id: str, refund_payload: Dict[str, Any]) -> Dict[str, Union[str, List[str]]]:
        """
        Issue a refund for a return request.

        Args:
            return_id (str): The return request identifier.
            refund_payload (Dict[str, Any]): Refund details.

        Returns:
            Dict[str, Union[str, List[str]]]: Response with status and errors if any.
        """
        if return_id not in self.returns:
            return {"status": "error", "errors": [f"Return {return_id} not found"]}
        
        return_request = self.returns[return_id]
        if return_request["status"] != "Approved":
            return {"status": "error", "errors": [f"Return {return_id} must be approved before refund can be issued"]}
        
        # Add refund information
        refund_info = {
            "refund_id": f"return_refund_{uuid.uuid4().hex[:8]}",
            "refund_date": datetime.now().isoformat(),
            "refund_details": refund_payload
        }
        
        return_request["refund"] = refund_info
        return_request["status"] = "Refunded"
        
        return {"status": "success", "message": f"Refund issued for return {return_id}", "refund_id": refund_info["refund_id"]}
