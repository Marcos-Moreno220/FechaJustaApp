import sqlite3
from datetime import datetime

# Configuración
DB_NAME = "fechajusta.db"
LISTA_BOCAS = ["Vea Centro", "Carrefour", "Chino", "Deposito"]

def inicializar_sistema():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boca TEXT,
            nombre TEXT,
            categoria TEXT,
            cantidad INTEGER,
            vencimiento TEXT,
            precio REAL,
            estado TEXT
        )
    """)
    conn.commit()
    conn.close()

def guardar_producto(boca, nombre, cat, cant, venc, precio):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO productos (boca, nombre, categoria, cantidad, vencimiento, precio, estado)
        VALUES (?, ?, ?, ?, ?, ?, 'Pendiente')
    """, (boca, nombre, cat, cant, venc, precio))
    conn.commit()
    conn.close()
    print(f"💾 Guardado: {nombre}")

def obtener_todos_pendientes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, boca, nombre, vencimiento, estado FROM productos ORDER BY vencimiento ASC")
    datos = cursor.fetchall()
    conn.close()
    return datos

# --- NUEVA FUNCIÓN: BUSCADOR ---
def buscar_productos(texto):
    """Busca productos cuyo nombre contenga el texto (filtro)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # El símbolo % sirve para buscar "algo que contenga este texto"
    parametro = f"%{texto}%" 
    cursor.execute("SELECT id, boca, nombre, vencimiento, estado FROM productos WHERE nombre LIKE ? ORDER BY vencimiento ASC", (parametro,))
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_estadisticas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM productos")
    total_items = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(precio * cantidad) FROM productos")
    resultado_dinero = cursor.fetchone()[0]
    total_dinero = resultado_dinero if resultado_dinero else 0
    conn.close()
    return total_items, total_dinero

def eliminar_producto_db(id_prod):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (id_prod,))
    conn.commit()
    conn.close()
    print(f"🗑️ Producto {id_prod} eliminado.")