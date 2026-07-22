from fastapi import FastAPI
from src.adapters.controllers.produto_controller import router as produto_router

app = FastAPI(title="Sistema Restaurante a Kilo")

app.include_router(produto_router)

@app.get("/")
def read_root():
    return {"status": "ok", "mensagem": "Sistema Restaurante a Kilo rodando!"}
