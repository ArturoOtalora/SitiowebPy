from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "¡Hola desde FastAPI en Railway!"}

# Para ejecutar localmente:
# uvicorn main:app --host 0.0.0.0 --port 8000
