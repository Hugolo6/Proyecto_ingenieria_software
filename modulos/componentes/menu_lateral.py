import flet as ft

class MenuLateral:
    def __init__(self, page: ft.Page, botones_menu=None):
        self.page = page
        self.botones_menu = botones_menu or []
        self.menu_abierto = False
        self.boton_menu = None
        self.menu_overlay = None
        self.top_bar = None
        
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
    
    def construir_top_bar(self, titulo, nombre_usuario, rol):
        """Construye la barra superior con el menú hamburguesa"""
        self.boton_menu = ft.IconButton(
            icon=ft.icons.Icons.MENU,
            icon_color="white",
            icon_size=30,
            on_click=self.toggle_menu,
        )

        top_bar = ft.Container(
            height=56,
            bgcolor="#004aad",
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            self.boton_menu,
                            ft.Text(titulo, color="white", size=18, weight="bold"),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(expand=True),  # Espacio
                    ft.Container(
                        content=ft.Text(f"USUARIO: {nombre_usuario.upper()} | ROL: {rol.upper()}", color="white", size=14),
                        margin=ft.margin.only(right=15),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        self.top_bar = top_bar
        return top_bar
    
    def construir_menu_overlay(self, botones_menu):
        """Construye el overlay del menú lateral"""
        menu_items = ft.Column(
            controls=botones_menu,
            spacing=15,
            padding=20,
        )
        
        menu_overlay = ft.Container(
            width=260,
            height=self.page.window.height,
            left=0,
            top=0,
            bgcolor="#2180ff",
            visible=False,
            content=ft.Stack(
                controls=[
                    menu_items,
                    ft.Container(
                        content=ft.Container(),
                        right=10,
                        top=10,
                    ),
                ],
                expand=True,
            )
        )
        self.menu_overlay = menu_overlay
        return menu_overlay
