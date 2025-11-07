
from random import choice

def asignar_rifa(usuario_id, intentos=3):
    """
    Intenta asignar una rifa a un usuario hasta 'intentos' veces.
    Retorna True si logra asignarla, False si no.
    """
    for _ in range(intentos):
        if choice([True, False]):
            return True
    return False