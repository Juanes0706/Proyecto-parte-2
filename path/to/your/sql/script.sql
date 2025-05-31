-- Script para crear la tabla buses en Supabase
CREATE TABLE IF NOT EXISTS buses (
  id UUID PRIMARY KEY,
  nombre TEXT NOT NULL,
  tipo TEXT NOT NULL,
  esta_activo BOOLEAN DEFAULT TRUE,
  imagen_url TEXT, -- Añadimos imagen_url como TEXT (puede ser NULL)
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
  -- También eliminamos updated_at para simplificar
);
