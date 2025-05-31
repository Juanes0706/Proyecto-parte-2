#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para resetear completamente la base de datos y crear tablas con IDs autonuméricos.
Este script:
1. Elimina todas las tablas existentes
2. Crea nuevas tablas con IDs autonuméricos (BIGSERIAL)
3. Verifica que las tablas se hayan creado correctamente

Uso:
    python scripts/reset_database.py
"""

import os
import sys
import time
from pathlib import Path

# Añadir directorio raíz al path para importar módulos de la aplicación
sys.path.append(str(Path(__file__).parent.parent))

from app.database import get_db, inicializar_storage
from dotenv import load_dotenv

load_dotenv()

def reset_database():
    """
    Elimina y recrea todas las tablas en la base de datos con IDs autonuméricos.
    """
    print("\n" + "=" * 80)
    print("🔄 INICIANDO RESETEO COMPLETO DE LA BASE DE DATOS")
    print("=" * 80)

    # Confirmar acción
    if input("⚠️  ADVERTENCIA: Esta acción eliminará TODOS los datos existentes. \n¿Estás seguro? (escribe 'SI' para confirmar): ").upper() != "SI":
        print("❌ Operación cancelada.")
        return False

    try:
        supabase = get_db()
        print("✅ Conexión a Supabase establecida")

        # 1. Eliminar tablas existentes en orden correcto (para evitar problemas con claves foráneas)
        print("\n📝 Eliminando tablas existentes...")

        try:
            # Eliminar en orden para evitar problemas con claves foráneas
            print("   - Eliminando tabla bus_estacion...")
            supabase.postgrest.rpc('execute', {"query": "DROP TABLE IF EXISTS public.bus_estacion CASCADE;"}).execute()

            print("   - Eliminando tabla imagenes...")
            supabase.postgrest.rpc('execute', {"query": "DROP TABLE IF EXISTS public.imagenes CASCADE;"}).execute()

            print("   - Eliminando tabla buses...")
            supabase.postgrest.rpc('execute', {"query": "DROP TABLE IF EXISTS public.buses CASCADE;"}).execute()

            print("   - Eliminando tabla estaciones...")
            supabase.postgrest.rpc('execute', {"query": "DROP TABLE IF EXISTS public.estaciones CASCADE;"}).execute()

            print("✅ Tablas eliminadas correctamente")
        except Exception as e:
            print(f"⚠️  Advertencia al eliminar tablas: {str(e)}")
            print("   Continuando con la creación de tablas...")

        # 2. Crear nuevas tablas con IDs autonuméricos
        print("\n📝 Creando nuevas tablas con IDs autonuméricos...")

        # Crear tabla buses
        print("   - Creando tabla buses...")
        supabase.postgrest.rpc('execute', {"query": """
        CREATE TABLE IF NOT EXISTS public.buses (
          id BIGSERIAL PRIMARY KEY,
          nombre TEXT NOT NULL,
          tipo TEXT NOT NULL,
          esta_activo BOOLEAN DEFAULT TRUE,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
          imagen_url TEXT
        );
        """}}).execute()

        # Crear tabla estaciones
        print("   - Creando tabla estaciones...")
        supabase.postgrest.rpc('execute', {"query": """
        CREATE TABLE IF NOT EXISTS public.estaciones (
          id BIGSERIAL PRIMARY KEY,
          nombre TEXT NOT NULL,
          localidad TEXT NOT NULL,
          esta_activo BOOLEAN DEFAULT TRUE,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
          imagen_url TEXT
        );
        """}}).execute()

        # Crear tabla imagenes
        print("   - Creando tabla imagenes...")
        supabase.postgrest.rpc('execute', {"query": """
        CREATE TABLE IF NOT EXISTS public.imagenes (
          id BIGSERIAL PRIMARY KEY,
          url TEXT NOT NULL,
          bus_id BIGINT REFERENCES public.buses(id),
          estacion_id BIGINT REFERENCES public.estaciones(id),
          created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
        );
        """}}).execute()

        # Crear tabla bus_estacion (relación muchos a muchos)
        print("   - Creando tabla bus_estacion...")
        supabase.postgrest.rpc('execute', {"query": """
        CREATE TABLE IF NOT EXISTS public.bus_estacion (
          id BIGSERIAL PRIMARY KEY,
          bus_id BIGINT NOT NULL REFERENCES public.buses(id),
          estacion_id BIGINT NOT NULL REFERENCES public.estaciones(id),
          created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
        );
        """}}).execute()

        # Crear índices para mejorar rendimiento
        print("   - Creando índices...")
        supabase.postgrest.rpc('execute', {"query": """
        CREATE INDEX IF NOT EXISTS idx_imagenes_bus_id ON public.imagenes(bus_id);
        CREATE INDEX IF NOT EXISTS idx_imagenes_estacion_id ON public.imagenes(estacion_id);
        CREATE INDEX IF NOT EXISTS idx_bus_estacion_bus_id ON public.bus_estacion(bus_id);
        CREATE INDEX IF NOT EXISTS idx_bus_estacion_estacion_id ON public.bus_estacion(estacion_id);
        """}}).execute()

        # Añadir comentarios a las tablas
        print("   - Añadiendo comentarios a las tablas...")
        supabase.postgrest.rpc('execute', {"query": """
        COMMENT ON TABLE public.buses IS 'Almacena información de buses con ID autonumérico';
        COMMENT ON TABLE public.estaciones IS 'Almacena información de estaciones con ID autonumérico';
        COMMENT ON TABLE public.imagenes IS 'Almacena URLs de imágenes relacionadas con buses o estaciones';
        COMMENT ON TABLE public.bus_estacion IS 'Tabla de relación muchos a muchos entre buses y estaciones';
        """}}).execute()

        print("\n✅ Tablas creadas correctamente con IDs autonuméricos")

        # 3. Verificar que las tablas se hayan creado correctamente
        print("\n📝 Verificando tablas creadas...")
        result, error = supabase.table("buses").select("count(*)").execute()
        if error:
            print(f"❌ Error al verificar tabla buses: {error}")
        else:
            print("✅ Tabla buses verificada")

        result, error = supabase.table("estaciones").select("count(*)").execute()
        if error:
            print(f"❌ Error al verificar tabla estaciones: {error}")
        else:
            print("✅ Tabla estaciones verificada")

        result, error = supabase.table("imagenes").select("count(*)").execute()
        if error:
            print(f"❌ Error al verificar tabla imagenes: {error}")
        else:
            print("✅ Tabla imagenes verificada")

        result, error = supabase.table("bus_estacion").select("count(*)").execute()
        if error:
            print(f"❌ Error al verificar tabla bus_estacion: {error}")
        else:
            print("✅ Tabla bus_estacion verificada")

        # 4. Inicializar Storage para asegurar que los buckets existan
        print("\n📝 Inicializando storage...")
        storage_ok = inicializar_storage()
        if storage_ok:
            print("✅ Storage inicializado correctamente")
        else:
            print("⚠️  No se pudo inicializar el storage correctamente")

        print("\n" + "=" * 80)
        print("✅ RESETEO DE BASE DE DATOS COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\n" + "=" * 80)
        print("❌ RESETEO DE BASE DE DATOS FALLÓ")
        print("=" * 80)
        return False

if __name__ == "__main__":
    reset_database()
