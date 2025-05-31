-- Script para corregir las referencias entre tablas buses e imagenes

-- 1. Verificar los tipos de las columnas id en buses y bus_id en imagenes
DO $$ 
DECLARE
    buses_id_type TEXT;
    imagenes_busid_type TEXT;
BEGIN
    -- Obtener tipo de datos de buses.id
    SELECT data_type INTO buses_id_type 
    FROM information_schema.columns 
    WHERE table_name = 'buses' AND column_name = 'id';

    -- Obtener tipo de datos de imagenes.bus_id
    SELECT data_type INTO imagenes_busid_type 
    FROM information_schema.columns 
    WHERE table_name = 'imagenes' AND column_name = 'bus_id';

    RAISE NOTICE 'Tipo de datos de buses.id: %', buses_id_type;
    RAISE NOTICE 'Tipo de datos de imagenes.bus_id: %', imagenes_busid_type;

    -- Si hay incompatibilidad, intentar corregir
    IF buses_id_type != imagenes_busid_type AND buses_id_type != 'uuid' AND imagenes_busid_type = 'uuid' THEN
        -- Eliminar la tabla imagenes y recrearla con el tipo correcto
        DROP TABLE IF EXISTS imagenes;
        RAISE NOTICE 'Tabla imagenes eliminada para recrearla con tipos compatibles';
    END IF;
END $$;

-- 2. Recrear la tabla imagenes con el tipo correcto
CREATE TABLE IF NOT EXISTS imagenes (
    id BIGSERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    bus_id BIGINT REFERENCES buses(id) ON DELETE CASCADE,
    estacion_id BIGINT REFERENCES estaciones(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 3. Verificar índices y crearlos si no existen
CREATE INDEX IF NOT EXISTS idx_imagenes_bus_id ON imagenes(bus_id);
CREATE INDEX IF NOT EXISTS idx_imagenes_estacion_id ON imagenes(estacion_id);

-- 4. Verificar la estructura después de los cambios
SELECT table_name, column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name IN ('buses', 'imagenes', 'estaciones', 'bus_estacion') 
ORDER BY table_name, ordinal_position;

-- 5. Verificar las restricciones de clave foránea
SELECT 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu 
      ON ccu.constraint_name = tc.constraint_name
WHERE constraint_type = 'FOREIGN KEY' AND tc.table_name='imagenes';
