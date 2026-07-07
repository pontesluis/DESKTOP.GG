"""Camada MODEL — Persistência.

ASSOCIAÇÃO: Repositorio existe independente do App. Responsável por
carregar/salvar o estado em disco (JSON), sem conhecer a interface.
"""

import json
import os

from .item import Lembrete, Tarefa
from .rotina import Rotina


class Repositorio:
    ARQUIVO = "dados.json"

    def __init__(self):
        self._lembretes = []
        self._rotinas = []
        self.carregar()

    # ── Lembretes ────────────────────────────────────────────────
    def adicionar_lembrete(self, l):
        self._lembretes.append(l)
        self.salvar()

    def get_lembretes(self):
        return self._lembretes

    def remover_lembrete(self, i):
        if 0 <= i < len(self._lembretes):
            self._lembretes.pop(i)
            self.salvar()

    # ── Rotinas ──────────────────────────────────────────────────
    def adicionar_rotina(self, r):
        self._rotinas.append(r)
        self.salvar()

    def get_rotinas(self):
        return self._rotinas

    def remover_rotina(self, i):
        if 0 <= i < len(self._rotinas):
            self._rotinas.pop(i)
            self.salvar()

    # ── I/O ──────────────────────────────────────────────────────
    def salvar(self):
        dados = {
            "lembretes": [l.para_dict() for l in self._lembretes],
            "rotinas": [r.para_dict() for r in self._rotinas],
        }
        try:
            with open(self.ARQUIVO, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
        except OSError:
            pass  # não quebra o app se não conseguir salvar

    def carregar(self):
        if not os.path.exists(self.ARQUIVO):
            return
        try:
            with open(self.ARQUIVO, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except (json.JSONDecodeError, OSError):
            return  # arquivo corrompido — começa do zero

        for d in dados.get("lembretes", []):
            try:
                self._lembretes.append(
                    Lembrete(d["titulo"], d["descricao"], d["horario"]))
            except KeyError:
                continue  # registro incompleto — pula sem travar

        for r in dados.get("rotinas", []):
            try:
                rot = Rotina(r["nome"])
                for t in r.get("tarefas", []):
                    try:
                        rot.adicionar_tarefa(
                            Tarefa(t["titulo"], t["descricao"],
                                   t["horario"], t.get("concluida", False)))
                    except KeyError:
                        continue
                self._rotinas.append(rot)
            except KeyError:
                continue
