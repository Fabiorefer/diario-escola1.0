import tkinter as tk

class Dashboard(tk.Toplevel):
    def __init__(self, master, usuario):
        super().__init__(master)

        self.usuario = usuario

        self.title("Diário de Classe")
        self.geometry("400x400")

        tk.Label(self, text=f"Bem-vindo, {usuario}", font=("Arial", 14)).pack(pady=10)

        tk.Button(self, text="Disciplinas", width=25, command=self.abrir_disciplinas).pack(pady=5)

        tk.Button(self, text="Turmas", width=25, command=self.abrir_turmas).pack(pady=5)

        tk.Button(self, text="Alunos", width=25, command=self.abrir_alunos).pack(pady=5)

        tk.Button(self, text="Presença", width=25, command=self.abrir_presenca).pack(pady=5)

        tk.Button(self, text="Notas", width=25, command=self.abrir_notas).pack(pady=5)
        
        tk.Button(self, text="Conteúdo", width=25, command=self.abrir_conteudo).pack(pady=5)

        tk.Button(self, text="Relatório PDF", width=25, command=self.abrir_relatorio).pack(pady=5)

    def abrir_disciplinas(self):
        from telas.tela_disciplinas.tela_disciplinas import TelaDisciplinas
        TelaDisciplinas(self, self.usuario)

    def abrir_turmas(self):
        from telas.tela_turmas.tela_turmas import TelaTurmas
        TelaTurmas(self, self.usuario)

    def abrir_alunos(self):
        from telas.tela_alunos.tela_alunos import TelaAlunos
        TelaAlunos(self, self.usuario)

    def abrir_presenca(self):
        from telas.tela_presenca.tela_presenca import TelaPresenca
        TelaPresenca(self, self.usuario)

    def abrir_notas(self):
        from telas.tela_notas.tela_notas import TelaNotas
        TelaNotas(self, self.usuario)

    def abrir_conteudo(self):
        from telas.tela_conteudo.tela_conteudo import TelaConteudo
        TelaConteudo(self, self.usuario)

    def abrir_relatorio(self):
        from telas.tela_relatorio.tela_relatorio import TelaRelatorio
        TelaRelatorio(self, self.usuario)