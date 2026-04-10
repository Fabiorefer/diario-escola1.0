import sqlite3

def conectar():
    return sqlite3.connect("diario.db")


def criar_banco():

    conn = conectar()
    c = conn.cursor()

    # PROFESSOR
    c.execute("""
    CREATE TABLE IF NOT EXISTS professores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT
    )
    """)

    # ALUNOS
    c.execute("""
    CREATE TABLE IF NOT EXISTS alunos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        professor TEXT,
        disciplina TEXT,
        turma TEXT,
        aluno TEXT
    )
    """)

    # CONTEUDOS
    c.execute("""
    CREATE TABLE IF NOT EXISTS conteudos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        professor TEXT,
        disciplina TEXT,
        turma TEXT,
        data TEXT,
        conteudo TEXT
    )
    """)

    # PRESENCA
    c.execute("""
    CREATE TABLE IF NOT EXISTS presenca (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        professor TEXT,
        disciplina TEXT,
        turma TEXT,
        data TEXT,
        aluno TEXT,
        valor TEXT
    )
    """)

    # NOTAS (NOVO MODELO)
    c.execute("""
    CREATE TABLE IF NOT EXISTS notas (
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

    conn.commit()
    conn.close()