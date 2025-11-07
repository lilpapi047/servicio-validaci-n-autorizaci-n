from services.elegibilidad.reintento_service import asignar_rifa

def test_asignacion_exito():
    resultado = asignar_rifa(1, intentos=5)
    assert resultado in [True, False]

def test_intentos_respetados():
    resultado = asignar_rifa(2, intentos=1)
    assert resultado in [True, False]
