import os
from supabase import create_client, Client

# Configuración de Supabase
SUPABASE_URL = "https://xcmswpameufxeczbbcia.supabase.co"
SUPABASE_KEY = "sb_publishable_VLojUcbrKIKkPMIQny15Bw_pss9PWgJ"

# Conexión a Supabase
supabase: Client = None

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Conexión a Supabase establecida correctamente")
except Exception as e:
    print(f"✗ Error al conectar con Supabase: {str(e)}")
    supabase = None

# Funciones para la tabla usuarios
def insertar_usuario(usuario, email, contraseña, nombre_completo):
    if not supabase:
        return None
    try:
        data = {
            "usuario": usuario,
            "email": email,
            "contraseña": contraseña,
            "nombre_completo": nombre_completo
        }
        response = supabase.table("usuarios").insert(data).execute()
        print(f"✓ Usuario '{usuario}' insertado correctamente")
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"✗ Error insertando usuario: {str(e)}")
        return None

def login(usuario, contraseña):
    if not supabase:
        return None
    try:
        response = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("contraseña", contraseña).execute()
        if response.data:
            print(f"✓ Login exitoso para usuario '{usuario}'")
            return response.data[0]
        else:
            print(f"✗ Usuario o contraseña incorrectos")
            return None
    except Exception as e:
        print(f"✗ Error en login: {str(e)}")
        return None

# Funciones para la tabla productos
def obtener_productos():
    if not supabase:
        return []
    try:
        response = supabase.table("productos").select("*").eq("estado", True).execute()
        return response.data
    except Exception as e:
        print(f"Error obteniendo productos: {str(e)}")
        return []

# Funciones para la tabla ventas
def insertar_venta(folio, usuario_id, turno_id, sucursal_id, subtotal, iva, total):
    if not supabase:
        return None
    try:
        data = {
            "folio": folio,
            "usuario_id": usuario_id,
            "turno_id": turno_id,
            "sucursal_id": sucursal_id,
            "subtotal": subtotal,
            "iva": iva,
            "total": total
        }
        response = supabase.table("ventas").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error insertando venta: {str(e)}")
        return None

def obtener_venta_por_folio(folio):
    if not supabase:
        return None
    try:
        response = supabase.table("ventas").select("*").eq("folio", folio).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error obteniendo venta: {str(e)}")
        return None

# Funciones para la tabla detalles_ventas
def insertar_detalle_venta(venta_id, producto_id, cantidad, precio_unitario, subtotal):
    if not supabase:
        return None
    try:
        data = {
            "venta_id": venta_id,
            "producto_id": producto_id,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "subtotal": subtotal
        }
        response = supabase.table("detalles_ventas").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error insertando detalle venta: {str(e)}")
        return None

# Funciones para la tabla pagos
def insertar_pago(venta_id, tipo_pago, monto, referencia=None, estado="completed"):
    if not supabase:
        return None
    try:
        data = {
            "venta_id": venta_id,
            "tipo_pago": tipo_pago,
            "monto": monto,
            "referencia": referencia,
            "estado": estado
        }
        response = supabase.table("pagos").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error insertando pago: {str(e)}")
        return None