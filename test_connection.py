# test_connection.py - Script para probar la conexión a Supabase

from db import supabase

if supabase:
    print("\n=== Prueba de Conexión a Supabase ===\n")
    
    # Prueba 1: Obtener productos
    try:
        print("1. Obteniendo productos...")
        response = supabase.table("productos").select("*").limit(5).execute()
        print(f"   ✓ Productos encontrados: {len(response.data)}")
        if response.data:
            print(f"   Primer producto: {response.data[0]['nombre']}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Prueba 2: Obtener categorías
    try:
        print("\n2. Obteniendo categorías...")
        response = supabase.table("categorias").select("*").limit(5).execute()
        print(f"   ✓ Categorías encontradas: {len(response.data)}")
        if response.data:
            print(f"   Primera categoría: {response.data[0]['nombre']}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Prueba 3: Obtener ventas
    try:
        print("\n3. Obteniendo ventas...")
        response = supabase.table("ventas").select("*").limit(5).execute()
        print(f"   ✓ Ventas encontradas: {len(response.data)}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Prueba 4: Insertar una categoría (prueba de escritura)
    try:
        print("\n4. Insertando categoría de prueba...")
        data = {
            "nombre": "Electrónica",
            "descripcion": "Productos electrónicos como celulares, laptops y accesorios"
        }
        response = supabase.table("categorias").insert(data).execute()
        if response.data:
            print(f"   ✓ Categoría insertada correctamente")
            print(f"   ID: {response.data[0]['id']}")
            print(f"   Nombre: {response.data[0]['nombre']}")
        else:
            print(f"   ✗ No se pudo insertar la categoría")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    print("\n=== Prueba completada ===\n")
else:
    print("✗ No hay conexión a Supabase disponible")
