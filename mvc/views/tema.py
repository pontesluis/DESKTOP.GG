"""Camada VIEW — Tema e helpers visuais.

Apenas apresentação: paleta de cores e fábricas de widgets.
"""

import tkinter as tk

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
    r, g, b = (int(hex_cor[i:i + 2], 16) for i in (0, 2, 4))
    return f"#{max(0, r - 30):02x}{max(0, g - 30):02x}{max(0, b - 30):02x}"


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
