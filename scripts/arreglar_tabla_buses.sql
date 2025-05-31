-- Arreglar el problema de la tabla buses y agregar la tabla imagenes

-- 1. Crear la tabla imagenes si no existe
CREATE TABLE IF NOT EXISTS imagenes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    url TEXT NOT NULL,
    bus_id UUID REFERENCES buses(id),
    estacion_id UUID REFERENCES estaciones(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 2. Agregar índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_imagenes_bus_id ON imagenes(bus_id);
CREATE INDEX IF NOT EXISTS idx_imagenes_estacion_id ON imagenes(estacion_id);

-- 3. Verificar que la tabla buses existe y tiene los campos correctos
DO $$
BEGIN
    -- Verificar si existe la columna imagen_url en buses
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'buses' AND column_name = 'imagen_url'
    ) THEN
        -- Si no existe, intentar agregarla (aunque no la vamos a usar realmente)
        BEGIN
            ALTER TABLE buses ADD COLUMN imagen_url TEXT;
            RAISE NOTICE 'Columna imagen_url agregada a la tabla buses';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Error al agregar columna imagen_url: %', SQLERRM;
        END;
    END IF;
END;
$$;

-- 4. Comentario explicando cómo usar el script
/*
Ejecutar este script en la base de datos Supabase para crear 
la tabla de imágenes y verificar la estructura de la tabla buses.

La aplicación ahora almacenará las imágenes en la tabla 'imagenes'
en lugar de usar el campo imagen_url en la tabla buses.
*/
