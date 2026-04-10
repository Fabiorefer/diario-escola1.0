import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os


class TelaTurmas(tk.Toplevel):
    def __init__(self, master, usuario):
        super().__init__(master)

        self.usuario = usuario

        self.title("Turmas")
        self.geometry("400x450")

        tk.Label(self, text="Disciplina", font=("Arial", 12)).pack()

        self.combo = tk.Listbox(self, height=5)
        self.combo.pack(pady=5)

        tk.Label(self, text="Turmas", font=("Arial", 12)).pack()

        self.lista = tk.Listbox(self, width=30, height=10)
        self.lista.pack(pady=5)

        tk.Button(self, text="Criar Turma", command=self.criar_turma).pack(pady=5)
        tk.Button(self, text="Excluir Turma", command=self.excluir_turma).pack(pady=5)

        self.carregar_disciplinas()

        self.combo.bind("<<ListboxSelect>>", self.carregar_turmas)

    def caminho_arquivo(self):
        pasta = f"dados/professores/{self.usuario}"
        os.makedirs(pasta, exist_ok=True)
        return f"{pasta}/turmas.json"

    def carregar_disciplinas(self):
        arquivo = f"dados/professores/{self.usuario}/disciplinas.json"

        if not os.path.exists(arquivo):
            return

        with open(arquivo, "r") as f:
            disciplinas = json.load(f)

        for d in disciplinas:
            self.combo.insert(tk.END, d)

    def carregar_turmas(self, event=None):
        self.lista.delete(0, tk.END)

        selecionado = self.combo.curselection()
        if not selecionado:
            return

        disciplina = self.combo.get(selecionado)

        arquivo = self.caminho_arquivo()

        if not os.path.exists(arquivo):
            return

        with open(arquivo, "r") as f:
            dados = json.load(f)

        turmas = dados.get(disciplina, [])

        for t in turmas:
            self.lista.insert(tk.END, t)

    def criar_turma(self):
        selecionado = self.combo.curselection()

        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma disciplina")
            return

        disciplina = self.combo.get(selecionado)

        turma = simpledialog.askstring("Nova Turma", "Nome da turma:")

        if not turma:
            return

        arquivo = self.caminho_arquivo()

        if os.path.exists(arquivo):
            with open(arquivo, "r") as f:
                dados = json.load(f)
        else:
            dados = {}

        if disciplina not in dados:
            dados[disciplina] = []

        if turma not in dados[disciplina]:
            dados[disciplina].append(turma)

        with open(arquivo, "w") as f:
            json.dump(dados, f, indent=4)

        self.carregar_turmas()

    def excluir_turma(self):
        selecionado_disc = self.combo.curselection()
        selecionado_turma = self.lista.curselection()

        if not selecionado_disc or not selecionado_turma:
            return

        disciplina = self.combo.get(selecionado_disc)
        turma = self.lista.get(selecionado_turma)

        arquivo = self.caminho_arquivo()

        with open(arquivo, "r") as f:
            dados = json.load(f)

        dados[disciplina].remove(turma)

        with open(arquivo, "w") as f:
            json.dump(dados, f, indent=4)

        self.carregar_turmas()