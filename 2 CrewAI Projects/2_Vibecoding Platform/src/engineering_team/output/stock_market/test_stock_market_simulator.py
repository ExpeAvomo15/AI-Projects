from datetime import datetime, timedelta
import unittest
from stock_market_simulator import StockMarketSimulator, User, Stock, Portfolio, Transaction, Market, Notification, LeaderboardEntry

class TestStockMarketSimulator(unittest.TestCase):

    def setUp(self):
        self.simulator = StockMarketSimulator()

    def test_register_user_successful(self):
        success, result = self.simulator.register("john_doe", "john_doe@example.com", "SecurePass!123")
        self.assertTrue(success)
        self.assertIn("user_id", result)

    def test_register_user_duplicate_username(self):
        self.simulator.register("john_doe", "john_doe@example.com", "SecurePass!123")
        success, errors = self.simulator.register("john_doe", "john2_doe@example.com", "SecurePass!123")
        self.assertFalse(success)
        self.assertIn("Username already taken.", errors)

    def test_register_user_duplicate_email(self):
        self.simulator.register("john_doe", "john_doe@example.com", "SecurePass!123")
        success, errors = self.simulator.register("john2", "john_doe@example.com", "SecurePass!123")
        self.assertFalse(success)
        self.assertIn("Email already registered.", errors)

    def test_register_user_weak_password(self):
        success, errors = self.simulator.register("john_doe", "john_doe@example.com", "weakpass")
        self.assertFalse(success)
        self.assertIn("Password must contain upper/lowercase letters, a digit, and a special character.", errors)

    def test_authenticate_successful(self):
        self.simulator.register("john_doe", "john_doe@example.com", "SecurePass!123")
        success, auth = self.simulator.authenticate("john_doe@example.com", "SecurePass!123")
        self.assertTrue(success)
        self.assertIn("token", auth)

    def test_authenticate_wrong_password(self):
        self.simulator.register("john_doe", "john_doe@example.com", "SecurePass!123")
        success, message = self.simulator.authenticate("john_doe@example.com", "WrongPass")
        self.assertFalse(success)
        self.assertEqual(message, "Invalid password.")

    def test_stock_price_update(self):
        stock = self.simulator.get_stock(1)
        initial_price = stock.get_current_price()
        self.simulator._market.update_stock_prices()
        updated_stock = self.simulator.get_stock(1)
        self.assertNotEqual(initial_price, updated_stock.get_current_price())

    def test_buy_stock_success(self):
        self.simulator.register("john_doe", "john_doe@example.com", "SecurePass!123")
        success, auth = self.simulator.authenticate("john_doe@example.com", "SecurePass!123")
        user_id = auth["user_id"]
        success, message = self.simulator.buy_stock(user_id, 1, 10)
        self.assertTrue(success)

    def test_buy_stock_insufficient_balance(self):
        self.simulator.register("richard_roe", "richard_roe@example.com", "SecurePass!123")
        success, auth = self.simulator.authenticate("richard_roe@example.com", "SecurePass!123")
        user_id = auth["user_id"]
        stock = self.simulator.get_stock(2)
        high_quantity = 1000000  # Assuming this exceeds balance
        success, message = self.simulator.buy_stock(user_id, stock.stock_id, high_quantity)
        self.assertFalse(success)
        self.assertEqual(message, "Insufficient balance.")

    def test_sell_stock_success(self):
        self.simulator.register("john_doe", "john_doe@example.com", "SecurePass!123")
        success, auth = self.simulator.authenticate("john_doe@example.com", "SecurePass!123")
        user_id = auth["user_id"]
        self.simulator.buy_stock(user_id, 1, 10)  # Buy first
        success, message = self.simulator.sell_stock(user_id, 1, 5)
        self.assertTrue(success)

    def test_sell_stock_not_enough_shares(self):
        self.simulator.register("john_doe", "john_doe@example.com", "SecurePass!123")
        success, auth = self.simulator.authenticate("john_doe@example.com", "SecurePass!123")
        user_id = auth["user_id"]
        self.simulator.buy_stock(user_id, 1, 5)
        success, message = self.simulator.sell_stock(user_id, 1, 10)
        self.assertFalse(success)
        self.assertEqual(message, "Not enough shares to sell.")

    def test_market_overview(self):
        overview = self.simulator.get_market_overview()
        self.assertTrue(len(overview) > 0)
        self.assertIn("name", overview[0])

    def test_leaderboard_update(self):
        entries_before = self.simulator.get_top_traders()
        self.simulator.register("alice", "alice@example.com", "Password!23")
        entries_after = self.simulator.get_top_traders()
        self.assertGreater(len(entries_after), len(entries_before))

    def test_submit_feedback(self):
        self.simulator.register("user", "user@example.com", "Password!23")
        success, auth = self.simulator.authenticate("user@example.com", "Password!23")
        user_id = auth["user_id"]
        feedback_text = "This is a feedback text."
        success, message = self.simulator.submit_feedback(user_id, feedback_text)
        self.assertTrue(success)
        self.assertEqual(message, "Feedback submitted. Thank you!")

    def test_get_notifications(self):
        self.simulator.register("user", "user@example.com", "Password!23")
        success, auth = self.simulator.authenticate("user@example.com", "Password!23")
        user_id = auth["user_id"]
        self.simulator.send_notification(user_id, "Test notification message!")
        notifications = self.simulator.get_notifications(user_id)
        self.assertGreater(len(notifications), 0)
        self.assertEqual(notifications[-1]['message'], "Test notification message!")

if __name__ == "__main__":
    unittest.main()