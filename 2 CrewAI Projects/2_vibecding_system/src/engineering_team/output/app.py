import gradio as gr
from inventario_bar import GestionInventario

# Initialize the inventory management system
inventario = GestionInventario()

def agregar_producto(nombre, descripcion, categoria, stock_inicial, unidad, stock_minimo):
    try:
        producto_id = inventario.add_producto(nombre, descripcion, categoria, stock_inicial, unidad, stock_minimo)
        return f"Producto agregado con ID: {producto_id}"
    except Exception as e:
        return str(e)

def listar_productos(filtro_nombre=None, filtro_categoria=None):
    filtro = {}
    if filtro_nombre:
        filtro['nombre'] = filtro_nombre
    if filtro_categoria:
        filtro['categoria'] = filtro_categoria
    productos = inventario.listar_productos(filtro)
    return productos

def registrar_movimiento(producto_id, cantidad, tipo, motivo, usuario):
    try:
        movimiento_id = inventario.registrar_movimiento(producto_id, cantidad, tipo, motivo, usuario)
        return f"Movimiento registrado con ID: {movimiento_id}"
    except Exception as e:
        return str(e)

def obtener_reporte_stock():
    return inventario.reporte_stock()

def obtener_reporte_productos_bajo_stock():
    return inventario.reporte_productos_bajo_stock()

with gr.Blocks() as app:
    gr.Markdown("## Sistema de Gestión de Inventario")
    
    with gr.Tab("Agregar Producto"):
        with gr.Row():
            nombre = gr.Textbox(label="Nombre")
            descripcion = gr.Textbox(label="Descripción")
            categoria = gr.Textbox(label="Categoría")
            stock_inicial = gr.Number(label="Stock Inicial", precision=0)
            unidad = gr.Textbox(label="Unidad")
            stock_minimo = gr.Number(label="Stock Mínimo", precision=0)
            agregar_btn = gr.Button("Agregar Producto")
        agregar_output = gr.Textbox(label="Resultado")
        agregar_btn.click(agregar_producto, inputs=[nombre, descripcion, categoria, stock_inicial, unidad, stock_minimo], outputs=agregar_output)
    
    with gr.Tab("Listar Productos"):
        with gr.Row():
            filtro_nombre = gr.Textbox(label="Filtrar por Nombre")
            filtro_categoria = gr.Textbox(label="Filtrar por Categoría")
            listar_btn = gr.Button("Listar Productos")
        productos_output = gr.Dataframe()
        listar_btn.click(listar_productos, inputs=[filtro_nombre, filtro_categoria], outputs=productos_output)

    with gr.Tab("Registrar Movimiento"):
        with gr.Row():
            producto_id = gr.Number(label="ID del Producto", precision=0)
            cantidad = gr.Number(label="Cantidad", precision=0)
            tipo = gr.Radio(["ingreso", "egreso"], label="Tipo")
            motivo = gr.Textbox(label="Motivo")
            usuario = gr.Textbox(label="Usuario")
            registrar_btn = gr.Button("Registrar Movimiento")
        movimiento_output = gr.Textbox(label="Resultado")
        registrar_btn.click(registrar_movimiento, inputs=[producto_id, cantidad, tipo, motivo, usuario], outputs=movimiento_output)

    with gr.Tab("Reportes"):
        with gr.Row():
            stock_btn = gr.Button("Reporte de Stock")
            productos_bajo_stock_btn = gr.Button("Productos Bajo Stock")
        stock_output = gr.Dataframe()
        productos_bajo_stock_output = gr.Dataframe()
        stock_btn.click(obtener_reporte_stock, outputs=stock_output)
        productos_bajo_stock_btn.click(obtener_reporte_productos_bajo_stock, outputs=productos_bajo_stock_output)

app.launch()