import tkinter as tk
from tkinter import messagebox
import json
import os


class TelaNotas(tk.Toplevel):

    def __init__(self, master, usuario):
        super().__init__(master)

        self.usuario = usuario

        self.title("Lançamento de Notas")
        self.geometry("1000x600")

        # DISCIPLINA
        tk.Label(self, text="Disciplina").pack()
        self.lista_disc = tk.Listbox(self, height=4, exportselection=False)
        self.lista_disc.pack()

        # TURMA
        tk.Label(self, text="Turma").pack()
        self.lista_turma = tk.Listbox(self, height=4, exportselection=False)
        self.lista_turma.pack()

        # BIMESTRE
        tk.Label(self, text="Bimestre").pack()

        self.bimestre = tk.StringVar()

        self.combo = tk.OptionMenu(
            self,
            self.bimestre,
            "1º Bimestre",
            "2º Bimestre",
            "3º Bimestre",
            "4º Bimestre",
            command=self.trocar_bimestre
        )
        self.combo.pack(pady=5)

        # FRAME PRINCIPAL
        self.frame = tk.Frame(self)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        # CABEÇALHO
        headers = [
            "Aluno",
            "Avaliação 1",
            "Avaliação 2",
            "Participação",
            "Rendimento",
            "Comportamento",
            "Média"
        ]

        for col, texto in enumerate(headers):
            tk.Label(
                self.frame,
                text=texto,
                font=("Arial", 10, "bold"),
                width=15
            ).grid(row=0, column=col, padx=5, pady=5)

        # FRAME ALUNOS
        self.frame_alunos = tk.Frame(self.frame)
        self.frame_alunos.grid(row=1, column=0, columnspan=7)

        tk.Button(self, text="Salvar Notas", command=self.salvar).pack(pady=10)

        self.campos = {}

        self.carregar_disciplinas()

        self.lista_disc.bind("<<ListboxSelect>>", self.carregar_turmas)
        self.lista_turma.bind("<<ListboxSelect>>", self.carregar_alunos)

    def pasta(self):
        pasta = f"dados/professores/{self.usuario}"
        os.makedirs(pasta, exist_ok=True)
        return pasta

    def caminho_alunos(self):
        return f"{self.pasta()}/alunos.json"

    def caminho_notas(self):
        return f"{self.pasta()}/notas.json"

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

    def trocar_bimestre(self, event=None):
        self.carregar_alunos()

    def calcular_media(self, n1, n2, p, r, c):
        try:
            media_av = (float(n1) + float(n2)) / 2
            media_comp = (float(p) + float(r) + float(c)) / 3
            return round((media_av * 0.6) + (media_comp * 0.4), 1)
        except:
            return ""

    def carregar_alunos(self, event=None):

        for w in self.frame_alunos.winfo_children():
            w.destroy()

        self.campos.clear()

        disc_sel = self.lista_disc.curselection()
        turma_sel = self.lista_turma.curselection()

        if not disc_sel or not turma_sel:
            return

        disciplina = self.lista_disc.get(disc_sel[0])
        turma = self.lista_turma.get(turma_sel[0])
        bimestre = self.bimestre.get()

        if not os.path.exists(self.caminho_alunos()):
            return

        with open(self.caminho_alunos(), "r") as f:
            dados = json.load(f)

        alunos = dados.get(disciplina, {}).get(turma, [])

        notas = {}
        if os.path.exists(self.caminho_notas()):
            with open(self.caminho_notas(), "r") as f:
                dados_notas = json.load(f)

            notas = dados_notas.get(disciplina, {}).get(turma, {}).get(bimestre, {})

        for i, aluno in enumerate(alunos):

            linha = i + 1

            tk.Label(self.frame_alunos, text=aluno, width=15).grid(row=linha, column=0)

            av1 = tk.Entry(self.frame_alunos, width=10)
            av1.grid(row=linha, column=1)

            av2 = tk.Entry(self.frame_alunos, width=10)
            av2.grid(row=linha, column=2)

            part = tk.Entry(self.frame_alunos, width=10)
            part.grid(row=linha, column=3)

            rend = tk.Entry(self.frame_alunos, width=10)
            rend.grid(row=linha, column=4)

            comp = tk.Entry(self.frame_alunos, width=10)
            comp.grid(row=linha, column=5)

            media = tk.Label(self.frame_alunos, text="", width=10)
            media.grid(row=linha, column=6)

            if aluno in notas:
                n = notas[aluno]

                if "avaliacao1" in n:
                    av1.insert(0, n["avaliacao1"])

                if "avaliacao2" in n:
                    av2.insert(0, n["avaliacao2"])

                if "participacao" in n:
                    part.insert(0, n["participacao"])

                if "rendimento" in n:
                    rend.insert(0, n["rendimento"])

                if "comportamento" in n:
                    comp.insert(0, n["comportamento"])

                if "media" in n:
                    media.config(text=n["media"])

            def calcular(e, a1=av1, a2=av2, p=part, r=rend, c=comp, m=media):
                valor = self.calcular_media(
                    a1.get() or 0,
                    a2.get() or 0,
                    p.get() or 0,
                    r.get() or 0,
                    c.get() or 0
                )
                m.config(text=valor)

            av1.bind("<KeyRelease>", calcular)
            av2.bind("<KeyRelease>", calcular)
            part.bind("<KeyRelease>", calcular)
            rend.bind("<KeyRelease>", calcular)
            comp.bind("<KeyRelease>", calcular)

            self.campos[aluno] = (av1, av2, part, rend, comp, media)

    def salvar(self):

        if not self.bimestre.get():
            messagebox.showwarning("Aviso", "Selecione o bimestre")
            return

        disc_sel = self.lista_disc.curselection()
        turma_sel = self.lista_turma.curselection()

        if not disc_sel or not turma_sel:
            messagebox.showwarning("Aviso", "Selecione disciplina e turma")
            return

        disciplina = self.lista_disc.get(disc_sel[0])
        turma = self.lista_turma.get(turma_sel[0])
        bimestre = self.bimestre.get()

        if os.path.exists(self.caminho_notas()):
            with open(self.caminho_notas(), "r") as f:
                dados = json.load(f)
        else:
            dados = {}

        dados.setdefault(disciplina, {})
        dados[disciplina].setdefault(turma, {})
        dados[disciplina][turma].setdefault(bimestre, {})

        for aluno, (av1, av2, part, rend, comp, media_label) in self.campos.items():

            dados[disciplina][turma][bimestre].setdefault(aluno, {})

            n = dados[disciplina][turma][bimestre][aluno]

            if av1.get():
                n["avaliacao1"] = float(av1.get())

            if av2.get():
                n["avaliacao2"] = float(av2.get())

            if part.get():
                n["participacao"] = float(part.get())

            if rend.get():
                n["rendimento"] = float(rend.get())

            if comp.get():
                n["comportamento"] = float(comp.get())

            media = self.calcular_media(
                n.get("avaliacao1", 0),
                n.get("avaliacao2", 0),
                n.get("participacao", 0),
                n.get("rendimento", 0),
                n.get("comportamento", 0)
            )

            n["media"] = media

        with open(self.caminho_notas(), "w") as f:
            json.dump(dados, f, indent=4)

        messagebox.showinfo("Sucesso", "Notas salvas com sucesso")