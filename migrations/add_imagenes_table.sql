-- Script para crear la tabla imagenes y adaptarse a la nueva estructura sin imagen_url

-- 1. Crear la extensión uuid-ossp si no existe
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Crear tabla imagenes si no existe
CREATE TABLE IF NOT EXISTS imagenes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    url TEXT NOT NULL,
    bus_id UUID REFERENCES buses(id),
    estacion_id UUID REFERENCES estaciones(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 3. Índices para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_imagenes_bus_id ON imagenes(bus_id);
CREATE INDEX IF NOT EXISTS idx_imagenes_estacion_id ON imagenes(estacion_id);

-- 4. Si existe la columna imagen_url en buses, migrar datos a la tabla imagenes
DO $$
DECLARE
    tiene_imagen_url BOOLEAN;
    bus_record RECORD;
BEGIN
    -- Verificar si existe la columna imagen_url
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'buses' AND column_name = 'imagen_url'
    ) INTO tiene_imagen_url;

    IF tiene_imagen_url THEN
        -- Migrar datos de imagen_url a la tabla imagenes
        FOR bus_record IN 
            SELECT id, imagen_url FROM buses 
            WHERE imagen_url IS NOT NULL AND imagen_url != ''
        LOOP
            INSERT INTO imagenes (bus_id, url, created_at)
            VALUES (bus_record.id, bus_record.imagen_url, NOW())
            ON CONFLICT DO NOTHING;
        END LOOP;

        -- Opcional: Eliminar la columna imagen_url de buses
        -- ALTER TABLE buses DROP COLUMN IF EXISTS imagen_url;
    END IF;
END;
$$;

-- INSTRUCCIONES DE USO:
-- 1. Ejecuta este script en tu base de datos Supabase
-- 2. Actualiza tu código para usar la tabla 'imagenes' en lugar de 'imagen_url'
-- 3. Las relaciones bus->imagenes y estacion->imagenes funcionarán automáticamente
