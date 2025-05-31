import uuid

def uuid_to_bigint(uuid_str):
    """
    Convierte un UUID a un entero positivo compatible con bigint en PostgreSQL.

    Args:
        uuid_str (str): String de UUID en formato estándar (con guiones)

    Returns:
        int: Valor entero compatible con bigint
    """
    try:
        # Convertir el UUID a un entero y asegurar que esté en el rango de bigint
        # en PostgreSQL usando una máscara de 63 bits (2^63-1)
        return int(uuid.UUID(uuid_str).int & (1<<63)-1)
    except (ValueError, TypeError):
        return None

def parse_id(id_value):
    """
    Intenta analizar un ID que puede ser un UUID o un entero.

    Args:
        id_value (str): El valor del ID a analizar

    Returns:
        int: El ID convertido a entero o None si no es posible convertirlo
    """
    if not id_value:
        return None

    # Si parece un UUID (contiene guiones)
    if isinstance(id_value, str) and '-' in id_value:
        return uuid_to_bigint(id_value)

    # Si es un string numérico o ya es un entero
    try:
        return int(id_value)
    except (ValueError, TypeError):
        return None
