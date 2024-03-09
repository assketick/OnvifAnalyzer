import asyncio
import pprint
import tkinter as tk
from services import get_services


class Window(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.title("Onvif Analyzer")

        WIDTH = 1200
        HEIGHT = 650
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
            # self.analyzer = OnvifAnalyzer(ip, port, username, password)
            # self.services = self.analyzer.get_services()
            # self._show_services()
        except:
            ...

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
        self.ip_label.pack(side=tk.LEFT, padx=4)
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
        # Listbox for services
        self.service_listbox = tk.Listbox(
            self.main_frame, 
            width=30,
            height=150
        )
        self.service_listbox.bind("<<ListboxSelect>>", self._on_service_select) # bind function to show capabilities
        self.service_listbox.pack(side=tk.LEFT, padx=20, pady=20)
        # Text box for capabilities
        self.functions_textbox = tk.Text(self.main_frame, width=200, height=200)
        self.functions_textbox.pack(side=tk.LEFT, padx=20, pady=17)

    def _show_services(self):
        for service_name in self.services.keys():
            self.service_listbox.insert(tk.END, service_name.capitalize())

    def _on_service_select(self, event):
        selected_index = self.service_listbox.curselection()
        if selected_index:
            selected_service = self.service_listbox.get(selected_index)
            self._show_capabilities(selected_service)

    def _show_capabilities(self, service_name):
        self.functions_textbox.config(state=tk.NORMAL)
        self.functions_textbox.delete('1.0', tk.END)
        capabilities = self.services.get(service_name.lower(), {})
        string_functions = pprint.pformat(capabilities, indent=2)
        self.functions_textbox.insert(tk.END, string_functions)
        self.functions_textbox.config(state=tk.DISABLED)

if __name__ == '__main__':
    window = Window()
    window.mainloop()