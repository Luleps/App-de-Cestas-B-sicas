from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
import sqlite3
import jwt
import bcrypt
from datetime import datetime, timedelta
from database import get_db

router = APIRouter(tags=["Autenticação"])

#Configuração do JWT e criptografia
SECRET_KEY = "sua_chave_secreta_super_segura_aqui"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

oath2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#schemas pydantic
class UsuarioCreate(BaseModel):
    nome: str
    senha: str

#funções utilitarias de senha
def gerar_hash_senha(senha: str) -> str:
    senha_bytes = senha.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(senha_bytes, salt)
    return hash_bytes.decode('utf-8')

def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    senha_bytes = senha_pura.encode('utf-8')
    hash_bytes = senha_hash.encode('utf-8')
    return bcrypt.checkpw(senha_bytes, hash_bytes)

def criar_token_acesso(data: dict) -> str:
    para_codificar = data.copy()
    expericao = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    para_codificar.update({"exp": expericao})
    return jwt.encode(para_codificar, SECRET_KEY, algorithm=ALGORITHM)

#1. rota para cadastrar usuarios
@router.post("/usuarios", status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(usuario: UsuarioCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    #verifica se ja existe um usuario com esse nome
    cursor.execute("SELECT id FROM usuarios WHERE nome = ?", (usuario.nome,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=400,
            detail="Já existe um usuário cadastrado com este nome."
        )

    senha_criptografada = gerar_hash_senha(usuario.senha)
    cursor.execute(
        "INSERT INTO usuarios (nome, senha) VALUES (?, ?)",
        (usuario.nome, senha_criptografada)
    )
    db.commit()
    return {"mensagem": f"Usuário '{usuario.nome}' criado com sucesso!"}

#2. rota de login
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    # o OAuth2PasswordRequestForm usa o campo 'username' para identificação
    cursor.execute("SELECT id, nome, senha FROM usuarios WHERE nome = ?", (form_data.username,))
    usuario = cursor.fetchone()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos."
        )

    if not verificar_senha(form_data.password, usuario["senha"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos."
        )

    #gera o token de acesso contendo o ID e o nome do usuario
    token = criar_token_acesso(data={"sub": str(usuario["id"]), "nome": usuario["nome"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario_id": usuario["id"],
        "usuario_nome": usuario["nome"]
    }

#3. função dependencia: recupera o usuario logado a partir do token nas futuras requisições
def obter_usuario_atual(token: str = Depends(oath2_scheme), db: sqlite3.Connection = Depends(get_db)):
    excecao_autenticacao = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada. Faça login novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        if usuario_id is None:
            raise excecao_autenticacao
    except jwt.PyJWTError:
        raise excecao_autenticacao

    cursor = db.cursor()
    cursor.execute("SELECT id, nome FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = cursor.fetchone()

    if usuario is None:
        raise excecao_autenticacao
    
    return dict(usuario)