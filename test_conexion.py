"""
Script de prueba de conexión a la base de datos
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.getcwd())

def test_env_loading():
    """Prueba 1: Carga de variables de entorno"""
    print("\n" + "="*60)
    print("PRUEBA 1: Carga de variables de entorno")
    print("="*60)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.getenv("DATABASE_URL")
    project_name = os.getenv("PROJECT_NAME")
    debug = os.getenv("DEBUG")
    port = os.getenv("PORT")
    
    print(f"✓ DATABASE_URL: {db_url[:50]}..." if db_url else "✗ DATABASE_URL no configurada")
    print(f"✓ PROJECT_NAME: {project_name}")
    print(f"✓ DEBUG: {debug}")
    print(f"✓ PORT: {port}")
    
    return db_url is not None

def test_config_loading():
    """Prueba 2: Carga de configuración"""
    print("\n" + "="*60)
    print("PRUEBA 2: Carga de configuración")
    print("="*60)
    
    try:
        from app.config import settings
        print(f"✓ Settings cargadas correctamente")
        print(f"  - DATABASE_URL: {settings.DATABASE_URL[:50]}...")
        print(f"  - PROJECT_NAME: {settings.PROJECT_NAME}")
        print(f"  - DEBUG: {settings.DEBUG}")
        print(f"  - PORT: {settings.PORT}")
        return True
    except Exception as e:
        print(f"✗ Error cargando settings: {e}")
        return False

def test_database_connection():
    """Prueba 3: Conexión a la base de datos"""
    print("\n" + "="*60)
    print("PRUEBA 3: Conexión a la base de datos")
    print("="*60)
    
    try:
        from services.api.database import engine, SessionLocal
        from sqlalchemy import text
        
        # Intentar conectar
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✓ Conexión exitosa a la BD")
            print(f"✓ Query de prueba ejecutada correctamente")
            
        # Verificar sesión
        db = SessionLocal()
        print(f"✓ Sesión de BD creada correctamente")
        db.close()
        
        return True
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_models():
    """Prueba 4: Modelos de la BD"""
    print("\n" + "="*60)
    print("PRUEBA 4: Modelos de la base de datos")
    print("="*60)
    
    try:
        from services.api.models import User, Match
        from services.api.database import Base, engine
        
        print(f"✓ Modelos importados correctamente")
        print(f"  - User: {User.__tablename__}")
        print(f"  - Match: {Match.__tablename__}")
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        print(f"✓ Tablas creadas/verificadas en la BD")
        
        return True
    except Exception as e:
        print(f"✗ Error con los modelos: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_routes():
    """Prueba 5: Rutas de la API"""
    print("\n" + "="*60)
    print("PRUEBA 5: Rutas de la API")
    print("="*60)
    
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # Test root
        response = client.get("/")
        print(f"✓ GET /: {response.status_code} - {response.json()}")
        
        # Test health
        response = client.get("/health")
        print(f"✓ GET /health: {response.status_code} - {response.json()}")
        
        return True
    except Exception as e:
        print(f"✗ Error con las rutas: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("\n")
    print("█" * 60)
    print("  PRUEBAS DE CONEXIÓN - SERVICIO DE VALIDACIÓN")
    print("█" * 60)
    
    results = []
    
    # Ejecutar pruebas
    results.append(("Carga de .env", test_env_loading()))
    results.append(("Carga de config", test_config_loading()))
    results.append(("Conexión BD", test_database_connection()))
    results.append(("Modelos", test_models()))
    results.append(("Rutas API", test_routes()))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASÓ" if result else "✗ FALLÓ"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
