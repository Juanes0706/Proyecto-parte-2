import uuid

def uuid_to_bigint(uuid_str):
    """
    Convierte un UUID a un entero positivo compatible con bigint en PostgreSQL.

    Args:
        uuid_str (str): El UUID en formato string (ej: '278a50a1-d24f-4d42-9671-df86a9926a79')

    Returns:
        int: Un número entero positivo compatible con bigint
    """
    try:
        # Convertir el UUID a un número entero y garantizar que sea positivo
        # aplicando una máscara de bits para limitar a 63 bits (bigint en PostgreSQL)
        return int(uuid.UUID(uuid_str).int & (1<<63)-1)
    except (ValueError, TypeError, AttributeError):
        # Devolver None si no se puede convertir
        return None


def try_parse_id(id_value):
    """
    Intenta analizar un ID que puede ser un UUID o un entero.
    Si es un UUID, lo convierte a bigint. Si ya es un entero o string numérico, lo devuelve como entero.

    Args:
        id_value (str): El valor del ID a analizar

    Returns:
        int: El ID convertido a entero o None si no es posible convertirlo
    """
    if not id_value:
        return None

    # Si es un string, intentar diferentes estrategias de conversión
    if isinstance(id_value, str):
        # Verificar si parece un UUID (contiene guiones)
        if '-' in id_value:
            return uuid_to_bigint(id_value)

        # Intentar convertir directamente a entero si es un string numérico
        try:
            return int(id_value)
        except ValueError:
            return None

    # Si ya es un entero
    if isinstance(id_value, int):
        return id_value

    return None
