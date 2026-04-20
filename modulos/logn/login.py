# modulos/logn/login.py
import flet as ft

class VistaLogin:
    def __init__(self, pagina: ft.Page, al_iniciar_sesion):
        self.pagina = pagina
        self.al_iniciar_sesion = al_iniciar_sesion
        self.pagina.title = "Inicio de Sesión - Punto de Venta"
        self.pagina.bgcolor = "#004aad"
        self.pagina.horizontal_alignment = "center"
        self.pagina.vertical_alignment = "center"
        self.pagina.window.width = 800
        self.pagina.window.height = 600
        self.pagina.window.resizable = False

        # --- Grupo Usuario ---
        self.etiqueta_usuario = ft.Text("Usuario", size=14, weight="bold", color="black")
        self.campo_usuario = ft.TextField(
            width=300,
            bgcolor="white",
            border_radius=10,
            height=45,
            text_size=16,
        )
        grupo_usuario = ft.Container(
            width=300,  # mismo ancho que el campo
            content=ft.Column(
                [
                    self.etiqueta_usuario,
                    ft.Container(height=5),
                    self.campo_usuario,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.START,  # alinea a la izquierda
                spacing=0,
            ),
        )

        # --- Grupo Contraseña ---
        self.etiqueta_contrasena = ft.Text("Contraseña", size=14, weight="bold", color="black")
        self.campo_contrasena = ft.TextField(
            password=True,
            can_reveal_password=False,
            width=300,
            bgcolor="white",
            border_radius=10,
            height=45,
            text_size=16,
        )
        grupo_contrasena = ft.Container(
            width=300,
            content=ft.Column(
                [
                    self.etiqueta_contrasena,
                    ft.Container(height=5),
                    self.campo_contrasena,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.START,
                spacing=0,
            ),
        )

        # Título con rectángulo gris (centrado)
        titulo = ft.Container(
            content=ft.Text("INICIO DE SESIÓN", size=24, weight="bold", color="black"),
            bgcolor="#DADADA",
            border_radius=51,
            padding=ft.padding.symmetric(horizontal=40, vertical=15),
            margin=ft.margin.only(top=20),
        )

        # Panel blanco principal
        panel = ft.Container(
            width=500,
            height=580,
            bgcolor="white",
            border_radius=51,
            content=ft.Column(
                [
                    ft.Container(height=30),
                    titulo,
                    ft.Container(height=40),
                    grupo_usuario,     
                    ft.Container(height=25),
                    grupo_contrasena,
                    ft.Container(height=50),
                    ft.ElevatedButton(
                        "INGRESAR",
                        width=200,
                        height=50,
                        style=ft.ButtonStyle(
                            bgcolor="#4CAF50",
                            color="white",
                            shape=ft.RoundedRectangleBorder(radius=51),
                        ),
                        on_click=self.validar_credenciales,
                    ),
                    ft.Container(height=20),
                ],
                horizontal_alignment="center",  # centra los contenedores 
                spacing=0,
            ),
        )

        self.pagina.add(panel)
        self.pagina.update()

    def mostrar_error(self, mensaje):
        self.pagina.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(mensaje, color="white"),
                bgcolor="red",
                action="Cerrar",
                duration=3000,
            )
        )

    def validar_credenciales(self, e):
        usuario = self.campo_usuario.value.strip()
        contrasena = self.campo_contrasena.value.strip()
        if usuario == "admin" and contrasena == "admin123":
            self.al_iniciar_sesion(usuario, "admin")
        elif usuario == "empleado" and contrasena == "empleado123":
            self.al_iniciar_sesion(usuario, "empleado")
        else:
            self.mostrar_error("❌ Usuario o contraseña incorrectos")