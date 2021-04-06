import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import threading
from queue import Queue
from queue import Empty

SERVICE_DELAY = 100

thread_lock = threading.Lock()

class GuiSeparator:
    def __init__(self, gui, fill='x', expand=True):
        def create_separator(tk_root):
            separator = ttk.Separator(tk_root, orient='horizontal')
            separator.pack(fill=fill, expand=expand)
        gui.dcall(create_separator)

class GuiLabel:
    def __init__(self, gui, label_text):
        def create_label(tk_root):
            label = tk.Label(tk_root, text=label_text)
            label.pack(fill="x", expand=1)
        gui.dcall(create_label)

class GuiButton:
    def __init__(self, gui, name, callback):
        def create_button(tk_root):
            button = tk.Button(tk_root, text=name, command=callback)
            button.pack(expand=1)
        GuiSeparator(gui)
        gui.dcall(create_button)

class GuiCheckbutton:
    def __init__(self, gui, name, callback):
        self.widget = None
        def create_checkbutton(tk_root):
            self.var = tk.StringVar()
            s = ttk.Style()
            s.configure('Dx.TCheckbutton', font=('Lucida Grande', 12))
            widget = ttk.Checkbutton(tk_root, text=name,
                                     variable=self.var,
                                     onvalue='yes', offvalue='no',
                                     style='Dx.TCheckbutton',
                                     command=callback)
            widget.pack(anchor='w', expand=1)
            self.widget = widget
        self.gui = gui
        GuiSeparator(gui)
        gui.dcall(create_checkbutton)

class GuiSlider:
    def __init__(self, gui, name, min, max, callback):
        def create_slider(tk_root):
            fontStyle = tkFont.Font(tk_root, family="Lucida Grande", size=14)
            slider = tk.Scale(tk_root, from_=min, to=max,
                                orient=tk.HORIZONTAL,
                                font=fontStyle,
                                label=name,
                                command=callback)
            slider.set(min)
            slider.pack(fill='x', expand=1)
        GuiSeparator(gui)
        gui.dcall(create_slider)

class Gui(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
        self.msg_queue = Queue()
        self.root = None

    def get_msg_queue(self):
        return self.msg_queue

    def callback(self):
        self.root.quit()

    def run_service(self):
        self.root.after(SERVICE_DELAY, self.run_service)
        if self.root is None:
            return
        try:
            while True:
                msg = self.msg_queue.get(timeout=0.00001)
                msg(self.root)
        except Empty:
            pass

    def run(self):
        root = self.root = tk.Tk()
#        root.geometry('300x100')
        root.minsize(300, 10)
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        self.root.title('Fake Devices')
        self.root.after(SERVICE_DELAY, self.run_service)
        self.root.mainloop()

    def dcall(self, func):
        self.get_msg_queue().put(func)

    def quit(self):
        def shutdown(tk_root):
            self.root.quit()
        self.dcall(shutdown)
        self.join()