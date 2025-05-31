-- Script para crear la tabla buses en Supabase
CREATE TABLE IF NOT EXISTS buses (
  id UUID PRIMARY KEY,
  nombre TEXT NOT NULL,
  tipo TEXT NOT NULL,
  esta_activo BOOLEAN DEFAULT TRUE,
  imagen_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
