from pymongo import MongoClient
import json

client = MongoClient("SUA_STRING_MONGODB")
db = client["diario_escolar"]

def handler(request):

    path = request.path

    # LISTAR ALUNOS
    if path == "/api/alunos":
        alunos = list(db.alunos.find({}, {"_id":0}))
        return {
            "statusCode":200,
            "body":json.dumps(alunos)
        }

    return {
        "statusCode":200,
        "body":"API Diario Escolar funcionando"
    }
