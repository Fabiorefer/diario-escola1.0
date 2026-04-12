from flask import Flask, render_template, request, redirect, session, url_for, send_file
import psycopg2
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

app = Flask(__name__)
app.secret_key = "diario_secret"

# ===============================
# BANCO (POSTGRES - SUPABASE)
# ===============================
def conectar():
    return psycopg2.connect(
        host="db.xxx.supabase.co",
        database="postgres",
        user="postgres",
        password="SUA_SENHA",
        port=5432
    )

# ===============================
# PROTEÇÃO LOGIN
# ===============================
def verificar_login():
    if "usuario" not in session:
        return False
    return True

# ===============================
# LOGIN
# ===============================
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        session["usuario"] = request.form["usuario"]
        return redirect("/menu")
    return render_template("login.html")

@app.route("/menu")
def menu():
    if not verificar_login():
        return redirect("/")
    return render_template("index.html")

# ===============================
# DISCIPLINAS
# ===============================
@app.route("/disciplinas", methods=["GET","POST"])
def disciplinas():

    if not verificar_login():
        return redirect("/")

    professor = session["usuario"]

    conn = conectar()
    c = conn.cursor()

    if request.method == "POST":
        nova = request.form.get("nova_disciplina")
        if nova:
            c.execute("""
            INSERT INTO disciplinas (professor,disciplina)
            VALUES (%s,%s)
            """,(professor,nova))
            conn.commit()

    c.execute("SELECT disciplina FROM disciplinas WHERE professor=%s",(professor,))
    lista = [x[0] for x in c.fetchall()]

    conn.close()
    return render_template("disciplinas.html", disciplinas=lista)

# ===============================
# ALUNOS
# ===============================
@app.route("/alunos", methods=["GET","POST"])
def alunos():

    if not verificar_login():
        return redirect("/")

    professor = session["usuario"]

    conn = conectar()
    c = conn.cursor()

    if request.method == "POST":
        disciplina = request.form["disciplina"]
        turma = request.form["turma"]
        aluno = request.form["aluno"]

        c.execute("""
        INSERT INTO alunos (professor,disciplina,turma,aluno)
        VALUES (%s,%s,%s,%s)
        """,(professor,disciplina,turma,aluno))

        conn.commit()

    c.execute("SELECT disciplina FROM disciplinas WHERE professor=%s",(professor,))
    disciplinas = [x[0] for x in c.fetchall()]

    c.execute("SELECT DISTINCT turma FROM alunos WHERE professor=%s",(professor,))
    turmas = [x[0] for x in c.fetchall()]

    c.execute("""
    SELECT disciplina,turma,aluno
    FROM alunos
    WHERE professor=%s AND aluno!=''
    """,(professor,))
    lista = c.fetchall()

    conn.close()

    return render_template("alunos.html", disciplinas=disciplinas, turmas=turmas, alunos=lista)

# ===============================
# PRESENÇA (CORRIGIDO)
# ===============================
@app.route("/presenca", methods=["GET","POST"])
def presenca():

    if not verificar_login():
        return redirect("/")

    professor = session["usuario"]

    disciplina = request.values.get("disciplina")
    turma = request.values.get("turma")
    data = request.values.get("data")

    conn = conectar()
    c = conn.cursor()

    c.execute("""
    SELECT aluno FROM alunos
    WHERE professor=%s AND disciplina=%s AND turma=%s AND aluno!=''
    ORDER BY aluno
    """,(professor,disciplina,turma))

    alunos = [x[0] for x in c.fetchall()]

    if request.method == "POST":

        c.execute("""
        DELETE FROM presenca
        WHERE professor=%s AND disciplina=%s AND turma=%s AND data=%s
        """,(professor,disciplina,turma,data))

        for aluno in alunos:
            valor = request.form.get("presenca_"+aluno) or "F"

            c.execute("""
            INSERT INTO presenca
            (professor,disciplina,turma,data,aluno,valor)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,(professor,disciplina,turma,data,aluno,valor))

        conn.commit()

    conn.close()
    return render_template("presenca.html", alunos=alunos)

# ===============================
# NOTAS
# ===============================
@app.route("/notas", methods=["GET","POST"])
def notas():

    if not verificar_login():
        return redirect("/")

    professor = session["usuario"]

    disciplina = request.values.get("disciplina")
    turma = request.values.get("turma")
    bimestre = request.values.get("bimestre")

    conn = conectar()
    c = conn.cursor()

    c.execute("""
    SELECT aluno FROM alunos
    WHERE professor=%s AND disciplina=%s AND turma=%s
    """,(professor,disciplina,turma))

    alunos = [x[0] for x in c.fetchall()]

    if request.method == "POST":

        c.execute("""
        DELETE FROM notas
        WHERE professor=%s AND disciplina=%s AND turma=%s AND bimestre=%s
        """,(professor,disciplina,turma,bimestre))

        for aluno in alunos:
            p1 = request.form.get("p1_"+aluno) or 0
            p2 = request.form.get("p2_"+aluno) or 0

            c.execute("""
            INSERT INTO notas
            (professor,disciplina,turma,bimestre,aluno,p1,p2)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,(professor,disciplina,turma,bimestre,aluno,p1,p2))

        conn.commit()

    conn.close()
    return render_template("notas.html", alunos=alunos)

# ===============================
# RODAR
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
