import flet as ft
import backend
from datetime import datetime

def main(page: ft.Page):
    # --- 1. CONFIGURACIÓN ---
    page.title = "FechaJusta Mobile"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 390
    page.window_height = 800
    page.padding = 15
    page.scroll = "AUTO"

    # Iniciamos DB
    backend.inicializar_sistema()

    # Memoria para el ID a borrar
    borrar_ctx = {"id": None}

    # --- 2. LÓGICA VISUAL ---
    def obtener_info_visual(fecha_str):
        try:
            hoy = datetime.now().date()
            venc = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            dias = (venc - hoy).days
            if dias <= 10: return "red", "warning"
            elif dias <= 30: return "amber", "access_time"
            else: return "green", "check_circle"
        except:
            return "grey", "help"

    # --- 3. DASHBOARD ---
    txt_total_items = ft.Text("0", size=28, weight="bold", color="blue")
    txt_total_plata = ft.Text("$0", size=28, weight="bold", color="green")

    card_items = ft.Container(
        content=ft.Column([
            ft.Text("Productos", size=12, color="grey"),
            txt_total_items
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=160, height=80, bgcolor="white", border_radius=10,
        border=ft.border.all(1, "blue"), padding=10
    )

    card_plata = ft.Container(
        content=ft.Column([
            ft.Text("Dinero en Riesgo", size=12, color="grey"),
            txt_total_plata
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=160, height=80, bgcolor="white", border_radius=10,
        border=ft.border.all(1, "green"), padding=10
    )

    fila_dashboard = ft.Row([card_items, card_plata], alignment=ft.MainAxisAlignment.CENTER)

    # --- 4. DIÁLOGO DE CONFIRMACIÓN (SOLUCIÓN UNIVERSAL) ---
    def cerrar_dialogo(e):
        dlg_confirmar.open = False
        page.update()

    def confirmar_borrado(e):
        id_a_borrar = borrar_ctx["id"]
        print(f"🗑️ Ejecutando borrado de ID: {id_a_borrar}") 
        
        if id_a_borrar is not None:
            backend.eliminar_producto_db(id_a_borrar)
            # Al borrar, limpiamos el buscador para ver todo de nuevo o mantenemos la busqueda
            actualizar_todo() 
            
        dlg_confirmar.open = False
        page.update()

    dlg_confirmar = ft.AlertDialog(
        modal=True,
        title=ft.Text("¿Borrar Producto?"),
        content=ft.Text("Esta acción no se puede deshacer."),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo),
            ft.TextButton("Sí, Borrar", on_click=confirmar_borrado, style=ft.ButtonStyle(color="red")),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def abrir_confirmacion(id_prod):
        borrar_ctx["id"] = id_prod
        print(f"⚠️ Preguntando por ID: {id_prod}")
        dlg_confirmar.open = True
        page.overlay.append(dlg_confirmar)
        page.update()

    # ==========================================
    #   VISTA: FORMULARIO
    # ==========================================
    dd_boca = ft.Dropdown(label="Sucursal", options=[ft.dropdown.Option(b) for b in backend.LISTA_BOCAS], width=350)
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
            
            txt_nombre.value = ""
            txt_cantidad.value = ""
            txt_precio.value = ""
            txt_fecha.value = ""
            page.update()
            
            if contenedor_principal.content == vista_lista:
                # Si guardamos, limpiamos la búsqueda para ver el nuevo producto
                txt_buscador.value = "" 
                actualizar_todo()

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
    #   VISTA: TABLA + DASHBOARD + BUSCADOR
    # ==========================================
    tabla_datos = ft.DataTable(
        width=350,
        columns=[
            ft.DataColumn(ft.Text("Est")),
            ft.DataColumn(ft.Text("Producto")),
            ft.DataColumn(ft.Text("Vence")),
            ft.DataColumn(ft.Text("Acción")),
        ],
        rows=[]
    )

    # --- NUEVO: BARRA DE BÚSQUEDA ---
    def buscador_change(e):
        actualizar_todo() # Cada vez que escribes, filtra

    txt_buscador = ft.TextField(
        label="🔍 Buscar producto...", 
        width=350, 
        on_change=buscador_change,
        border_radius=20
    )

    vista_lista = ft.Column([
        ft.Text("Mis Estadísticas 📊", size=20, weight="bold"),
        fila_dashboard,
        ft.Divider(),
        txt_buscador, # <--- AQUÍ ESTÁ EL BUSCADOR
        ft.Text("Detalle de Vencimientos", size=16, weight="bold"),
        tabla_datos
    ])

    def actualizar_todo():
        cant, plata = backend.obtener_estadisticas()
        txt_total_items.value = str(cant)
        txt_total_plata.value = f"${plata:,.0f}"
        
        tabla_datos.rows.clear()
        
        # --- LÓGICA DE FILTRADO ---
        termino = txt_buscador.value
        if termino and len(termino) > 0:
            # Si hay algo escrito, buscamos
            datos = backend.buscar_productos(termino)
        else:
            # Si está vacío, traemos todo
            datos = backend.obtener_todos_pendientes()
        
        for p in datos:
            pid, boca, nombre, venc, estado = p
            color, icono_nom = obtener_info_visual(venc)
            fecha_bonita = datetime.strptime(venc, "%Y-%m-%d").strftime("%d/%m")

            boton_alerta = ft.ElevatedButton(
                "Borrar", color="white", bgcolor="red", height=30,
                style=ft.ButtonStyle(padding=5),
                on_click=lambda e, id=pid: abrir_confirmacion(id)
            )

            fila = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Icon(icono_nom, color=color)),
                    ft.DataCell(ft.Text(nombre, weight="bold")),
                    ft.DataCell(ft.Text(fecha_bonita)),
                    ft.DataCell(boton_alerta),
                ]
            )
            tabla_datos.rows.append(fila)
        page.update()

    # ==========================================
    #   NAVEGACIÓN
    # ==========================================
    contenedor_principal = ft.Container(content=vista_carga)

    def ir_a_carga(e):
        contenedor_principal.content = vista_carga
        page.update()

    def ir_a_lista(e):
        actualizar_todo()
        contenedor_principal.content = vista_lista
        page.update()

    botonera = ft.Row(
        controls=[
            ft.ElevatedButton("📝 Cargar", on_click=ir_a_carga, expand=True),
            ft.ElevatedButton("📊 Ver Datos", on_click=ir_a_lista, expand=True),
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    page.add(contenedor_principal, ft.Divider(), botonera)

ft.app(target=main)