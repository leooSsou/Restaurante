from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.adapters.controllers.produto_controller import router as produto_router
from src.adapters.controllers.comanda_controller import router as comanda_router

app = FastAPI(title="Sistema Restaurante a Kilo")

# Monta a pasta estática para servir CSS e JS
app.mount("/static", StaticFiles(directory="src/infrastructure/web/static"), name="static")

# Inclui os controladores da API
app.include_router(produto_router)
app.include_router(comanda_router)

@app.get("/")
def read_root():
    """Retorna o painel SPA do frontend."""
    return FileResponse("src/infrastructure/web/static/index.html")
