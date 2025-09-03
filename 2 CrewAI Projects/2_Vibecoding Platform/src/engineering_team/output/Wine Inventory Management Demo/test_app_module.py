import unittest
from app_module import Product, Inventory, Supplier, User, Report


class TestProduct(unittest.TestCase):

    def setUp(self):
        Product.products.clear()

    def test_add_product(self):
        product = Product(1, "Product1", "Description1", 10.0, 100, "Category1", 1)
        self.assertIn("Product1", Product.products)

    def test_add_product_with_duplicate_name(self):
        Product(1, "UniqueProduct", "Description1", 10.0, 100, "Category1", 1)
        with self.assertRaises(ValueError):
            Product(2, "UniqueProduct", "Description2", 15.0, 50, "Category2", 2)

    def test_update_product(self):
        product = Product(1, "Product1", "Description1", 10.0, 100, "Category1", 1)
        product.update_product(1, price=20.0, quantity=150)
        self.assertEqual(product.price, 20.0)
        self.assertEqual(product.quantity, 150)

    def test_delete_product(self):
        product = Product(1, "Product1", "Description1", 10.0, 100, "Category1", 1)
        product.delete_product(1)
        self.assertNotIn("Product1", Product.products)

    def test_get_product_details(self):
        product = Product(1, "Product1", "Description1", 10.0, 100, "Category1", 1)
        details = product.get_product_details(1)
        self.assertEqual(details['name'], "Product1")


class TestInventory(unittest.TestCase):

    def setUp(self):
        Inventory.inventory_records.clear()

    def test_register_stock_entry(self):
        inventory = Inventory(1, 1, 100, "2023-10-01 10:00:00")
        inventory.register_stock_entry(1, 50)
        self.assertEqual(inventory.current_quantity, 150)

    def test_register_stock_exit(self):
        inventory = Inventory(1, 1, 100, "2023-10-01 10:00:00")
        inventory.register_stock_exit(1, 50)
        self.assertEqual(inventory.current_quantity, 50)

    def test_register_stock_exit_error(self):
        inventory = Inventory(1, 1, 50, "2023-10-01 10:00:00")
        with self.assertRaises(ValueError):
            inventory.register_stock_exit(1, 60)

    def test_check_low_stock(self):
        Inventory(1, 1, 50, "2023-10-01 10:00:00")
        low_stock = Inventory(1, 2, 30, "2023-10-01 10:00:00")
        result = inventory.check_low_stock(40)
        self.assertIn(2, result)


class TestSupplier(unittest.TestCase):

    def setUp(self):
        Supplier.suppliers.clear()

    def test_add_supplier(self):
        supplier = Supplier(1, "Supplier1", "Contact1", "Address1")
        self.assertIn(1, Supplier.suppliers)

    def test_update_supplier(self):
        supplier = Supplier(1, "Supplier1", "Contact1", "Address1")
        supplier.update_supplier(1, contact="NewContact1")
        self.assertEqual(supplier.contact, "NewContact1")

    def test_delete_supplier(self):
        supplier = Supplier(1, "Supplier1", "Contact1", "Address1")
        supplier.delete_supplier(1)
        self.assertNotIn(1, Supplier.suppliers)


class TestUser(unittest.TestCase):

    def setUp(self):
        User.users.clear()

    def test_authenticate_user(self):
        user = User(1, "user1", "passhash", "admin")
        self.assertTrue(user.authenticate("user1", "passhash"))

    def test_authorize_user(self):
        user = User(1, "user1", "passhash", "admin")
        self.assertTrue(user.authorize("admin", "some_action"))

    def test_authenticate_fail(self):
        user = User(1, "user1", "passhash", "admin")
        self.assertFalse(user.authenticate("user1", "wronghash"))


class TestReport(unittest.TestCase):

    def setUp(self):
        Inventory.inventory_records.clear()
        Inventory(1, 1, 100, "2023-10-01 10:00:00")

    def test_generate_inventory_report(self):
        report = Report(1, "Inventory", "2023-10-01", {})
        inventory_report = report.generate_inventory_report()
        self.assertIn(1, inventory_report)

    def test_view_stock_trends(self):
        report = Report(1, "Inventory", "2023-10-01", {})
        trends = report.view_stock_trends()
        self.assertIn(1, trends)


if __name__ == '__main__':
    unittest.main()