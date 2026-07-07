"""Camada VIEW — Janela de edição de um item.

Coleta os dados no formulário e devolve ao chamador (Controller) via callback.
"""

import tkinter as tk

from .tema import CORES, make_label, make_entry, make_btn
from .notificador import Notificador


class JanelaEdicao(tk.Toplevel):
    def __init__(self, parent, item, ao_salvar):
        super().__init__(parent)
        self.title("✏  Editar")
        self.configure(bg=CORES["fundo"])
        self.resizable(False, False)
        self.grab_set()
        self._item = item
        self._ao_salvar = ao_salvar
        self._build()

    def _build(self):
        frame = tk.Frame(self, bg=CORES["painel"], padx=24, pady=20)
        frame.pack(padx=16, pady=16)

        make_label(frame, "Editar item", 14, bold=True).grid(
            row=0, column=0, columnspan=2, pady=(0, 16), sticky="w")

        campos = [("Título", self._item.titulo),
                  ("Descrição", self._item.descricao),
                  ("Horário (HH:MM)", self._item.horario)]

        self.entries = []
        for i, (label, valor) in enumerate(campos, start=1):
            make_label(frame, label, cor=CORES["texto_sub"]).grid(
                row=i, column=0, sticky="w", pady=4)
            e = make_entry(frame)
            e.insert(0, valor)
            e.grid(row=i, column=1, padx=(12, 0), pady=4)
            self.entries.append(e)

        make_btn(frame, "💾  Salvar", self._salvar, CORES["verde"], width=20).grid(
            row=len(campos) + 1, column=0, columnspan=2, pady=(20, 0))

        self.bind("<Return>", lambda e: self._salvar())

    def _salvar(self):
        titulo = self.entries[0].get().strip()
        desc = self.entries[1].get().strip()
        hora = self.entries[2].get().strip()
        if not titulo or not hora:
            Notificador.erro("Título e horário são obrigatórios.")
            return
        self._item.editar(titulo, desc, hora)
        self._ao_salvar()
        self.destroy()
