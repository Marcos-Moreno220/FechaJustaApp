import flet as ft
import backend
from datetime import datetime

def main(page: ft.Page):
    # 1. Configuración de pantalla
    page.title = "FechaJusta Mobile"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 390
    page.window_height = 800
    page.window_resizable = True
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.START

    # Iniciamos DB
    backend.inicializar_sistema()

    # 2. Lógica de Semáforo
    def obtener_color_icono(fecha_str):
        try:
            hoy = datetime.now().date()
            venc = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            dias = (venc - hoy).days
            
            if dias <= 10: return "red", "warning"
            elif dias <= 30: return "amber", "access_time"
            else: return "green", "check_circle"
        except:
            return "grey", "help"

    # ==========================================
    #   VISTA 1: FORMULARIO DE CARGA
    # ==========================================
    dd_boca = ft.Dropdown(
        label="Sucursal", 
        options=[ft.dropdown.Option(b) for b in backend.LISTA_BOCAS], 
        width=350
    )
    txt_nombre = ft.TextField(label="Producto", width=350)
    
    txt_cantidad = ft.TextField(label="Cant.", width=160, keyboard_type=ft.KeyboardType.NUMBER)
    txt_precio = ft.TextField(label="Precio $", width=160, keyboard_type=ft.KeyboardType.NUMBER)
    fila_precios = ft.Row([txt_cantidad, txt_precio], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    txt_fecha = ft.TextField(label="Vencimiento", hint_text="DD/MM/AAAA", width=350)
    lbl_resultado = ft.Text("", weight="bold", size=16)

    def guardar_click(e):
        try:
            if not dd_boca.value or not txt_nombre.value or not txt_fecha.value:
                lbl_resultado.value = "❌ Faltan datos"
                lbl_resultado.color = "red"
                page.update()
                return

            fecha_obj = datetime.strptime(txt_fecha.value, "%d/%m/%Y")
            vencimiento_db = fecha_obj.strftime("%Y-%m-%d")
            
            backend.guardar_producto(
                dd_boca.value, txt_nombre.value, "Gral", 
                int(txt_cantidad.value or 0), vencimiento_db, float(txt_precio.value or 0)
            )
            
            lbl_resultado.value = "✅ Guardado!"
            lbl_resultado.color = "green"
            
            # Limpiar
            txt_nombre.value = ""
            txt_cantidad.value = ""
            txt_precio.value = ""
            txt_fecha.value = ""
            page.update()

        except ValueError:
            lbl_resultado.value = "❌ Error en fecha"
            lbl_resultado.color = "red"
            page.update()

    btn_guardar = ft.ElevatedButton("GUARDAR", on_click=guardar_click, width=350, bgcolor="blue", color="white")

    vista_carga = ft.Column([
        ft.Text("Nueva Carga 📝", size=24, weight="bold", color="blue"),
        dd_boca, txt_nombre, fila_precios, txt_fecha, 
        ft.Divider(), btn_guardar, lbl_resultado
    ])

    # ==========================================
    #   VISTA 2: LISTADO (Solución Rígida)
    # ==========================================
    lista_items = ft.Column(spacing=10, scroll=ft.ScrollMode.ALWAYS, height=500)
    
    vista_lista = ft.Column([
        ft.Text("Vencimientos 📅", size=20, weight="bold"),
        lista_items
    ])

    def actualizar_lista():
        print("🔄 Refrescando lista...")
        lista_items.controls.clear()
        
        datos = backend.obtener_todos_pendientes()
        print(f"📦 Productos encontrados: {len(datos)}")
        
        if not datos:
            lista_items.controls.append(ft.Text("No hay datos cargados."))
        
        for p in datos:
            pid, boca, nombre, venc, estado = p
            color, icono_nom = obtener_color_icono(venc)
            fecha_bonita = datetime.strptime(venc, "%Y-%m-%d").strftime("%d/%m")

            tarjeta = ft.Container(
                content=ft.Row([
                    # Icono (sin name=)
                    ft.Icon(icono_nom, color=color, size=30),
                    
                    # Texto (Ancho fijo)
                    ft.Container(
                        content=ft.Column([
                            ft.Text(nombre, weight="bold", size=16, no_wrap=False),
                            ft.Text(f"{boca} - {fecha_bonita}", size=12, color="grey")
                        ], spacing=2),
                        width=200 
                    ), 
                    
                    # Botón BORRAR (Texto simple, sin la palabra prohibida DELETE en mayúscula)
                    ft.IconButton(icon="delete", icon_color="red", on_click=lambda e, id=pid: borrar_click(id))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                padding=10,
                bgcolor="white",
                border_radius=10,
                border=ft.border.all(1, "grey")
            )
            
            lista_items.controls.append(tarjeta)
        page.update()

    def borrar_click(id_prod):
        backend.eliminar_producto_db(id_prod)
        actualizar_lista()

    # ==========================================
    #   NAVEGACIÓN
    # ==========================================
    
    contenedor_principal = ft.Container(content=vista_carga, expand=True)

    def ir_a_carga(e):
        contenedor_principal.content = vista_carga
        page.update()

    def ir_a_lista(e):
        actualizar_lista()
        contenedor_principal.content = vista_lista
        page.update()

    botonera = ft.Row(
        controls=[
            ft.ElevatedButton("📝 Cargar", on_click=ir_a_carga, expand=True),
            ft.ElevatedButton("📋 Ver Lista", on_click=ir_a_lista, expand=True),
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    page.add(
        contenedor_principal,
        ft.Divider(),
        botonera
    )

ft.app(target=main)