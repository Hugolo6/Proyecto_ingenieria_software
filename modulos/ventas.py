# modulos/ventas.py
import flet as ft
from datetime import datetime

class VistaVentas:
    def __init__(self, page: ft.Page, nombre_usuario: str, rol: str):
        self.page = page
        self.nombre_usuario = nombre_usuario
        self.rol = rol
        self.productos_agregados = []
        self.ventas_realizadas = []
        self.turno_activo = True
        self.efectivo_inicial = 0.0
        self.efectivo_final = 0.0
        self.folio_contador = self.cargar_folio_dia()

        # Productos disponibles (simulados)


        self.page.title = "Módulo de Ventas"
        self.page.bgcolor = "#ffffff"
        # Quitar width y height fijos para que se ajuste a pantalla completa
        self.page.padding = 0
        self.page.spacing = 0
        self.page.vertical_alignment = ft.MainAxisAlignment.START

        # Widgets (se asignan después)
        self.metodo_pago = None
        self.pago_con = None
        self.cambio = None
        self.boton_cobrar = None
        
        # Control para el menú lateral
        self.menu_abierto = False

        self.build()
        self.pedir_efectivo_inicial()

    # --------------------------------------------------------------
    # Funciones de turno y corte
    # --------------------------------------------------------------
    def pedir_efectivo_inicial(self):
        def guardar_inicial(e):
            try:
                self.efectivo_inicial = float(input_inicial.value)
                self.efectivo_final = self.efectivo_inicial
                dialogo.open = False
                self.page.update()
            except:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Monto inválido"), bgcolor="red"))
        input_inicial = ft.TextField(label="Efectivo inicial en caja", value="0", width=200)
        dialogo = ft.AlertDialog(
            title=ft.Text("Apertura de turno"),
            content=input_inicial,
            actions=[ft.TextButton("Aceptar", on_click=guardar_inicial)],
        )
        self.page.dialog = dialogo
        dialogo.open = True
        self.page.update()

    def cerrar_turno(self, e):
        if not self.turno_activo:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("El turno ya está cerrado"), bgcolor="orange"))
            return
        total_ventas = sum(v["total"] for v in self.ventas_realizadas)
        formas_pago = {}
        for v in self.ventas_realizadas:
            metodo = v["metodo_pago"]
            formas_pago[metodo] = formas_pago.get(metodo, 0) + v["total"]
        diferencia_efectivo = self.efectivo_final - self.efectivo_inicial
        contenido_corte = f"""
=== CORTE DE CAJA ===
Total ventas: ${total_ventas:.2f}
Formas de pago:
""" + "\n".join([f"  {m}: ${monto:.2f}" for m, monto in formas_pago.items()]) + f"""
Efectivo inicial: ${self.efectivo_inicial:.2f}
Efectivo final: ${self.efectivo_final:.2f}
Diferencia (final - inicial): ${diferencia_efectivo:.2f}
Ventas realizadas: {len(self.ventas_realizadas)}
"""
        dialogo = ft.AlertDialog(
            title=ft.Text("Corte de caja"),
            content=ft.Text(contenido_corte, size=14),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: setattr(dialogo, 'open', False) or self.page.update())],
        )
        self.page.dialog = dialogo
        dialogo.open = True
        self.page.update()
        self.turno_activo = False
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Turno cerrado. Ya no se pueden hacer ventas."), bgcolor="red"))

    # --------------------------------------------------------------
    # Folio único por día
    # --------------------------------------------------------------
    def cargar_folio_dia(self):
        hoy = datetime.now().strftime("%Y%m%d")
        if not hasattr(VistaVentas, 'ultimo_dia') or VistaVentas.ultimo_dia != hoy:
            VistaVentas.ultimo_dia = hoy
            VistaVentas.folio_secuencia = 1
        else:
            VistaVentas.folio_secuencia += 1
        return VistaVentas.folio_secuencia

    # --------------------------------------------------------------
    # Construcción de la interfaz
    # --------------------------------------------------------------
    def toggle_menu(self, e):
        """Abre o cierra el menú overlay"""
        self.menu_abierto = not self.menu_abierto
        if self.menu_abierto:
            # Mover botón a la esquina superior derecha del overlay
            self.top_bar.content.controls[0].controls.remove(self.boton_menu)
            self.menu_overlay.content.controls[1].content = self.boton_menu
            self.menu_overlay.visible = True
        else:
            # Mover botón de vuelta al top_bar
            self.menu_overlay.content.controls[1].content = ft.Container()
            self.top_bar.content.controls[0].controls.insert(0, self.boton_menu)
            self.menu_overlay.visible = False
        self.page.update()
    
    def crear_boton_menu(self, texto, icono, on_click=None):
        """Crea un botón estilo menú con contenedor pill-shaped"""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon=icono, color="#2180ff", size=20),
                    ft.Text(texto, color="#2180ff", size=14, weight="w500"),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=12,
            bgcolor="white",
            border_radius=50,
            border=ft.border.all(1, "#2180ff"),
            on_click=on_click,
        )

    # --------------------------------------------------------------
    # Construcción de la interfaz
    # --------------------------------------------------------------
    def build(self):
        # Botón menú hamburguesa
        self.boton_menu = ft.IconButton(
            icon=ft.icons.Icons.MENU,
            icon_color="white",
            icon_size=30,
            on_click=self.toggle_menu,
        )

        # Top bar
        top_bar = ft.Container(
            height=56,
            bgcolor="#004aad",
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            self.boton_menu,
                            ft.Text("CAJA-01 | Abarrotes: El Guayabo", color="white", size=18, weight="bold"),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(expand=True),  # Espacio
                    ft.Container(
                        content=ft.Text(f"USUARIO: {self.nombre_usuario.upper()} | ROL: {self.rol.upper()}", color="white", size=14),
                        margin=ft.margin.only(right=15),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        self.top_bar = top_bar

        # Menú overlay
        self.menu_overlay = ft.Container(
            width=260,
            height=self.page.window.height,
            left=0,
            top=0,
            bgcolor="#2180ff",
            visible=False,
            content=ft.Stack(
                controls=[
                    ft.Container(),  # Espacio vacío para el panel
                    ft.Container(
                        content=ft.Container(),  # Placeholder para el botón
                        right=10,
                        top=10,
                    ),
                ],
                expand=True,
            )
        )

        # Barra de búsqueda
        self.campo_busqueda = ft.TextField(
            hint_text="Buscar producto por código o descripción",
            border=ft.InputBorder.OUTLINE,
            border_radius=50,
            filled=True,
            fill_color="white",
            color="black",
            expand=True,
            on_submit=self.buscar_producto,
        )
        boton_buscar = ft.ElevatedButton(
            "Buscar",
            icon="search",
            style=ft.ButtonStyle(bgcolor="#4CAF50", color="white", shape=ft.RoundedRectangleBorder(radius=50)),
            on_click=self.buscar_producto_click,
        )
        contenedor_busqueda = ft.Container(
            content=ft.Row([self.campo_busqueda, boton_buscar], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            width=self.page.window.width * 0.661,
            bgcolor="#dadada",
            border_radius=50,
            padding=5,
            margin=ft.margin.only(top=20),
        )

        # Tickets rápidos
        tickets = ft.Row(
            controls=[ft.ElevatedButton(f"Ticket {i}", on_click=lambda e, num=i: self.cambiar_ticket(num)) for i in range(1, 6)],
            spacing=10,
        )

        # Tabla de productos
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código", text_align=ft.TextAlign.CENTER), numeric=True),
                ft.DataColumn(ft.Text("Descripción", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Precio Unit.", text_align=ft.TextAlign.CENTER), numeric=True),
                ft.DataColumn(ft.Text("Cant.", text_align=ft.TextAlign.CENTER), numeric=True),
                ft.DataColumn(ft.Text("Unidad", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("IVA", text_align=ft.TextAlign.CENTER), numeric=True),
                ft.DataColumn(ft.Text("Subtotal", text_align=ft.TextAlign.CENTER), numeric=True),
                ft.DataColumn(ft.Text("Total", text_align=ft.TextAlign.CENTER), numeric=True),
            ],
            rows=[],
            width=1300,
            column_spacing=50,
            height=60,  # Aumentado para que los textos se vean mejor
        )

        # Panel para la tabla
        panel_tabla = ft.Container(
            content=self.tabla,
            bgcolor="#004aad",
            border_radius=20,  # Esquinas medio círculos
            padding=15,
            width=1330,  # Ancho fijo
        )

        # Widgets de pago (creación sin on_change en el constructor)
        self.metodo_pago = ft.Dropdown(
            label="Método de pago",
            width=200,
            options=[
                ft.dropdown.Option("efectivo", "Efectivo"),
                ft.dropdown.Option("tarjeta", "Tarjeta"),
                ft.dropdown.Option("paypal", "PayPal"),
                ft.dropdown.Option("transferencia", "Transferencia"),
            ],
            value="efectivo",
        )
        # Asignar evento on_change después de crear
        self.metodo_pago.on_change = self.on_metodo_pago_change

        self.pago_con = ft.TextField(label="Pago con", width=200, value="0", bgcolor="white", color="black")
        self.pago_con.on_change = self.calcular_cambio
        
        # Contenedor para el cambio
        panel_cambio = ft.Container(
            content=ft.Text("Cambio: $0.00", size=16, color="white"),
            bgcolor="#004aad",
            padding=10,
            border_radius=10,
            alignment=ft.Alignment.CENTER,
        )
        self.cambio = panel_cambio
        self.boton_cobrar = ft.ElevatedButton(
            "Cobrar",
            on_click=self.realizar_venta,
            bgcolor="#4CAF50",
            color="white",
            width=100,
        )

        # Contenedor para el total
        panel_total = ft.Container(
            content=ft.Text("TOTAL: $0.00", size=20, color="white", weight="bold"),
            bgcolor="#004aad",
            padding=15,
            border_radius=10,
            alignment=ft.Alignment.CENTER,
        )
        self.total_text = panel_total
        # Fila de pago con total a izquierda y cobrar a derecha
        fila_pago = ft.Row(
            controls=[
                panel_total,
                ft.Container(expand=True),  # Espacio
                self.metodo_pago,
                ft.Container(width=10),
                self.pago_con,
                ft.Container(width=10),
                panel_cambio,
                ft.Container(width=10),
                self.boton_cobrar,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            margin=ft.margin.only(bottom=15, left=15, right=15),
        )

        # Botón devolución
        boton_devolucion = ft.ElevatedButton("Devolución", icon="undo", on_click=self.abrir_devolucion, bgcolor="#FFA500", color="white")
        fila_botones = ft.Row([boton_devolucion], alignment=ft.MainAxisAlignment.END)

        contenido_principal = ft.Column(
            controls=[
                contenedor_busqueda,
                ft.Container(height=5),
                panel_tabla,
                ft.Container(expand=True),  # Espacio flexible
                fila_botones,
                ft.Container(height=5),
                fila_pago,
            ],
            horizontal_alignment="center",
            spacing=0,
            expand=True,
        )
        
        # Layout principal con top_bar, contenido y overlay de menú
        stack = ft.Stack(
            controls=[
                ft.Column([self.top_bar, contenido_principal], expand=True),
                self.menu_overlay,
            ],
            expand=True,
        )
        
        self.page.add(stack)
        self.page.update()

    # --------------------------------------------------------------
    # Búsqueda y agregado de productos
    # --------------------------------------------------------------
    def buscar_producto_click(self, e):
        self.buscar_producto(e)

    def buscar_producto(self, e):
        texto = self.campo_busqueda.value.lower()
        resultados = [p for p in self.productos_disponibles.values() if texto in p["codigo"] or texto in p["descripcion"].lower()]
        if resultados:
            self.mostrar_dialogo_productos(resultados)
        else:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Producto no encontrado"), bgcolor="orange"))

    def mostrar_dialogo_productos(self, productos):
        items = []
        for p in productos:
            items.append(
                ft.ListTile(
                    title=ft.Text(f"{p['codigo']} - {p['descripcion']}"),
                    subtitle=ft.Text(f"${p['precio']:.2f} / {p['unidad']}"),
                    on_click=lambda e, prod=p: self.agregar_producto(prod),
                )
            )
        dialogo = ft.AlertDialog(
            title=ft.Text("Seleccione producto"),
            content=ft.Column(items, scroll=ft.ScrollMode.AUTO, height=300),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: self.cerrar_dialogo(dialogo))],
        )
        self.page.dialog = dialogo
        dialogo.open = True
        self.page.update()

    def cerrar_dialogo(self, dialogo):
        dialogo.open = False
        self.page.dialog = None
        self.page.update()

    def agregar_producto(self, producto):
        def confirmar(e):
            try:
                cantidad = float(input_cantidad.value)
                if cantidad <= 0:
                    raise ValueError
                importe = producto["precio"] * cantidad
                nuevo_item = {
                    "codigo": producto["codigo"],
                    "descripcion": producto["descripcion"],
                    "precio": producto["precio"],
                    "cantidad": cantidad,
                    "unidad": producto["unidad"],
                    "importe": importe,
                    "iva_tasa": producto["iva"],
                }
                self.productos_agregados.append(nuevo_item)
                self.actualizar_tabla()
                dialogo.open = False
                self.page.update()
            except:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Cantidad inválida"), bgcolor="red"))
        input_cantidad = ft.TextField(label="Cantidad (unidades o kg)", value="1", width=200)
        dialogo = ft.AlertDialog(
            title=ft.Text(f"Agregar {producto['descripcion']}"),
            content=input_cantidad,
            actions=[ft.TextButton("Agregar", on_click=confirmar), ft.TextButton("Cancelar", on_click=lambda e: setattr(dialogo, 'open', False) or self.page.update())],
        )
        self.page.dialog = dialogo
        dialogo.open = True
        self.page.update()

    def actualizar_tabla(self):
        self.tabla.rows.clear()
        for idx, item in enumerate(self.productos_agregados):
            subtotal = item["importe"]
            boton_eliminar = ft.TextButton(content=ft.Text("🗑️", size=20), on_click=lambda e, i=idx: self.eliminar_producto(i), style=ft.ButtonStyle(padding=0))
            self.tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["codigo"])),
                        ft.DataCell(ft.Text(item["descripcion"])),
                        ft.DataCell(ft.Text(f"${item['precio']:.2f}")),
                        ft.DataCell(ft.Text(f"{item['cantidad']:.2f}")),
                        ft.DataCell(ft.Text(item["unidad"])),
                        ft.DataCell(ft.Text(f"${subtotal:.2f}")),
                        ft.DataCell(boton_eliminar),
                    ]
                )
            )
        total = sum(item["importe"] for item in self.productos_agregados)
        self.total_text.value = f"TOTAL: ${total:.2f}"
        self.calcular_cambio(None)
        self.page.update()

    def eliminar_producto(self, indice):
        del self.productos_agregados[indice]
        self.actualizar_tabla()

    # --------------------------------------------------------------
    # Pago, cambio y venta
    # --------------------------------------------------------------
    def on_metodo_pago_change(self, e):
        if self.metodo_pago.value != "efectivo":
            self.pago_con.disabled = True
            self.pago_con.value = "0"
            self.cambio.value = "Cambio: $0.00"
        else:
            self.pago_con.disabled = False
        self.page.update()
        self.calcular_cambio(None)

    def calcular_cambio(self, e):
        total = sum(item["importe"] for item in self.productos_agregados)
        if self.metodo_pago.value == "efectivo":
            try:
                pago = float(self.pago_con.value) if self.pago_con.value else 0
                cambio = max(0, pago - total)
                self.cambio.value = f"Cambio: ${cambio:.2f}"
            except:
                self.cambio.value = "Cambio: $0.00"
        else:
            self.cambio.value = "Cambio: $0.00"
        self.page.update()

    def realizar_venta(self, e):
        if not self.turno_activo:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Turno cerrado, no se pueden realizar ventas"), bgcolor="red"))
            return
        if not self.productos_agregados:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Agregue productos a la venta"), bgcolor="orange"))
            return
        total = sum(item["importe"] for item in self.productos_agregados)
        metodo = self.metodo_pago.value
        if metodo == "efectivo":
            try:
                pago = float(self.pago_con.value)
                if pago < total:
                    self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Pago insuficiente"), bgcolor="red"))
                    return
                cambio = pago - total
                self.efectivo_final += pago
            except:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Monto de pago inválido"), bgcolor="red"))
                return
        else:
            pago = total
            cambio = 0
        folio = f"{datetime.now().strftime('%Y%m%d')}-{self.folio_contador:04d}"
        self.folio_contador += 1
        venta = {
            "folio": folio,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "productos": self.productos_agregados.copy(),
            "total": total,
            "metodo_pago": metodo,
            "pago_recibido": pago if metodo == "efectivo" else None,
            "cambio": cambio,
        }
        self.ventas_realizadas.append(venta)
        self.mostrar_ticket(venta)
        self.productos_agregados.clear()
        self.actualizar_tabla()
        self.pago_con.value = "0"
        self.calcular_cambio(None)
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Venta registrada con folio {folio}"), bgcolor="green"))

    def mostrar_ticket(self, venta):
        contenido = f"""
=== TICKET DE VENTA ===
Folio: {venta['folio']}
Fecha: {venta['fecha']}
-----------------------------------
Productos:
"""
        for prod in venta["productos"]:
            subtotal = prod["importe"]
            contenido += f"\n{prod['codigo']} {prod['descripcion']} {prod['cantidad']:.2f} {prod['unidad']} x ${prod['precio']:.2f} = ${subtotal:.2f}"
        contenido += f"\n-----------------------------------"
        contenido += f"\nTOTAL: ${venta['total']:.2f}"
        if venta["metodo_pago"] == "efectivo":
            contenido += f"\nPago con: ${venta['pago_recibido']:.2f}\nCambio: ${venta['cambio']:.2f}"
        else:
            contenido += f"\nMétodo de pago: {venta['metodo_pago']}"
        dialogo = ft.AlertDialog(
            title=ft.Text("Ticket de compra"),
            content=ft.Text(contenido, size=12, font_family="monospace"),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: setattr(dialogo, 'open', False) or self.page.update())],
        )
        self.page.dialog = dialogo
        dialogo.open = True
        self.page.update()

    # --------------------------------------------------------------
    # Devoluciones
    # --------------------------------------------------------------
    def abrir_devolucion(self, e):
        input_folio = ft.TextField(label="Folio de venta original", width=300)
        def buscar_venta(e):
            folio = input_folio.value.strip()
            venta_original = None
            for v in self.ventas_realizadas:
                if v["folio"] == folio:
                    venta_original = v
                    break
            if not venta_original:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Venta no encontrada"), bgcolor="red"))
                return
            self.mostrar_seleccion_devolucion(venta_original)
            dialogo.open = False
            self.page.update()
        dialogo = ft.AlertDialog(
            title=ft.Text("Devolución de productos"),
            content=input_folio,
            actions=[ft.TextButton("Buscar", on_click=buscar_venta), ft.TextButton("Cancelar", on_click=lambda e: setattr(dialogo, 'open', False) or self.page.update())],
        )
        self.page.dialog = dialogo
        dialogo.open = True
        self.page.update()

    def mostrar_seleccion_devolucion(self, venta_original):
        items = []
        selecciones = {}
        for prod in venta_original["productos"]:
            chk = ft.Checkbox(label=f"{prod['descripcion']} - Cantidad: {prod['cantidad']:.2f} - Precio: ${prod['precio']:.2f}")
            selecciones[chk] = prod
            items.append(chk)
        def procesar_devolucion(e):
            total_reembolso = 0.0
            productos_a_devolver = []
            for chk, prod in selecciones.items():
                if chk.value:
                    total_reembolso += prod["importe"]
                    productos_a_devolver.append(prod)
            if not productos_a_devolver:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text("No seleccionó productos"), bgcolor="orange"))
                return
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Devolución procesada. Reembolso: ${total_reembolso:.2f}. Se actualizará inventario."), bgcolor="green"))
            if venta_original["metodo_pago"] == "efectivo":
                self.efectivo_final -= total_reembolso
            dialogo_devolucion.open = False
            self.page.update()
        dialogo_devolucion = ft.AlertDialog(
            title=ft.Text(f"Seleccione productos a devolver (Venta {venta_original['folio']})"),
            content=ft.Column(items, scroll=ft.ScrollMode.AUTO, height=300),
            actions=[ft.TextButton("Procesar devolución", on_click=procesar_devolucion), ft.TextButton("Cancelar", on_click=lambda e: setattr(dialogo_devolucion, 'open', False) or self.page.update())],
        )
        self.page.dialog = dialogo_devolucion
        dialogo_devolucion.open = True
        self.page.update()

    # --------------------------------------------------------------
    # Otros
    # --------------------------------------------------------------
    def cambiar_ticket(self, num):
        self.productos_agregados.clear()
        self.actualizar_tabla()
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Ticket {num} (nueva venta)"), bgcolor="green"))

    def cerrar_sesion(self, e):
        from modulos.login import VistaLogin
        def reiniciar(nombre, rol):
            self.page.controls.clear()
            VistaVentas(self.page, nombre, rol)
        self.page.controls.clear()
        VistaLogin(self.page, reiniciar)
        self.page.update()

    