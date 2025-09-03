```python
# test_wine_inventory_management.py

import unittest
from datetime import datetime, timedelta
from wine_inventory_management import WineProduct, Supplier, Order, Sale, Report, WineInventoryManager

class TestWineProduct(unittest.TestCase):
    
    def test_initialization(self):
        product = WineProduct("p1", "Chateau Margaux", "Red", "Margaux", "2015", 450.0, 20)
        self.assertEqual(product.product_id, "p1")
        self.assertEqual(product.name, "Chateau Margaux")
        self.assertEqual(product.type, "Red")
        self.assertEqual(product.brand, "Margaux")
        self.assertEqual(product.vintage, "2015")
        self.assertEqual(product.price, 450.0)
        self.assertEqual(product.stock_level, 20)

    def test_invalid_price(self):
        with self.assertRaises(ValueError):
            WineProduct("p2", "Some Wine", "Red", "Brand", "2010", -10.0, 10)

    def test_invalid_stock_level(self):
        with self.assertRaises(ValueError):
            WineProduct("p3", "Some Wine", "Red", "Brand", "2010", 10.0, -5)

    def test_update_stock(self):
        product = WineProduct("p4", "Some Wine", "Red", "Brand", "2010", 10.0, 5)
        product.update_stock(5)
        self.assertEqual(product.stock_level, 10)
        with self.assertRaises(ValueError):
            product.update_stock(-20)

class TestWineInventoryManager(unittest.TestCase):
    
    def setUp(self):
        self.manager = WineInventoryManager()
        self.product = WineProduct("p1", "Chateau Margaux", "Red", "Margaux", "2015", 450.0, 20)
        self.manager.add_wine_product(self.product)
        self.supplier = Supplier("s1", "Great Wines Co.", "email: contact@greatwines.com", ["p1"])
        self.manager.add_supplier(self.supplier)

    def test_add_wine_product(self):
        self.assertIn("p1", self.manager.wine_products)
        with self.assertRaises(ValueError):
            self.manager.add_wine_product(self.product)

    def test_update_stock_level(self):
        self.manager.update_stock_level("p1", 10)
        self.assertEqual(self.manager.wine_products["p1"].stock_level, 30)
        with self.assertRaises(ValueError):
            self.manager.update_stock_level("p2", 10)

    def test_get_product_info(self):
        product_info = self.manager.get_product_info("p1")
        self.assertEqual(product_info, self.product)
        with self.assertRaises(ValueError):
            self.manager.get_product_info("p2")

    def test_create_order(self):
        order = Order("o1", "s1", [{"product_id": "p1", "quantity": 10}], datetime.now(), datetime.now())
        self.manager.create_order(order)
        self.assertIn("o1", self.manager.orders)
        with self.assertRaises(ValueError):
            self.manager.create_order(order)

    def test_add_sale(self):
        sale = Sale("sale1", "John Doe", [{"product_id": "p1", "quantity": 5}], datetime.now(), 2250.0)
        self.manager.add_sale(sale)
        self.assertIn("sale1", self.manager.sales)
        self.assertEqual(self.manager.wine_products["p1"].stock_level, 15)
        with self.assertRaises(ValueError):
            self.manager.add_sale(sale)

    def test_generate_report(self):
        report = self.manager.generate_report("stock_levels")
        self.assertIsInstance(report, Report)
        with self.assertRaises(ValueError):
            self.manager.generate_report("unknown_report_type")

    def test_check_stock_levels(self):
        low_stock_msgs = self.manager.check_stock_levels()
        self.assertEqual(len(low_stock_msgs), 0)

    def test_notify_upcoming_deliveries(self):
        now = datetime.now()
        order = Order("o2", "s1", [{"product_id": "p1", "quantity": 5}], now, now + timedelta(days=5))
        self.manager.create_order(order)
        notifications = self.manager.notify_upcoming_deliveries()
        self.assertEqual(len(notifications), 1)

if __name__ == "__main__":
    unittest.main()
```