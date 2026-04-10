
from pymongo import MongoClient
import json

client = MongoClient("SUA_STRING_MONGODB")
db = client["diario_escolar"]

def handler(request):

    if request.path == "/api/alunos":
        alunos = list(db.alunos.find({}, {"_id":0}))

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(alunos)
        }

    return {
        "statusCode": 200,
        "body": "API Diario Escolar Online"
    }
