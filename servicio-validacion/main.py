from database import init_db

# Donde tengas tu app
app = FastAPI()

# Agregar esto
@app.on_event("startup")
def startup():
    init_db()  # Crea las tablas