-- Script para crear la tabla de relación entre buses y estaciones
CREATE TABLE IF NOT EXISTS bus_estacion (
  bus_id UUID REFERENCES buses(id) ON DELETE CASCADE,
  estacion_id UUID REFERENCES estaciones(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  PRIMARY KEY (bus_id, estacion_id)
);
