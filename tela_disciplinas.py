import tkinter as tk
from tkinter import messagebox
import json
import os

class TelaDisciplinas(tk.Toplevel):
    def __init__(self, master, usuario):
        super().__init__(master)

        self.usuario = usuario  # professor logado

        self.title("Disciplinas")
        self.geometry("350x400")

        tk.Label(self, text="Escolha a Disciplina", font=("Arial", 14)).pack(pady=10)

        self.disciplinas = [
            "Matemática",
            "Português",
            "Ciências",
            "Biologia",
            "Química",
            "Redação",
            "Inglês",
            "Pensamento Computacional",
            "BENE"
        ]

        self.lista = tk.Listbox(self, width=30, height=15)
        self.lista.pack(pady=10)

        for d in self.disciplinas:
            self.lista.insert(tk.END, d)

        tk.Button(self, text="Selecionar", command=self.salvar).pack(pady=5)

    def salvar(self):
        selecionado = self.lista.curselection()

        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma disciplina")
            return

        disciplina = self.lista.get(selecionado)

        # pasta do professor
        pasta = f"dados/professores/{self.usuario}"
        os.makedirs(pasta, exist_ok=True)

        arquivo = f"{pasta}/disciplinas.json"

        # carrega existentes
        if os.path.exists(arquivo):
            with open(arquivo, "r") as f:
                dados = json.load(f)
        else:
            dados = []

        # evita duplicado
        if disciplina not in dados:
            dados.append(disciplina)

        # salva
        with open(arquivo, "w") as f:
            json.dump(dados, f, indent=4)

        messagebox.showinfo("Sucesso", f"Disciplina {disciplina} salva!")