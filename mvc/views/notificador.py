"""Camada VIEW — Notificações.

DEPENDÊNCIA: usado pontualmente para feedback ao usuário via diálogos.
"""

from tkinter import messagebox


class Notificador:
    @staticmethod
    def alerta(titulo, msg):
        messagebox.showinfo(titulo, msg)

    @staticmethod
    def erro(msg):
        messagebox.showerror("Erro", msg)

    @staticmethod
    def confirmar(msg):
        return messagebox.askyesno("Confirmar", msg)
