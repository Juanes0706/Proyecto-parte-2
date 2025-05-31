-- Script para crear las tablas con IDs autonuméricos desde cero

-- Eliminar tablas existentes (en orden para evitar problemas con claves foráneas)
DROP TABLE IF EXISTS public.bus_estacion CASCADE;
DROP TABLE IF EXISTS public.imagenes CASCADE;
DROP TABLE IF EXISTS public.buses CASCADE;
DROP TABLE IF EXISTS public.estaciones CASCADE;

-- Crear tabla buses con ID autonumérico
CREATE TABLE IF NOT EXISTS public.buses (
  id BIGSERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  tipo TEXT NOT NULL,
  esta_activo BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  imagen_url TEXT
);

-- Crear tabla estaciones con ID autonumérico
CREATE TABLE IF NOT EXISTS public.estaciones (
  id BIGSERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  localidad TEXT NOT NULL,
  esta_activo BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  imagen_url TEXT
);

-- Crear tabla imagenes con ID autonumérico
CREATE TABLE IF NOT EXISTS public.imagenes (
  id BIGSERIAL PRIMARY KEY,
  url TEXT NOT NULL,
  bus_id BIGINT REFERENCES public.buses(id) ON DELETE CASCADE,
  estacion_id BIGINT REFERENCES public.estaciones(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Crear tabla bus_estacion con ID autonumérico
CREATE TABLE IF NOT EXISTS public.bus_estacion (
  id BIGSERIAL PRIMARY KEY,
  bus_id BIGINT NOT NULL REFERENCES public.buses(id) ON DELETE CASCADE,
  estacion_id BIGINT NOT NULL REFERENCES public.estaciones(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_imagenes_bus_id ON public.imagenes(bus_id);
CREATE INDEX IF NOT EXISTS idx_imagenes_estacion_id ON public.imagenes(estacion_id);
CREATE INDEX IF NOT EXISTS idx_bus_estacion_bus_id ON public.bus_estacion(bus_id);
CREATE INDEX IF NOT EXISTS idx_bus_estacion_estacion_id ON public.bus_estacion(estacion_id);

-- Añadir restricción única a bus_estacion para evitar duplicados
ALTER TABLE public.bus_estacion ADD CONSTRAINT bus_estacion_unique UNIQUE (bus_id, estacion_id);

-- Comentario explicativo
COMMENT ON TABLE public.buses IS 'Almacena información de buses con ID autonumérico';
COMMENT ON TABLE public.estaciones IS 'Almacena información de estaciones con ID autonumérico';
COMMENT ON TABLE public.imagenes IS 'Almacena URLs de imágenes relacionadas con buses o estaciones';
COMMENT ON TABLE public.bus_estacion IS 'Tabla de relación muchos a muchos entre buses y estaciones';
