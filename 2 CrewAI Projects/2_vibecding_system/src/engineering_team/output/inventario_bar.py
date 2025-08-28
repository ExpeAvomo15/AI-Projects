import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

class GestionInventario:
    def __init__(self, db_path: str = "inventario_bar.db"):
        """
        Initialize the inventory management system.
        Creates necessary tables if database is empty.
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._crear_tablas()

    # ---------- PRODUCT MANAGEMENT ----------
    def add_producto(self, nombre: str, descripcion: str, categoria: str, stock_inicial: int, unidad: str, stock_minimo: int) -> int:
        """
        Add a new product to inventory.
        :returns: Product ID.
        """
        if not nombre or stock_inicial < 0 or stock_minimo < 0:
            raise ValueError("Nombre requerido y stock/stock_minimo >= 0")
        now = datetime.now().isoformat(sep=' ', timespec='seconds')
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO productos (nombre, descripcion, categoria, unidad, stock_minimo, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nombre, descripcion, categoria, unidad, stock_minimo, now))
            producto_id = cur.lastrowid
            if stock_inicial > 0:
                cur.execute("""
                    INSERT INTO movimientos (producto_id, tipo, cantidad, motivo, usuario, fecha)
                    VALUES (?, 'ingreso', ?, ?, ?, ?)
                """, (producto_id, stock_inicial, "Stock inicial", "system", now))
            conn.commit()
            return producto_id

    def editar_producto(self, producto_id: int, **kwargs) -> bool:
        """
        Edit product details. kwargs may include nombre, descripcion, categoria, unidad, stock_minimo.
        :returns: True on success, False if product not found.
        """
        valid_fields = {'nombre', 'descripcion', 'categoria', 'unidad', 'stock_minimo'}
        fields = []
        values = []
        for k, v in kwargs.items():
            if k in valid_fields:
                fields.append(f"{k}=?")
                values.append(v)
        if not fields:
            raise ValueError("No hay campos válidos para actualizar")
        values.append(producto_id)
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM productos WHERE id=?", (producto_id,))
            if not cur.fetchone():
                return False
            sql = f"UPDATE productos SET {', '.join(fields)} WHERE id=?"
            cur.execute(sql, values)
            conn.commit()
            return cur.rowcount > 0

    def eliminar_producto(self, producto_id: int) -> bool:
        """
        Remove a product. Refuses if movements exist.
        :returns: True on success, False on error.
        """
        with self._conectar() as conn:
            cur = conn.cursor()
            # Check if product exists
            cur.execute("SELECT id FROM productos WHERE id=?", (producto_id,))
            if not cur.fetchone():
                return False
            # Refuse deletion if movements exist
            cur.execute("SELECT COUNT(*) FROM movimientos WHERE producto_id=?", (producto_id,))
            if cur.fetchone()[0] > 0:
                raise RuntimeError("No se puede eliminar: existen movimientos para este producto.")
            cur.execute("DELETE FROM productos WHERE id=?", (producto_id,))
            conn.commit()
            return True

    def obtener_producto(self, producto_id: int) -> Optional[Dict]:
        """
        Get product details.
        :returns: Dict with product info or None.
        """
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, nombre, descripcion, categoria, unidad, stock_minimo, fecha_creacion
                FROM productos
                WHERE id=?
            """, (producto_id,))
            row = cur.fetchone()
            if row:
                return dict(zip(['id','nombre','descripcion','categoria','unidad','stock_minimo','fecha_creacion'], row))
            return None

    def listar_productos(self, filtro: dict = None) -> List[Dict]:
        """
        List all products, optionally filtered by name/category/etc.
        :param filtro: Dict with filter keys (nombre, categoria).
        :returns: List of product dicts.
        """
        filtro = filtro or {}
        filtros = []
        params = []
        if 'nombre' in filtro:
            filtros.append("nombre LIKE ?")
            params.append(f"%{filtro['nombre']}%")
        if 'categoria' in filtro:
            filtros.append("categoria=?")
            params.append(filtro['categoria'])
        sql = "SELECT id, nombre, descripcion, categoria, unidad, stock_minimo, fecha_creacion FROM productos"
        if filtros:
            sql += " WHERE " + " AND ".join(filtros)
        sql += " ORDER BY nombre ASC"
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            campos = ['id','nombre','descripcion','categoria','unidad','stock_minimo','fecha_creacion']
            return [dict(zip(campos, r)) for r in rows]

    # ---------- STOCK MOVEMENTS ----------
    def registrar_movimiento(self, producto_id: int, cantidad: int, tipo: str, motivo: str, usuario: str) -> int:
        """
        Register an ingreso (stock in) or egreso (stock out) for a product.
        :param tipo: 'ingreso' or 'egreso'
        :returns: Movement ID
        """
        tipo = tipo.lower()
        if tipo not in ("ingreso", "egreso"):
            raise ValueError("Tipo debe ser 'ingreso' o 'egreso'")
        if cantidad <= 0:
            raise ValueError("Cantidad debe ser mayor que cero")
        producto = self.obtener_producto(producto_id)
        if not producto:
            raise ValueError("Producto no existe")
        now = datetime.now().isoformat(sep=' ', timespec='seconds')
        with self._conectar() as conn:
            cur = conn.cursor()
            # For egreso, ensure enough stock
            stock_actual = self._stock_actual(conn, producto_id)
            if tipo == "egreso" and cantidad > stock_actual:
                raise RuntimeError("Stock insuficiente para este egreso")
            cur.execute("""
                INSERT INTO movimientos (producto_id, tipo, cantidad, motivo, usuario, fecha)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (producto_id, tipo, cantidad, motivo, usuario, now))
            conn.commit()
            return cur.lastrowid

    def obtener_movimientos(self, producto_id: int = None, tipo: str = None, fecha_inicio: str = None, fecha_fin: str = None) -> List[Dict]:
        """
        List movements for a product or in a date range.
        :returns: List of movement dicts.
        """
        filtros = []
        params = []
        if producto_id is not None:
            filtros.append("producto_id=?")
            params.append(producto_id)
        if tipo is not None:
            filtros.append("tipo=?")
            params.append(tipo.lower())
        if fecha_inicio is not None:
            filtros.append("fecha>=?")
            params.append(f"{fecha_inicio} 00:00:00")
        if fecha_fin is not None:
            filtros.append("fecha<=?")
            params.append(f"{fecha_fin} 23:59:59")
        sql = """
            SELECT id, producto_id, tipo, cantidad, motivo, usuario, fecha
            FROM movimientos
        """
        if filtros:
            sql += " WHERE " + " AND ".join(filtros)
        sql += " ORDER BY fecha DESC"
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            campos = ['id','producto_id','tipo','cantidad','motivo','usuario','fecha']
            return [dict(zip(campos, r)) for r in rows]

    # ---------- REPORTING ----------
    def reporte_stock(self) -> List[Dict]:
        """
        Returns the complete current stock as a list of dicts with product info and quantities.
        """
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT p.id, p.nombre, p.descripcion, p.categoria, p.unidad, p.stock_minimo,
                       IFNULL(SUM(CASE WHEN m.tipo='ingreso' THEN m.cantidad ELSE 0 END), 0)
                     - IFNULL(SUM(CASE WHEN m.tipo='egreso' THEN m.cantidad ELSE 0 END), 0) as stock_actual
                FROM productos p
                LEFT JOIN movimientos m ON p.id = m.producto_id
                GROUP BY p.id, p.nombre, p.descripcion, p.categoria, p.unidad, p.stock_minimo
                ORDER BY p.nombre ASC
            """)
            rows = cur.fetchall()
            campos = ['id', 'nombre', 'descripcion', 'categoria', 'unidad', 'stock_minimo', 'stock_actual']
            return [dict(zip(campos, r)) for r in rows]

    def reporte_productos_bajo_stock(self) -> List[Dict]:
        """
        Returns list of products under minimum stock levels.
        """
        reporte = self.reporte_stock()
        bajo = [prod for prod in reporte if prod['stock_actual'] < prod['stock_minimo']]
        return bajo

    def reporte_movimientos(self, fecha_inicio: str = None, fecha_fin: str = None, tipo: str = None) -> List[Dict]:
        """
        Returns list of movements within date range and/or by type.
        """
        return self.obtener_movimientos(tipo=tipo, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

    # ---------- UTILITY / INTERNALS ----------
    def _crear_tablas(self):
        with self._conectar() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    categoria TEXT,
                    unidad TEXT,
                    stock_minimo INTEGER NOT NULL DEFAULT 0,
                    fecha_creacion TIMESTAMP NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS movimientos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL CHECK(tipo IN ('ingreso', 'egreso')),
                    cantidad INTEGER NOT NULL CHECK(cantidad > 0),
                    motivo TEXT,
                    usuario TEXT,
                    fecha TIMESTAMP NOT NULL,
                    FOREIGN KEY (producto_id) REFERENCES productos(id)
                )
            """)
            conn.commit()

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    def _stock_actual(self, conn, producto_id: int) -> int:
        # Internal: returns current stock for product
        cur = conn.cursor()
        cur.execute("""
            SELECT
                IFNULL(SUM(CASE WHEN tipo='ingreso' THEN cantidad ELSE 0 END),0) -
                IFNULL(SUM(CASE WHEN tipo='egreso' THEN cantidad ELSE 0 END),0)
            FROM movimientos
            WHERE producto_id=?
        """, (producto_id,))
        r = cur.fetchone()
        return int(r[0]) if r else 0