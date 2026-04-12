from pymongo import MongoClient
import os

# conexão única (melhor performance)
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["diario_escolar"]


def get_db():
    return db


def criar_banco():
    db = get_db()

    # cria collections (opcional)
    db.create_collection("professores", capped=False) if "professores" not in db.list_collection_names() else None
    db.create_collection("alunos") if "alunos" not in db.list_collection_names() else None
    db.create_collection("conteudos") if "conteudos" not in db.list_collection_names() else None
    db.create_collection("presenca") if "presenca" not in db.list_collection_names() else None
    db.create_collection("notas") if "notas" not in db.list_collection_names() else None

    print("Banco MongoDB conectado com sucesso")
