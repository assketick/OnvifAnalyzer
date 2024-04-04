import asyncio
import pprint
import tkinter as tk
from tkinter import messagebox
from services import OnvifAnalyzer
from httpx import ConnectTimeout


class Window(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.title("Onvif Analyzer")

        WIDTH = 1200
        HEIGHT = 50
        # calculate monitor size to center window
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (WIDTH/2)
        y = (hs/2) - (HEIGHT/2)
        self.geometry('%dx%d+%d+%d' % (WIDTH, HEIGHT, x, y))
        self.resizable(False, False)
        
        self.create_UI()
    
    def create_UI(self):
        ''' User UI creation '''
        self._create_frames()
        self._create_widgets()

    def _get_connection_attributes(self):
        ip = self.ip_entry.get()
        port = self.port_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        return ip, port, username, password

    def connect(self):
        try:
            ip, port, username, password = self._get_connection_attributes()
            self.analyzer = OnvifAnalyzer(ip, port, username, password)
            self.services = asyncio.run(self.analyzer.get_services())
            messagebox.showinfo('Результат работы', 'Создан файл output/res.xlsx!')
            exit()
        except ValueError:
            messagebox.showerror('Ошибка', 'Заполните все поля')
        except IndexError:
            messagebox.showerror('Ошибка', 'Не удалось найти путь до wsdl файлов')
        except ConnectTimeout:
            messagebox.showerror('Ошибка', 'Не удалось подключиться к устройству! Проверьте данные авторизации.')

    def _create_frames(self):
        ''' Creation frame to display widgets '''
        self.connection_frame = tk.Frame()
        self.connection_frame.pack(anchor=tk.NW, fill='both')
        self.main_frame = tk.Frame()
        self.main_frame.pack(anchor=tk.NW, fill='both')

    def _create_widgets(self):
        ''' Widgets creation '''
        # Labels and Entries for connection
        self.ip_label = tk.Label(self.connection_frame, text="IP:")
        self.ip_label.pack(side=tk.LEFT, anchor='center', padx=4)
        self.ip_entry = tk.Entry(self.connection_frame)
        self.ip_entry.pack(side=tk.LEFT)
        self.port_label = tk.Label(self.connection_frame, text="Port:")
        self.port_label.pack(side=tk.LEFT, padx=4)
        self.port_entry = tk.Entry(self.connection_frame)
        self.port_entry.pack(side=tk.LEFT)
        self.username_label = tk.Label(self.connection_frame, text="Username:")
        self.username_label.pack(side=tk.LEFT, padx=4)
        self.username_entry = tk.Entry(self.connection_frame)
        self.username_entry.pack(side=tk.LEFT)
        self.password_label = tk.Label(self.connection_frame, text="Password")
        self.password_label.pack(side=tk.LEFT, padx=4)
        self.password_entry = tk.Entry(self.connection_frame, show='*')
        self.password_entry.pack(side=tk.LEFT)
        # Button for connection
        self.connection_button = tk.Button(
            self.connection_frame, 
            text='Подключиться', 
            command=self.connect
        )
        self.connection_button.pack(side=tk.LEFT, padx=4)


if __name__ == '__main__':
    window = Window()
    window.mainloop()