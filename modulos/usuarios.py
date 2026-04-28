# modulos/usuarios.py
import flet as ft
from datetime import datetime
from componentes.menu_lateral import MenuLateral
from db import insertar_usuario

class VistaUsuarios:
    def __init__(self, page: ft.Page, nombre_usuario: str, rol: str, usuario_id: int, turno_id: int, sucursal_id: int):
        self.page = page
        self.nombre_usuario = nombre_usuario
        self.rol = rol
        self.usuario_id = usuario_id
        self.turno_id = turno_id
        self.sucursal_id = sucursal_id
        self.usuarios_lista = []

        self.page.title = "Módulo de Usuarios"
        self.page.bgcolor = "#ffffff"
        self.page.padding = 0
        self.page.spacing = 0
        self.page.vertical_alignment = ft.MainAxisAlignment.START

        # Inicializar menú lateral
        self.menu_lateral = MenuLateral(self.page)

        self.build()

    # --------------------------------------------------------------
    # Construcción de la interfaz
    # --------------------------------------------------------------
    def build(self):
        # Construir top bar con menú
        top_bar = self.menu_lateral.construir_top_bar(
            "GESTIÓN DE USUARIOS",
            self.nombre_usuario,
            self.rol
        )
        self.top_bar = top_bar

        # Construir menú overlay
        boton_ventas = self.menu_lateral.crear_boton_menu(
            "Ventas", ft.icons.SHOPPING_CART, on_click=self.ir_a_ventas
        )
        menu_overlay = self.menu_lateral.construir_menu_overlay([boton_ventas])
        self.menu_overlay = menu_overlay

        # Título de la sección de formulario
        titulo_formulario = ft.Text(
            "Agregar Nuevo Usuario",
            size=20,
            weight="bold",
            color="#004aad",
        )

        # Campos del formulario
        self.campo_usuario = ft.TextField(
            label="Nombre de usuario",
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color="white",
            color="black",
            width=300,
        )
        
        self.campo_nombre_completo = ft.TextField(
            label="Nombre completo",
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color="white",
            color="black",
            width=300,
        )
        
        self.campo_email = ft.TextField(
            label="Correo electrónico",
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color="white",
            color="black",
            width=300,
        )
        
        self.campo_contrasena = ft.TextField(
            label="Contraseña",
            password=True,
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color="white",
            color="black",
            width=300,
        )

        # Botón para agregar usuario
        boton_agregar = ft.ElevatedButton(
            "Agregar Usuario",
            on_click=self.agregar_usuario,
            bgcolor="#4CAF50",
            color="white",
            width=300,
        )

        # Formulario
        formulario = ft.Container(
            content=ft.Column(
                controls=[
                    titulo_formulario,
                    ft.Container(height=10),
                    self.campo_usuario,
                    ft.Container(height=10),
                    self.campo_nombre_completo,
                    ft.Container(height=10),
                    self.campo_email,
                    ft.Container(height=10),
                    self.campo_contrasena,
                    ft.Container(height=20),
                    boton_agregar,
                ],
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#f5f5f5",
            padding=20,
            border_radius=10,
            margin=ft.margin.only(top=20, left=20, right=20),
        )

        # Tabla de usuarios
        self.tabla_usuarios = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Usuario", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Nombre Completo", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Email", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Acciones", text_align=ft.TextAlign.CENTER)),
            ],
            rows=[],
            width=900,
        )

        # Título de usuarios
        titulo_usuarios = ft.Text(
            "Usuarios Registrados",
            size=20,
            weight="bold",
            color="#004aad",
            margin=ft.margin.only(top=30, left=20),
        )

        # Panel para la tabla
        panel_tabla = ft.Container(
            content=self.tabla_usuarios,
            bgcolor="#f5f5f5",
            border_radius=10,
            padding=15,
            margin=ft.margin.only(top=10, left=20, right=20, bottom=20),
        )

        contenido_principal = ft.Column(
            controls=[
                formulario,
                titulo_usuarios,
                panel_tabla,
            ],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Layout principal
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
    # Gestión de usuarios
    # --------------------------------------------------------------
    def agregar_usuario(self, e):
        """Agrega un nuevo usuario a la tabla y a la base de datos"""
        usuario = self.campo_usuario.value.strip()
        nombre_completo = self.campo_nombre_completo.value.strip()
        email = self.campo_email.value.strip()
        contrasena = self.campo_contrasena.value.strip()

        # Validaciones
        if not usuario or not nombre_completo or not email or not contrasena:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Complete todos los campos"), bgcolor="red")
            )
            return

        if len(contrasena) < 6:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("La contraseña debe tener al menos 6 caracteres"), bgcolor="red")
            )
            return

        # Validar email básico
        if "@" not in email or "." not in email:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Ingrese un email válido"), bgcolor="red")
            )
            return

        # Crear datos del usuario
        nuevo_usuario = {
            "usuario": usuario,
            "nombre_completo": nombre_completo,
            "email": email,
            "contraseña": contrasena,
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Intentar enviar a base de datos
        try:
            resultado = insertar_usuario(usuario, email, contrasena, nombre_completo)
            if resultado:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"Usuario '{usuario}' agregado exitosamente"), bgcolor="green")
                )
                print(f"✓ Usuario insertado: {resultado}")
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Error al guardar en BD"), bgcolor="red")
                )
                print("Error: No se pudo insertar el usuario")
                return
        except Exception as ex:
            print(f"Error al guardar en BD: {str(ex)}")
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="red")
            )
            return

        # Agregar a la lista local
        self.usuarios_lista.append(nuevo_usuario)
        self.actualizar_tabla()

        # Limpiar campos
        self.campo_usuario.value = ""
        self.campo_nombre_completo.value = ""
        self.campo_email.value = ""
        self.campo_contrasena.value = ""
        self.page.update()

    def actualizar_tabla(self):
        """Actualiza la tabla de usuarios"""
        self.tabla_usuarios.rows.clear()
        
        for idx, usuario in enumerate(self.usuarios_lista):
            boton_eliminar = ft.TextButton(
                content=ft.Text("🗑️", size=16),
                on_click=lambda e, i=idx: self.eliminar_usuario(i),
                style=ft.ButtonStyle(padding=0),
            )
            
            self.tabla_usuarios.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(usuario["usuario"])),
                        ft.DataCell(ft.Text(usuario["nombre_completo"])),
                        ft.DataCell(ft.Text(usuario["email"])),
                        ft.DataCell(boton_eliminar),
                    ]
                )
            )
        
        self.page.update()

    def eliminar_usuario(self, indice):
        """Elimina un usuario de la tabla"""
        usuario_eliminado = self.usuarios_lista[indice]
        del self.usuarios_lista[indice]
        
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(f"Usuario '{usuario_eliminado['usuario']}' eliminado"), bgcolor="orange")
        )
        
        self.actualizar_tabla()

    # --------------------------------------------------------------
    # Navegación
    # --------------------------------------------------------------
    def ir_a_ventas(self, e):
        from modulos.ventas import VistaVentas
        self.page.controls.clear()
        VistaVentas(self.page, self.nombre_usuario, self.rol, self.usuario_id, self.turno_id, self.sucursal_id)
        self.page.update()
