from pymongo import MongoClient

def conectar():
    client = MongoClient("SUA_STRING_MONGODB")
    db = client["diario_escolar"]
    return db


def criar_banco():
    db = conectar()

    db["professores"]
    db["alunos"]
    db["conteudos"]
    db["presenca"]
    db["notas"]

    print("Banco MongoDB conectado com sucesso")
