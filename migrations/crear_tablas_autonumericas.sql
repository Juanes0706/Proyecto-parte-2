-- Script para crear las tablas con IDs autonuméricos desde cero

-- Crear tabla buses con ID autonumérico
CREATE TABLE IF NOT EXISTS buses (
  id BIGSERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  tipo TEXT NOT NULL,
  esta_activo BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  imagen_url TEXT
);

-- Crear tabla estaciones con ID autonumérico
CREATE TABLE IF NOT EXISTS estaciones (
  id BIGSERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  localidad TEXT NOT NULL,
  esta_activo BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Crear tabla imagenes con ID autonumérico
CREATE TABLE IF NOT EXISTS imagenes (
  id BIGSERIAL PRIMARY KEY,
  url TEXT NOT NULL,
  bus_id BIGINT REFERENCES buses(id),
  estacion_id BIGINT REFERENCES estaciones(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Crear tabla bus_estacion con ID autonumérico
CREATE TABLE IF NOT EXISTS bus_estacion (
  id BIGSERIAL PRIMARY KEY,
  bus_id BIGINT REFERENCES buses(id) NOT NULL,
  estacion_id BIGINT REFERENCES estaciones(id) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_imagenes_bus_id ON imagenes(bus_id);
CREATE INDEX IF NOT EXISTS idx_imagenes_estacion_id ON imagenes(estacion_id);
CREATE INDEX IF NOT EXISTS idx_bus_estacion_bus_id ON bus_estacion(bus_id);
CREATE INDEX IF NOT EXISTS idx_bus_estacion_estacion_id ON bus_estacion(estacion_id);

-- Comentario explicativo
COMMENT ON TABLE buses IS 'Almacena información de buses con ID autonumérico';
COMMENT ON TABLE estaciones IS 'Almacena información de estaciones con ID autonumérico';
COMMENT ON TABLE imagenes IS 'Almacena URLs de imágenes relacionadas con buses o estaciones';
COMMENT ON TABLE bus_estacion IS 'Tabla de relación muchos a muchos entre buses y estaciones';
