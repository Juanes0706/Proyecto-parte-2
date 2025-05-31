import pkg_resources
import sys
import subprocess

print("==== Verificación de versiones de paquetes ====\n")

try:
    # Verificar versión de supabase
    supabase_version = pkg_resources.get_distribution("supabase").version
    print(f"Versión de supabase instalada: {supabase_version}")

    # Verificar versiones de dependencias importantes
    python_version = sys.version.split()[0]
    print(f"Versión de Python: {python_version}")

    # Listar paquetes relacionados
    packages_to_check = [
        "supabase",
        "httpx",
        "pydantic",
        "gotrue",
        "postgrest",
        "storage3",
        "realtime",
        "supafunc"
    ]

    print("\nVersiones de paquetes relacionados:")
    for package in packages_to_check:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"- {package}: {version}")
        except pkg_resources.DistributionNotFound:
            print(f"- {package}: No instalado")

    # Recomendación para versión compatible
    print("\n==== Recomendación ====\n")
    if supabase_version.startswith("0."):
        print("La versión instalada es antigua. Se recomienda actualizar a la versión 1.0.3:")
        print("pip install supabase==1.0.3")
    elif supabase_version.startswith("1."):
        print("La versión instalada es reciente. Para asegurar compatibilidad con el código:")
        print("pip install supabase==1.0.3")

    # Comprobar si hay errores comunes
    print("\n==== Verificando posibles problemas ====\n")
    try:
        from supabase import create_client, Client
        print("✅ Importación de create_client correcta")

        # Verificar si storage3 está instalado correctamente
        try:
            import storage3
            print("✅ storage3 importado correctamente")
        except ImportError:
            print("❌ Error al importar storage3. Instálalo con: pip install storage3")

    except ImportError as e:
        print(f"❌ Error al importar supabase: {e}")
        print("   Intenta reinstalar el paquete con: pip install --force-reinstall supabase==1.0.3")

    print("\n==== Comandos útiles ====\n")
    print("# Actualizar a una versión específica:")
    print("pip install supabase==1.0.3")
    print("\n# Reinstalar forzando la actualización de dependencias:")
    print("pip install --force-reinstall supabase==1.0.3")
    print("\n# Limpiar la caché de pip:")
    print("pip cache purge")

except Exception as e:
    print(f"Error durante la verificación: {e}")
