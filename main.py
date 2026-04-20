# main.py
import flet as ft
from modulos.logn.login import VistaLogin

def pagina_principal(pagina: ft.Page, nombre: str, rol: str):
    pagina.controls.clear()
    pagina.title = f"Panel Principal - {nombre} ({rol})"
    pagina.bgcolor = "#e9ecef"
    pagina.add(
        ft.Column(
            [
                ft.Text(f"Bienvenido {nombre}", size=30, weight="bold"),
                ft.Container(height=30),
                ft.ElevatedButton(
                    "Cerrar Sesión",
                    on_click=lambda e: reiniciar_login(pagina),
                    bgcolor="red",
                    color="white",
                ),
            ],
            horizontal_alignment="center",
        )
    )
    pagina.update()

def reiniciar_login(pagina: ft.Page):
    pagina.controls.clear()
    VistaLogin(pagina, lambda u, r: pagina_principal(pagina, u, r))

def main(pagina: ft.Page):
    VistaLogin(pagina, lambda u, r: pagina_principal(pagina, u, r))

if __name__ == "__main__":
    ft.run(main)