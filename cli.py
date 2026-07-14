"""Interface de TERMINAL (CLI) para apresentação em vídeo.
Execute a partir da pasta que CONTÉM a pasta mvc:  python -m mvc.cli
"""

import sqlite3
from .models import Repositorio, Lembrete, Rotina, Tarefa


def _pausa():
    input("\n(pressione ENTER para continuar) ")

def _linha():
    print("=" * 52)


# ── LEMBRETES ──
def listar_lembretes(repo):
    _linha(); print("LEMBRETES"); _linha()
    lembretes = repo.get_lembretes()
    if not lembretes:
        print("(nenhum lembrete cadastrado)")
    for i, l in enumerate(lembretes):
        print(f"[{i}] 🔔 {l.exibir()}")

def adicionar_lembrete(repo):
    titulo = input("Título: ").strip()
    desc = input("Descrição: ").strip()
    hora = input("Horário (HH:MM): ").strip()
    if not titulo or not hora:
        print(">> Título e horário são obrigatórios."); return
    repo.adicionar_lembrete(Lembrete(titulo, desc, hora))
    print(">> Lembrete salvo no banco de dados!")

def remover_lembrete(repo):
    listar_lembretes(repo)
    try:
        i = int(input("Índice do lembrete para remover: "))
    except ValueError:
        print(">> Índice inválido."); return
    repo.remover_lembrete(i)
    print(">> Lembrete removido do banco de dados!")


# ── ROTINAS ──
def listar_rotinas(repo):
    _linha(); print("ROTINAS"); _linha()
    rotinas = repo.get_rotinas()
    if not rotinas:
        print("(nenhuma rotina cadastrada)")
    for i, r in enumerate(rotinas):
        print(f"[{i}] 📋 {r.nome}  ({r.concluidas()}/{r.total()} concluídas)")

def adicionar_rotina(repo):
    nome = input("Nome da rotina: ").strip()
    if not nome:
        print(">> Nome é obrigatório."); return
    repo.adicionar_rotina(Rotina(nome))
    print(">> Rotina salva no banco de dados!")

def remover_rotina(repo):
    listar_rotinas(repo)
    try:
        i = int(input("Índice da rotina para remover: "))
    except ValueError:
        print(">> Índice inválido."); return
    repo.remover_rotina(i)
    print(">> Rotina (e suas tarefas) removida do banco de dados!")

def _escolher_rotina(repo):
    listar_rotinas(repo)
    if not repo.get_rotinas():
        return None
    try:
        i = int(input("Índice da rotina: "))
        return repo.get_rotinas()[i]
    except (ValueError, IndexError):
        print(">> Rotina inválida."); return None


# ── TAREFAS ──
def listar_tarefas(repo):
    rot = _escolher_rotina(repo)
    if rot is None: return
    _linha(); print(f"TAREFAS DA ROTINA: {rot.nome}"); _linha()
    tarefas = rot.get_tarefas()
    if not tarefas:
        print("(nenhuma tarefa nesta rotina)")
    for i, t in enumerate(tarefas):
        icone = "✅" if t.concluida else "⭕"
        print(f"[{i}] {icone} {t.exibir()}")

def adicionar_tarefa(repo):
    rot = _escolher_rotina(repo)
    if rot is None: return
    titulo = input("Tarefa: ").strip()
    desc = input("Descrição: ").strip()
    hora = input("Horário (HH:MM): ").strip()
    if not titulo or not hora:
        print(">> Título e horário são obrigatórios."); return
    rot.adicionar_tarefa(Tarefa(titulo, desc, hora))
    repo.salvar()
    print(">> Tarefa salva no banco de dados!")

def concluir_tarefa(repo):
    rot = _escolher_rotina(repo)
    if rot is None: return
    for i, t in enumerate(rot.get_tarefas()):
        icone = "✅" if t.concluida else "⭕"
        print(f"[{i}] {icone} {t.exibir()}")
    try:
        i = int(input("Índice da tarefa para concluir: "))
        rot.get_tarefas()[i].concluir()
    except (ValueError, IndexError):
        print(">> Tarefa inválida."); return
    repo.salvar()
    print(">> Tarefa concluída e atualizada no banco!")

def editar_tarefa(repo):
    rot = _escolher_rotina(repo)
    if rot is None: return
    for i, t in enumerate(rot.get_tarefas()):
        print(f"[{i}] {t.exibir()}")
    try:
        i = int(input("Índice da tarefa para editar: "))
        tar = rot.get_tarefas()[i]
    except (ValueError, IndexError):
        print(">> Tarefa inválida."); return
    titulo = input(f"Novo título ({tar.titulo}): ").strip() or tar.titulo
    desc = input(f"Nova descrição ({tar.descricao}): ").strip() or tar.descricao
    hora = input(f"Novo horário ({tar.horario}): ").strip() or tar.horario
    tar.editar(titulo, desc, hora)
    repo.salvar()
    print(">> Tarefa editada e atualizada no banco!")

def remover_tarefa(repo):
    rot = _escolher_rotina(repo)
    if rot is None: return
    for i, t in enumerate(rot.get_tarefas()):
        print(f"[{i}] {t.exibir()}")
    try:
        i = int(input("Índice da tarefa para remover: "))
    except ValueError:
        print(">> Índice inválido."); return
    rot.remover_tarefa(i)
    repo.salvar()
    print(">> Tarefa removida do banco de dados!")


# ── PROVA DO BANCO: consulta SQL crua ──
def ver_banco_cru(repo):
    _linha(); print(f"CONSULTA DIRETA AO BANCO ({repo.BANCO}) VIA SQL"); _linha()
    with sqlite3.connect(repo.BANCO) as con:
        cur = con.cursor()
        for tabela in ("lembretes", "rotinas", "tarefas"):
            print(f"\n--- Tabela: {tabela} ---")
            cur.execute(f"SELECT * FROM {tabela}")
            colunas = [d[0] for d in cur.description]
            print(" | ".join(colunas))
            linhas = cur.fetchall()
            if not linhas:
                print("(vazia)")
            for linha in linhas:
                print(" | ".join(str(c) for c in linha))


# ── MENU PRINCIPAL ──
MENU = """
============ ROTINA & LEMBRETES (TERMINAL) ============
 LEMBRETES
   1) Listar lembretes
   2) Adicionar lembrete
   3) Remover lembrete
 ROTINAS
   4) Listar rotinas
   5) Adicionar rotina
   6) Remover rotina
 TAREFAS
   7) Listar tarefas de uma rotina
   8) Adicionar tarefa
   9) Concluir tarefa
  10) Editar tarefa
  11) Remover tarefa
 BANCO DE DADOS
  12) Ver dados crus no banco (SQL)
   0) Sair
======================================================="""

ACOES = {
    "1": listar_lembretes, "2": adicionar_lembrete, "3": remover_lembrete,
    "4": listar_rotinas,   "5": adicionar_rotina,   "6": remover_rotina,
    "7": listar_tarefas,   "8": adicionar_tarefa,   "9": concluir_tarefa,
    "10": editar_tarefa,   "11": remover_tarefa,    "12": ver_banco_cru,
}

def main():
    repo = Repositorio()
    print("Banco de dados conectado:", repo.BANCO)
    while True:
        print(MENU)
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "0":
            print("Até logo! Os dados continuam salvos no banco.")
            break
        acao = ACOES.get(opcao)
        if acao is None:
            print(">> Opção inválida."); continue
        print()
        acao(repo)
        _pausa()

if __name__ == "__main__":
    main()