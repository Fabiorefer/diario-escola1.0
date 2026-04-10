import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import json
import os


class TelaConteudo(tk.Toplevel):

    def __init__(self, master, usuario):
        super().__init__(master)

        self.usuario = usuario

        self.title("Resumo de Conteúdos")
        self.geometry("700x600")

        # DATA
        tk.Label(self, text="Data").pack()

        self.data = DateEntry(self, date_pattern="dd/mm/yyyy")
        self.data.pack(pady=5)

        # DISCIPLINA
        tk.Label(self, text="Disciplina").pack()

        self.lista_disc = tk.Listbox(self, height=4, exportselection=False)
        self.lista_disc.pack(fill="x", padx=20)

        # TURMA
        tk.Label(self, text="Turma").pack()

        self.lista_turma = tk.Listbox(self, height=4, exportselection=False)
        self.lista_turma.pack(fill="x", padx=20)

        # TEXTO
        tk.Label(self, text="Resumo do Conteúdo / Atividades").pack(pady=5)

        self.texto = tk.Text(self, height=15)
        self.texto.pack(fill="both", expand=True, padx=20)

        tk.Button(self, text="Salvar", command=self.salvar).pack(pady=10)

        self.carregar_disciplinas()

        self.lista_disc.bind("<<ListboxSelect>>", self.carregar_turmas)
        self.lista_turma.bind("<<ListboxSelect>>", self.carregar_conteudo)
        self.data.bind("<<DateEntrySelected>>", self.carregar_conteudo)

    def pasta(self):
        pasta = f"dados/professores/{self.usuario}"
        os.makedirs(pasta, exist_ok=True)
        return pasta

    def caminho(self):
        return f"{self.pasta()}/conteudo.json"

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

        sel = self.lista_disc.curselection()

        if not sel:
            return

        disciplina = self.lista_disc.get(sel[0])

        arquivo = f"{self.pasta()}/turmas.json"

        if not os.path.exists(arquivo):
            return

        with open(arquivo, "r") as f:
            dados = json.load(f)

        for t in dados.get(disciplina, []):
            self.lista_turma.insert(tk.END, t)

    def carregar_conteudo(self, event=None):

        self.texto.delete("1.0", tk.END)

        disc_sel = self.lista_disc.curselection()
        turma_sel = self.lista_turma.curselection()

        if not disc_sel or not turma_sel:
            return

        disciplina = self.lista_disc.get(disc_sel[0])
        turma = self.lista_turma.get(turma_sel[0])
        data = self.data.get()

        if not os.path.exists(self.caminho()):
            return

        with open(self.caminho(), "r") as f:
            dados = json.load(f)

        conteudo = (
            dados
            .get(disciplina, {})
            .get(turma, {})
            .get(data, "")
        )

        self.texto.insert(tk.END, conteudo)

    def salvar(self):

        disc_sel = self.lista_disc.curselection()
        turma_sel = self.lista_turma.curselection()

        if not disc_sel or not turma_sel:
            messagebox.showwarning("Aviso", "Selecione disciplina e turma")
            return

        disciplina = self.lista_disc.get(disc_sel[0])
        turma = self.lista_turma.get(turma_sel[0])
        data = self.data.get()

        texto = self.texto.get("1.0", tk.END).strip()

        if os.path.exists(self.caminho()):
            with open(self.caminho(), "r") as f:
                dados = json.load(f)
        else:
            dados = {}

        dados.setdefault(disciplina, {})
        dados[disciplina].setdefault(turma, {})
        dados[disciplina][turma][data] = texto

        with open(self.caminho(), "w") as f:
            json.dump(dados, f, indent=4)

        messagebox.showinfo("Sucesso", "Conteúdo salvo com sucesso")