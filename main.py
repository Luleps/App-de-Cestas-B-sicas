from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from funcionarios import router as funcionarios_router
from frequencia import router as frequencia_router
from entregas import router as entregas_router
from competencias import router as competencias_router

app = FastAPI()

#1. Configura a pasta de arquivos estáticos (CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

#2. Inclui os endpoints da API
app.include_router(funcionarios_router)
app.include_router(frequencia_router)
app.include_router(entregas_router)
app.include_router(competencias_router)

#3. Rota principal que carrega a página WEB no navegador
@app.get("/", response_class=HTMLResponse)
def pagina_inicial():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()






