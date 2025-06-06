-- Añadir la columna imagen_url a la tabla buses
-- Usamos TEXT para almacenar URLs completas sin limitación de longitud
ALTER TABLE buses ADD COLUMN IF NOT EXISTS imagen_url TEXT;

-- Añadir la misma columna a la tabla estaciones si existe
ALTER TABLE estaciones ADD COLUMN IF NOT EXISTS imagen_url TEXT;

-- Verificar la estructura de la tabla después del cambio
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'buses';

-- Verificar también la estructura de la tabla estaciones
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'estaciones';

