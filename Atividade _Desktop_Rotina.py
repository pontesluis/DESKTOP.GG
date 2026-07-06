import tkinter as tk
from tkinter import messagebox, ttk
from abc import ABC, abstractmethod
from datetime import datetime
import json
import os

# =============================================================
# PALETA DE CORES
# =============================================================

CORES = {
    "fundo":     "#0D1117",
    "painel":    "#161B22",
    "card":      "#21262D",
    "borda":     "#30363D",
    "texto":     "#F0F6FC",
    "texto_sub": "#8B949E",
    "roxo":      "#7C3AED",
    "verde":     "#10B981",
    "amarelo":   "#F59E0B",
    "vermelho":  "#EF4444",
    "azul":      "#3B82F6",
    "rosa":      "#EC4899",
    "ciano":     "#06B6D4",
}

# =============================================================
# DOMÍNIO
# =============================================================

class Item(ABC):
    def __init__(self, titulo, descricao):
        self.titulo = titulo
        self._descricao = descricao
        self._criado_em = datetime.now().strftime("%d/%m/%Y %H:%M")

    @abstractmethod
    def get_tipo(self) -> str: pass

    @abstractmethod
    def get_resumo(self) -> str: pass

    def exibir(self) -> str:
        return f"{self.titulo} — {self.get_resumo()}"

    @abstractmethod
    def para_dict(self) -> dict: pass


class Lembrete(Item):
    def __init__(self, titulo, descricao, horario):
        super().__init__(titulo, descricao)
        self.horario = horario

    def get_tipo(self): return "Lembrete"
    def get_resumo(self): return f"{self.horario} — {self._descricao}"

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

    def get_tipo(self): return "Tarefa"

    def get_resumo(self):
        status = "✓" if self.concluida else "○"
        return f"{self.horario} {status} — {self._descricao}"

    def concluir(self): self.concluida = True

    def editar(self, titulo, descricao, horario):
        self.titulo = titulo
        self._descricao = descricao
        self.horario = horario

    def para_dict(self):
        return {"tipo": "tarefa", "titulo": self.titulo,
                "descricao": self._descricao, "horario": self.horario,
                "concluida": self.concluida, "criado_em": self._criado_em}


# COMPOSIÇÃO: Rotina possui Tarefas — sem a Rotina, as Tarefas não existem
class Rotina:
    def __init__(self, nome):
        self.nome = nome
        self._tarefas = []

    def adicionar_tarefa(self, t): self._tarefas.append(t)

    def get_tarefas(self, filtro="todas"):
        if filtro == "pendentes":  return [t for t in self._tarefas if not t.concluida]
        if filtro == "concluidas": return [t for t in self._tarefas if t.concluida]
        return list(self._tarefas)  # FIX: retorna cópia para evitar mutação acidental

    def remover_tarefa(self, i):
        if 0 <= i < len(self._tarefas): self._tarefas.pop(i)

    def total(self):      return len(self._tarefas)
    def concluidas(self): return sum(1 for t in self._tarefas if t.concluida)

    def para_dict(self):
        return {"nome": self.nome,
                "tarefas": [t.para_dict() for t in self._tarefas]}


# DEPENDÊNCIA: Notificador é usado pontualmente — não é atributo do App
class Notificador:
    @staticmethod
    def alerta(titulo, msg): messagebox.showinfo(titulo, msg)
    @staticmethod
    def erro(msg): messagebox.showerror("Erro", msg)
    @staticmethod
    def confirmar(msg): return messagebox.askyesno("Confirmar", msg)


# ASSOCIAÇÃO: Repositorio existe independente do App
class Repositorio:
    ARQUIVO = "dados.json"

    def __init__(self):
        self._lembretes = []
        self._rotinas   = []
        self.carregar()

    def adicionar_lembrete(self, l): self._lembretes.append(l); self.salvar()
    def get_lembretes(self):         return self._lembretes

    def remover_lembrete(self, i):
        if 0 <= i < len(self._lembretes):
            self._lembretes.pop(i); self.salvar()

    def adicionar_rotina(self, r): self._rotinas.append(r); self.salvar()
    def get_rotinas(self):         return self._rotinas

    def remover_rotina(self, i):
        if 0 <= i < len(self._rotinas):
            self._rotinas.pop(i); self.salvar()

    def salvar(self):
        dados = {
            "lembretes": [l.para_dict() for l in self._lembretes],
            "rotinas":   [r.para_dict() for r in self._rotinas],
        }
        try:
            with open(self.ARQUIVO, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
        except OSError:
            pass  # FIX: não quebra o app se não conseguir salvar (sem permissão, disco cheio, etc)

    def carregar(self):
        if not os.path.exists(self.ARQUIVO): return
        try:
            with open(self.ARQUIVO, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except (json.JSONDecodeError, OSError):
            return  # FIX: arquivo corrompido — ignora e começa do zero

        for d in dados.get("lembretes", []):
            try:
                self._lembretes.append(
                    Lembrete(d["titulo"], d["descricao"], d["horario"]))
            except KeyError:
                continue  # FIX: registro incompleto — pula sem travar

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


# =============================================================
# HELPERS VISUAIS
# =============================================================

def make_label(parent, texto, size=11, cor=None, bold=False):
    return tk.Label(parent, text=texto, bg=parent["bg"],
                    fg=cor or CORES["texto"],
                    font=("Segoe UI", size, "bold" if bold else "normal"))

def make_entry(parent, width=28):
    return tk.Entry(parent, bg=CORES["card"], fg=CORES["texto"],
                    insertbackground=CORES["texto"],
                    font=("Segoe UI", 11), relief="flat",
                    highlightthickness=2,
                    highlightbackground=CORES["borda"],
                    highlightcolor=CORES["roxo"],
                    width=width)

def _escurecer(hex_cor):
    hex_cor = hex_cor.lstrip("#")
    r, g, b = (int(hex_cor[i:i+2], 16) for i in (0, 2, 4))
    return f"#{max(0,r-30):02x}{max(0,g-30):02x}{max(0,b-30):02x}"

def make_btn(parent, texto, comando, cor_bg, cor_fg="#FFFFFF", width=18):
    btn = tk.Button(
        parent, text=texto, command=comando,
        bg=cor_bg, fg=cor_fg,
        font=("Segoe UI", 10, "bold"),
        relief="flat", bd=0, padx=14, pady=8,
        cursor="hand2",
        activebackground=_escurecer(cor_bg),
        activeforeground=cor_fg,
        width=width,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=_escurecer(cor_bg)))
    btn.bind("<Leave>", lambda e: btn.config(bg=cor_bg))
    return btn

def separador(parent):
    tk.Frame(parent, bg=CORES["borda"], height=1).pack(fill="x", pady=8)


# =============================================================
# JANELA DE EDIÇÃO
# =============================================================

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
                  ("Descrição", self._item._descricao),
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
            row=len(campos)+1, column=0, columnspan=2, pady=(20, 0))

        # FIX: Enter na janela de edição aciona salvar
        self.bind("<Return>", lambda e: self._salvar())

    def _salvar(self):
        titulo = self.entries[0].get().strip()
        desc   = self.entries[1].get().strip()
        hora   = self.entries[2].get().strip()
        if not titulo or not hora:
            Notificador.erro("Título e horário são obrigatórios.")
            return
        self._item.editar(titulo, desc, hora)
        self._ao_salvar()
        self.destroy()


# =============================================================
# APP PRINCIPAL
# =============================================================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("✦  Rotina & Lembretes")
        self.root.geometry("780x620")
        self.root.configure(bg=CORES["fundo"])
        self.root.resizable(False, False)

        self.repositorio = Repositorio()
        self._filtro = "todas"
        self._build()

    def _build(self):
        # Header
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

        # Abas
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

        card = tk.Frame(F, bg=CORES["painel"], padx=20, pady=16)
        card.pack(fill="x", padx=20, pady=(20, 8))

        make_label(card, "Novo lembrete", 13, bold=True).grid(
            row=0, column=0, columnspan=6, sticky="w", pady=(0, 12))

        campos = [("Título", "entry_lt"), ("Descrição", "entry_ld"),
                  ("Horário (HH:MM)", "entry_lh")]
        for col, (label, attr) in enumerate(campos):
            make_label(card, label, cor=CORES["texto_sub"]).grid(
                row=1, column=col*2, sticky="w",
                padx=(0 if col == 0 else 12, 4))
            e = make_entry(card, width=20)
            e.grid(row=2, column=col*2,
                   padx=(0 if col == 0 else 12, 0), pady=4)
            setattr(self, attr, e)
        card.columnconfigure(1, weight=1)

        # FIX: Enter no último campo de lembrete adiciona direto
        self.entry_lh.bind("<Return>", lambda e: self._add_lem())

        btn_row = tk.Frame(F, bg=CORES["fundo"])
        btn_row.pack(fill="x", padx=20, pady=4)
        make_btn(btn_row, "➕  Adicionar", self._add_lem,  CORES["roxo"]).pack(side="left", padx=(0,8))
        make_btn(btn_row, "✏  Editar",    self._edit_lem, CORES["azul"]).pack(side="left", padx=(0,8))
        make_btn(btn_row, "🗑  Remover",  self._rem_lem,  CORES["vermelho"]).pack(side="left")

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

        # FIX: Delete na lista remove o item selecionado
        self.lista_lem.bind("<Delete>", lambda e: self._rem_lem())

        self._refresh_lem()

    def _add_lem(self):
        titulo = self.entry_lt.get().strip()
        desc   = self.entry_ld.get().strip()
        hora   = self.entry_lh.get().strip()
        if not titulo or not hora:
            Notificador.erro("Título e horário são obrigatórios.")
            return
        self.repositorio.adicionar_lembrete(Lembrete(titulo, desc, hora))
        for e in (self.entry_lt, self.entry_ld, self.entry_lh):
            e.delete(0, tk.END)
        self.entry_lt.focus()
        self._refresh_lem()

    def _edit_lem(self):
        sel = self.lista_lem.curselection()
        if not sel: Notificador.erro("Selecione um lembrete."); return
        item = self.repositorio.get_lembretes()[sel[0]]
        JanelaEdicao(self.root, item,
                     lambda: (self.repositorio.salvar(), self._refresh_lem()))

    def _rem_lem(self):
        sel = self.lista_lem.curselection()
        if not sel: Notificador.erro("Selecione um lembrete."); return
        if Notificador.confirmar("Remover este lembrete?"):
            self.repositorio.remover_lembrete(sel[0])
            self._refresh_lem()

    def _refresh_lem(self):
        self.lista_lem.delete(0, tk.END)
        for i, l in enumerate(self.repositorio.get_lembretes()):
            self.lista_lem.insert(tk.END, f"  🔔  {l.exibir()}")
            self.lista_lem.itemconfig(i, fg=CORES["ciano"])

    # ── ROTINA ───────────────────────────────────────────────────

    def _build_rotina(self):
        F = self.aba_rot

        card_rot = tk.Frame(F, bg=CORES["painel"], padx=20, pady=14)
        card_rot.pack(fill="x", padx=20, pady=(20, 6))

        make_label(card_rot, "Nova rotina", 13, bold=True).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        make_label(card_rot, "Nome", cor=CORES["texto_sub"]).grid(
            row=1, column=0, sticky="w")
        self.entry_rn = make_entry(card_rot, width=30)
        self.entry_rn.grid(row=1, column=1, padx=12)

        # FIX: Enter cria a rotina direto
        self.entry_rn.bind("<Return>", lambda e: self._criar_rot())

        btn_rot = tk.Frame(F, bg=CORES["fundo"])
        btn_rot.pack(fill="x", padx=20, pady=4)
        make_btn(btn_rot, "➕  Criar Rotina",    self._criar_rot, CORES["rosa"]).pack(side="left", padx=(0,8))
        make_btn(btn_rot, "🗑  Remover Rotina",  self._rem_rot,   CORES["vermelho"]).pack(side="left")

        self.lista_rot = tk.Listbox(
            F, bg=CORES["card"], fg=CORES["texto"],
            font=("Segoe UI", 12, "bold"),
            selectbackground=CORES["rosa"], selectforeground="#FFFFFF",
            borderwidth=0, highlightthickness=0,
            activestyle="none", height=3,
        )
        self.lista_rot.pack(fill="x", padx=20, pady=6)
        # FIX: não reseta o filtro ao trocar de rotina
        self.lista_rot.bind("<<ListboxSelect>>", lambda e: self._refresh_tar())

        separador(F)

        card_tar = tk.Frame(F, bg=CORES["painel"], padx=20, pady=12)
        card_tar.pack(fill="x", padx=20, pady=(0, 6))

        make_label(card_tar, "Nova tarefa", 13, bold=True).grid(
            row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))

        campos_tar = [("Tarefa", "entry_tt"), ("Descrição", "entry_td"),
                      ("Horário (HH:MM)", "entry_th")]
        for col, (label, attr) in enumerate(campos_tar):
            make_label(card_tar, label, cor=CORES["texto_sub"]).grid(
                row=1, column=col*2, sticky="w",
                padx=(0 if col == 0 else 12, 4))
            e = make_entry(card_tar, width=18)
            e.grid(row=2, column=col*2,
                   padx=(0 if col == 0 else 12, 0), pady=4)
            setattr(self, attr, e)

        # FIX: Enter no horário adiciona a tarefa
        self.entry_th.bind("<Return>", lambda e: self._add_tar())

        btn_tar = tk.Frame(F, bg=CORES["fundo"])
        btn_tar.pack(fill="x", padx=20, pady=4)
        make_btn(btn_tar, "➕  Adicionar", self._add_tar,  CORES["verde"]).pack(side="left", padx=(0,8))
        make_btn(btn_tar, "✏  Editar",    self._edit_tar, CORES["azul"]).pack(side="left", padx=(0,8))
        make_btn(btn_tar, "✓  Concluir",  self._done_tar, CORES["amarelo"], "#000000").pack(side="left", padx=(0,8))

        filtro_f = tk.Frame(F, bg=CORES["fundo"])
        filtro_f.pack(fill="x", padx=20, pady=(6, 4))
        make_label(filtro_f, "Filtrar:", cor=CORES["texto_sub"]).pack(side="left", padx=(0, 8))
        make_btn(filtro_f, "Todas",      lambda: self._set_filtro("todas"),     CORES["card"],    CORES["texto"], 10).pack(side="left", padx=2)
        make_btn(filtro_f, "Pendentes",  lambda: self._set_filtro("pendentes"), CORES["amarelo"], "#000000",      10).pack(side="left", padx=2)
        make_btn(filtro_f, "Concluídas", lambda: self._set_filtro("concluidas"),CORES["verde"],   "#000000",      10).pack(side="left", padx=2)

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

        # FIX: Delete na lista remove tarefa; Enter conclui
        self.lista_tar.bind("<Delete>", lambda e: self._remover_tar_selecionada())
        self.lista_tar.bind("<Return>", lambda e: self._done_tar())

        self._refresh_rot()

    def _set_filtro(self, f):
        self._filtro = f
        self._refresh_tar()

    def _criar_rot(self):
        nome = self.entry_rn.get().strip()
        if not nome: Notificador.erro("Digite o nome da rotina."); return
        self.repositorio.adicionar_rotina(Rotina(nome))
        self.entry_rn.delete(0, tk.END)
        self._refresh_rot()

    def _rem_rot(self):
        sel = self.lista_rot.curselection()
        if not sel: Notificador.erro("Selecione uma rotina."); return
        if Notificador.confirmar("Remover rotina e todas as tarefas?"):
            self.repositorio.remover_rotina(sel[0])
            self.lista_tar.delete(0, tk.END)
            self._refresh_rot()

    def _add_tar(self):
        sel = self.lista_rot.curselection()
        if not sel: Notificador.erro("Selecione uma rotina primeiro."); return
        titulo = self.entry_tt.get().strip()
        desc   = self.entry_td.get().strip()
        hora   = self.entry_th.get().strip()
        if not titulo or not hora:
            Notificador.erro("Título e horário são obrigatórios.")
            return
        rot = self.repositorio.get_rotinas()[sel[0]]
        rot.adicionar_tarefa(Tarefa(titulo, desc, hora))
        self.repositorio.salvar()
        for e in (self.entry_tt, self.entry_td, self.entry_th):
            e.delete(0, tk.END)
        self.entry_tt.focus()
        self._refresh_tar()
        self._refresh_rot()

    def _edit_tar(self):
        sel_r = self.lista_rot.curselection()
        sel_t = self.lista_tar.curselection()
        if not sel_r or not sel_t:
            Notificador.erro("Selecione uma rotina e uma tarefa."); return
        rot = self.repositorio.get_rotinas()[sel_r[0]]
        tar = rot.get_tarefas(self._filtro)[sel_t[0]]
        JanelaEdicao(self.root, tar, lambda: (
            self.repositorio.salvar(),
            self._refresh_tar(),
            self._refresh_rot()))

    def _done_tar(self):
        sel_r = self.lista_rot.curselection()
        sel_t = self.lista_tar.curselection()
        if not sel_r or not sel_t:
            Notificador.erro("Selecione uma rotina e uma tarefa."); return
        rot = self.repositorio.get_rotinas()[sel_r[0]]
        tar = rot.get_tarefas(self._filtro)[sel_t[0]]
        if tar.concluida:
            Notificador.alerta("Aviso", "Esta tarefa já está concluída.")
            return
        tar.concluir()
        self.repositorio.salvar()
        self._refresh_tar()
        self._refresh_rot()

    def _remover_tar_selecionada(self):
        sel_r = self.lista_rot.curselection()
        sel_t = self.lista_tar.curselection()
        if not sel_r or not sel_t: return
        if not Notificador.confirmar("Remover esta tarefa?"): return
        rot = self.repositorio.get_rotinas()[sel_r[0]]
        # FIX: encontra o índice real na lista completa, não na filtrada
        tar_filtrada = rot.get_tarefas(self._filtro)[sel_t[0]]
        idx_real = rot._tarefas.index(tar_filtrada)
        rot.remover_tarefa(idx_real)
        self.repositorio.salvar()
        self._refresh_tar()
        self._refresh_rot()

    def _refresh_rot(self):
        sel = self.lista_rot.curselection()
        self.lista_rot.delete(0, tk.END)
        for i, r in enumerate(self.repositorio.get_rotinas()):
            self.lista_rot.insert(
                tk.END,
                f"  📋  {r.nome}   ({r.concluidas()}/{r.total()} concluídas)")
            self.lista_rot.itemconfig(i, fg=CORES["rosa"])
        if sel: self.lista_rot.selection_set(sel[0])

    def _refresh_tar(self):
        self.lista_tar.delete(0, tk.END)
        sel = self.lista_rot.curselection()
        if not sel: return
        rot = self.repositorio.get_rotinas()[sel[0]]
        for i, t in enumerate(rot.get_tarefas(self._filtro)):
            icone = "✅" if t.concluida else "⭕"
            self.lista_tar.insert(tk.END, f"  {icone}  {t.exibir()}")
            self.lista_tar.itemconfig(
                i, fg=CORES["verde"] if t.concluida else CORES["texto"])


# =============================================================
# PONTO DE ENTRADA
# =============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()