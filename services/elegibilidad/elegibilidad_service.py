# servicios relacionados con la elegibilidad del usuario para la rifa

def verificar_elegibilidad(usuario_id):
    """
    Verifica si un usuario es elegible para la rifa.
    Por ahora, simulamos:
        - Usuarios con ID <= 100 son elegibles
        - Otros no
    """
    if usuario_id <= 100:
        return True
    return False
