# Migración a IDs Autonuméricos

Se ha implementado una solución para cambiar los IDs UUID por IDs autonuméricos (BIGSERIAL) en todas las tablas del sistema.

## Opciones de Implementación

Tienes dos opciones para implementar este cambio:

### Opción 1: Modificar tablas existentes

Si ya tienes datos en tu base de datos y deseas mantenerlos, puedes ejecutar el script de migración:

```bash
# Desde la consola SQL de Supabase o psql
psql -f migrations/auto_incremento_ids.sql
```

**Advertencia**: Antes de ejecutar este script, haz una copia de seguridad de tu base de datos, ya que cambia los tipos de datos de las claves primarias y relaciones.

### Opción 2: Crear tablas nuevas

Si prefieres empezar con tablas limpias, puedes eliminar las existentes y crear nuevas con el esquema actualizado:

```bash
# Para eliminar tablas existentes (cuidado: perderás todos los datos)
DROP TABLE IF EXISTS bus_estacion, imagenes, buses, estaciones CASCADE;

# Crear nuevas tablas con IDs autonuméricos
psql -f migrations/crear_tablas_autonumericas.sql
```

## Cambios en el Código

1. El código de Python ha sido actualizado para no generar UUIDs manualmente
2. Al crear buses o estaciones, el ID ahora es asignado automáticamente por la base de datos
3. Después de cada inserción, se obtiene el ID generado para usarlo en operaciones subsecuentes

## Ventajas de IDs Autonuméricos

1. **Rendimiento**: Los enteros son más eficientes que los UUIDs para indexación y búsqueda
2. **Legibilidad**: Los IDs numéricos son más fáciles de leer y recordar
3. **Espacio**: Ocupan menos espacio en la base de datos (8 bytes vs 16 bytes)
4. **Simplicidad**: No es necesario generar IDs en el código

## Impacto en API

La API seguirá funcionando igual, pero ahora los IDs serán números enteros en lugar de strings UUID. Esto podría requerir ajustes en aplicaciones cliente que esperen UUIDs.

## Verificación

Puedes verificar que todo funcione correctamente usando el endpoint `/api/debug/tablas` que mostrará la estructura actual de las tablas.
