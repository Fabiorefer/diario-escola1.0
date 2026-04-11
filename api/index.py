
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "API online"

@app.route("/alunos")
def alunos():
    return jsonify({"status":"ok"})

# Vercel precisa disso
def handler(request, response):
    return app(request.environ, response.start_response)
