"""Camada VIEW — Janela principal.

Responsável APENAS por montar/atualizar widgets. Toda ação do usuário é
delegada ao Controller (injetado). A View expõe métodos de leitura dos
formulários e de renderização das listas.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from .tema import CORES, make_label, make_entry, make_btn, separador


class JanelaPrincipal:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.root.title("✦  Rotina & Lembretes")
        self.root.geometry("780x620")
        self.root.configure(bg=CORES["fundo"])
        self.root.resizable(False, False)

        self._build()

    def _build(self):
        header = tk.Frame(self.root, bg=CORES["painel"], pady=16)
        header.pack(fill="x")

        tk.Label(header, text="✦  Rotina & Lembretes",
                 bg=CORES["painel"], fg=CORES["texto"],
                 font=("Segoe UI", 20, "bold")).pack(side="left", padx=24)

        self._hora_label = tk.Label(header, bg=CORES["painel"],
                                    fg=CORES["texto_sub"],
                                    font=("Segoe UI", 11))
        self._hora_label.pack(side="right", padx=24)
        self._tick()

        style = ttk.Style()
        style.theme_use("default")
        style.configure("V.TNotebook", background=CORES["fundo"], borderwidth=0)
        style.configure("V.TNotebook.Tab", background=CORES["card"],
                        foreground=CORES["texto_sub"],
                        padding=[20, 10], font=("Segoe UI", 11, "bold"),
                        borderwidth=0)
        style.map("V.TNotebook.Tab",
                  background=[("selected", CORES["roxo"])],
                  foreground=[("selected", "#FFFFFF")])

        nb = ttk.Notebook(self.root, style="V.TNotebook")
        nb.pack(fill="both", expand=True)

        self.aba_lem = tk.Frame(nb, bg=CORES["fundo"])
        self.aba_rot = tk.Frame(nb, bg=CORES["fundo"])
        nb.add(self.aba_lem, text="  🔔  Lembretes  ")
        nb.add(self.aba_rot, text="  📋  Rotina Diária  ")

        self._build_lembretes()
        self._build_rotina()

    def _tick(self):
        self._hora_label.config(
            text=datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))
        self.root.after(1000, self._tick)

    # ── LEMBRETES ────────────────────────────────────────────────
    def _build_lembretes(self):
        F = self.aba_lem
        c = self.controller

        card = tk.Frame(F, bg=CORES["painel"], padx=20, pady=16)
        card.pack(fill="x", padx=20, pady=(20, 8))

        make_label(card, "Novo lembrete", 13, bold=True).grid(
            row=0, column=0, columnspan=6, sticky="w", pady=(0, 12))

        campos = [("Título", "entry_lt"), ("Descrição", "entry_ld"),
                  ("Horário (HH:MM)", "entry_lh")]
        for col, (label, attr) in enumerate(campos):
            make_label(card, label, cor=CORES["texto_sub"]).grid(
                row=1, column=col * 2, sticky="w",
                padx=(0 if col == 0 else 12, 4))
            e = make_entry(card, width=20)
            e.grid(row=2, column=col * 2,
                   padx=(0 if col == 0 else 12, 0), pady=4)
            setattr(self, attr, e)
        card.columnconfigure(1, weight=1)

        self.entry_lh.bind("<Return>", lambda e: c.add_lembrete())

        btn_row = tk.Frame(F, bg=CORES["fundo"])
        btn_row.pack(fill="x", padx=20, pady=4)
        make_btn(btn_row, "➕  Adicionar", c.add_lembrete,  CORES["roxo"]).pack(side="left", padx=(0, 8))
        make_btn(btn_row, "✏  Editar",    c.edit_lembrete, CORES["azul"]).pack(side="left", padx=(0, 8))
        make_btn(btn_row, "🗑  Remover",  c.rem_lembrete,  CORES["vermelho"]).pack(side="left")

        separador(F)

        lf = tk.Frame(F, bg=CORES["fundo"])
        lf.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        sb = tk.Scrollbar(lf, bg=CORES["card"], troughcolor=CORES["fundo"])
        sb.pack(side="right", fill="y")

        self.lista_lem = tk.Listbox(
            lf, bg=CORES["card"], fg=CORES["texto"],
            font=("Segoe UI", 12),
            selectbackground=CORES["roxo"], selectforeground="#FFFFFF",
            borderwidth=0, highlightthickness=0,
            activestyle="none", relief="flat",
            yscrollcommand=sb.set,
        )
        self.lista_lem.pack(fill="both", expand=True)
        sb.config(command=self.lista_lem.yview)

        self.lista_lem.bind("<Delete>", lambda e: c.rem_lembrete())

    # ── ROTINA ───────────────────────────────────────────────────
    def _build_rotina(self):
        F = self.aba_rot
        c = self.controller

        card_rot = tk.Frame(F, bg=CORES["painel"], padx=20, pady=14)
        card_rot.pack(fill="x", padx=20, pady=(20, 6))

        make_label(card_rot, "Nova rotina", 13, bold=True).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        make_label(card_rot, "Nome", cor=CORES["texto_sub"]).grid(
            row=1, column=0, sticky="w")
        self.entry_rn = make_entry(card_rot, width=30)
        self.entry_rn.grid(row=1, column=1, padx=12)
        self.entry_rn.bind("<Return>", lambda e: c.criar_rotina())

        btn_rot = tk.Frame(F, bg=CORES["fundo"])
        btn_rot.pack(fill="x", padx=20, pady=4)
        make_btn(btn_rot, "➕  Criar Rotina",   c.criar_rotina, CORES["rosa"]).pack(side="left", padx=(0, 8))
        make_btn(btn_rot, "🗑  Remover Rotina", c.rem_rotina,   CORES["vermelho"]).pack(side="left")

        self.lista_rot = tk.Listbox(
            F, bg=CORES["card"], fg=CORES["texto"],
            font=("Segoe UI", 12, "bold"),
            selectbackground=CORES["rosa"], selectforeground="#FFFFFF",
            borderwidth=0, highlightthickness=0,
            activestyle="none", height=3,
        )
        self.lista_rot.pack(fill="x", padx=20, pady=6)
        self.lista_rot.bind("<<ListboxSelect>>", lambda e: c.refresh_tarefas())

        separador(F)

        card_tar = tk.Frame(F, bg=CORES["painel"], padx=20, pady=12)
        card_tar.pack(fill="x", padx=20, pady=(0, 6))

        make_label(card_tar, "Nova tarefa", 13, bold=True).grid(
            row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))

        campos_tar = [("Tarefa", "entry_tt"), ("Descrição", "entry_td"),
                      ("Horário (HH:MM)", "entry_th")]
        for col, (label, attr) in enumerate(campos_tar):
            make_label(card_tar, label, cor=CORES["texto_sub"]).grid(
                row=1, column=col * 2, sticky="w",
                padx=(0 if col == 0 else 12, 4))
            e = make_entry(card_tar, width=18)
            e.grid(row=2, column=col * 2,
                   padx=(0 if col == 0 else 12, 0), pady=4)
            setattr(self, attr, e)

        self.entry_th.bind("<Return>", lambda e: c.add_tarefa())

        btn_tar = tk.Frame(F, bg=CORES["fundo"])
        btn_tar.pack(fill="x", padx=20, pady=4)
        make_btn(btn_tar, "➕  Adicionar", c.add_tarefa,  CORES["verde"]).pack(side="left", padx=(0, 8))
        make_btn(btn_tar, "✏  Editar",    c.edit_tarefa, CORES["azul"]).pack(side="left", padx=(0, 8))
        make_btn(btn_tar, "✓  Concluir",  c.done_tarefa, CORES["amarelo"], "#000000").pack(side="left", padx=(0, 8))

        filtro_f = tk.Frame(F, bg=CORES["fundo"])
        filtro_f.pack(fill="x", padx=20, pady=(6, 4))
        make_label(filtro_f, "Filtrar:", cor=CORES["texto_sub"]).pack(side="left", padx=(0, 8))
        make_btn(filtro_f, "Todas",      lambda: c.set_filtro("todas"),     CORES["card"],    CORES["texto"], 10).pack(side="left", padx=2)
        make_btn(filtro_f, "Pendentes",  lambda: c.set_filtro("pendentes"), CORES["amarelo"], "#000000",      10).pack(side="left", padx=2)
        make_btn(filtro_f, "Concluídas", lambda: c.set_filtro("concluidas"), CORES["verde"],  "#000000",      10).pack(side="left", padx=2)

        lf2 = tk.Frame(F, bg=CORES["fundo"])
        lf2.pack(fill="both", expand=True, padx=20, pady=(4, 16))

        sb2 = tk.Scrollbar(lf2, bg=CORES["card"], troughcolor=CORES["fundo"])
        sb2.pack(side="right", fill="y")

        self.lista_tar = tk.Listbox(
            lf2, bg=CORES["card"], fg=CORES["texto"],
            font=("Segoe UI", 12),
            selectbackground=CORES["verde"], selectforeground="#000000",
            borderwidth=0, highlightthickness=0,
            activestyle="none",
            yscrollcommand=sb2.set,
        )
        self.lista_tar.pack(fill="both", expand=True)
        sb2.config(command=self.lista_tar.yview)

        self.lista_tar.bind("<Delete>", lambda e: c.rem_tarefa())
        self.lista_tar.bind("<Return>", lambda e: c.done_tarefa())

    # ── LEITURA DOS FORMULÁRIOS ──────────────────────────────────
    def get_form_lembrete(self):
        return (self.entry_lt.get().strip(),
                self.entry_ld.get().strip(),
                self.entry_lh.get().strip())

    def limpar_form_lembrete(self):
        for e in (self.entry_lt, self.entry_ld, self.entry_lh):
            e.delete(0, tk.END)
        self.entry_lt.focus()

    def get_form_tarefa(self):
        return (self.entry_tt.get().strip(),
                self.entry_td.get().strip(),
                self.entry_th.get().strip())

    def limpar_form_tarefa(self):
        for e in (self.entry_tt, self.entry_td, self.entry_th):
            e.delete(0, tk.END)
        self.entry_tt.focus()

    def get_nome_rotina(self):
        return self.entry_rn.get().strip()

    def limpar_nome_rotina(self):
        self.entry_rn.delete(0, tk.END)

    def sel_lembrete(self):
        s = self.lista_lem.curselection()
        return s[0] if s else None

    def sel_rotina(self):
        s = self.lista_rot.curselection()
        return s[0] if s else None

    def sel_tarefa(self):
        s = self.lista_tar.curselection()
        return s[0] if s else None

    # ── RENDERIZAÇÃO ─────────────────────────────────────────────
    def render_lembretes(self, lembretes):
        self.lista_lem.delete(0, tk.END)
        for i, l in enumerate(lembretes):
            self.lista_lem.insert(tk.END, f"  🔔  {l.exibir()}")
            self.lista_lem.itemconfig(i, fg=CORES["ciano"])

    def render_rotinas(self, rotinas):
        sel = self.lista_rot.curselection()
        self.lista_rot.delete(0, tk.END)
        for i, r in enumerate(rotinas):
            self.lista_rot.insert(
                tk.END,
                f"  📋  {r.nome}   ({r.concluidas()}/{r.total()} concluídas)")
            self.lista_rot.itemconfig(i, fg=CORES["rosa"])
        if sel:
            self.lista_rot.selection_set(sel[0])

    def render_tarefas(self, tarefas):
        self.lista_tar.delete(0, tk.END)
        for i, t in enumerate(tarefas):
            icone = "✅" if t.concluida else "⭕"
            self.lista_tar.insert(tk.END, f"  {icone}  {t.exibir()}")
            self.lista_tar.itemconfig(
                i, fg=CORES["verde"] if t.concluida else CORES["texto"])

    def limpar_tarefas(self):
        self.lista_tar.delete(0, tk.END)
