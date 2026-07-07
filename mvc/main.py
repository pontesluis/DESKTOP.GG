"""PONTO DE ENTRADA.

Inicializa o Tk e entrega o controle ao Controller, que por sua vez monta
a View e conecta o Model.

Execute com:  python -m mvc.main   (a partir da pasta pasted_text)
"""

import tkinter as tk

from .controllers import AppController


def main():
    root = tk.Tk()
    AppController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
