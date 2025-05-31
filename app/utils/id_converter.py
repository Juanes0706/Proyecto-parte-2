# Utilidad para convertir y validar IDs en diferentes formatos

def parse_id(id_str):
    """
    Intenta parsear un ID que puede venir en varios formatos
    y devolverlo como el tipo correcto (entero en este caso)

    Args:
        id_str: String o valor que representa el ID

    Returns:
        Un entero si la conversión es exitosa, None en caso contrario
    """
    if id_str is None:
        return None

    # Si ya es un entero, devolverlo tal cual
    if isinstance(id_str, int):
        return id_str

    # Intentar convertir a entero directamente
    try:
        return int(id_str)
    except (ValueError, TypeError):
        pass

    # Otras conversiones según sea necesario
    # Por ejemplo, si en algún momento hay UUIDs en formato string
    # se podrían añadir aquí más métodos de conversión

    return None

def is_valid_id(id_val):
    """
    Verifica si un valor puede ser usado como ID válido

    Args:
        id_val: Valor a verificar

    Returns:
        True si es un ID válido, False en caso contrario
    """
    return parse_id(id_val) is not None
