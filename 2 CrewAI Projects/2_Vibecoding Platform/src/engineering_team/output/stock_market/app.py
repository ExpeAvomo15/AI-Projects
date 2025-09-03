import gradio as gr
from stock_market_simulator import StockMarketSimulator
import time

sim = StockMarketSimulator()

# Session vars for demo (just 1 user at a time in UI)
DEMO_SESSION = {"token": None, "user_id": None, "username": None}

def reset_session():
    DEMO_SESSION["token"] = None
    DEMO_SESSION["user_id"] = None
    DEMO_SESSION["username"] = None

# === User registration & login ===
def register_ui(username, email, password):
    ok, resp = sim.register(username.strip(), email.strip(), password)
    if not ok:
        if isinstance(resp, list):
            return False, "\n".join(resp)
        else:
            return False, str(resp)
    return True, "Registration successful. You can now login!"

def login_ui(email, password):
    ok, resp = sim.authenticate(email.strip(), password)
    if not ok:
        return False, resp
    DEMO_SESSION["token"] = resp["token"]
    DEMO_SESSION["user_id"] = resp["user_id"]
    DEMO_SESSION["username"] = resp["username"]
    return True, f"Welcome {DEMO_SESSION['username']}!"

def logout_ui():
    reset_session()
    return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

# === Market overview ===
def get_market_view():
    stocks = sim.get_market_overview()
    rows = [[
        s["stock_id"],
        s["name"],
        f"{s['current_price']:.2f}",
        s["market_trend"]
    ] for s in stocks]
    return rows

# === Portfolio view ===
def get_portfolio_view():
    user_id = DEMO_SESSION["user_id"]
    data = sim.get_portfolio(user_id)
    if not data:
        return "No portfolio found.", []
    lines = [f"Balance: ${data['balance']:.2f}", f"Portfolio Value: ${data['portfolio_value']:.2f}"]
    stock_rows = []
    if not data["stocks"]:
        lines.append("(You do not own any stocks yet.)")
    else:
        for row in data["stocks"]:
            stock_rows.append([row["stock_id"], row["name"], row["quantity"], f"{row['current_price']:.2f}", row["market_trend"]])
    return "\n".join(lines), stock_rows

# === Buy/Sell ===
def buy_stock_ui(stock_id, quantity):
    user_id = DEMO_SESSION["user_id"]
    try:
        stock_id = int(stock_id)
        quantity = int(quantity)
        if quantity < 1:
            return "Quantity must be at least 1."
    except Exception:
        return "Enter valid stock ID and quantity."
    ok, msg = sim.buy_stock(user_id, stock_id, quantity)
    return msg

def sell_stock_ui(stock_id, quantity):
    user_id = DEMO_SESSION["user_id"]
    try:
        stock_id = int(stock_id)
        quantity = int(quantity)
        if quantity < 1:
            return "Quantity must be at least 1."
    except Exception:
        return "Enter valid stock ID and quantity."
    ok, msg = sim.sell_stock(user_id, stock_id, quantity)
    return msg

# === Notifications ===
def get_notifications_view():
    user_id = DEMO_SESSION["user_id"]
    notes = sim.get_notifications(user_id)
    lines = [f"[{n['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] {n['message']}" for n in notes]
    return "\n".join(lines[-7:]) if lines else "No notifications yet."

# === Educational ===
def get_educational_content():
    tuts = sim.get_tutorials()
    return "\n\n".join([f"**{t['title']}**\n{t['content']}" for t in tuts])

# === Feedback ===
def feedback_ui(feedback_text):
    user_id = DEMO_SESSION["user_id"]
    ok, msg = sim.submit_feedback(user_id, feedback_text)
    return msg

# === Leaderboard ===
def get_leaderboard():
    entries = sim.get_top_traders()
    return [[e["rank"], e["username"], f"{e['portfolio_value']:.2f}"] for e in entries]

#### --- UI Layout --- ####

with gr.Blocks(title="Stock Market Simulator Demo") as demo:

    # -------- Registration/Login Panel --------
    login_register_panel = gr.TabbedInterface(tab_names=["Login", "Register"], interface_list=[gr.Blocks(), gr.Blocks()])
    with login_register_panel:
        # Login Tab
        with gr.Tab("Login"):
            login_email = gr.Text(label="Email")
            login_pw = gr.Text(label="Password", type="password")
            login_btn = gr.Button("Login")
            login_status = gr.Markdown("")
        # Register Tab
        with gr.Tab("Register"):
            reg_username = gr.Text(label="Username")
            reg_email = gr.Text(label="Email")
            reg_pw = gr.Text(label="Password", type="password")
            reg_btn = gr.Button("Register")
            reg_status = gr.Markdown("")
    # -------- Main Dashboard Panel --------
    dashboard_panel = gr.Group(visible=False)
    with dashboard_panel:
        gr.Markdown("## Stock Market Simulator")
        gr.Markdown(lambda: f"Welcome, **{DEMO_SESSION['username']}**!", elem_id="greeting")
        logout_btn = gr.Button("Logout", variant="secondary")
        with gr.Row():
            with gr.Column(scale=3):
                gr.Markdown("### Market Overview")
                market_table = gr.Dataframe(
                    headers=["Stock ID", "Name", "Price", "Trend"],
                    value=get_market_view,
                    interactive=False,
                    height=180,
                    every=3,
                )
            with gr.Column(scale=2):
                gr.Markdown("### Your Portfolio")
                port_summary = gr.Textbox(label="Portfolio Summary", interactive=False)
                port_table = gr.Dataframe(
                    headers=["Stock ID", "Name", "Qty", "Price", "Trend"],
                    value=[],
                    interactive=False,
                    height=120,
                )
                gr.Button("Refresh Portfolio", elem_id="refresh_port")
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Buy Stock")
                buy_id = gr.Number(label="Stock ID", value=1)
                buy_qty = gr.Number(label="Quantity", value=1)
                buy_btn = gr.Button("Buy")
                buy_msg = gr.Markdown("")
            with gr.Column():
                gr.Markdown("#### Sell Stock")
                sell_id = gr.Number(label="Stock ID", value=1)
                sell_qty = gr.Number(label="Quantity", value=1)
                sell_btn = gr.Button("Sell")
                sell_msg = gr.Markdown("")
        with gr.Row():
            gr.Markdown("### Notifications")
            notif_box = gr.Textbox(label="", lines=6, max_lines=8, interactive=False, value=get_notifications_view, every=3)
        with gr.Row():
            gr.Markdown("### Educational: Market Basics")
            edu_box = gr.Markdown(get_educational_content())
        with gr.Row():
            gr.Markdown("### Submit Feedback")
            feedback_in = gr.Textbox(label="Feedback", lines=2)
            feedback_btn = gr.Button("Submit Feedback")
            feedback_ack = gr.Markdown("")

        with gr.Row():
            gr.Markdown("### Leaderboard")
            leaderboard_df = gr.Dataframe(
                headers=["Rank", "Username", "Portfolio Value"],
                value=get_leaderboard,
                interactive=False,
                height=130,
                every=5,
            )

    # Callbacks
    reg_btn.click(
        fn=register_ui,
        inputs=[reg_username, reg_email, reg_pw],
        outputs=[reg_status, reg_status],
    ).then(lambda ok,msg: (gr.update(selected="Login"), gr.update(value="Registration successful. You can now login!") if ok else gr.update()), outputs=[login_register_panel, login_status])

    login_btn.click(
        fn=login_ui, inputs=[login_email, login_pw], outputs=[login_status, login_status]
    ).then(
        fn=lambda ok, msg: (
            gr.update(visible=not ok),
            gr.update(visible=ok),
            gr.update(visible=ok),
            gr.update(visible=ok),
        ),
        inputs=[login_status, login_status],  # Trick just to invoke this after login
        outputs=[login_register_panel, dashboard_panel, port_summary, port_table],
        show_progress=False,
    ).then(
        lambda: get_portfolio_view(),
        None,
        outputs=[port_summary, port_table],
    )

    logout_btn.click(fn=logout_ui, outputs=[login_register_panel, dashboard_panel, port_summary, port_table])

    buy_btn.click(
        fn=buy_stock_ui,
        inputs=[buy_id, buy_qty],
        outputs=[buy_msg]
    ).then(
        fn=lambda: get_portfolio_view(),
        inputs=None,
        outputs=[port_summary, port_table]
    )

    sell_btn.click(
        fn=sell_stock_ui,
        inputs=[sell_id, sell_qty],
        outputs=[sell_msg]
    ).then(
        fn=lambda: get_portfolio_view(),
        inputs=None,
        outputs=[port_summary, port_table]
    )

    # feedback
    feedback_btn.click(fn=feedback_ui, inputs=[feedback_in], outputs=[feedback_ack])

    # portfolio refresh
    demo.reload(fn=get_portfolio_view, outputs=[port_summary, port_table])

if __name__ == "__main__":
    demo.launch()