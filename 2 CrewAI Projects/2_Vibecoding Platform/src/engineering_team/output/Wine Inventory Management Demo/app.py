import gradio as gr
from datetime import datetime
import uuid

from wine_inventory_management import (
    WineInventoryManager,
    WineProduct,
    Supplier,
    Order,
    Sale,
)

manager = WineInventoryManager()

# Initialize demo data
def init_demo_data():
    if not manager.wine_products:
        p1 = WineProduct("p1", "Chateau Margaux", "Red", "Margaux", "2015", 450.0, 20)
        p2 = WineProduct("p2", "Screaming Eagle", "Red", "Screaming Eagle", "2012", 3200.0, 2)
        manager.add_wine_product(p1)
        manager.add_wine_product(p2)
    if not manager.suppliers:
        s1 = Supplier("s1", "Great Wines Co.", "email: contact@greatwines.com", ["p1", "p2"])
        manager.add_supplier(s1)
    if not manager.orders:
        o1 = Order("o1", "s1", [{"product_id": "p1", "quantity": 10}], datetime.now(), datetime.now())
        manager.create_order(o1)
    if not manager.sales:
        sale1 = Sale("sale1", "John Doe, 123 Main St", [{"product_id": "p1", "quantity": 2}], datetime.now(), 900.0)
        manager.add_sale(sale1)

init_demo_data()

### Inventory Management Tab Functions

def list_wine_products():
    products = manager.list_all_products()
    if not products:
        return "No wine products in inventory."
    header = "| ID | Name | Type | Brand | Vintage | Price | Stock |\n|---|---|---|---|---|---|---|"
    rows = [
        f"| {p['product_id']} | {p['name']} | {p['type']} | {p['brand']} | {p['vintage']} | ${p['price']:.2f} | {p['stock_level']} |"
        for p in products
    ]
    return header + "\n" + "\n".join(rows)

def add_wine_product(
    name, typ, brand, vintage, price, stock_level
):
    try:
        product_id = str(uuid.uuid4())[:8]
        price = float(price)
        stock_level = int(stock_level)
        product = WineProduct(product_id, name, typ, brand, vintage, price, stock_level)
        manager.add_wine_product(product)
        return f"WineProduct '{name}' added with ID {product_id}."
    except Exception as e:
        return f"Error: {str(e)}"

def update_stock(product_id, quantity):
    try:
        quantity = int(quantity)
        manager.update_stock_level(product_id, quantity)
        new_stock = manager.get_product_info(product_id).stock_level
        return f"Stock updated. New stock level for {product_id}: {new_stock}"
    except Exception as e:
        return f"Error: {str(e)}"

### Supplier Management Tab Functions

def list_suppliers():
    suppliers = manager.list_all_suppliers()
    if not suppliers:
        return "No suppliers available."
    header = "| ID | Name | Contact | Product List |\n|---|---|---|---|"
    rows = [
        f"| {s['supplier_id']} | {s['name']} | {s['contact_info']} | {', '.join(s['product_list'])} |"
        for s in suppliers
    ]
    return header + "\n" + "\n".join(rows)

def add_supplier(name, contact_info, product_list):
    try:
        supplier_id = str(uuid.uuid4())[:8]
        products = [p.strip() for p in product_list.split(",") if p.strip()]
        supplier = Supplier(supplier_id, name, contact_info, products)
        manager.add_supplier(supplier)
        return f"Supplier '{name}' added with ID {supplier_id}."
    except Exception as e:
        return f"Error: {str(e)}"

### Order Management Tab Functions

def list_orders():
    orders = manager.list_all_orders()
    if not orders:
        return "No supplier orders."
    header = "| Order ID | Supplier | Products | Order Date | Delivery Date |\n|---|---|---|---|---|"
    rows = []
    for o in orders:
        prods = ", ".join(f"{x['product_id']} x{x['quantity']}" for x in o['product_list'])
        rows.append(f"| {o['order_id']} | {o['supplier_id']} | {prods} | {o['order_date'][:10]} | {o['delivery_date'][:10]} |")
    return header + "\n" + "\n".join(rows)

def create_order(supplier_id, product_id_quantity, order_date, delivery_date):
    try:
        odate = datetime.strptime(order_date, "%Y-%m-%d")
        ddate = datetime.strptime(delivery_date, "%Y-%m-%d")
        if not supplier_id or not product_id_quantity:
            return "Supplier ID and Product List required."
        product_list = []
        for entry in product_id_quantity.split(","):
            prod = entry.strip().split("x")
            if len(prod) == 2:
                pid, qty = prod
                product_list.append({"product_id": pid.strip(), "quantity": int(qty.strip())})
        order_id = str(uuid.uuid4())[:8]
        order = Order(order_id, supplier_id, product_list, odate, ddate)
        manager.create_order(order)
        return f"Order '{order_id}' placed."
    except Exception as e:
        return f"Error: {str(e)}"

### Sales Tracking Tab

def list_sales():
    sales = manager.list_all_sales()
    if not sales:
        return "No sales recorded."
    header = "| Sale ID | Customer | Products | Sale Date | Total Amount |\n|---|---|---|---|---|"
    rows = []
    for s in sales:
        prods = ", ".join(f"{x['product_id']} x{x['quantity']}" for x in s['product_list'])
        rows.append(f"| {s['sale_id']} | {s['customer_info']} | {prods} | {s['sale_date'][:10]} | ${s['total_amount']:.2f} |")
    return header + "\n" + "\n".join(rows)

def add_sale(
    customer_info, product_id_quantity, sale_date, total_amount
):
    try:
        sdate = datetime.strptime(sale_date, "%Y-%m-%d")
        product_list = []
        for entry in product_id_quantity.split(","):
            prod = entry.strip().split("x")
            if len(prod) == 2:
                pid, qty = prod
                product_list.append({"product_id": pid.strip(), "quantity": int(qty.strip())})
        sale_id = str(uuid.uuid4())[:8]
        total_amount = float(total_amount)
        sale = Sale(sale_id, customer_info, product_list, sdate, total_amount)
        manager.add_sale(sale)
        return f"Sale '{sale_id}' added."
    except Exception as e:
        return f"Error: {str(e)}"

### Reporting Tab

def report_stock_levels():
    try:
        rep = manager.generate_report("stock_levels")
        return rep.content
    except Exception as e:
        return f"Error: {str(e)}"

def report_sales_performance():
    try:
        rep = manager.generate_report("sales_performance")
        return rep.content
    except Exception as e:
        return f"Error: {str(e)}"

def report_supplier_orders():
    try:
        rep = manager.generate_report("supplier_orders")
        return rep.content
    except Exception as e:
        return f"Error: {str(e)}"

### Notifications

def notifications():
    lines = []
    lows = manager.check_stock_levels()
    upcoming = manager.notify_upcoming_deliveries()
    if lows:
        lines.append("**Low Stock Alerts:**")
        lines += lows
    if upcoming:
        if lines:
            lines.append("")
        lines.append("**Upcoming Deliveries:**")
        lines += upcoming
    if not lines:
        return "No notifications."
    return "\n".join(lines)

### Gradio UI Layout

with gr.Blocks() as demo:
    gr.Markdown("# 🍷 Wine Inventory Management Demo")
    with gr.Tabs():
        with gr.Tab("Inventory"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Add New Wine Product")
                    name = gr.Textbox(label="Name")
                    typ = gr.Textbox(label="Type (Red/White, etc.)")
                    brand = gr.Textbox(label="Brand")
                    vintage = gr.Textbox(label="Vintage")
                    price = gr.Textbox(label="Price", value="100.0")
                    stock = gr.Textbox(label="Stock Level", value="10")
                    add_btn = gr.Button("Add Product")
                    add_out = gr.Markdown()
                    add_btn.click(
                        add_wine_product,
                        inputs=[name, typ, brand, vintage, price, stock],
                        outputs=add_out,
                    )
                with gr.Column():
                    gr.Markdown("#### All Wine Products")
                    refresh_btn = gr.Button("Refresh Table")
                    products_md = gr.Markdown()
                    refresh_btn.click(list_wine_products, outputs=products_md)
                    products_md.value = list_wine_products()
                    gr.Markdown("#### Update Stock Level")
                    product_id_upd = gr.Textbox(label="Product ID")
                    qty = gr.Textbox(label="Quantity (+/-)")
                    upd_btn = gr.Button("Update Stock")
                    upd_out = gr.Markdown()
                    upd_btn.click(update_stock, inputs=[product_id_upd, qty], outputs=upd_out)
        with gr.Tab("Suppliers"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Add Supplier")
                    supplier_name = gr.Textbox(label="Supplier Name")
                    supplier_contact = gr.Textbox(label="Contact Info")
                    supplier_list = gr.Textbox(label="Supplied Products CSV (e.g. p1,p2)")
                    supplier_btn = gr.Button("Add Supplier")
                    supplier_out = gr.Markdown()
                    supplier_btn.click(add_supplier, inputs=[supplier_name, supplier_contact, supplier_list], outputs=supplier_out)
                with gr.Column():
                    gr.Markdown("#### All Suppliers")
                    sup_refresh_btn = gr.Button("Refresh Suppliers")
                    suppliers_md = gr.Markdown()
                    sup_refresh_btn.click(list_suppliers, outputs=suppliers_md)
                    suppliers_md.value = list_suppliers()
        with gr.Tab("Orders"):
            gr.Markdown("#### Place Order To Supplier")
            supp_id = gr.Textbox(label="Supplier ID")
            prod_qty = gr.Textbox(label="Products to Order (prodid x qty, comma separated, e.g. p1x5,p2x2)")
            odate = gr.Textbox(label="Order Date (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"))
            ddate = gr.Textbox(label="Delivery Date (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"))
            order_btn = gr.Button("Place Order")
            order_out = gr.Markdown()
            order_btn.click(create_order, inputs=[supp_id, prod_qty, odate, ddate], outputs=order_out)
            gr.Markdown("#### All Orders")
            order_refresh_btn = gr.Button("Refresh Orders")
            orders_md = gr.Markdown()
            order_refresh_btn.click(list_orders, outputs=orders_md)
            orders_md.value = list_orders()
        with gr.Tab("Sales"):
            gr.Markdown("#### Record Sale")
            cust_info = gr.Textbox(label="Customer Info")
            sale_prods = gr.Textbox(label="Products Sold (prodid x qty, comma separated, e.g. p1x2)")
            sale_date = gr.Textbox(label="Sale Date (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"))
            total = gr.Textbox(label="Total Amount")
            sale_btn = gr.Button("Add Sale")
            sale_out = gr.Markdown()
            sale_btn.click(add_sale, inputs=[cust_info, sale_prods, sale_date, total], outputs=sale_out)
            gr.Markdown("#### All Sales")
            sale_refresh_btn = gr.Button("Refresh Sales")
            sales_md = gr.Markdown()
            sale_refresh_btn.click(list_sales, outputs=sales_md)
            sales_md.value = list_sales()
        with gr.Tab("Reports"):
            gr.Markdown("#### Generate Reports")
            stock_btn = gr.Button("Stock Levels")
            stock_out = gr.Markdown()
            stock_btn.click(report_stock_levels, outputs=stock_out)
            salesrep_btn = gr.Button("Sales Performance")
            salesrep_out = gr.Markdown()
            salesrep_btn.click(report_sales_performance, outputs=salesrep_out)
            orderrep_btn = gr.Button("Supplier Orders")
            orderrep_out = gr.Markdown()
            orderrep_btn.click(report_supplier_orders, outputs=orderrep_out)
        with gr.Tab("Notifications"):
            gr.Markdown("#### Alerts & Notifications")
            notif_btn = gr.Button("Check Now")
            notif_md = gr.Markdown()
            notif_btn.click(notifications, outputs=notif_md)
            notif_md.value = notifications()

if __name__ == "__main__":
    demo.launch()