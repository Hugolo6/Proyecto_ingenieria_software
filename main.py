# main.py - Aplicación principal Punto de Venta
import flet as ft
from modulos.login import VistaLogin
from modulos.ventas import VistaVentas

class AplicacionPuntoVenta:
    def __init__(self, page: ft.Page):
        self.page = page
        self.usuario_actual = None
        self.mostrar_login()
    
    def mostrar_login(self):
        """Mostrar pantalla de login"""
        self.page.clean()
        vista_login = VistaLogin(self.page, self.al_iniciar_sesion)
    
    def al_iniciar_sesion(self, usuario, nombre_completo, rol, usuario_id):
        """Callback cuando el usuario inicia sesión exitosamente"""
        self.usuario_actual = {
            "usuario": usuario,
            "nombre_completo": nombre_completo,
            "rol": rol,
            "usuario_id": usuario_id
        }
        self.mostrar_ventas()
    
    def mostrar_ventas(self):
        """Mostrar pantalla de ventas"""
        self.page.clean()
        vista_ventas = VistaVentas(
            page=self.page,
            nombre_usuario=self.usuario_actual["nombre_completo"],
            rol=self.usuario_actual["rol"],
            usuario_id=self.usuario_actual["usuario_id"],
            turno_id=1,
            sucursal_id=1
        )

def main(page: ft.Page):
    app = AplicacionPuntoVenta(page)

if __name__ == "__main__":
    ft.app(target=main)