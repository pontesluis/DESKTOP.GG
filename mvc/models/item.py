"""Camada MODEL — Entidades de domínio.

Contém as classes que representam os dados e as regras de negócio.
Não conhece nada sobre a interface (View) nem sobre a coordenação (Controller).
"""

from abc import ABC, abstractmethod
from datetime import datetime


class Item(ABC):
    def __init__(self, titulo, descricao):
        self.titulo = titulo
        self._descricao = descricao
        self._criado_em = datetime.now().strftime("%d/%m/%Y %H:%M")

    @property
    def descricao(self):
        return self._descricao

    @abstractmethod
    def get_tipo(self) -> str: ...

    @abstractmethod
    def get_resumo(self) -> str: ...

    def exibir(self) -> str:
        return f"{self.titulo} — {self.get_resumo()}"

    @abstractmethod
    def para_dict(self) -> dict: ...


class Lembrete(Item):
    def __init__(self, titulo, descricao, horario):
        super().__init__(titulo, descricao)
        self.horario = horario

    def get_tipo(self):
        return "Lembrete"

    def get_resumo(self):
        return f"{self.horario} — {self._descricao}"

    def editar(self, titulo, descricao, horario):
        self.titulo = titulo
        self._descricao = descricao
        self.horario = horario

    def para_dict(self):
        return {"tipo": "lembrete", "titulo": self.titulo,
                "descricao": self._descricao, "horario": self.horario,
                "criado_em": self._criado_em}


class Tarefa(Item):
    def __init__(self, titulo, descricao, horario, concluida=False):
        super().__init__(titulo, descricao)
        self.horario = horario
        self.concluida = concluida

    def get_tipo(self):
        return "Tarefa"

    def get_resumo(self):
        status = "✓" if self.concluida else "○"
        return f"{self.horario} {status} — {self._descricao}"

    def concluir(self):
        self.concluida = True

    def editar(self, titulo, descricao, horario):
        self.titulo = titulo
        self._descricao = descricao
        self.horario = horario

    def para_dict(self):
        return {"tipo": "tarefa", "titulo": self.titulo,
                "descricao": self._descricao, "horario": self.horario,
                "concluida": self.concluida, "criado_em": self._criado_em}
