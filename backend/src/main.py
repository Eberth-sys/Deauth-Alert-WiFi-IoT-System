#/backend/src/main.py

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "¡FastAPI está funcionando correctamente!"}
