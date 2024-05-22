import tkinter as tk
from tkinter import messagebox


def show_message_box(message: str) -> str:
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askquestion("Подтверждение", message)
    root.destroy()
    return result

def ask_user(message: str) -> str:
    answer = show_message_box(message)
    if answer == "yes":
        return "Поддерживается"
    return "Не работает"
