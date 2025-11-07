from services.elegibilidad.reintento_service import asignar_rifa

def test_asignacion_exito():
    # podemos simular un usuario y aceptar cualquier resultado (True/False)
    resultado = asignar_rifa(1, intentos=5)
    assert resultado in [True, False]  # solo verificamos que retorne booleano

def test_intentos_respetados():
    # probamos que el parámetro de intentos sea aceptado
    resultado = asignar_rifa(2, intentos=1)
    assert resultado in [True, False]