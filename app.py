from flask import Flask, render_template, request, redirect, session, url_for
from banco import get_db

app = Flask(__name__)
app.secret_key = "diario_secret"

# ===============================
# PROTEÇÃO LOGIN
# ===============================
def verificar_login():
    return "usuario" in session

# ===============================
# LOGIN
# ===============================
@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        senha = request.form["senha"]

        db = get_db()

        prof = db.professores.find_one({
            "usuario": usuario,
            "senha": senha
        })

        if prof:
            session["usuario"] = usuario
            return redirect("/menu")
        else:
            return render_template("login.html", erro="Usuário ou senha inválidos")

    return render_template("login.html")

# ===============================
# MENU
# ===============================
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

    db = get_db()
    professor = session["usuario"]

    sucesso = False

    if request.method == "POST":

        nova = request.form.get("nova_disciplina")

        if nova:
            db.disciplinas.insert_one({
                "professor": professor,
                "disciplina": nova
            })
            sucesso = True

    lista = db.disciplinas.find({"professor": professor})
    disciplinas = [d["disciplina"] for d in lista]

    return render_template(
        "disciplinas.html",
        disciplinas=disciplinas,
        sucesso=sucesso
    )

#================================
#TURMAS
#================================
@app.route("/turmas", methods=["GET","POST"])
def turmas():

    if not verificar_login():
        return redirect("/")

    db = get_db()
    professor = session["usuario"]

    sucesso = False

    if request.method == "POST":

        disciplina = request.form["disciplina"]
        turma = request.form["turma"]

        # evita duplicar turma
        existe = db.turmas.find_one({
            "professor": professor,
            "disciplina": disciplina,
            "turma": turma
        })

        if not existe:
            db.turmas.insert_one({
                "professor": professor,
                "disciplina": disciplina,
                "turma": turma
            })
            sucesso = True

    disciplinas = list(db.disciplinas.find({"professor": professor}))

    turmas = list(db.turmas.find({"professor": professor}))

    return render_template(
        "turmas.html",
        disciplinas=disciplinas,
        turmas=turmas,
        sucesso=sucesso
    )

# ===============================
# ALUNOS
# ===============================
@app.route("/alunos", methods=["GET","POST"])
def alunos():

    if not verificar_login():
        return redirect("/")

    db = get_db()
    professor = session["usuario"]

    sucesso = False

    if request.method == "POST":

        db.alunos.insert_one({
            "professor": professor,
            "disciplina": request.form["disciplina"],
            "turma": request.form["turma"],
            "aluno": request.form["aluno"]
        })

        sucesso = True

    disciplinas = list(db.disciplinas.find({"professor": professor}))
    turmas = db.alunos.distinct("turma", {"professor": professor})
    alunos = list(db.alunos.find({"professor": professor, "aluno": {"$ne": ""}}))

    return render_template(
        "alunos.html",
        disciplinas=disciplinas,
        turmas=turmas,
        alunos=alunos,
        sucesso=sucesso
    )

# ===============================
# PRESENÇA
# ===============================
@app.route("/presenca", methods=["GET","POST"])
def presenca():

    if not verificar_login():
        return redirect("/")

    db = get_db()
    professor = session["usuario"]

    disciplina = request.values.get("disciplina")
    turma = request.values.get("turma")
    data = request.values.get("data")

    # carregar disciplinas e turmas
    disciplinas = list(db.disciplinas.find({"professor": professor}))
    turmas = db.turmas.distinct("turma", {"professor": professor})

    alunos = []
    presencas = {}
    salvo = False

    if disciplina and turma:

        alunos = list(db.alunos.find({
            "professor": professor,
            "disciplina": disciplina,
            "turma": turma
        }))

    # SALVAR
    if request.method == "POST":

        db.presenca.delete_many({
            "professor": professor,
            "disciplina": disciplina,
            "turma": turma,
            "data": data
        })

        for a in alunos:

            nome = a["aluno"]
            valor = request.form.get("presenca_"+nome) or "F"

            db.presenca.insert_one({
                "professor": professor,
                "disciplina": disciplina,
                "turma": turma,
                "data": data,
                "aluno": nome,
                "valor": valor
            })

        salvo = True

    # CARREGAR PRESENÇA
    if disciplina and turma and data:

        lista = db.presenca.find({
            "professor": professor,
            "disciplina": disciplina,
            "turma": turma,
            "data": data
        })

        for p in lista:
            presencas[p["aluno"]] = p["valor"]

    return render_template(
        "presenca.html",
        disciplinas=disciplinas,
        turmas=turmas,
        disciplina=disciplina,
        turma=turma,
        data=data,
        alunos=alunos,
        presencas=presencas,
        salvo=salvo
    )

# ===============================
# NOTAS
# ===============================
@app.route("/notas", methods=["GET","POST"])
def notas():

    if not verificar_login():
        return redirect("/")

    db = get_db()
    professor = session["usuario"]

    disciplina = request.values.get("disciplina")
    turma = request.values.get("turma")
    bimestre = request.values.get("bimestre")

    disciplinas = list(db.disciplinas.find({"professor": professor}))
    turmas = db.turmas.distinct("turma", {"professor": professor})

    alunos = []
    notas_dict = {}
    salvo = False

    if disciplina and turma:
        alunos = list(db.alunos.find({
            "professor": professor,
            "disciplina": disciplina,
            "turma": turma
        }))

    # carregar notas
    if disciplina and turma and bimestre:

        lista = db.notas.find({
            "professor": professor,
            "disciplina": disciplina,
            "turma": turma,
            "bimestre": bimestre
        })

        for n in lista:
            notas_dict[n["aluno"]] = n

    # salvar
    if request.method == "POST":

        db.notas.delete_many({
            "professor": professor,
            "disciplina": disciplina,
            "turma": turma,
            "bimestre": bimestre
        })

        for a in alunos:

            nome = a["aluno"]

            db.notas.insert_one({
                "professor": professor,
                "disciplina": disciplina,
                "turma": turma,
                "bimestre": bimestre,
                "aluno": nome,
                "p1": request.form.get("p1_"+nome) or 0,
                "p2": request.form.get("p2_"+nome) or 0,
                "trab": request.form.get("trab_"+nome) or 0,
                "part": request.form.get("part_"+nome) or 0,
                "tarefa": request.form.get("tarefa_"+nome) or 0
            })

        salvo = True

    return render_template(
        "notas.html",
        disciplinas=disciplinas,
        turmas=turmas,
        alunos=alunos,
        notas=notas_dict,
        disciplina=disciplina,
        turma=turma,
        bimestre=bimestre,
        salvo=salvo
    )

#================================
#CONTEUDOS
#================================
@app.route("/conteudos", methods=["GET","POST"])
def conteudos():

    if not verificar_login():
        return redirect("/")

    db = get_db()
    professor = session["usuario"]

    disciplina = request.values.get("disciplina")
    turma = request.values.get("turma")
    data = request.values.get("data")

    disciplinas = list(db.disciplinas.find({"professor": professor}))
    turmas = db.turmas.distinct("turma", {"professor": professor})

    conteudo_atual = ""
    lista_conteudos = []
    salvo = False

    # carregar conteúdo atual
    if disciplina and turma and data:

        c = db.conteudos.find_one({
            "professor": professor,
            "disciplina": disciplina,
            "turma": turma,
            "data": data
        })

        if c:
            conteudo_atual = c["conteudo"]

    # salvar
    if request.method == "POST":

        conteudo = request.form.get("conteudo")

        db.conteudos.delete_many({
            "professor": professor,
            "disciplina": disciplina,
            "turma": turma,
            "data": data
        })

        db.conteudos.insert_one({
            "professor": professor,
            "disciplina": disciplina,
            "turma": turma,
            "data": data,
            "conteudo": conteudo
        })

        salvo = True

    # listar conteúdos
    if disciplina and turma:

        lista_conteudos = list(db.conteudos.find({
            "professor": professor,
            "disciplina": disciplina,
            "turma": turma
        }).sort("data", -1))

    return render_template(
        "conteudos.html",
        disciplinas=disciplinas,
        turmas=turmas,
        disciplina=disciplina,
        turma=turma,
        data=data,
        conteudo_atual=conteudo_atual,
        conteudos=lista_conteudos,
        salvo=salvo
    )

#================================
#RELATÓRIOS
#================================
@app.route("/relatorio_pdf")
def relatorio_pdf():

    if not verificar_login():
        return redirect("/")

    db = get_db()
    professor = session["usuario"]

    disciplina = request.args.get("disciplina")
    turma = request.args.get("turma")
    bimestre = request.args.get("bimestre")

    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph(f"Professor: {professor}", styles['Heading2']))
    elementos.append(Paragraph(f"Disciplina: {disciplina}", styles['Normal']))
    elementos.append(Paragraph(f"Turma: {turma}", styles['Normal']))
    elementos.append(Paragraph(f"Bimestre: {bimestre}", styles['Normal']))
    elementos.append(Spacer(1,12))

    dados = [["Aluno","P1","P2","Trab","Part","Tarefa","Faltas","Média"]]

    notas = list(db.notas.find({
        "professor": professor,
        "disciplina": disciplina,
        "turma": turma,
        "bimestre": bimestre
    }))

    for n in notas:

        aluno = n["aluno"]

        p1 = float(n.get("p1",0))
        p2 = float(n.get("p2",0))
        trab = float(n.get("trab",0))
        part = float(n.get("part",0))
        tarefa = float(n.get("tarefa",0))

        # calcular faltas
        faltas = db.presenca.count_documents({
            "professor": professor,
            "disciplina": disciplina,
            "turma": turma,
            "aluno": aluno,
            "valor": "F"
        })

        media = (
            (p1*0.3)+
            (p2*0.3)+
            (trab*0.1333)+
            (part*0.1333)+
            (tarefa*0.1333)
        )

        dados.append([
            aluno, p1, p2, trab, part, tarefa,
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

    return send_file(
        caminho,
        as_attachment=True,
        download_name="Relatorio.pdf"
    )

# ===============================
# LOGOUT
# ===============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ===============================
# RODAR
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
