# wine_inventory_management.py

import uuid
from datetime import datetime
from typing import List, Dict, Optional

# Entity Classes

class WineProduct:
    def __init__(self, product_id: str, name: str, type: str, brand: str, vintage: str, price: float, stock_level: int) -> None:
        if not isinstance(price, (float, int)) or price <= 0:
            raise ValueError("Price must be a positive number.")
        if not isinstance(stock_level, int) or stock_level < 0:
            raise ValueError("Stock level cannot be negative.")
        self.product_id = product_id
        self.name = name
        self.type = type
        self.brand = brand
        self.vintage = vintage
        self.price = float(price)
        self.stock_level = stock_level

    def update_stock(self, quantity: int) -> None:
        if not isinstance(quantity, int):
            raise ValueError("Stock update quantity must be an integer.")
        if self.stock_level + quantity < 0:
            raise ValueError("Stock level cannot be negative after update.")
        self.stock_level += quantity

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "type": self.type,
            "brand": self.brand,
            "vintage": self.vintage,
            "price": self.price,
            "stock_level": self.stock_level
        }

class Supplier:
    def __init__(self, supplier_id: str, name: str, contact_info: str, product_list: List[str]) -> None:
        self.supplier_id = supplier_id
        self.name = name
        self.contact_info = contact_info
        self.product_list = product_list  # List of product_ids (str)

    def to_dict(self) -> dict:
        return {
            "supplier_id": self.supplier_id,
            "name": self.name,
            "contact_info": self.contact_info,
            "product_list": self.product_list
        }

class Order:
    def __init__(self, order_id: str, supplier_id: str, product_list: List[Dict], order_date: datetime, delivery_date: datetime) -> None:
        if delivery_date < order_date:
            raise ValueError("Delivery date cannot precede order date.")
        self.order_id = order_id
        self.supplier_id = supplier_id
        self.product_list = product_list  # List of dicts: {'product_id': str, 'quantity': int}
        self.order_date = order_date
        self.delivery_date = delivery_date

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "supplier_id": self.supplier_id,
            "product_list": self.product_list,
            "order_date": self.order_date.isoformat(),
            "delivery_date": self.delivery_date.isoformat()
        }

class Sale:
    def __init__(self, sale_id: str, customer_info: str, product_list: List[Dict], sale_date: datetime, total_amount: float) -> None:
        if not isinstance(total_amount, (int, float)) or total_amount < 0:
            raise ValueError("Total amount must be a non-negative number.")
        self.sale_id = sale_id
        self.customer_info = customer_info
        self.product_list = product_list  # List of dicts: {'product_id': str, 'quantity': int}
        self.sale_date = sale_date
        self.total_amount = float(total_amount)

    def to_dict(self) -> dict:
        return {
            "sale_id": self.sale_id,
            "customer_info": self.customer_info,
            "product_list": self.product_list,
            "sale_date": self.sale_date.isoformat(),
            "total_amount": self.total_amount
        }

class Report:
    def __init__(self, report_id: str, report_type: str, date_generated: datetime, content: str) -> None:
        self.report_id = report_id
        self.report_type = report_type
        self.date_generated = date_generated
        self.content = content

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "date_generated": self.date_generated.isoformat(),
            "content": self.content
        }

# Main System Manager

class WineInventoryManager:
    LOW_STOCK_THRESHOLD = 10  # Can be set as needed

    def __init__(self):
        self.wine_products: Dict[str, WineProduct] = dict()
        self.suppliers: Dict[str, Supplier] = dict()
        self.orders: Dict[str, Order] = dict()
        self.sales: Dict[str, Sale] = dict()

    # Inventory Management
    def add_wine_product(self, product: WineProduct) -> None:
        if product.product_id in self.wine_products:
            raise ValueError(f"WineProduct with id '{product.product_id}' already exists.")
        self.wine_products[product.product_id] = product

    def update_stock_level(self, product_id: str, quantity: int) -> None:
        if product_id not in self.wine_products:
            raise ValueError(f"Product id '{product_id}' not found.")
        self.wine_products[product_id].update_stock(quantity)

    def get_product_info(self, product_id: str) -> WineProduct:
        if product_id not in self.wine_products:
            raise ValueError(f"Product id '{product_id}' not found.")
        return self.wine_products[product_id]

    # Supplier Management
    def add_supplier(self, supplier: Supplier) -> None:
        if supplier.supplier_id in self.suppliers:
            raise ValueError(f"Supplier with id '{supplier.supplier_id}' already exists.")
        self.suppliers[supplier.supplier_id] = supplier

    # Order Management
    def create_order(self, order: Order) -> None:
        if order.order_id in self.orders:
            raise ValueError(f"Order with id '{order.order_id}' already exists.")
        if order.supplier_id not in self.suppliers:
            raise ValueError(f"Supplier id '{order.supplier_id}' not found.")
        # Optionally check products are available in supplier's list
        for prod in order.product_list:
            if prod['product_id'] not in self.wine_products:
                raise ValueError(f"Product id '{prod['product_id']}' in order not found in inventory.")
            if prod['product_id'] not in self.suppliers[order.supplier_id].product_list:
                raise ValueError(f"Product id '{prod['product_id']}' not supplied by supplier '{order.supplier_id}'.")
            if prod.get('quantity', 0) <= 0:
                raise ValueError(f"Order must have positive quantities for each product.")
        self.orders[order.order_id] = order
        # Notification for upcoming deliveries handled elsewhere

    # Sales Tracking
    def add_sale(self, sale: Sale) -> None:
        if sale.sale_id in self.sales:
            raise ValueError(f"Sale with id '{sale.sale_id}' already exists.")
        # Check product stocks
        for prod in sale.product_list:
            product_id = prod['product_id']
            quantity = prod.get('quantity', 0)
            if product_id not in self.wine_products:
                raise ValueError(f"Product id '{product_id}' in sale not found in inventory.")
            current_stock = self.wine_products[product_id].stock_level
            if quantity <= 0:
                raise ValueError("Sale must have positive quantity for each product.")
            if current_stock < quantity:
                raise ValueError(f"Not enough stock for product '{product_id}'.")
        # Deduct stock
        for prod in sale.product_list:
            self.wine_products[prod['product_id']].update_stock(-prod['quantity'])
        self.sales[sale.sale_id] = sale

    # Reporting
    def generate_report(self, report_type: str) -> Report:
        report_id = str(uuid.uuid4())
        now = datetime.now()
        content = ""
        if report_type == "stock_levels":
            content = self._report_stock_levels()
        elif report_type == "sales_performance":
            content = self._report_sales_performance()
        elif report_type == "supplier_orders":
            content = self._report_supplier_orders()
        else:
            raise ValueError(f"Unknown report type: {report_type}")
        return Report(report_id, report_type, now, content)

    def _report_stock_levels(self) -> str:
        lines = ["Wine Inventory Stock Levels:"]
        for product in self.wine_products.values():
            lines.append(f"{product.name} ({product.product_id}): {product.stock_level}")
        return "\n".join(lines)

    def _report_sales_performance(self) -> str:
        lines = ["Sales Performance:"]
        total_sales = 0.0
        for sale in self.sales.values():
            lines.append(f"Sale {sale.sale_id}: {sale.total_amount} on {sale.sale_date.strftime('%Y-%m-%d')}")
            total_sales += sale.total_amount
        lines.append(f"Total Sales: {total_sales}")
        return "\n".join(lines)

    def _report_supplier_orders(self) -> str:
        lines = ["Supplier Orders:"]
        for order in self.orders.values():
            prod_details = ", ".join([f"{prod['product_id']} x{prod['quantity']}" for prod in order.product_list])
            lines.append(f"Order {order.order_id} from {order.supplier_id} on {order.order_date.strftime('%Y-%m-%d')}: {prod_details}")
        return "\n".join(lines)

    # Alerts and Notifications
    def check_stock_levels(self) -> List[str]:
        """Returns a list of product_ids that are below the low stock threshold."""
        low_stock = []
        for product in self.wine_products.values():
            if product.stock_level <= self.LOW_STOCK_THRESHOLD:
                low_stock.append(f"Product {product.product_id} ({product.name}) is low on stock: {product.stock_level}")
        return low_stock

    def notify_upcoming_deliveries(self) -> List[str]:
        """Returns a list of strings describing upcoming deliveries within the next 7 days."""
        notifications = []
        now = datetime.now()
        for order in self.orders.values():
            days_ahead = (order.delivery_date - now).days
            if 0 <= days_ahead <= 7:
                notif = (f"Order {order.order_id} from Supplier {order.supplier_id} "
                         f"with products {[prod['product_id'] for prod in order.product_list]} "
                         f"is scheduled for delivery on {order.delivery_date.strftime('%Y-%m-%d')}")
                notifications.append(notif)
        return notifications

    # Utility methods for convenience/testing
    def list_all_products(self) -> List[dict]:
        return [product.to_dict() for product in self.wine_products.values()]

    def list_all_suppliers(self) -> List[dict]:
        return [supplier.to_dict() for supplier in self.suppliers.values()]

    def list_all_orders(self) -> List[dict]:
        return [order.to_dict() for order in self.orders.values()]

    def list_all_sales(self) -> List[dict]:
        return [sale.to_dict() for sale in self.sales.values()]

# --- Persistence & Security Stub Notes ---

"""
# Data Persistence Stub:
# For full persistence, you would implement SQLAlchemy or Django ORM models, set up 
# database sessions, and replace the in-memory dicts above with DB queries.
# For a real deployment, you would:
# - Set up models mapped to tables (wine_products, suppliers, orders, sales)
# - Use session transactions for atomic operations
# - Implement CRUD via DB
# - Implement authentication & authorization with flask/django
# - Employ field encryption for sensitive data (customer_info) per compliance

# RESTful API Stub:
# - Use FastAPI, Flask, or Django REST Framework to expose these methods as API endpoints.
# - Protect endpoints with API tokens or OAuth.
# - Validate all incoming data server-side.

# UI Stub:
# - A lightweight interface (Flask-admin, Streamlit, etc.) can connect to this manager.

# The code provided is ready for business logic; adaptation to persistence, API, and UI is straightforward.
"""

# Example usage for testing (comment out in production):

if __name__ == "__main__":
    manager = WineInventoryManager()
    # Create some products
    product1 = WineProduct("p1", "Chateau Margaux", "Red", "Margaux", "2015", 450.0, 20)
    product2 = WineProduct("p2", "Screaming Eagle", "Red", "Screaming Eagle", "2012", 3200.0, 2)
    manager.add_wine_product(product1)
    manager.add_wine_product(product2)
    # Supplier
    supplier1 = Supplier("s1", "Great Wines Co.", "email: contact@greatwines.com", ["p1", "p2"])
    manager.add_supplier(supplier1)
    # Order
    order1 = Order("o1", "s1", [{"product_id": "p1", "quantity": 10}], datetime.now(), datetime.now())
    manager.create_order(order1)
    # Sale
    sale1 = Sale("sale1", "John Doe, 123 Main St", [{"product_id": "p1", "quantity": 2}], datetime.now(), 900.0)
    manager.add_sale(sale1)
    # Generate reports
    stock_report = manager.generate_report("stock_levels")
    print(stock_report.content)
    sales_report = manager.generate_report("sales_performance")
    print(sales_report.content)
    # Notifications
    for msg in manager.check_stock_levels():
        print(msg)
    for msg in manager.notify_upcoming_deliveries():
        print(msg)