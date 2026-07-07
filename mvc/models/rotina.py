"""Camada MODEL — Agregado Rotina.

COMPOSIÇÃO: Rotina possui Tarefas — sem a Rotina, as Tarefas não existem.
"""

from .item import Tarefa


class Rotina:
    def __init__(self, nome):
        self.nome = nome
        self._tarefas = []

    def adicionar_tarefa(self, t):
        self._tarefas.append(t)

    def get_tarefas(self, filtro="todas"):
        if filtro == "pendentes":
            return [t for t in self._tarefas if not t.concluida]
        if filtro == "concluidas":
            return [t for t in self._tarefas if t.concluida]
        return list(self._tarefas)  # cópia para evitar mutação acidental

    def indice_real(self, tarefa):
        """Retorna o índice da tarefa na lista completa (não filtrada)."""
        return self._tarefas.index(tarefa)

    def remover_tarefa(self, i):
        if 0 <= i < len(self._tarefas):
            self._tarefas.pop(i)

    def total(self):
        return len(self._tarefas)

    def concluidas(self):
        return sum(1 for t in self._tarefas if t.concluida)

    def para_dict(self):
        return {"nome": self.nome,
                "tarefas": [t.para_dict() for t in self._tarefas]}
