import flet as ft
import backend
from datetime import datetime

def main(page: ft.Page):
    # --- 1. CONFIGURACIÓN ---
    page.title = "FechaJusta 2.0"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 390
    page.window_height = 800
    page.padding = 10
    page.scroll = "AUTO"

    # Iniciamos DB
    backend.inicializar_sistema()

    # Memoria para gestión
    ctx_gestion = {"id": None, "nombre": ""}

    # --- 2. LÓGICA VISUAL (EMOJIS) ---
    def obtener_emoji(fecha_str, estado):
        if estado == "Corregido": return "🔵"
        try:
            hoy = datetime.now().date()
            venc = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            dias = (venc - hoy).days
            if dias <= 10: return "🔴"
            elif dias <= 30: return "🟡"
            else: return "🟢"
        except: return "⚪"

    # --- 3. DASHBOARD Y EXCEL ---
    txt_total_items = ft.Text("0", size=26, weight="bold", color="blue")
    txt_total_plata = ft.Text("$0", size=26, weight="bold", color="green")

    def crear_tarjeta(titulo, widget_dato, color_borde):
        return ft.Container(
            content=ft.Column([
                ft.Text(titulo, size=12, color="grey"),
                widget_dato
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=160, height=80, bgcolor="white", border_radius=12,
            border=ft.border.all(1, color_borde), padding=10,
            shadow=ft.BoxShadow(blur_radius=5, color="black12")
        )

    fila_dashboard = ft.Row([
        crear_tarjeta("Productos Activos", txt_total_items, "blue"),
        crear_tarjeta("Dinero en Riesgo", txt_total_plata, "green")
    ], alignment=ft.MainAxisAlignment.CENTER)

    # --- FUNCIÓN DESCARGA EXCEL ---
    def descargar_excel_click(e):
        resultado = backend.exportar_a_excel()
        # Mostramos mensaje con la ruta
        color_msg = "green" if "Guardado" in resultado else "red"
        page.snack_bar = ft.SnackBar(ft.Text(resultado), bgcolor=color_msg)
        page.snack_bar.open = True
        page.update()

    # CORRECCIÓN AQUÍ: Usamos ElevatedButton con Emoji en vez de IconButton
    btn_excel = ft.ElevatedButton(
        "📥", # Emoji de bandeja de entrada/descarga
        color="white",
        bgcolor="green",
        tooltip="Descargar Excel",
        on_click=descargar_excel_click,
        width=50
    )

    # Título con el botón al lado
    encabezado_lista = ft.Row([
        ft.Text("Mis Estadísticas", size=20, weight="bold"),
        btn_excel
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # --- 4. DIÁLOGOS ---
    def cerrar_dialogos(e):
        dlg_opciones.open = False
        page.update()

    def accion_corregido(e):
        backend.cambiar_estado(ctx_gestion["id"], "Corregido")
        dlg_opciones.open = False
        actualizar_todo()
        page.snack_bar = ft.SnackBar(ft.Text("✅ Corregido"))
        page.snack_bar.open = True
        page.update()

    def accion_borrar(e):
        backend.eliminar_producto_db(ctx_gestion["id"])
        dlg_opciones.open = False
        actualizar_todo()
        page.snack_bar = ft.SnackBar(ft.Text("🗑️ Eliminado"))
        page.snack_bar.open = True
        page.update()

    dlg_opciones = ft.AlertDialog(
        title=ft.Text("Opciones"),
        content=ft.Text("Elige una acción:"),
        actions=[
            ft.ElevatedButton("✅ Corregido", on_click=accion_corregido, bgcolor="blue", color="white"),
            ft.OutlinedButton("🗑️ Borrar", on_click=accion_borrar, style=ft.ButtonStyle(color="red")),
            ft.TextButton("Cancelar", on_click=cerrar_dialogos),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    def abrir_menu_gestion(id_prod, nombre_prod):
        ctx_gestion["id"] = id_prod
        ctx_gestion["nombre"] = nombre_prod
        dlg_opciones.title.value = f"{nombre_prod}"
        dlg_opciones.open = True
        page.overlay.append(dlg_opciones)
        page.update()

    # --- 5. VISTAS ---
    # Formulario
    dd_boca = ft.Dropdown(label="Sucursal", options=[ft.dropdown.Option(b) for b in backend.LISTA_BOCAS], width=350)
    txt_nombre = ft.TextField(label="Producto", width=350)
    txt_marca = ft.TextField(label="Marca", width=350)
    txt_cantidad = ft.TextField(label="Cant.", width=160, keyboard_type=ft.KeyboardType.NUMBER)
    txt_precio = ft.TextField(label="Precio $", width=160, keyboard_type=ft.KeyboardType.NUMBER)
    fila_precios = ft.Row([txt_cantidad, txt_precio], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    txt_fecha = ft.TextField(label="Vencimiento", hint_text="DD/MM/AAAA", width=350)
    lbl_resultado = ft.Text("", weight="bold", size=16)

    def guardar_click(e):
        try:
            if not dd_boca.value or not txt_nombre.value or not txt_fecha.value:
                lbl_resultado.value = "❌ Datos incompletos"
                lbl_resultado.color = "red"
                page.update()
                return
            fecha_obj = datetime.strptime(txt_fecha.value, "%d/%m/%Y")
            venc_db = fecha_obj.strftime("%Y-%m-%d")
            backend.guardar_producto(dd_boca.value, txt_nombre.value, txt_marca.value, "Gral", int(txt_cantidad.value or 0), venc_db, float(txt_precio.value or 0))
            lbl_resultado.value = "✅ Guardado"
            lbl_resultado.color = "green"
            txt_nombre.value = ""
            txt_marca.value = ""
            txt_cantidad.value = ""
            txt_precio.value = ""
            txt_fecha.value = ""
            page.update()
            if contenedor_principal.content == vista_lista:
                txt_buscador.value = "" 
                actualizar_todo()
        except ValueError:
            lbl_resultado.value = "❌ Fecha incorrecta"
            lbl_resultado.color = "red"
            page.update()

    btn_guardar = ft.ElevatedButton("GUARDAR", on_click=guardar_click, width=350, bgcolor="blue", color="white", height=50)

    vista_carga = ft.Column([
        ft.Text("Nueva Carga", size=24, weight="bold", color="blue"),
        dd_boca, txt_marca, txt_nombre, fila_precios, txt_fecha, 
        ft.Divider(), btn_guardar, lbl_resultado
    ], scroll="AUTO")

    # Lista
    tabla_datos = ft.DataTable(
        width=360, column_spacing=10, heading_row_height=40, data_row_min_height=50,
        columns=[
            ft.DataColumn(ft.Text("Est")),
            ft.DataColumn(ft.Text("Producto")),
            ft.DataColumn(ft.Text("Vence")),
            ft.DataColumn(ft.Text("Acción")),
        ], rows=[]
    )

    def buscador_change(e): actualizar_todo()

    txt_buscador = ft.TextField(prefix_icon="search", hint_text="Buscar...", width=350, on_change=buscador_change, border_radius=20, content_padding=10)

    vista_lista = ft.Column([
        encabezado_lista, # Aquí está el título con el botón Excel
        fila_dashboard,
        ft.Divider(),
        txt_buscador,
        ft.Text("Vencimientos", size=16, weight="bold"),
        ft.Container(content=tabla_datos, padding=0)
    ], scroll="AUTO")

    def actualizar_todo():
        cant, plata = backend.obtener_estadisticas()
        txt_total_items.value = str(cant)
        txt_total_plata.value = f"${plata:,.0f}"
        tabla_datos.rows.clear()
        termino = txt_buscador.value
        datos = backend.obtener_productos(termino if termino else None)
        for p in datos:
            pid, boca, nombre, marca, venc, estado, cant, precio = p
            emoji = obtener_emoji(venc, estado)
            try: fecha_bonita = datetime.strptime(venc, "%Y-%m-%d").strftime("%d/%m/%y")
            except: fecha_bonita = venc
            marca_mostrar = marca if marca else "-"
            col_prod = ft.Column([ft.Text(marca_mostrar.upper(), weight="bold", size=12), ft.Text(nombre, size=13)], spacing=2)
            btn_gestion = ft.ElevatedButton("⚙️", color="white", bgcolor="blue", width=40, on_click=lambda e, id=pid, nom=nombre: abrir_menu_gestion(id, nom), style=ft.ButtonStyle(padding=0))
            fila = ft.DataRow(cells=[ft.DataCell(ft.Text(emoji, size=20)), ft.DataCell(col_prod), ft.DataCell(ft.Text(fecha_bonita, size=12)), ft.DataCell(btn_gestion)])
            tabla_datos.rows.append(fila)
        page.update()

    # Navegación
    contenedor_principal = ft.Container(content=vista_carga, expand=True)
    def ir_a_carga(e):
        contenedor_principal.content = vista_carga
        page.update()
    def ir_a_lista(e):
        actualizar_todo()
        contenedor_principal.content = vista_lista
        page.update()

    botonera = ft.Row(
        controls=[ft.ElevatedButton("📝 Cargar", on_click=ir_a_carga, expand=True, height=50), ft.ElevatedButton("📊 Ver Datos", on_click=ir_a_lista, expand=True, height=50)],
        alignment=ft.MainAxisAlignment.CENTER
    )
    page.add(contenedor_principal, ft.Divider(), botonera)

ft.app(target=main)