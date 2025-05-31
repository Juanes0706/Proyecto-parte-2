# Tutorial: Trabajando con IDs Autonuméricos

Este tutorial explica cómo se han configurado las tablas con IDs autonuméricos y cómo trabajar con ellos en el código Python.

## Estructura de las Tablas

Las tablas ahora usan IDs autonuméricos (BIGSERIAL) en lugar de UUIDs:

```sql
CREATE TABLE IF NOT EXISTS public.buses (
  id BIGSERIAL PRIMARY KEY,  -- ID autonumérico
  nombre TEXT NOT NULL,
  tipo TEXT NOT NULL,
  esta_activo BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  imagen_url TEXT
);
```

Esto significa que:

1. No necesitas generar un ID manualmente al insertar un registro
2. La base de datos asignará automáticamente un número entero incremental
3. El ID será un número entero, no un UUID (más eficiente y legible)

## Inserción de Registros

### Antes (con UUID):

```python
bus_id = str(uuid.uuid4())
bus_data = {
    "id": bus_id,  # Generábamos UUID manualmente
    "nombre": nombre,
    "tipo": tipo,
    "esta_activo": esta_activo_bool
}
result, error = supabase.table("buses").insert(bus_data).execute()
```

### Ahora (con autonumérico):

```python
bus_data = {
    # No incluimos el ID, se generará automáticamente
    "nombre": nombre,
    "tipo": tipo,
    "esta_activo": esta_activo_bool
}
result, error = supabase.table("buses").insert(bus_data).execute()

# Obtener el ID generado
bus_id = result[1][0]["id"]
```

## Trabajando con Relaciones

Las relaciones entre tablas ahora usan BIGINT en lugar de UUID, pero la lógica es la misma:

```python
# Asociar una imagen a un bus
imagen_data = {
    "url": url,
    "bus_id": bus_id,  # Ahora bus_id es un entero
    "created_at": datetime.utcnow().isoformat()
}
supabase.table("imagenes").insert(imagen_data).execute()
```

## Ventajas

1. **Mejor rendimiento**: Los enteros son más eficientes que los UUIDs para indexación y búsqueda
2. **Menor espacio**: Un BIGINT ocupa 8 bytes, mientras que un UUID ocupa 16 bytes
3. **Más legible**: Los IDs numéricos son más fáciles de leer y recordar (ej: 42 vs 550e8400-e29b-41d4-a716-446655440000)
4. **Código más simple**: No es necesario generar UUIDs en el código

## Consideraciones

1. Los IDs son ahora secuenciales y predecibles, lo que puede ser menos seguro en ciertos contextos
2. No hay garantía de unicidad global (pero sí dentro de cada tabla)
3. Las aplicaciones cliente pueden necesitar actualizarse si esperaban UUIDs

## Migraciones y Datos Existentes

Si tienes datos existentes y necesitas migrarlos, ejecuta el script de migración:

```bash
python scripts/reset_database.py
```

Este script elimina todas las tablas existentes y crea nuevas con la estructura correcta.

## Conclusión

El uso de IDs autonuméricos simplifica el código y mejora el rendimiento de la base de datos, especialmente para aplicaciones donde no es crítica la generación distribuida de IDs.
