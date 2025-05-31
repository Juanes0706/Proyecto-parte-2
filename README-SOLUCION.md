# Solución al problema de imagen_url en la tabla buses

Se ha detectado un problema con el campo `imagen_url` en la tabla `buses`. Este campo ha sido eliminado de la tabla, lo que causa errores en el código que intenta actualizarlo.

## Solución implementada

En lugar de volver a añadir el campo `imagen_url` a la tabla `buses`, hemos implementado una solución más robusta:

1. Crear una tabla `imagenes` separada que almacena las URLs de las imágenes
2. Esta tabla tiene relaciones con `buses` y `estaciones`
3. El código ha sido actualizado para usar esta tabla en lugar del campo `imagen_url`

## Pasos para implementar la solución

1. Ejecutar el script SQL para crear la tabla `imagenes`:
   ```bash
   # Desde la consola SQL de Supabase o psql
   psql -f migrations/add_imagenes_table.sql
   ```

2. Reemplazar el archivo `buses.py` actual con el nuevo `buses_nuevo.py`:
   ```bash
   # Hacer una copia de seguridad primero
   cp app/routers/buses.py app/routers/buses_backup.py
   # Reemplazar con el nuevo archivo
   cp app/routers/buses_nuevo.py app/routers/buses.py
   ```

## Ventajas de esta solución

1. **Mejor estructura de datos**: Las imágenes ahora son entidades separadas
2. **Soporte para múltiples imágenes**: Cada bus puede tener varias imágenes
3. **Compatibilidad**: El código mantiene compatibilidad con la interfaz existente
4. **Seguridad**: No depende de un campo que puede ser eliminado

## Verificación

Para verificar que todo funciona correctamente:

1. Usa el endpoint `/api/debug/tablas` para comprobar que la tabla `imagenes` existe
2. Intenta crear un nuevo bus con imagen para probar la nueva funcionalidad
3. Verifica que puedes obtener buses con sus imágenes usando `/api/buses`

## Nota técnica

Este enfoque sigue el patrón de normalización de bases de datos, evitando almacenar URLs en la tabla principal y utilizando relaciones entre tablas, lo que es una práctica recomendada en el diseño de bases de datos.
