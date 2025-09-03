
import datetime

class Product:
    products = {}

    def __init__(self, id: int, name: str, description: str, price: float, quantity: int, category: str, supplier_id: int):
        if name in self.__class__.products:
            raise ValueError("Product name must be unique")
        if price <= 0:
            raise ValueError("Price must be positive")
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
        self.category = category
        self.supplier_id = supplier_id
        self.__class__.products[name] = self

    def add_product(self):
        # Add product logic handled in the constructor
        pass

    def update_product(self, id: int, **kwargs):
        product = [prod for prod in self.__class__.products.values() if prod.id == id][0]
        for key, value in kwargs.items():
            setattr(product, key, value)

    def delete_product(self, id: int):
        product = [name for name, prod in self.__class__.products.items() if prod.id == id][0]
        del self.__class__.products[product]

    def get_product_details(self, id: int) -> dict:
        return next((vars(prod) for prod in self.__class__.products.values() if prod.id == id), None)


class Inventory:
    inventory_records = {}

    def __init__(self, id: int, product_id: int, current_quantity: int, last_update: str):
        self.id = id
        self.product_id = product_id
        self.current_quantity = current_quantity
        self.last_update = last_update
        self.__class__.inventory_records[product_id] = self

    def register_stock_entry(self, product_id: int, quantity: int):
        inventory = self.__class__.inventory_records[product_id]
        inventory.current_quantity += quantity
        inventory.last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def register_stock_exit(self, product_id: int, quantity: int):
        inventory = self.__class__.inventory_records[product_id]
        if inventory.current_quantity - quantity < 0:
            raise ValueError("Cannot have negative stock quantity")
        inventory.current_quantity -= quantity
        inventory.last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def check_low_stock(self, threshold: int) -> list:
        low_stock_products = [prod_id for prod_id, inv in self.__class__.inventory_records.items()
                              if inv.current_quantity < threshold]
        return low_stock_products


class Supplier:
    suppliers = {}

    def __init__(self, id: int, name: str, contact: str, address: str):
        self.id = id
        self.name = name
        self.contact = contact
        self.address = address
        self.__class__.suppliers[id] = self

    def add_supplier(self):
        # Add supplier logic handled in the constructor
        pass

    def update_supplier(self, id: int, **kwargs):
        supplier = self.__class__.suppliers[id]
        for key, value in kwargs.items():
            setattr(supplier, key, value)

    def delete_supplier(self, id: int):
        del self.__class__.suppliers[id]

    def associate_product_to_supplier(self, product_id: int, supplier_id: int):
        product = Product.products[product_id]
        product.supplier_id = supplier_id


class User:
    users = {}

    def __init__(self, id: int, username: str, password_hash: str, role: str):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.__class__.users[username] = self

    def authenticate(self, username: str, password: str) -> bool:
        # For demonstration: Password check is just matching the hashes as it's a simulation
        user = self.__class__.users.get(username)
        if user and user.password_hash == password:
            return True
        return False

    def authorize(self, role: str, action: str) -> bool:
        user = self.__class__.users.get(self.username)
        if user and user.role == role:
            return True
        return False


class Report:
    reports = {}

    def __init__(self, id: int, type: str, generation_date: str, data: dict):
        self.id = id
        self.type = type
        self.generation_date = generation_date
        self.data = data
        self.__class__.reports[id] = self

    def generate_inventory_report(self) -> dict:
        return {prod_id: vars(inv) for prod_id, inv in Inventory.inventory_records.items()}

    def view_stock_trends(self) -> dict:
        # Placeholder for trend visualization
        trends = {prod_id: inv.current_quantity for prod_id, inv in Inventory.inventory_records.items()}
        return trends


class NotificationSystem:
    def send_low_stock_alert(self, product_id: int):
        print(f"Alert: Low stock for product ID {product_id}")


class MainClass:
    def __init__(self):
        self.products = Product
        self.inventory = Inventory
        self.suppliers = Supplier
        self.users = User
        self.reports = Report
        self.notifications = NotificationSystem()

    def system_status(self):
        print("System running with following components:")
        print(f"Products: {list(self.products.products.keys())}")
        print(f"Suppliers: {list(self.suppliers.suppliers.keys())}")
        print(f"Users: {list(self.users.users.keys())}")
