import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os


class TelaAlunos(tk.Toplevel):
    def __init__(self, master, usuario):
        super().__init__(master)

        self.usuario = usuario

        self.title("Alunos")
        self.geometry("450x500")

        tk.Label(self, text="Disciplina").pack()
        self.lista_disc = tk.Listbox(
            self, height=5,
            selectmode=tk.SINGLE,
            exportselection=False
        )
        self.lista_disc.pack()

        tk.Label(self, text="Turma").pack()
        self.lista_turma = tk.Listbox(
            self, height=5,
            selectmode=tk.SINGLE,
            exportselection=False
        )
        self.lista_turma.pack()

        tk.Label(self, text="Alunos").pack()
        self.lista_alunos = tk.Listbox(
            self, width=30,
            height=10,
            selectmode=tk.SINGLE,
            exportselection=False
        )
        self.lista_alunos.pack(pady=5)

        tk.Button(self, text="Adicionar Aluno", command=self.adicionar).pack(pady=5)
        tk.Button(self, text="Excluir Aluno", command=self.excluir).pack(pady=5)

        self.carregar_disciplinas()

        self.lista_disc.bind("<<ListboxSelect>>", self.carregar_turmas)
        self.lista_turma.bind("<<ListboxSelect>>", self.carregar_alunos)

    def pasta(self):
        pasta = f"dados/professores/{self.usuario}"
        os.makedirs(pasta, exist_ok=True)
        return pasta

    def caminho(self):
        return f"{self.pasta()}/alunos.json"

    def carregar_disciplinas(self):
        arquivo = f"{self.pasta()}/disciplinas.json"

        if not os.path.exists(arquivo):
            return

        with open(arquivo, "r") as f:
            dados = json.load(f)

        self.lista_disc.delete(0, tk.END)

        for d in dados:
            self.lista_disc.insert(tk.END, d)

    def carregar_turmas(self, event=None):
        self.lista_turma.delete(0, tk.END)
        self.lista_alunos.delete(0, tk.END)

        selecionado = self.lista_disc.curselection()
        if not selecionado:
            return

        disciplina = self.lista_disc.get(selecionado[0])

        arquivo = f"{self.pasta()}/turmas.json"

        if not os.path.exists(arquivo):
            return

        with open(arquivo, "r") as f:
            dados = json.load(f)

        turmas = dados.get(disciplina, [])

        for t in turmas:
            self.lista_turma.insert(tk.END, t)

    def carregar_alunos(self, event=None):
        self.lista_alunos.delete(0, tk.END)

        disc_sel = self.lista_disc.curselection()
        turma_sel = self.lista_turma.curselection()

        if not disc_sel or not turma_sel:
            return

        disciplina = self.lista_disc.get(disc_sel[0])
        turma = self.lista_turma.get(turma_sel[0])

        arquivo = self.caminho()

        if not os.path.exists(arquivo):
            return

        with open(arquivo, "r") as f:
            dados = json.load(f)

        alunos = dados.get(disciplina, {}).get(turma, [])

        for a in alunos:
            self.lista_alunos.insert(tk.END, a)

    def adicionar(self):
        disc_sel = self.lista_disc.curselection()
        turma_sel = self.lista_turma.curselection()

        if not disc_sel or not turma_sel:
            messagebox.showwarning("Aviso", "Selecione disciplina e turma")
            return

        disciplina = self.lista_disc.get(disc_sel[0])
        turma = self.lista_turma.get(turma_sel[0])

        aluno = simpledialog.askstring("Aluno", "Nome do aluno:")

        if not aluno:
            return

        arquivo = self.caminho()

        if os.path.exists(arquivo):
            with open(arquivo, "r") as f:
                dados = json.load(f)
        else:
            dados = {}

        dados.setdefault(disciplina, {})
        dados[disciplina].setdefault(turma, [])

        if aluno not in dados[disciplina][turma]:
            dados[disciplina][turma].append(aluno)

        with open(arquivo, "w") as f:
            json.dump(dados, f, indent=4)

        self.carregar_alunos()

    def excluir(self):
        disc_sel = self.lista_disc.curselection()
        turma_sel = self.lista_turma.curselection()
        aluno_sel = self.lista_alunos.curselection()

        if not disc_sel or not turma_sel or not aluno_sel:
            return

        disciplina = self.lista_disc.get(disc_sel[0])
        turma = self.lista_turma.get(turma_sel[0])
        aluno = self.lista_alunos.get(aluno_sel[0])

        arquivo = self.caminho()

        with open(arquivo, "r") as f:
            dados = json.load(f)

        dados[disciplina][turma].remove(aluno)

        with open(arquivo, "w") as f:
            json.dump(dados, f, indent=4)

        self.carregar_alunos()