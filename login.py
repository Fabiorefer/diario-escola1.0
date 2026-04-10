import tkinter as tk
from tkinter import messagebox
import json
import os


class TelaLogin(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Login - Diário de Classe")
        self.geometry("300x300")

        tk.Label(self, text="Usuário").pack(pady=5)
        self.usuario = tk.Entry(self)
        self.usuario.pack()

        tk.Label(self, text="Senha").pack(pady=5)
        self.senha = tk.Entry(self, show="*")
        self.senha.pack()

        tk.Button(self, text="Entrar", command=self.login).pack(pady=5)
        tk.Button(self, text="Criar Usuário", command=self.abrir_criar_usuario).pack(pady=5)

        self.criar_base()

    def criar_base(self):
        os.makedirs("dados", exist_ok=True)

        if not os.path.exists("dados/professores.json"):
            with open("dados/professores.json", "w") as f:
                json.dump({}, f)

    def criar_banco_professor(self, usuario):

        pasta = f"dados/professores/{usuario}"
        os.makedirs(pasta, exist_ok=True)

        arquivos = [
            "disciplinas.json",
            "turmas.json",
            "alunos.json",
            "notas.json",
            "presenca.json",
            "conteudo.json",
            "relatorio.json"
        ]

        for arq in arquivos:
            caminho = f"{pasta}/{arq}"

            if not os.path.exists(caminho):
                with open(caminho, "w") as f:
                    json.dump([], f)

    def login(self):
        user = self.usuario.get()
        senha = self.senha.get()

        with open("dados/professores.json", "r") as f:
            dados = json.load(f)

        if user in dados and dados[user] == senha:

            self.criar_banco_professor(user)

            messagebox.showinfo("Sucesso", "Login realizado!")

            self.destroy()

            # abrir dashboard
            from dashboard import Dashboard
            Dashboard(user)

        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos")

    def abrir_criar_usuario(self):
        janela = tk.Toplevel(self)
        janela.title("Criar Usuário")
        janela.geometry("250x220")

        tk.Label(janela, text="Novo Usuário").pack(pady=5)
        novo_usuario = tk.Entry(janela)
        novo_usuario.pack()

        tk.Label(janela, text="Senha").pack(pady=5)
        nova_senha = tk.Entry(janela, show="*")
        nova_senha.pack()

        def salvar():
            user = novo_usuario.get()
            senha = nova_senha.get()

            if user == "" or senha == "":
                messagebox.showwarning("Aviso", "Preencha todos os campos")
                return

            with open("dados/professores.json", "r") as f:
                dados = json.load(f)

            if user in dados:
                messagebox.showerror("Erro", "Usuário já existe")
                return

            dados[user] = senha

            with open("dados/professores.json", "w") as f:
                json.dump(dados, f)

            self.criar_banco_professor(user)

            messagebox.showinfo("Sucesso", "Usuário criado com sucesso")
            janela.destroy()

        tk.Button(janela, text="Salvar", command=salvar).pack(pady=10)


if __name__ == "__main__":
    app = TelaLogin()
    app.mainloop()