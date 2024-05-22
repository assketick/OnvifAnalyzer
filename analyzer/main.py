import os
import asyncio
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from services import OnvifAnalyzer
import logging

logger = logging.getLogger("Interface")


class Window(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.title("Onvif Analyzer")

        WIDTH = 450
        HEIGHT = 300
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (WIDTH/2)
        y = (hs/2) - (HEIGHT/2)
        self.geometry('%dx%d+%d+%d' % (WIDTH, HEIGHT, x, y))
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.create_UI()

    def _get_entries_values(self):
        entries = ["ip_entry", "port_entry", "username_entry", "password_entry", "save_entry"]
        values = []
        for entry in entries:
            e_obj = getattr(self, entry)
            value = e_obj.get()
            if value == "":
                messagebox.showerror('Ошибка', 'Заполните все поля')
                return

            values += [value]
        return values
    
    def _pretty_path(self, path):
        path_slitted = path.split('/')
        if len(path_slitted) < 5:
            return path
        return '/'.join(path_slitted[:2]) + '/.../' + '/'.join(path_slitted[-3:])
    
    def _browse_folder(self):
        self.save_entry.config(state=tk.ACTIVE)
        self.folder_selected = filedialog.askdirectory()
        pretty_path = self._pretty_path(self.folder_selected)
        logger.warning(f"path - {[pretty_path]}")
        if self.folder_selected:
            self.save_entry.delete(0, tk.END)
            self.save_entry.insert(0, pretty_path)
        self.save_entry.config(state=tk.DISABLED)

    def _check_folder_path(self, path):
        if not os.path.exists(path):
            messagebox.showerror("Ошибка", "Указан неверный путь для сохранения файла!")
            return
        return True

    def _exit_app(self):
        self.destroy()

    def _create_frames(self):
        ''' Creation frame to display widgets '''
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.grid(row=5, column=0, columnspan=2, pady=5)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.columnconfigure(2, weight=1)

        self.status_frame = ttk.Frame(self.frame)
        self.status_frame.grid(row=6, column=0, columnspan=2, pady=5)
        self.button_frame.columnconfigure(0, weight=1)

    def _create_widgets(self):
        ''' Widgets creation '''
        # Поле ввода IP устройства
        ttk.Label(self.frame, text="IP устройства:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ip_entry = ttk.Entry(self.frame, width=30)
        self.ip_entry.grid(row=0, column=1, pady=5)

        # Поле ввода порта
        ttk.Label(self.frame, text="Порт:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.port_entry = ttk.Entry(self.frame, width=30)
        self.port_entry.grid(row=1, column=1, pady=5)

        # Поле ввода имени пользователя
        ttk.Label(self.frame, text="Имя пользователя:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(self.frame, width=30)
        self.username_entry.grid(row=2, column=1, pady=5)

        # Поле ввода пароля
        ttk.Label(self.frame, text="Пароль:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(self.frame, width=30, show="*")
        self.password_entry.grid(row=3, column=1, pady=5)

        # Поле "Сохранить результаты"
        ttk.Label(self.frame, text="Сохранить результаты:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.save_entry = ttk.Entry(self.frame, width=30)
        self.save_entry.config(state=tk.DISABLED)
        self.save_entry.grid(row=4, column=1, pady=5)

        # Кнопка для выбора папки
        self.browse_button = ttk.Button(self.button_frame, text="Обзор", command=self._browse_folder)
        self.browse_button.grid(row=0, column=0, padx=5)

        # Кнопка "Подключиться"
        self.connect_button = ttk.Button(self.button_frame, text="Подключиться", command=self.connect)
        self.connect_button.grid(row=0, column=1, padx=5)

        # Кнопка "Выйти"
        self.exit_button = ttk.Button(self.button_frame, text="Выйти", command=self._exit_app)
        self.exit_button.grid(row=0, column=2, padx=5)

        self.status_label = ttk.Label(self.status_frame, text="")
        self.status_label.grid(row=0, column=0, padx=5)

    def create_UI(self):
        ''' User UI creation '''
        self._create_frames()
        self._create_widgets()

    def connect(self):
        values = self._get_entries_values()
        if not values or not self._check_folder_path(self.folder_selected):
            return

        ip, port, username, password, _ = values
        try:
            ip, port, username, password, folder_path = self._get_entries_values()
            dt = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")
            to_save = self.folder_selected + f"/analyze-{dt}.xlsx"
            self.analyzer = OnvifAnalyzer(ip, port, username, password, to_save)
            self.status_label.config(text="Анализируем...")
            self.status_label.update()
            asyncio.run(self.analyzer.analyze())
            messagebox.showinfo('Результат работы', f'Результат сохранен в {to_save}!')
            self.status_label.config(text="Анализ завершен!")
        except ValueError as e:
            logger.error(f"Exception - {e}")
            messagebox.showerror('Ошибка', 'Заполните все поля')
        except IndexError as e:
            logger.error(f"Exception - {e}")
            messagebox.showerror('Ошибка', 'Не удалось найти путь до wsdl файлов')
        except Exception as e:
            logger.error(f"Exception - {e}")
            messagebox.showerror('Ошибка', 'Не удалось подключиться к устройству! Проверьте данные авторизации.')


if __name__ == '__main__':
    window = Window()
    window.mainloop()