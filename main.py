# main.py
import flet as ft
from modulos.login import VistaLogin
from modulos.ventas import VistaVentas

def main(page: ft.Page):
    def al_iniciar_sesion(nombre, rol):
        page.controls.clear()
        VistaVentas(page, nombre, rol)

    VistaLogin(page, al_iniciar_sesion)

if __name__ == "__main__":
    ft.run(main)
    