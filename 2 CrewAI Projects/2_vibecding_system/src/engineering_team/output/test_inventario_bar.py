import pytest
import sqlite3
import os
from inventario_bar import GestionInventario

@pytest.fixture
def gestion_inventario():
    db_path = "test_inventario_bar.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    gestion = GestionInventario(db_path)
    yield gestion
    os.remove(db_path)

def test_add_producto(gestion_inventario):
    producto_id = gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", 100, "litros", 10)
    producto = gestion_inventario.obtener_producto(producto_id)
    assert producto is not None
    assert producto['nombre'] == "Cerveza"

def test_add_producto_invalid(gestion_inventario):
    with pytest.raises(ValueError):
        gestion_inventario.add_producto("", "Cerveza rubia", "Bebidas", 100, "litros", 10)
    with pytest.raises(ValueError):
        gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", -1, "litros", 10)
    with pytest.raises(ValueError):
        gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", 100, "litros", -1)

def test_editar_producto(gestion_inventario):
    producto_id = gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", 100, "litros", 10)
    assert gestion_inventario.editar_producto(producto_id, nombre="Cerveza Negra", categoria="Bebidas")
    producto = gestion_inventario.obtener_producto(producto_id)
    assert producto['nombre'] == "Cerveza Negra"

def test_editar_producto_invalid(gestion_inventario):
    producto_id = gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", 100, "litros", 10)
    with pytest.raises(ValueError):
        gestion_inventario.editar_producto(producto_id)

def test_eliminar_producto(gestion_inventario):
    producto_id = gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", 100, "litros", 10)
    assert gestion_inventario.eliminar_producto(producto_id) is True
    assert gestion_inventario.obtener_producto(producto_id) is None

def test_eliminar_producto_con_movimientos(gestion_inventario):
    producto_id = gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", 100, "litros", 10)
    gestion_inventario.registrar_movimiento(producto_id, 50, "ingreso", "Stock inicial", "system")
    with pytest.raises(RuntimeError):
        gestion_inventario.eliminar_producto(producto_id)

def test_listar_productos(gestion_inventario):
    gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", 100, "litros", 10)
    productos = gestion_inventario.listar_productos()
    assert len(productos) == 1
    assert productos[0]['nombre'] == "Cerveza"

def test_registrar_movimiento(gestion_inventario):
    producto_id = gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", 100, "litros", 10)
    movimiento_id = gestion_inventario.registrar_movimiento(producto_id, 20, "ingreso", "Compra", "user")
    movimiento = gestion_inventario.obtener_movimientos(producto_id)[0]
    assert movimiento['cantidad'] == 20
    assert movimiento['tipo'] == "ingreso"

def test_registrar_movimiento_stock_insuficiente(gestion_inventario):
    producto_id = gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", 100, "litros", 10)
    gestion_inventario.registrar_movimiento(producto_id, 20, "ingreso", "Compra", "user")
    with pytest.raises(RuntimeError):
        gestion_inventario.registrar_movimiento(producto_id, 200, "egreso", "Venta", "user")

def test_reporte_stock(gestion_inventario):
    gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", 100, "litros", 10)
    gestion_inventario.registrar_movimiento(1, 50, "ingreso", "Compra", "user")
    stock = gestion_inventario.reporte_stock()
    assert len(stock) > 0
    assert stock[0]['stock_actual'] >= 50

def test_reporte_productos_bajo_stock(gestion_inventario):
    gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", 100, "litros", 200)
    bajo_stock = gestion_inventario.reporte_productos_bajo_stock()
    assert len(bajo_stock) == 1
    assert bajo_stock[0]['nombre'] == "Cerveza"

def test_obtener_movimientos(gestion_inventario):
    producto_id = gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", 100, "litros", 10)
    gestion_inventario.registrar_movimiento(producto_id, 20, "ingreso", "Compra", "user")
    movimientos = gestion_inventario.obtener_movimientos(producto_id)
    assert len(movimientos) == 1
    assert movimientos[0]['cantidad'] == 20
    
def test_obtener_movimientos_filtro_fecha(gestion_inventario):
    producto_id = gestion_inventario.add_producto("Cerveza", "Cerveza rubia", "Bebidas", 100, "litros", 10)
    gestion_inventario.registrar_movimiento(producto_id, 20, "ingreso", "Compra", "user")
    movimientos = gestion_inventario.obtener_movimientos(fecha_inicio="2022-01-01", fecha_fin="2023-12-31")
    assert len(movimientos) == 1

def test_obtener_producto_no_existente(gestion_inventario):
    assert gestion_inventario.obtener_producto(999) is None