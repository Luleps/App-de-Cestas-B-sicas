from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from funcionarios import router as funcionarios_router
from frequencia import router as frequencia_router
from entregas import router as entregas_router
from competencias import router as competencias_router
from database import init_db
import auth

#Garante a inicialização do banco ao ligar a API
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Sistema de Gestão de Cestas Básicas",
    description="API para gerenciamento de funcionários, frequência e elegibilidade/entrega de cestas básicas.",
    version="1.0.0",
    lifespan=lifespan,
)

# Permite requisições DELETE, PUT, POST e GET do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#1. Configura a pasta de arquivos estáticos (CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

#2. Inclui os endpoints da API
app.include_router(auth.router)
app.include_router(funcionarios_router, tags=["Funcionários"])
app.include_router(frequencia_router, tags=["Frequência"])
app.include_router(entregas_router, tags=["Entregas"])
app.include_router(competencias_router, tags=["Competências"])

#3. Rota principal que carrega a página WEB no navegador
@app.get("/", response_class=HTMLResponse)
def pagina_inicial():
    with open("templates/index.html", "r", encoding="utf-8") as arquivo:
        return arquivo.read()






