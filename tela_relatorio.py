import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import cm


class TelaRelatorio(tk.Toplevel):

    def __init__(self, master, usuario):
        super().__init__(master)

        self.usuario = usuario

        self.title("Relatório Diário em PDF")
        self.geometry("400x400")

        tk.Label(self, text="Disciplina").pack()

        self.lista_disc = tk.Listbox(self, height=5, exportselection=False)
        self.lista_disc.pack(fill="x", padx=20)

        tk.Label(self, text="Turma").pack()

        self.lista_turma = tk.Listbox(self, height=5, exportselection=False)
        self.lista_turma.pack(fill="x", padx=20)

        tk.Button(self, text="Gerar PDF", command=self.gerar_pdf).pack(pady=20)

        self.carregar_disciplinas()

        self.lista_disc.bind("<<ListboxSelect>>", self.carregar_turmas)

    def pasta(self):
        pasta = f"dados/professores/{self.usuario}"
        os.makedirs(pasta, exist_ok=True)
        return pasta

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

    def gerar_pdf(self):

        disc_sel = self.lista_disc.curselection()
        turma_sel = self.lista_turma.curselection()

        if not disc_sel or not turma_sel:
            messagebox.showwarning("Aviso", "Selecione disciplina e turma")
            return

        disciplina = self.lista_disc.get(disc_sel[0])
        turma = self.lista_turma.get(turma_sel[0])

        caminho = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            title="Salvar relatório"
        )

        if not caminho:
            return

        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(f"<b>Diário de Classe</b>", styles["Heading1"]))
        story.append(Spacer(1, 10))

        story.append(Paragraph(f"Professor: {self.usuario}", styles["Normal"]))
        story.append(Paragraph(f"Disciplina: {disciplina}", styles["Normal"]))
        story.append(Paragraph(f"Turma: {turma}", styles["Normal"]))

        story.append(Spacer(1, 20))

        # ================= ALUNOS =================

        alunos_arquivo = f"{self.pasta()}/alunos.json"

        if os.path.exists(alunos_arquivo):
            with open(alunos_arquivo, "r") as f:
                alunos = json.load(f)

            lista_alunos = alunos.get(disciplina, {}).get(turma, [])

            story.append(Paragraph("<b>Alunos</b>", styles["Heading2"]))

            for a in lista_alunos:
                story.append(Paragraph(a, styles["Normal"]))

        story.append(Spacer(1, 20))

        # ================= PRESENÇA =================

        presenca_arquivo = f"{self.pasta()}/presenca.json"

        if os.path.exists(presenca_arquivo):

            with open(presenca_arquivo, "r") as f:
                presenca = json.load(f)

            dados = presenca.get(disciplina, {}).get(turma, {})

            story.append(Paragraph("<b>Presença</b>", styles["Heading2"]))

            for data, alunos in dados.items():

                story.append(Paragraph(f"<b>Data: {data}</b>", styles["Normal"]))

                for aluno, presente in alunos.items():

                    status = "Presente" if presente else "Falta"

                    story.append(
                        Paragraph(f"{aluno} - {status}", styles["Normal"])
                    )

                story.append(Spacer(1, 10))

        story.append(Spacer(1, 20))

        # ================= NOTAS =================

        notas_arquivo = f"{self.pasta()}/notas.json"

        if os.path.exists(notas_arquivo):

            with open(notas_arquivo, "r") as f:
                notas = json.load(f)

            dados = notas.get(disciplina, {}).get(turma, {})

            story.append(Paragraph("<b>Notas</b>", styles["Heading2"]))

            for bimestre, alunos in dados.items():

                story.append(
                    Paragraph(f"<b>{bimestre}</b>", styles["Heading3"])
                )

                for aluno, n in alunos.items():

                    av1 = n.get("avaliacao1", "")
                    av2 = n.get("avaliacao2", "")
                    media = n.get("media", "")

                    texto = f"{aluno} - Av1: {av1} | Av2: {av2} | Média: {media}"

                    story.append(Paragraph(texto, styles["Normal"]))

                story.append(Spacer(1, 10))

        story.append(Spacer(1, 20))

        # ================= CONTEÚDO =================

        conteudo_arquivo = f"{self.pasta()}/conteudo.json"

        if os.path.exists(conteudo_arquivo):

            with open(conteudo_arquivo, "r") as f:
                conteudo = json.load(f)

            dados = conteudo.get(disciplina, {}).get(turma, {})

            story.append(Paragraph("<b>Conteúdos das Aulas</b>", styles["Heading2"]))

            for data, texto in dados.items():

                story.append(
                    Paragraph(f"<b>Data: {data}</b>", styles["Normal"])
                )

                story.append(
                    Paragraph(texto.replace("\n", "<br/>"), styles["Normal"])
                )

                story.append(Spacer(1, 10))

        doc = SimpleDocTemplate(
            caminho,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )

        doc.build(story)

        messagebox.showinfo("Sucesso", "Relatório PDF gerado com sucesso")