import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import json
import os


class TelaPresenca(tk.Toplevel):

    def __init__(self, master, usuario):
        super().__init__(master)

        self.usuario = usuario

        self.title("Chamada / Presença")
        self.geometry("500x600")

        # DATA
        tk.Label(self, text="Data da chamada").pack(pady=5)

        self.data = DateEntry(self, date_pattern="dd/mm/yyyy")
        self.data.pack(pady=5)

        # DISCIPLINA
        tk.Label(self, text="Disciplina").pack()
        self.lista_disc = tk.Listbox(self, height=5, exportselection=False)
        self.lista_disc.pack()

        # TURMA
        tk.Label(self, text="Turma").pack()
        self.lista_turma = tk.Listbox(self, height=5, exportselection=False)
        self.lista_turma.pack()

        # FRAME CHAMADA
        tk.Label(self, text="Chamada").pack(pady=5)

        self.frame_lista = tk.Frame(self)
        self.frame_lista.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.frame_lista)
        self.scroll = tk.Scrollbar(self.frame_lista, orient="vertical", command=self.canvas.yview)

        self.frame_alunos = tk.Frame(self.canvas)

        self.frame_alunos.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.frame_alunos, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")

        # BOTÃO SALVAR (AGORA VISÍVEL)
        tk.Button(
            self,
            text="Salvar Presença",
            width=20,
            bg="#4CAF50",
            fg="white",
            command=self.salvar
        ).pack(pady=10)

        self.checks = {}

        self.carregar_disciplinas()

        self.lista_disc.bind("<<ListboxSelect>>", self.carregar_turmas)
        self.lista_turma.bind("<<ListboxSelect>>", self.carregar_alunos)

    # pasta do professor
    def pasta(self):
        pasta = f"dados/professores/{self.usuario}"
        os.makedirs(pasta, exist_ok=True)
        return pasta

    # alunos
    def caminho_alunos(self):
        return f"{self.pasta()}/alunos.json"

    # presença
    def caminho_presenca(self):
        return f"{self.pasta()}/presenca.json"

    # carregar disciplinas
    def carregar_disciplinas(self):

        arquivo = f"{self.pasta()}/disciplinas.json"

        if not os.path.exists(arquivo):
            return

        with open(arquivo, "r") as f:
            dados = json.load(f)

        self.lista_disc.delete(0, tk.END)

        for d in dados:
            self.lista_disc.insert(tk.END, d)

    # carregar turmas
    def carregar_turmas(self, event=None):

        self.lista_turma.delete(0, tk.END)

        sel = self.lista_disc.curselection()

        if not sel:
            return

        disciplina = self.lista_disc.get(sel[0])

        arquivo = f"{self.pasta()}/turmas.json"

        if not os.path.exists(arquivo):
            return

        with open(arquivo, "r") as f:
            dados = json.load(f)

        turmas = dados.get(disciplina, [])

        for t in turmas:
            self.lista_turma.insert(tk.END, t)

    # carregar alunos
    def carregar_alunos(self, event=None):

        for widget in self.frame_alunos.winfo_children():
            widget.destroy()

        self.checks.clear()

        disc_sel = self.lista_disc.curselection()
        turma_sel = self.lista_turma.curselection()

        if not disc_sel or not turma_sel:
            return

        disciplina = self.lista_disc.get(disc_sel[0])
        turma = self.lista_turma.get(turma_sel[0])

        arquivo = self.caminho_alunos()

        if not os.path.exists(arquivo):
            return

        with open(arquivo, "r") as f:
            dados = json.load(f)

        alunos = dados.get(disciplina, {}).get(turma, [])

        for aluno in alunos:

            var = tk.BooleanVar()

            chk = tk.Checkbutton(
                self.frame_alunos,
                text=aluno,
                variable=var,
                anchor="w",
                width=40
            )

            chk.pack(anchor="w")

            self.checks[aluno] = var

    # SALVAR CHAMADA
    def salvar(self):

        data = self.data.get()

        disc_sel = self.lista_disc.curselection()
        turma_sel = self.lista_turma.curselection()

        if not disc_sel or not turma_sel:

            messagebox.showwarning(
                "Aviso",
                "Selecione disciplina e turma"
            )

            return

        disciplina = self.lista_disc.get(disc_sel[0])
        turma = self.lista_turma.get(turma_sel[0])

        arquivo = self.caminho_presenca()

        if os.path.exists(arquivo):

            with open(arquivo, "r") as f:
                dados = json.load(f)

        else:
            dados = {}

        dados.setdefault(disciplina, {})
        dados[disciplina].setdefault(turma, {})
        dados[disciplina][turma].setdefault(data, {})

        for aluno, var in self.checks.items():

            dados[disciplina][turma][data][aluno] = var.get()

        with open(arquivo, "w") as f:
            json.dump(dados, f, indent=4)

        messagebox.showinfo(
            "Sucesso",
            "Presença salva com sucesso!"
        )