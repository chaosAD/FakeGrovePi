import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import threading, time
from queue import Queue
from queue import Empty

import beeper
from grovepi import *
from mfrc522 import *

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
    def __init__(self, gui, name, listener):
        self.widget = None
        def create_checkbutton(tk_root):
            var = tk.BooleanVar()
            var.set(False)
            s = ttk.Style()
            s.configure('DPin.TCheckbutton', font=('Lucida Grande', 13))
            widget = ttk.Checkbutton(tk_root, text=name,
                                     variable=var,
                                     onvalue=True, offvalue=False,
                                     style='DPin.TCheckbutton',
                                     command=listener.on_event)
            listener.set_variables(widget, var)
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

class GuiMifareRfid:
    def __init__(self, gui, name, listener, card_num=0):
        def create_mifare_rfid(tk_root):
            num_var = self.num = tk.StringVar()
            num_var.set(str(card_num))
            card_num_entry = tk.Entry(tk_root, textvariable=num_var,
                                      font=('Lucida Grande', 16, 'normal'),
                                      background='Green')
            button = tk.Button(tk_root, text=name,
                               font=('Lucida Grande', 14, 'normal'))
            # http://epydoc.sourceforge.net/stdlib/Tkinter.Event-class.html
            # https://subscription.packtpub.com/book/web_development/9781788622301/1/ch01lvl1sec20/handling-mouse-and-keyboard-events
            button.bind("<ButtonPress>", listener.on_touch)
            button.bind("<ButtonRelease>", listener.on_remove)
            listener.set_variables(card_num_entry, num_var)
#            card_num_entry.grid(row=0,column=0)
#            button.grid(row=0,column=1)
            card_num_entry.pack(expand=1)
            button.pack(expand=1)
        GuiSeparator(gui)
        gui.dcall(create_mifare_rfid)

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
        self.msg_queue.put(func)

    def quit(self):
        def shutdown(tk_root):
            self.root.quit()
        self.dcall(shutdown)
        self.join()

    def add(self, widget):
        widget.start(self)


###########################################################

class DigitalPin:
    __num_of_sounder = 0

    def __init__(self, pin, name=None, should_sound=False, verbose=True):
        self.name = name
        self.verbose = verbose
        self.var = None
        self.should_sound = should_sound
        self.prev_state = False
        self.name = f'Digital Pin {pin}' if name is None else name
        assert_digital_pin(pin)
        if digital_pins[pin]:
            raise Exception(f'Digital pin {pin} already exists')
        digital_pins[pin] = 1
        devices[f'D{pin}'] = self

    def start(self, gui):
        buzzer_self = self
        class BuzzerEventListener:
            def __init__(self):
                self.checkbox = None
                self.var = None
            def on_event(self):
                buzzer_self.handle_noise()
            def set_variables(self, checkbutton, var):
                self.checkbox = checkbutton
                self.var = var
                buzzer_self.var = var
        # https://stackoverflow.com/questions/270648/tkinter-invoke-event-in-main-loop
        self.checkbutton = GuiCheckbutton(gui, self.name, BuzzerEventListener())

    def set_value(self, value):
        while not self.var:
            # Wait till self.var is set by the caller of set_variables(.)
            time.sleep(0.05)
        self.var.set(value)
        self.handle_noise()

    def get_value(self):
        while not self.var:
            # Wait till self.var is set by the caller of set_variables(.)
            time.sleep(0.05)
        return int(self.var.get())

    def handle_noise(self):
        if self.should_sound:
            with thread_lock:
                current_state = self.var.get()
                if current_state == True:
                    if DigitalPin.__num_of_sounder == 0:
                        beeper.start_beeping()
                    if current_state != self.prev_state:
                        DigitalPin.__num_of_sounder += 1
                        self.prev_state = current_state
                else:
                    if current_state != self.prev_state:
                        DigitalPin.__num_of_sounder -= 1
                        self.prev_state = current_state
                    if DigitalPin.__num_of_sounder == 0:
                        beeper.stop_beeping()

class AnalogReadPin:
    def __init__(self, pin, name=None, min=0, max=1023):
        self.value = min
        self.min = min
        self.max = max
        self.name = f'Analog Read Pin {pin}' if name is None else name
        assert_analog_read_pin(pin)
        if analog_pins[pin]:
            raise Exception(f'Analog read pin {pin} already exists')
        analog_pins[pin] = 1
        devices[f'A{pin}'] = self


    def start(self, gui):
        def slider_callback(value):
            with thread_lock:
                self.value = int(value)
        self.checkbutton = GuiSlider(gui, self.name, self.min, self.max, slider_callback)

    def get_value(self):
        with thread_lock:
            return self.value

class Ultrasonic:
    def __init__(self, pin, name=None):
        self.value = 0
        self.pin = pin
        self.name = f'Ultrasonic Ranger (D{pin})' if name is None else name
        assert_digital_pin(pin)
        if digital_pins[pin]:
            raise Exception(f'Digital pin {pin} already been defined')
        pin_name = f'Ultrasonic{pin}'
        if pin_name in devices:
            raise Exception(f'{name} already exists')
        digital_pins[pin] = 1
        devices[pin_name] = self

    def start(self, gui):
        def slider_callback(value):
            with thread_lock:
                self.value = int(value)
        self.checkbutton = GuiSlider(gui, self.name, 0, 500, slider_callback)

    def get_value(self):
        with thread_lock:
            return self.value

class DHT:
    def __init__(self, pin, name=None):
        self.temp_value = self.humidity_value = 0
        self.pin = pin
        self.name = f'DHT (D{pin})' if name is None else name
        assert_digital_pin(pin)
        if digital_pins[pin]:
            raise Exception(f'Digital pin {pin} already been defined')
        pin_name = f'DHT{pin}'
        if pin_name in devices:
            raise Exception(f'{name} already exists')
        digital_pins[pin] = 1
        devices[pin_name] = self

    def start(self, gui):
        def temp_callback(value):
            with thread_lock:
                self.temp_value = int(value)
        def humidity_callback(value):
            with thread_lock:
                self.humidity_value = int(value)
        self.temp = GuiSlider(gui, self.name + ' temperature \xb0C', 0, 110,
                              temp_callback)
        self.temp = GuiSlider(gui, self.name + ' humidity %', 0, 100,
                              humidity_callback)

    def get_temp_value(self):
        with thread_lock:
            return self.temp_value

    def get_humidity_value(self):
        with thread_lock:
            return self.humidity_value


class MifareRfid():
    def __init__(self, file, name=None):
        self.filename = file
        self.name = f'Mifare Card Reader/Writer' if name is None else name

    def start(self, gui):
        storage = CardStorage(self.filename)
        SimpleMFRC522.set_writer(storage)
        rfids = storage.read()
        class TagEventListener():
            def __init__(self):
                self.card_num = None
            def on_touch(self, event):
                num = self.card_num.get()
                with thread_lock:
                    if not num.isnumeric():
                        return
                    card_name = CardStorage.get_card_name(int(num))
                    if card_name in rfids:
                        SimpleMFRC522.load_data(rfids[card_name])
            def on_remove(self, event):
                with thread_lock:
                    SimpleMFRC522.load_data(None)
            def set_variables(self, tk_entry, var):
                def callback(*args):
                    txt = tk_entry.get()
                    if txt == '':
                        tk_entry.configure({'background': 'White'})
                        return
                    if not txt.isnumeric():
                        tk_entry.configure({'background': 'Red'})
                        return
                    card_name = CardStorage.get_card_name(int(txt))
                    if card_name in rfids:
                        tk_entry.configure({'background': 'Green'})
                    else:
                        tk_entry.configure({'background': 'Magenta'})
                self.card_num = var
                var.trace(mode="w", callback=callback)
        card_names = sorted(rfids.keys())
        c = card_names[0].split('_')
        self.mfrc522 = GuiMifareRfid(gui, self.name, TagEventListener(), int(c[1]))
