from fastapi import FastAPI
from funcionarios import router as funcionarios_router
from frequencia import router as frequencia_router
from entregas import router as entregas_router

app = FastAPI()

app.include_router(funcionarios_router)
app.include_router(frequencia_router)
app.include_router(entregas_router)






