from fastapi import FastAPI

app = FastAPI(title="Sistema Restaurante a Kilo")

@app.get("/")
def read_root():
    return {"status": "ok", "mensagem": "Sistema Restaurante a Kilo rodando!"}
