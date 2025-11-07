import pytest
from services.elegibilidad.elegibilidad_service import verificar_elegibilidad

def test_usuario_elegible():
    assert verificar_elegibilidad(1) == True

def test_usuario_no_elegible():
    assert verificar_elegibilidad(101) == False