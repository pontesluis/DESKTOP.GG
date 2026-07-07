"""Camada CONTROLLER — Coordenação.

Faz a ponte entre a View (interface) e o Model (dados). Contém a lógica de
fluxo: valida entradas, aciona o repositório e manda a View re-renderizar.
"""

from ..models import Repositorio, Lembrete, Tarefa, Rotina
from ..views import JanelaPrincipal, JanelaEdicao, Notificador


class AppController:
    def __init__(self, root):
        self.root = root
        self.repositorio = Repositorio()
        self._filtro = "todas"

        # A View recebe o controller para delegar as ações do usuário.
        self.view = JanelaPrincipal(root, self)

        self.refresh_lembretes()
        self.refresh_rotinas()

    # ── LEMBRETES ────────────────────────────────────────────────
    def add_lembrete(self):
        titulo, desc, hora = self.view.get_form_lembrete()
        if not titulo or not hora:
            Notificador.erro("Título e horário são obrigatórios.")
            return
        self.repositorio.adicionar_lembrete(Lembrete(titulo, desc, hora))
        self.view.limpar_form_lembrete()
        self.refresh_lembretes()

    def edit_lembrete(self):
        i = self.view.sel_lembrete()
        if i is None:
            Notificador.erro("Selecione um lembrete.")
            return
        item = self.repositorio.get_lembretes()[i]
        JanelaEdicao(self.root, item, lambda: (
            self.repositorio.salvar(), self.refresh_lembretes()))

    def rem_lembrete(self):
        i = self.view.sel_lembrete()
        if i is None:
            Notificador.erro("Selecione um lembrete.")
            return
        if Notificador.confirmar("Remover este lembrete?"):
            self.repositorio.remover_lembrete(i)
            self.refresh_lembretes()

    def refresh_lembretes(self):
        self.view.render_lembretes(self.repositorio.get_lembretes())

    # ── ROTINAS ──────────────────────────────────────────────────
    def criar_rotina(self):
        nome = self.view.get_nome_rotina()
        if not nome:
            Notificador.erro("Digite o nome da rotina.")
            return
        self.repositorio.adicionar_rotina(Rotina(nome))
        self.view.limpar_nome_rotina()
        self.refresh_rotinas()

    def rem_rotina(self):
        i = self.view.sel_rotina()
        if i is None:
            Notificador.erro("Selecione uma rotina.")
            return
        if Notificador.confirmar("Remover rotina e todas as tarefas?"):
            self.repositorio.remover_rotina(i)
            self.view.limpar_tarefas()
            self.refresh_rotinas()

    def refresh_rotinas(self):
        self.view.render_rotinas(self.repositorio.get_rotinas())

    # ── TAREFAS ──────────────────────────────────────────────────
    def set_filtro(self, f):
        self._filtro = f
        self.refresh_tarefas()

    def _rotina_selecionada(self):
        i = self.view.sel_rotina()
        if i is None:
            return None
        return self.repositorio.get_rotinas()[i]

    def add_tarefa(self):
        rot = self._rotina_selecionada()
        if rot is None:
            Notificador.erro("Selecione uma rotina primeiro.")
            return
        titulo, desc, hora = self.view.get_form_tarefa()
        if not titulo or not hora:
            Notificador.erro("Título e horário são obrigatórios.")
            return
        rot.adicionar_tarefa(Tarefa(titulo, desc, hora))
        self.repositorio.salvar()
        self.view.limpar_form_tarefa()
        self.refresh_tarefas()
        self.refresh_rotinas()

    def edit_tarefa(self):
        rot = self._rotina_selecionada()
        ti = self.view.sel_tarefa()
        if rot is None or ti is None:
            Notificador.erro("Selecione uma rotina e uma tarefa.")
            return
        tar = rot.get_tarefas(self._filtro)[ti]
        JanelaEdicao(self.root, tar, lambda: (
            self.repositorio.salvar(),
            self.refresh_tarefas(),
            self.refresh_rotinas()))

    def done_tarefa(self):
        rot = self._rotina_selecionada()
        ti = self.view.sel_tarefa()
        if rot is None or ti is None:
            Notificador.erro("Selecione uma rotina e uma tarefa.")
            return
        tar = rot.get_tarefas(self._filtro)[ti]
        if tar.concluida:
            Notificador.alerta("Aviso", "Esta tarefa já está concluída.")
            return
        tar.concluir()
        self.repositorio.salvar()
        self.refresh_tarefas()
        self.refresh_rotinas()

    def rem_tarefa(self):
        rot = self._rotina_selecionada()
        ti = self.view.sel_tarefa()
        if rot is None or ti is None:
            return
        if not Notificador.confirmar("Remover esta tarefa?"):
            return
        tar = rot.get_tarefas(self._filtro)[ti]
        rot.remover_tarefa(rot.indice_real(tar))  # índice real, não o filtrado
        self.repositorio.salvar()
        self.refresh_tarefas()
        self.refresh_rotinas()

    def refresh_tarefas(self):
        rot = self._rotina_selecionada()
        if rot is None:
            self.view.limpar_tarefas()
            return
        self.view.render_tarefas(rot.get_tarefas(self._filtro))
