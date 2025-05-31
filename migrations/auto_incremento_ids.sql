-- Script para modificar las tablas y usar IDs autonuméricos en lugar de UUIDs

-- 1. Primero crear secuencias para autoincremento
CREATE SEQUENCE IF NOT EXISTS buses_id_seq;
CREATE SEQUENCE IF NOT EXISTS estaciones_id_seq;
CREATE SEQUENCE IF NOT EXISTS imagenes_id_seq;
CREATE SEQUENCE IF NOT EXISTS bus_estacion_id_seq;

-- 2. Modificar la tabla buses para usar BIGINT como ID autonumérico
ALTER TABLE buses 
    ALTER COLUMN id DROP DEFAULT,
    ALTER COLUMN id SET DATA TYPE BIGINT USING (id::text::bigint),
    ALTER COLUMN id SET DEFAULT nextval('buses_id_seq'),
    ALTER COLUMN id SET NOT NULL;

-- Asignar propiedad de la secuencia a la columna
ALTER SEQUENCE buses_id_seq OWNED BY buses.id;

-- 3. Modificar la tabla estaciones para usar BIGINT como ID autonumérico
ALTER TABLE estaciones 
    ALTER COLUMN id DROP DEFAULT,
    ALTER COLUMN id SET DATA TYPE BIGINT USING (id::text::bigint),
    ALTER COLUMN id SET DEFAULT nextval('estaciones_id_seq'),
    ALTER COLUMN id SET NOT NULL;

ALTER SEQUENCE estaciones_id_seq OWNED BY estaciones.id;

-- 4. Modificar la tabla imagenes para usar BIGINT como ID autonumérico
ALTER TABLE imagenes 
    ALTER COLUMN id DROP DEFAULT,
    ALTER COLUMN id SET DATA TYPE BIGINT USING (id::text::bigint),
    ALTER COLUMN id SET DEFAULT nextval('imagenes_id_seq'),
    ALTER COLUMN id SET NOT NULL;

ALTER SEQUENCE imagenes_id_seq OWNED BY imagenes.id;

-- 5. Modificar la tabla bus_estacion para usar BIGINT como ID autonumérico
ALTER TABLE bus_estacion 
    ALTER COLUMN id DROP DEFAULT,
    ALTER COLUMN id SET DATA TYPE BIGINT USING (id::text::bigint),
    ALTER COLUMN id SET DEFAULT nextval('bus_estacion_id_seq'),
    ALTER COLUMN id SET NOT NULL;

ALTER SEQUENCE bus_estacion_id_seq OWNED BY bus_estacion.id;

-- 6. Modificar las columnas de relaciones en bus_estacion
ALTER TABLE bus_estacion 
    ALTER COLUMN bus_id SET DATA TYPE BIGINT USING (bus_id::text::bigint),
    ALTER COLUMN estacion_id SET DATA TYPE BIGINT USING (estacion_id::text::bigint);

-- 7. Modificar las columnas de relaciones en imagenes
ALTER TABLE imagenes 
    ALTER COLUMN bus_id SET DATA TYPE BIGINT USING (bus_id::text::bigint),
    ALTER COLUMN estacion_id SET DATA TYPE BIGINT USING (estacion_id::text::bigint);

-- 8. Actualizar las secuencias para que comiencen después del valor máximo actual
SELECT setval('buses_id_seq', COALESCE((SELECT MAX(id) FROM buses), 0) + 1);
SELECT setval('estaciones_id_seq', COALESCE((SELECT MAX(id) FROM estaciones), 0) + 1);
SELECT setval('imagenes_id_seq', COALESCE((SELECT MAX(id) FROM imagenes), 0) + 1);
SELECT setval('bus_estacion_id_seq', COALESCE((SELECT MAX(id) FROM bus_estacion), 0) + 1);

-- NOTA: Este script debe ejecutarse con precaución ya que cambia el tipo de dato de las claves primarias.
-- Es recomendable hacer una copia de seguridad de la base de datos antes de ejecutarlo.
-- También es posible que se requiera ajustar las claves foráneas y relaciones entre tablas.
