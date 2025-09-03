import hashlib
import secrets
import string
import threading
import time
from datetime import datetime, timedelta

class User:
    def __init__(self, user_id, username, email, password_hash, registration_date, portfolio):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.registration_date = registration_date
        self.portfolio = portfolio

class Stock:
    def __init__(self, stock_id, name, current_price):
        self.stock_id = stock_id
        self.name = name
        self.current_price = current_price
        self.price_history = [(datetime.now(), current_price)]
        self.market_trend = "Stable"  # "Bull" "Bear" or "Stable"

    def get_current_price(self):
        return self.current_price

    def update_price(self, new_price):
        self.current_price = new_price
        self.price_history.append((datetime.now(), new_price))
        self.update_market_trend()

    def update_market_trend(self):
        if len(self.price_history) < 2:
            self.market_trend = "Stable"
            return
        prices = [p for (d, p) in self.price_history[-10:]]
        if len(prices) < 2:
            self.market_trend = "Stable"
        elif prices[-1] > prices[0]:
            self.market_trend = "Bull"
        elif prices[-1] < prices[0]:
            self.market_trend = "Bear"
        else:
            self.market_trend = "Stable"

class Portfolio:
    def __init__(self, portfolio_id, user_id, balance=100000.0):
        self.portfolio_id = portfolio_id
        self.user_id = user_id
        self.stocks = {}  # stock_id -> quantity
        self.balance = balance

    def buy_stock(self, stock, quantity, price):
        cost = quantity * price
        if cost > self.balance:
            return False, "Insufficient balance."
        self.stocks[stock.stock_id] = self.stocks.get(stock.stock_id, 0) + quantity
        self.balance -= cost
        return True, f"Purchased {quantity} shares of {stock.name}."

    def sell_stock(self, stock, quantity, price):
        if stock.stock_id not in self.stocks or self.stocks[stock.stock_id] < quantity:
            return False, "Not enough shares to sell."
        self.stocks[stock.stock_id] -= quantity
        if self.stocks[stock.stock_id] == 0:
            del self.stocks[stock.stock_id]
        self.balance += price * quantity
        return True, f"Sold {quantity} shares of {stock.name}."

    def get_portfolio_value(self, stock_lookup):
        value = self.balance
        for stock_id, qty in self.stocks.items():
            stock = stock_lookup(stock_id)
            if stock: value += qty * stock.current_price
        return value

    def get_positions(self):
        return self.stocks.copy()

class Transaction:
    def __init__(self, transaction_id, user_id, stock_id, transaction_type, quantity, date):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.stock_id = stock_id
        self.transaction_type = transaction_type  # "buy" or "sell"
        self.quantity = quantity
        self.date = date

class Market:
    def __init__(self, market_id, stocks, update_interval=5):
        self.market_id = market_id
        self.stocks = {stock.stock_id: stock for stock in stocks}
        self.update_interval = update_interval  # seconds

    def update_stock_prices(self):
        # Simulate price change for each stock with random walk + occasional big moves
        import random
        for stock in self.stocks.values():
            last_price = stock.current_price
            pct_move = random.gauss(0, 0.015)  # about +-1.5%
            if random.random() < 0.05:
                pct_move += random.choice([-1, 1]) * random.uniform(0.05, 0.15) # 5-15% jump/drop
            new_price = round(max(1.0, last_price * (1 + pct_move)), 2)
            stock.update_price(new_price)

    def get_market_overview(self):
        return [
            {
                "stock_id": s.stock_id,
                "name": s.name,
                "current_price": s.current_price,
                "market_trend": s.market_trend
            }
            for s in self.stocks.values()
        ]

    def get_stock(self, stock_id):
        return self.stocks.get(stock_id)

    def get_all_stocks(self):
        return list(self.stocks.values())

class Notification:
    def __init__(self, notification_id, user_id, message, timestamp):
        self.notification_id = notification_id
        self.user_id = user_id
        self.message = message
        self.timestamp = timestamp

class LeaderboardEntry:
    def __init__(self, leaderboard_id, user_id, rank, score):
        self.leaderboard_id = leaderboard_id
        self.user_id = user_id
        self.rank = rank
        self.score = score

class StockMarketSimulator:
    def __init__(self):
        self._next_user_id = 1
        self._next_portfolio_id = 1
        self._next_transaction_id = 1
        self._next_notification_id = 1
        self._next_leaderboard_id = 1
        self._user_db = {}      # user_id -> User
        self._user_email_index = {}   # email -> user_id
        self._user_username_index = {} # username -> user_id
        self._stock_db = {}     # stock_id -> Stock
        self._portfolio_db = {} # user_id -> Portfolio
        self._transaction_db = []  # list of Transaction
        self._market = None
        self._notification_db = []  # list of Notification
        self._leaderboard = []      # list of LeaderboardEntry
        self._feedback_db = []      # (user_id, feedback_text, timestamp)

        self._user_auth_tokens = {} # token -> user_id
        self._user_account_status = {} # user_id -> status ("active", "suspended")
        self._transaction_rate_limit = {} # user_id -> [ordered list of timestamps]
        self._transaction_limit = 10   # max transactions per minute

        # Seed initial stocks & market
        stocks = [
            Stock(1, "ACME Corp", 100.00),
            Stock(2, "Globex Inc", 240.50),
            Stock(3, "Soylent Ltd", 57.70),
            Stock(4, "Initech PLC", 150.10),
            Stock(5, "Umbrella Corp", 32.40),
        ]
        self._stock_db = {s.stock_id: s for s in stocks}
        self._market = Market(1, stocks)
        self._start_market_simulation()

    # === User Registration and Authentication ===

    def register(self, username, email, password):
        errors = []
        if not self._validate_username_uniqueness(username):
            errors.append("Username already taken.")
        if not self._validate_email_uniqueness(email):
            errors.append("Email already registered.")
        pw_ok, pw_error = self._validate_password_strength(password)
        if not pw_ok:
            errors.append(pw_error)
        if errors:
            return False, errors

        hash_pw = self._hash_password(password)
        user_id = self._next_user_id
        self._next_user_id += 1

        portfolio = Portfolio(self._next_portfolio_id, user_id)
        self._next_portfolio_id += 1

        registration_date = datetime.now()
        user = User(user_id, username, email, hash_pw, registration_date, portfolio)
        self._user_db[user_id] = user
        self._user_email_index[email.lower()] = user_id
        self._user_username_index[username.lower()] = user_id
        self._portfolio_db[user_id] = portfolio
        self._user_account_status[user_id] = "active"
        return True, {"user_id": user_id, "message": "Registration successful."}

    def authenticate(self, email, password):
        user_id = self._user_email_index.get(email.lower())
        if not user_id: return False, "User not found."
        user = self._user_db[user_id]
        if not self._check_password(password, user.password_hash):
            return False, "Invalid password."
        if self._user_account_status.get(user_id, "active") != "active":
            return False, "Account is not active."
        # Generate OAuth2-like token (simulated)
        token = self._generate_auth_token(user_id)
        return True, {"user_id": user_id, "token": token, "username": user.username}

    def _generate_auth_token(self, user_id):
        token = secrets.token_urlsafe(32)
        self._user_auth_tokens[token] = user_id
        return token

    def check_token(self, token):
        return self._user_auth_tokens.get(token, None)

    def get_user(self, user_id):
        return self._user_db.get(user_id)

    def update_profile(self, user_id, new_data):
        user = self._user_db.get(user_id)
        if not user: return False, "User not found."
        if "username" in new_data:
            username = new_data["username"]
            if username != user.username:
                if not self._validate_username_uniqueness(username):
                    return False, "Username already exists."
                del self._user_username_index[user.username.lower()]
                self._user_username_index[username.lower()] = user_id
                user.username = username
        if "email" in new_data:
            email = new_data["email"]
            if email != user.email:
                if not self._validate_email_uniqueness(email):
                    return False, "Email already exists."
                del self._user_email_index[user.email.lower()]
                self._user_email_index[email.lower()] = user_id
                user.email = email
        return True, "Profile updated."

    def change_password(self, user_id, old_password, new_password):
        user = self._user_db.get(user_id)
        if not user: return False, "User not found."
        if not self._check_password(old_password, user.password_hash):
            return False, "Old password incorrect."
        pw_ok, pw_error = self._validate_password_strength(new_password)
        if not pw_ok: return False, pw_error
        user.password_hash = self._hash_password(new_password)
        return True, "Password changed successfully."

    # === Security & Validation Functions ===

    def _validate_email_uniqueness(self, email):
        return email.lower() not in self._user_email_index

    def _validate_username_uniqueness(self, username):
        return username.lower() not in self._user_username_index

    def _validate_password_strength(self, password):
        min_len = 8
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in string.punctuation for c in password)
        if len(password) < min_len:
            return False, f"Password must be at least {min_len} characters."
        if not (has_upper and has_lower and has_digit and has_special):
            return False, "Password must contain upper/lowercase letters, a digit, and a special character."
        return True, None

    def _hash_password(self, password):
        salt = secrets.token_bytes(16)
        h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return salt.hex() + h.hex()

    def _check_password(self, password, password_hash):
        try:
            salt_hex = password_hash[:32]
            hash_hex = password_hash[32:]
            salt = bytes.fromhex(salt_hex)
            h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
            return h.hex() == hash_hex
        except Exception:
            return False

    # === Stock Market Simulation / Real-Time Data ===

    def _start_market_simulation(self):
        def market_loop():
            while True:
                self._market.update_stock_prices()
                self._push_market_notifications()
                time.sleep(self._market.update_interval)
        th = threading.Thread(target=market_loop, daemon=True)
        th.start()

    def _push_market_notifications(self):
        for s in self._stock_db.values():
            if len(s.price_history) < 2:
                continue
            delta = s.price_history[-1][1] - s.price_history[-2][1]
            pct = abs(delta / s.price_history[-2][1]) if s.price_history[-2][1] > 0 else 0
            if pct > 0.06: # Notify if stock moves by >6%
                msg = f"{s.name} changed by {pct*100:.1f}% to {s.current_price:.2f}."
                for user_id in self._user_db:
                    self.send_notification(user_id, msg)

    def get_market_overview(self):
        return self._market.get_market_overview()

    def get_stock(self, stock_id):
        return self._market.get_stock(stock_id)

    def get_all_stocks(self):
        return self._market.get_all_stocks()

    # === Portfolio Management ===

    def buy_stock(self, user_id, stock_id, quantity):
        status = self._user_account_status.get(user_id, "active")
        if status != "active":
            return False, "Account not in active state."
        if not self._limit_transactions(user_id):
            return False, "Too many transactions, slow down."
        stock = self._stock_db.get(stock_id)
        if not stock: return False, "Stock not found."
        portfolio = self._portfolio_db.get(user_id)
        if not portfolio: return False, "Portfolio not found."
        ok, msg = portfolio.buy_stock(stock, quantity, stock.current_price)
        if ok:
            self._record_transaction(user_id, stock_id, "buy", quantity)
            self.send_notification(user_id, f"Bought {quantity}x {stock.name} at {stock.current_price:.2f}")
        return ok, msg

    def sell_stock(self, user_id, stock_id, quantity):
        status = self._user_account_status.get(user_id, "active")
        if status != "active":
            return False, "Account not in active state."
        if not self._limit_transactions(user_id):
            return False, "Too many transactions, slow down."
        stock = self._stock_db.get(stock_id)
        if not stock: return False, "Stock not found."
        portfolio = self._portfolio_db.get(user_id)
        if not portfolio: return False, "Portfolio not found."
        ok, msg = portfolio.sell_stock(stock, quantity, stock.current_price)
        if ok:
            self._record_transaction(user_id, stock_id, "sell", quantity)
            self.send_notification(user_id, f"Sold {quantity}x {stock.name} at {stock.current_price:.2f}")
        return ok, msg

    def get_portfolio(self, user_id):
        portfolio = self._portfolio_db.get(user_id)
        if not portfolio: return None
        result = {
            "user_id": user_id,
            "balance": round(portfolio.balance, 2),
            "stocks": [],
            "portfolio_value": round(portfolio.get_portfolio_value(lambda sid: self._stock_db.get(sid)), 2)
        }
        for stock_id, qty in portfolio.stocks.items():
            stock = self._stock_db.get(stock_id)
            if stock:
                result["stocks"].append({
                    "stock_id": stock_id,
                    "name": stock.name,
                    "quantity": qty,
                    "current_price": stock.current_price,
                    "market_trend": stock.market_trend
                })
        return result

    # === Transactions: Record & Limiting ===

    def _record_transaction(self, user_id, stock_id, transaction_type, quantity):
        transaction_id = self._next_transaction_id
        self._next_transaction_id += 1
        tran = Transaction(transaction_id, user_id, stock_id, transaction_type, quantity, datetime.now())
        self._transaction_db.append(tran)
        return tran

    def _limit_transactions(self, user_id):
        now = datetime.now()
        window_start = now - timedelta(minutes=1)
        history = self._transaction_rate_limit.get(user_id, [])
        # Remove old times
        history = [d for d in history if d > window_start]
        if len(history) >= self._transaction_limit:
            self._transaction_rate_limit[user_id] = history
            return False
        history.append(now)
        self._transaction_rate_limit[user_id] = history
        return True

    # === Notifications ===

    def send_notification(self, user_id, message):
        notification_id = self._next_notification_id
        self._next_notification_id += 1
        n = Notification(notification_id, user_id, message, datetime.now())
        self._notification_db.append(n)

    def get_notifications(self, user_id):
        return [
            {
                "notification_id": n.notification_id,
                "message": n.message,
                "timestamp": n.timestamp
            }
            for n in self._notification_db if n.user_id == user_id
        ][-20:]

    # === Leaderboard ===

    def update_leaderboard(self):
        entries = []
        users = list(self._user_db.values())
        users.sort(
            key=lambda u: self._portfolio_db[u.user_id].get_portfolio_value(lambda sid: self._stock_db.get(sid)),
            reverse=True)
        for i, user in enumerate(users):
            score = self._portfolio_db[user.user_id].get_portfolio_value(lambda sid: self._stock_db.get(sid))
            entry = LeaderboardEntry(self._next_leaderboard_id + i, user.user_id, i+1, score)
            entries.append(entry)
        self._leaderboard = entries

    def get_top_traders(self, top_n=10):
        self.update_leaderboard()
        result = []
        for entry in self._leaderboard[:top_n]:
            user = self._user_db.get(entry.user_id)
            if not user: continue
            result.append({
                "rank": entry.rank,
                "username": user.username,
                "portfolio_value": round(entry.score, 2)
            })
        return result

    # === Educational Content ===

    def get_tutorials(self):
        return [
            {
                "title": "What is a Stock?",
                "content": "A stock is a type of security that gives you ownership in a company."
            },
            {
                "title": "How Does the Stock Market Work?",
                "content": "Stock prices fluctuate based on supply and demand, news, and earnings reports."
            },
            {
                "title": "Buying and Selling Stocks",
                "content": "You can buy low and sell high, or try to day trade for short term gains."
            },
            {
                "title": "Portfolio Diversification",
                "content": "Spreading investments across several stocks reduces your risk."
            }
        ]

    # === User Feedback ===

    def submit_feedback(self, user_id, feedback_text):
        ts = datetime.now()
        self._feedback_db.append((user_id, feedback_text, ts))
        return True, "Feedback submitted. Thank you!"

    def get_feedback(self):
        # For admin only
        return [
            {"user_id": user_id, "feedback": text, "timestamp": ts}
            for (user_id, text, ts) in self._feedback_db
        ]

    # === Additional Utility Methods ===

    def is_username_taken(self, username):
        return not self._validate_username_uniqueness(username)

    def is_email_taken(self, email):
        return not self._validate_email_uniqueness(email)

    def suspend_user(self, user_id):
        self._user_account_status[user_id] = "suspended"

    def activate_user(self, user_id):
        self._user_account_status[user_id] = "active"

# You can create an instance of StockMarketSimulator and use its APIs directly.
# Example:
# sim = StockMarketSimulator()
# sim.register("alice", "alice@email.com", "Password!23")
# success, auth = sim.authenticate("alice@email.com", "Password!23")
# sim.buy_stock(auth["user_id"], 1, 10)
# sim.get_portfolio(auth["user_id"])
# etc.