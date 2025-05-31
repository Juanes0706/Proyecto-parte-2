import requests
import json
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# URL de la API en Render
render_url = os.getenv("RENDER_URL", "https://proyecto-sjyf.onrender.com")

def probar_api():
    """Realiza pruebas básicas a la API en Render"""
    print(f"\n==== Probando API en Render ({render_url}) ====\n")

    # Prueba 1: Endpoint de debug para verificar tablas
    try:
        print("Prueba 1: Verificando estructura de tablas...")
        response = requests.get(f"{render_url}/api/debug/tablas")
        print(f"  Código: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("  ✅ Conexión a la base de datos funciona")
            print(f"  Tablas disponibles: {list(data.get('tablas', {}).keys())}")

            # Verificar campos de buses
            buses_campos = data.get('tablas', {}).get('buses', {}).get('campos_disponibles', [])
            print(f"  Campos en tabla buses: {buses_campos}")

            # Verificar campos de imagenes
            imagenes_campos = data.get('tablas', {}).get('imagenes', {}).get('campos_disponibles', [])
            print(f"  Campos en tabla imagenes: {imagenes_campos}")
        else:
            print(f"  ❌ Error: {response.text}")
    except Exception as e:
        print(f"  ❌ Error en prueba de tablas: {str(e)}")

    # Prueba 2: Listar buses
    try:
        print("\nPrueba 2: Listando buses existentes...")
        response = requests.get(f"{render_url}/api/buses")
        print(f"  Código: {response.status_code}")
        if response.status_code == 200:
            buses = response.json()
            print(f"  ✅ {len(buses)} buses encontrados")
            if buses:
                print(f"  Primer bus: {buses[0]['nombre']} (ID: {buses[0]['id']})")
                # Verificar si tiene imagen_url
                if 'imagen_url' in buses[0]:
                    print(f"  URL de imagen: {'✅ Presente' if buses[0]['imagen_url'] else '❌ No tiene'}")
                else:
                    print("  ❌ Campo imagen_url no está presente")
        else:
            print(f"  ❌ Error: {response.text}")
    except Exception as e:
        print(f"  ❌ Error al listar buses: {str(e)}")

    # Prueba 3: Crear un bus sin imagen
    try:
        print("\nPrueba 3: Creando bus sin imagen...")
        data = {
            "nombre": "Bus Prueba Render",
            "tipo": "Troncal",
            "esta_activo": "true"
        }
        response = requests.post(f"{render_url}/api/buses", data=data)
        print(f"  Código: {response.status_code}")
        print(f"  Respuesta: {response.text}")

        if response.status_code == 200:
            print("  ✅ Bus creado exitosamente")
            try:
                bus_id = response.json().get('bus_id')
                print(f"  ID del bus creado: {bus_id}")
                return bus_id
            except:
                print("  ⚠️ No se pudo obtener el ID del bus creado")
        else:
            print("  ❌ Error al crear bus")
    except Exception as e:
        print(f"  ❌ Error en solicitud: {str(e)}")

def main():
    """Función principal"""
    print("=== Diagnóstico de API en Render ===\n")
    print(f"URL base: {render_url}")

    if "tu-app-en-render" in render_url:
        print("\n⚠️ IMPORTANTE: Debes configurar la URL correcta de Render en el archivo .env")
        print("Ejemplo: RENDER_URL=https://tu-app-actual.onrender.com")
        return

    # Probar la API
    bus_id = probar_api()

    # Si creamos un bus, intentar obtener sus detalles
    if bus_id:
        try:
            print(f"\nPrueba 4: Obteniendo detalles del bus creado (ID: {bus_id})...")
            response = requests.get(f"{render_url}/api/buses/{bus_id}")
            if response.status_code == 200:
                print(f"  ✅ Bus encontrado: {response.json()['nombre']}")
            else:
                print(f"  ❌ Error al obtener bus: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

    print("\n=== Diagnóstico completado ===\n")

if __name__ == "__main__":
    main()
