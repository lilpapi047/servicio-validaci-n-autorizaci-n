"""
Script de prueba para endpoints de perfil
"""
import sys
import os
sys.path.insert(0, os.getcwd())

from fastapi.testclient import TestClient
from main import app
from services.api.database import SessionLocal, Base, engine
import uuid

# Preparar BD de prueba
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_perfil_api():
    """Pruebas de endpoints de perfil"""
    
    print("\n" + "="*60)
    print("PRUEBAS DE ENDPOINTS DE PERFIL")
    print("="*60)
    
    # 1. Registro de usuario
    print("\n[1] Registrando nuevo usuario...")
    email_test = f"juan_{uuid.uuid4().hex[:8]}@example.com"
    user_data = {
        "email": email_test,
        "hash_pwd": "password123",
        "first_name": "Juan",
        "last_name": "Perez",
        "country_code": "CO",
        "phone": "3001234567"
    }
    
    response = client.post("/api/registro", json=user_data)
    print(f"Status: {response.status_code}")
    user_response = response.json()
    print(f"Response: {user_response}")
    
    if response.status_code != 200:
        print("[ERROR] Error en registro")
        return False
    
    user_id = user_response['id']
    print(f"[OK] Usuario registrado con ID: {user_id}")
    
    # 2. Obtener perfil
    print(f"\n[2] Obteniendo perfil del usuario {user_id}...")
    response = client.get(f"/api/perfil/{user_id}")
    print(f"Status: {response.status_code}")
    perfil = response.json()
    print(f"Email: {perfil['email']}")
    print(f"Nombre: {perfil['first_name']} {perfil['last_name']}")
    print(f"Pais: {perfil['country_code']}")
    print(f"Telefono: {perfil['phone']}")
    
    if response.status_code != 200:
        print("[ERROR] Error obteniendo perfil")
        return False
    
    print("[OK] Perfil obtenido correctamente")
    
    # 3. Actualizar perfil
    print(f"\n[3] Actualizando perfil...")
    update_data = {
        "first_name": "Juan Carlos",
        "phone": "3109876543",
        "country_code": "MX"
    }
    
    response = client.put(f"/api/perfil/{user_id}", json=update_data)
    print(f"Status: {response.status_code}")
    updated = response.json()
    print(f"Nombre actualizado: {updated['first_name']}")
    print(f"Telefono actualizado: {updated['phone']}")
    print(f"Pais actualizado: {updated['country_code']}")
    
    if response.status_code != 200:
        print("[ERROR] Error actualizando perfil")
        return False
    
    print("[OK] Perfil actualizado correctamente")
    
    # 4. Cambiar contraseña
    print(f"\n[4] Cambiando contrasena...")
    password_data = {
        "old_password": "password123",
        "new_password": "nuevoPassword456",
        "confirm_password": "nuevoPassword456"
    }
    
    response = client.post(f"/api/perfil/{user_id}/cambiar-password", json=password_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Mensaje: {result.get('mensaje', 'Sin mensaje')}")
    
    if response.status_code != 200:
        print("[ERROR] Error cambiando contrasena")
        return False
    
    print("[OK] Contrasena cambiada correctamente")
    
    # 5. Intentar cambiar con contraseña anterior incorrecta
    print(f"\n[5] Intentando cambiar contrasena con contrasena anterior incorrecta...")
    wrong_password_data = {
        "old_password": "wrongPassword",
        "new_password": "otherPassword789",
        "confirm_password": "otherPassword789"
    }
    
    response = client.post(f"/api/perfil/{user_id}/cambiar-password", json=wrong_password_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 401:
        print("[OK] Error esperado: Contrasena anterior incorrecta")
    else:
        print("[ERROR] Deberia haber devuelto error 401")
        return False
    
    # 6. Registrar segundo usuario para probar duplicados
    print(f"\n[6] Intentando registrar usuario con email duplicado...")
    duplicate_user = {
        "email": email_test,
        "hash_pwd": "password456"
    }
    
    response = client.post("/api/registro", json=duplicate_user)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 400:
        print("[OK] Error esperado: Email ya registrado")
    else:
        print("[ERROR] Deberia haber devuelto error 400")
        return False
    
    # 7. Eliminar cuenta
    print(f"\n[7] Eliminando cuenta del usuario {user_id}...")
    response = client.delete(f"/api/perfil/{user_id}")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Mensaje: {result['mensaje']}")
    
    if response.status_code != 200:
        print("[ERROR] Error eliminando cuenta")
        return False
    
    print("[OK] Cuenta eliminada correctamente")
    
    # 8. Verificar que el usuario fue eliminado
    print(f"\n[8] Verificando que el usuario fue eliminado...")
    response = client.get(f"/api/perfil/{user_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 404:
        print("[OK] Usuario no encontrado (eliminado correctamente)")
    else:
        print("[ERROR] Deberia devolver 404")
        return False
    
    return True

def main():
    print("\n")
    print("=" * 60)
    print("  PRUEBAS DE ENDPOINTS - GESTION DE PERFIL")
    print("=" * 60)
    
    try:
        success = test_perfil_api()
        
        if success:
            print("\n" + "="*60)
            print("[OK] TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
            print("="*60)
            return 0
        else:
            print("\n" + "="*60)
            print("[ERROR] ALGUNAS PRUEBAS FALLARON")
            print("="*60)
            return 1
    except Exception as e:
        print(f"\n[ERROR] Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
