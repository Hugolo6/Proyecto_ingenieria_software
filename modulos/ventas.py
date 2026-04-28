# modulos/ventas.py
import flet as ft
from datetime import datetime
from db import obtener_productos, insertar_venta, obtener_venta_por_folio, insertar_detalle_venta, insertar_pago
from componentes.menu_lateral import MenuLateral

class VistaVentas:
    def __init__(self, page: ft.Page, nombre_usuario: str, rol: str, usuario_id: int, turno_id: int, sucursal_id: int):
        self.page = page
        self.nombre_usuario = nombre_usuario
        self.rol = rol
        self.usuario_id = usuario_id
        self.turno_id = turno_id
        self.sucursal_id = sucursal_id
        self.productos_agregados = []
        self.ventas_realizadas = []
        self.turno_activo = True
        self.efectivo_inicial = 0.0
        self.efectivo_final = 0.0
        self.folio_contador = self.cargar_folio_dia()

        # Cargar productos desde la base de datos
        try:
            productos_db = obtener_productos()
            if productos_db:
                self.productos_disponibles = {p["codigo"]: p for p in productos_db}
            else:
                self.productos_disponibles = {}
                print("Advertencia: No hay conexión a la base de datos o no hay productos disponibles")
        except Exception as e:
            self.productos_disponibles = {}
            print(f"Error cargando productos: {e}")

        self.page.title = "Módulo de Ventas"
        self.page.bgcolor = "#ffffff"
        # Quitar width y height fijos para que se ajuste a pantalla completa
        self.page.padding = 0
        self.page.spacing = 0
        self.page.vertical_alignment = ft.MainAxisAlignment.START

        # Inicializar menú lateral
        self.menu_lateral = MenuLateral(self.page)

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
    def build(self):
        # Construir top bar con menú
        top_bar = self.menu_lateral.construir_top_bar(
            "CAJA-01 | Abarrotes: El Guayabo",
            self.nombre_usuario,
            self.rol
        )
        self.top_bar = top_bar

        # Construir menú overlay
        boton_usuarios = self.menu_lateral.crear_boton_menu(
            "Usuarios", ft.icons.PEOPLE, on_click=self.ir_a_usuarios
        )
        menu_overlay = self.menu_lateral.construir_menu_overlay([boton_usuarios])
        self.menu_overlay = menu_overlay

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
                ft.DataColumn(ft.Text("Eliminar", text_align=ft.TextAlign.CENTER)),
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

        # Contenedor para el total
        panel_total = ft.Container(
            content=ft.Text("TOTAL: $0.00", size=20, color="white", weight="bold"),
            bgcolor="#004aad",
            padding=15,
            border_radius=10,
            alignment=ft.Alignment.CENTER,
        )
        self.total_text = panel_total
        # Fila de pago con solo el total
        fila_pago = ft.Row(
            controls=[
                panel_total,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
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
                precio = producto["precio_venta"]
                iva_tasa = producto["porcentaje_iva"] if producto["aplica_iva"] else 0
                subtotal = precio * cantidad
                iva = subtotal * iva_tasa
                total = subtotal + iva
                nuevo_item = {
                    "codigo": producto["codigo"],
                    "descripcion": producto["descripcion"],
                    "precio": precio,
                    "cantidad": cantidad,
                    "unidad": producto["tipo_venta"],
                    "subtotal": subtotal,
                    "iva": iva,
                    "total": total,
                    "producto_id": producto["id"],
                    "iva_tasa": iva_tasa,
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
            boton_eliminar = ft.TextButton(content=ft.Text("🗑️", size=20), on_click=lambda e, i=idx: self.eliminar_producto(i), style=ft.ButtonStyle(padding=0))
            self.tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["codigo"])),
                        ft.DataCell(ft.Text(item["descripcion"])),
                        ft.DataCell(ft.Text(f"${item['precio']:.2f}")),
                        ft.DataCell(ft.Text(f"{item['cantidad']:.2f}")),
                        ft.DataCell(ft.Text(item["unidad"])),
                        ft.DataCell(ft.Text(f"${item['iva']:.2f}")),
                        ft.DataCell(ft.Text(f"${item['subtotal']:.2f}")),
                        ft.DataCell(ft.Text(f"${item['total']:.2f}")),
                        ft.DataCell(boton_eliminar),
                    ]
                )
            )
        total = sum(item["total"] for item in self.productos_agregados)
        subtotal_general = sum(item["subtotal"] for item in self.productos_agregados)
        iva_general = sum(item["iva"] for item in self.productos_agregados)
        self.total_text.value = f"TOTAL: ${total:.2f}"
        self.page.update()

    def eliminar_producto(self, indice):
        del self.productos_agregados[indice]
        self.actualizar_tabla()

    # --------------------------------------------------------------
    # Pago, cambio y venta
    # --------------------------------------------------------------
    def realizar_venta(self, e):
        if not self.turno_activo:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Turno cerrado, no se pueden realizar ventas"), bgcolor="red"))
            return
        if not self.productos_agregados:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Agregue productos a la venta"), bgcolor="orange"))
            return
        subtotal = sum(item["subtotal"] for item in self.productos_agregados)
        iva = sum(item["iva"] for item in self.productos_agregados)
        total = sum(item["total"] for item in self.productos_agregados)
        metodo = "efectivo"  # Por ahora, solo efectivo
        pago = total
        cambio = 0
        self.efectivo_final += pago
        
        folio = f"{datetime.now().strftime('%Y%m%d')}-{self.folio_contador:04d}"
        self.folio_contador += 1
        # Intentar insertar en la base de datos
        venta_id = None
        try:
            venta_db = insertar_venta(folio, self.usuario_id, self.turno_id, self.sucursal_id, subtotal, iva, total)
            if venta_db:
                venta_id = venta_db["id"]
                # Insertar detalles
                for item in self.productos_agregados:
                    insertar_detalle_venta(venta_id, item["producto_id"], item["cantidad"], item["precio"], item["subtotal"])
                # Insertar pago
                insertar_pago(venta_id, metodo, total, None)
            else:
                print("Advertencia: No se pudo guardar en la base de datos, continuando localmente")
        except Exception as ex:
            print(f"Error al guardar en base de datos: {str(ex)}")
        venta = {
            "folio": folio,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "productos": self.productos_agregados.copy(),
            "subtotal": subtotal,
            "iva": iva,
            "total": total,
            "metodo_pago": metodo,
            "pago_recibido": pago,
            "cambio": cambio,
        }
        self.ventas_realizadas.append(venta)
        self.mostrar_ticket(venta)
        self.productos_agregados.clear()
        self.actualizar_tabla()
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
            contenido += f"\n{prod['codigo']} {prod['descripcion']} {prod['cantidad']:.2f} {prod['unidad']} x ${prod['precio']:.2f} = ${prod['total']:.2f}"
        contenido += f"\n-----------------------------------"
        contenido += f"\nSubtotal: ${venta['subtotal']:.2f}"
        contenido += f"\nIVA: ${venta['iva']:.2f}"
        contenido += f"\nTOTAL: ${venta['total']:.2f}"
        contenido += f"\nPago: ${venta['pago_recibido']:.2f}"
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
            try:
                venta_original = obtener_venta_por_folio(folio)
                if not venta_original:
                    self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Venta no encontrada"), bgcolor="red"))
                    return
                # Para mostrar productos, necesitaríamos detalles_ventas, pero por ahora, simular
                productos_simulados = [
                    {"descripcion": "Producto 1", "cantidad": 2, "precio": 10.0, "importe": 20.0},
                    {"descripcion": "Producto 2", "cantidad": 1, "precio": 15.0, "importe": 15.0},
                ]
                venta_original["productos"] = productos_simulados
                self.mostrar_seleccion_devolucion(venta_original)
                dialogo.open = False
                self.page.update()
            except Exception as ex:
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="red"))
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
            VistaVentas(self.page, nombre, rol, self.usuario_id, self.turno_id, self.sucursal_id)
        self.page.controls.clear()
        VistaLogin(self.page, reiniciar)
        self.page.update()

    def ir_a_usuarios(self, e):
        from modulos.usuarios import VistaUsuarios
        self.page.controls.clear()
        VistaUsuarios(self.page, self.nombre_usuario, self.rol, self.usuario_id, self.turno_id, self.sucursal_id)
        self.page.update()

    