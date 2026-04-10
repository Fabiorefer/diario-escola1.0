from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from flask import send_file

from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "diario_secret"

# ===============================
# BANCO
# ===============================

import psycopg2

def conectar():
    return psycopg2.connect(
        host="db.xxx.supabase.co",
        database="postgres",
        user="postgres",
        password="SUA_SENHA",
        port=5432
    )

def criar_tabelas():

    conn = conectar()
    c = conn.cursor()

    # DISCIPLINAS
    c.execute("""
    CREATE TABLE IF NOT EXISTS disciplinas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        professor TEXT,
        disciplina TEXT
    )
    """)

    # ALUNOS
    c.execute("""
    CREATE TABLE IF NOT EXISTS alunos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        professor TEXT,
        disciplina TEXT,
        turma TEXT,
        aluno TEXT
    )
    """)

    # PRESENÇA
    c.execute("""
    CREATE TABLE IF NOT EXISTS presenca(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        professor TEXT,
        disciplina TEXT,
        turma TEXT,
        data TEXT,
        aluno TEXT,
        valor TEXT
    )
    """)

    # NOTAS
    c.execute("""
    CREATE TABLE IF NOT EXISTS notas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        professor TEXT,
        disciplina TEXT,
        turma TEXT,
        bimestre TEXT,
        aluno TEXT,
        p1 REAL,
        p2 REAL,
        trabalho REAL,
        participacao REAL,
        tarefa REAL
    )
    """)

    # CONTEUDOS
    c.execute("""
    CREATE TABLE IF NOT EXISTS conteudos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        professor TEXT,
        disciplina TEXT,
        turma TEXT,
        data TEXT,
        conteudo TEXT
    )
    """)

    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

# ===============================
# LOGIN
# ===============================

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":
        session["usuario"] = request.form["usuario"]
        return redirect("/index")

    return render_template("login.html")

@app.route("/index")
def menu():
    return render_template("index.html")

# ===============================
# DISCIPLINAS
# ===============================

@app.route("/disciplinas", methods=["GET","POST"])
def disciplinas():

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

    c.execute("""
    SELECT disciplina
    FROM disciplinas
    WHERE professor=%s
    ORDER BY disciplina
    """,(professor,))

    lista = [x[0] for x in c.fetchall()]

    conn.close()

    return render_template("disciplinas.html", disciplinas=lista)

# ===============================
# TURMAS
# ===============================

@app.route("/turmas", methods=["GET","POST"])
def turmas():

    professor = session["usuario"]

    conn = conectar()
    c = conn.cursor()

    # cadastrar turma
    if request.method == "POST":

        disciplina = request.form["disciplina"]
        turma = request.form["turma"]

        c.execute("""
        INSERT INTO alunos (professor,disciplina,turma,aluno)
        VALUES (%s,%s,%s,?%s)
        """,(professor,disciplina,turma,""))

        conn.commit()

    # pegar disciplinas
    c.execute("""
    SELECT disciplina
    FROM disciplinas
    WHERE professor=%s
    """,(professor,))

    disciplinas = [x[0] for x in c.fetchall()]

    # pegar turmas
    c.execute("""
    SELECT DISTINCT disciplina,turma
    FROM alunos
    WHERE professor=%s
    ORDER BY disciplina,turma
    """,(professor,))

    registros = c.fetchall()

    conn.close()

    return render_template(
        "turmas.html",
        disciplinas=disciplinas,
        registros=registros
    )

# ===============================
# ALUNOS
# ===============================

@app.route("/alunos", methods=["GET","POST"])
def alunos():

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
    ORDER BY disciplina,turma,aluno
    """,(professor,))
    lista = c.fetchall()

    conn.close()

    return render_template(
        "alunos.html",
        disciplinas=disciplinas,
        turmas=turmas,
        alunos=lista
    )

# ===============================
# PRESENÇA
# ===============================

@app.route("/presenca", methods=["GET","POST"])
def presenca():

    professor = session["usuario"]

    disciplina = request.values.get("disciplina")
    turma = request.values.get("turma")
    data = request.values.get("data")

    conn = conectar()
    c = conn.cursor()

    # carregar disciplinas e turmas
    c.execute("""
    SELECT DISTINCT disciplina,turma
    FROM alunos
    WHERE professor=%s
    """,(professor,))
    registros = c.fetchall()

    disciplinas = sorted(list(set([r[0] for r in registros])))
    turmas = sorted(list(set([r[1] for r in registros])))

    alunos = []

    if disciplina and turma:
        c.execute("""
        SELECT aluno FROM alunos
        WHERE professor=%s AND disciplina=%s AND turma=%s AND aluno!=''
        ORDER BY aluno
        """,(professor,disciplina,turma))

        alunos = [x[0] for x in c.fetchall()]

# ===============================
# SALVAR PRESENÇA
# ===============================
    if request.method == "POST":

        c.execute("""
        DELETE FROM presenca
        WHERE professor=%s AND disciplina=%s AND turma=%s AND data=%s
        """,(professor,disciplina,turma,data))

        i = 1
        for aluno in alunos:

            valor = request.form.get(f"presenca_{i}")

        if not valor:
            valor = "F"

        c.execute("""
        INSERT INTO presenca
        (professor,disciplina,turma,data,aluno,valor)
        VALUES (%s,%s,%s,%s,%s,%s)
        """,(professor,disciplina,turma,data,aluno,valor))

        i += 1

    conn.commit()

    # ===============================
    # CARREGAR PRESENÇAS SALVAS
    # ===============================
    presencas = {}

    if disciplina and turma and data:

        c.execute("""
        SELECT aluno,valor
        FROM presenca
        WHERE professor=%s AND disciplina=%s AND turma=%s AND data=%s
        """,(professor,disciplina,turma,data))

        for aluno,valor in c.fetchall():
            presencas[aluno] = valor

    conn.close()

    return render_template(
        "presenca.html",
        disciplinas=disciplinas,
        turmas=turmas,
        disciplina=disciplina,
        turma=turma,
        data=data,
        alunos=alunos,
        presencas=presencas,
        salvo=(request.method=="POST")
    )

# ===============================
# NOTAS
# ===============================

@app.route("/notas", methods=["GET","POST"])
def notas():

    professor = session["usuario"]

    disciplina = request.values.get("disciplina")
    turma = request.values.get("turma")
    bimestre = request.values.get("bimestre")

    conn = conectar()
    c = conn.cursor()

    c.execute("""
    SELECT DISTINCT disciplina,turma
    FROM alunos
    WHERE professor=%s
    """,(professor,))
    registros = c.fetchall()

    disciplinas = sorted(list(set([r[0] for r in registros])))
    turmas = sorted(list(set([r[1] for r in registros])))

    alunos = []

    if disciplina and turma:
        c.execute("""
        SELECT aluno FROM alunos
        WHERE professor=%s AND disciplina=%s AND turma=%s AND aluno!=''
        ORDER BY aluno
        """,(professor,disciplina,turma))

        alunos = [x[0] for x in c.fetchall()]

    notas = {}

    # CARREGAR NOTAS JÁ SALVAS
    if disciplina and turma and bimestre:

        c.execute("""
        SELECT aluno,p1,p2,trabalho,participacao,tarefa
        FROM notas
        WHERE professor=%s AND disciplina=%s AND turma=%s AND bimestre=%s
        """,(professor,disciplina,turma,bimestre))

        for row in c.fetchall():
            notas[row[0]] = {
                "p1": row[1],
                "p2": row[2],
                "trab": row[3],
                "part": row[4],
                "tarefa": row[5]
            }

    # SALVAR
    if request.method == "POST":

        c.execute("""
        DELETE FROM notas
        WHERE professor=%s AND disciplina=%s AND turma=%s AND bimestre=%s
        """,(professor,disciplina,turma,bimestre))

        for aluno in alunos:

            p1 = request.form.get("p1_"+aluno) or 0
            p2 = request.form.get("p2_"+aluno) or 0
            trab = request.form.get("trab_"+aluno) or 0
            part = request.form.get("part_"+aluno) or 0
            tarefa = request.form.get("tarefa_"+aluno) or 0

            c.execute("""
            INSERT INTO notas
            (professor,disciplina,turma,bimestre,aluno,p1,p2,trabalho,participacao,tarefa)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,(professor,disciplina,turma,bimestre,aluno,p1,p2,trab,part,tarefa))

        conn.commit()
        conn.close()

        return redirect(url_for("notas",
            disciplina=disciplina,
            turma=turma,
            bimestre=bimestre
        ))

    conn.close()

    return render_template(
        "notas.html",
        disciplinas=disciplinas,
        turmas=turmas,
        disciplina=disciplina,
        turma=turma,
        bimestre=bimestre,
        alunos=alunos,
        notas=notas
    )

# ===============================
# CONTEUDOS
# ===============================

@app.route("/conteudos", methods=["GET","POST"])
def conteudos():

    professor = session["usuario"]

    disciplina = request.values.get("disciplina")
    turma = request.values.get("turma")
    data = request.values.get("data")

    conn = conectar()
    c = conn.cursor()

    # carregar disciplinas e turmas
    c.execute("""
    SELECT DISTINCT disciplina,turma
    FROM alunos
    WHERE professor=%s
    """,(professor,))
    registros = c.fetchall()

    disciplinas = sorted(list(set([r[0] for r in registros])))
    turmas = sorted(list(set([r[1] for r in registros])))

    conteudo_atual = ""

    # carregar conteúdo da data
    if disciplina and turma and data:

        c.execute("""
        SELECT conteudo
        FROM conteudos
        WHERE professor=%s AND disciplina=%s AND turma=%s AND data=%s
        """,(professor,disciplina,turma,data))

        row = c.fetchone()

        if row:
            conteudo_atual = row[0]

    # salvar
    if request.method == "POST":

        conteudo = request.form.get("conteudo")

        c.execute("""
        DELETE FROM conteudos
        WHERE professor=%s AND disciplina=%s AND turma=%s AND data=%s
        """,(professor,disciplina,turma,data))

        c.execute("""
        INSERT INTO conteudos
        (professor,disciplina,turma,data,conteudo)
        VALUES (%s,%s,%s,%s,%s)
        """,(professor,disciplina,turma,data,conteudo))

        conn.commit()

        return render_template(
            "conteudos.html",
            disciplinas=disciplinas,
            turmas=turmas,
            disciplina=disciplina,
            turma=turma,
            data=data,
            conteudo_atual=conteudo,
            salvo=True,
            conteudos=[]
        )

    # lista conteúdos já lançados
    conteudos = []

    if disciplina and turma:

        c.execute("""
        SELECT data,conteudo
        FROM conteudos
        WHERE professor=%s AND disciplina=%s AND turma=%s
        ORDER BY data DESC
        """,(professor,disciplina,turma))

        conteudos = c.fetchall()

    conn.close()

    return render_template(
        "conteudos.html",
        disciplinas=disciplinas,
        turmas=turmas,
        disciplina=disciplina,
        turma=turma,
        data=data,
        conteudo_atual=conteudo_atual,
        conteudos=conteudos
    )

# ===============================
# RELATORIO
# ===============================

@app.route("/relatorio", methods=["GET"])
def relatorio():

    professor = session["usuario"]

    conn = conectar()
    c = conn.cursor()

    c.execute("""
    SELECT DISTINCT disciplina,turma
    FROM alunos
    WHERE professor=%s
    """,(professor,))

    registros = c.fetchall()

    disciplinas = sorted(list(set([r[0] for r in registros])))
    turmas = sorted(list(set([r[1] for r in registros])))

    conn.close()

    return render_template(
        "relatorio.html",
        disciplinas=disciplinas,
        turmas=turmas
    )

# ===============================
# GERAR PDF
# ===============================

@app.route("/relatorio_pdf")
def relatorio_pdf():

    professor = session["usuario"]

    disciplina = request.args.get("disciplina")
    turma = request.args.get("turma")
    bimestre = request.args.get("bimestre")

    conn = conectar()
    c = conn.cursor()

    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph(f"Professor: {professor}", styles['Heading2']))
    elementos.append(Paragraph(f"Disciplina: {disciplina}", styles['Normal']))
    elementos.append(Paragraph(f"Turma: {turma}", styles['Normal']))
    elementos.append(Paragraph(f"Bimestre: {bimestre}", styles['Normal']))
    elementos.append(Spacer(1,12))

    dados = [["Aluno","P1","P2","Trab","Part","Tarefa","Presenças","Faltas","Média"]]

    # ===============================
    # PEGAR NOTAS
    # ===============================
    c.execute("""
    SELECT aluno,p1,p2,trabalho,participacao,tarefa
    FROM notas
    WHERE professor=%s AND disciplina=%s AND turma=%s AND bimestre=%s
    ORDER BY aluno
    """,(professor,disciplina,turma,bimestre))

    alunos = c.fetchall()

    for row in alunos:

        aluno = row[0]

        p1 = float(row[1] or 0)
        p2 = float(row[2] or 0)
        trab = float(row[3] or 0)
        part = float(row[4] or 0)
        tarefa = float(row[5] or 0)

        # ===============================
        # FILTRO BIMESTRE ESCOLAR
        # ===============================
        if bimestre == "1":
            meses = ("02","03","04")

        elif bimestre == "2":
            meses = ("05","06")

        elif bimestre == "3":
            meses = ("08","09")

        else:
            meses = ("10","11","12")

        # ===============================
        # BUSCAR PRESENÇAS
        # ===============================
        placeholders = ",".join(["?"] * len(meses))

        query = f"""
        SELECT valor,data
        FROM presenca
        WHERE professor=%s
        AND disciplina=%s
        AND turma=%s
        AND aluno=%s
        AND substr(data,6,2) IN ({placeholders})
        ORDER BY data
        """

        c.execute(query,(professor,disciplina,turma,aluno,*meses))

        lista_presencas = c.fetchall()

        faltas = 0
        presencas_txt = ""

        for valor,data in lista_presencas:

            if valor == "F":
                faltas += 1
                presencas_txt += "F "
            else:
                presencas_txt += "P "

        # ===============================
        # MEDIA
        # ===============================
        media = (
            (p1*0.3)+
            (p2*0.3)+
            (trab*0.1333)+
            (part*0.1333)+
            (tarefa*0.1333)
        )

        dados.append([
            aluno,
            p1,
            p2,
            trab,
            part,
            tarefa,
            presencas_txt.strip(),
            faltas,
            round(media,1)
        ])

    tabela = Table(dados)
    tabela.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.grey),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('FONTSIZE',(0,0),(-1,-1),8)
    ]))

    elementos.append(tabela)

    caminho = "relatorio.pdf"

    doc = SimpleDocTemplate(caminho, pagesize=A4)
    doc.build(elementos)

    conn.close()

    return send_file(
        caminho,
        as_attachment=True,
        download_name="Relatorio.pdf"
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)