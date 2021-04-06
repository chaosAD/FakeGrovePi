import threading, math
from FakeDevices import *

MAX_DIGITAL_PIN = 9
MAX_ANALOG_WRITE_PIN = 9
MAX_ANALOG_READ_PIN = 2

digital_pins = [0,0,0,0,0,0,0,0,0,0]
analog_pins  = [0,0,0]
devices = {}

thread_lock = threading.Lock()

def pinMode(port, mode):
    print("**config: pin {} has been set to {}**".format(port, mode))

def assert_analog_write_pin(pin):
    if pin > MAX_ANALOG_WRITE_PIN or pin < 0:
        raise Exception(f'Analog write pin {pin} does not exist')

def analogWrite(pin, value):
    assert_analog_write_pin(pin)
    print(f'analogWrite({pin}, {value})')

def assert_analog_read_pin(pin):
    if pin > MAX_ANALOG_READ_PIN or pin < 0:
        raise Exception(f'Analog read pin {pin} does not exist')

def analogRead(pin):
    assert_analog_read_pin(pin)
    name = f'A{pin}'
    if name not in devices:
        raise Exception(f'Analog read pin {pin} has not been configured')
    return devices[name].get_value()

def assert_digital_pin(pin):
    if pin > MAX_DIGITAL_PIN or pin < 0:
        raise Exception(f'Digital pin {pin} does not exist')

def digitalWrite(pin, value):
    assert_digital_pin(pin)
    name = f'D{pin}'
    if name not in devices:
        raise Exception(f'Digital pin {pin} has not been configured')
    dig_pin = devices[name]
    dig_pin.set_value(value)
    if dig_pin.verbose:
        print(f'digitalWrite({pin}, {value})')

def digitalRead(pin):
    assert_digital_pin(pin)
    name = f'D{pin}'
    if name not in devices:
        raise Exception(f'Digital pin {pin} has not been configured')
    return devices[name].get_value()

# Read temp in Celsius from Grove Temperature Sensor
def temp(pin, model='1.0'):
  # each of the sensor revisions use different thermistors, each with their own B value constant
  if model == '1.2':
    bValue = 4250  # sensor v1.2 uses thermistor ??? (assuming NCP18WF104F03RC until SeeedStudio clarifies)
  elif model == '1.1':
    bValue = 4250  # sensor v1.1 uses thermistor NCP18WF104F03RC
  else:
    bValue = 3975  # sensor v1.0 uses thermistor TTC3A103*39H
  a = analogRead(pin)
  resistance = (float)(1023 - a) * 10000 / a
  t = (float)(1 / (math.log(resistance / 10000) / bValue + 1 / 298.15) - 273.15)
  return t

def dht(port, dht_type):
    assert_digital_pin(port)
    name = f'DHT{port}'
    if name not in devices:
        raise Exception(f'DHT on pin {port} has not been configured')
    dht = devices[name]
    return [dht.get_temp_value(), dht.get_humidity_value()]

def ultrasonicRead(pin):
    assert_digital_pin(pin)
    name = f'Ultrasonic{pin}'
    if name not in devices:
        raise Exception(f'Ultrasonic ranger on pin {pin} has not been configured')
    return devices[name].get_value()

def version():
    return "%s.%s.%s" % (1, 4, 2)

gui = Gui()

class DigitalPin:
    def __init__(self, pin, name=None, verbose=True):
        self.state = 0
        self.verbose = verbose
        if name is None:
            name = f'Digital Pin {pin}'
        def checkbutton_callback():
            with thread_lock:
                self.state ^= 1
        assert_digital_pin(pin)
        if digital_pins[pin]:
            raise Exception(f'Digital pin {pin} already exists')
        digital_pins[pin] = 1
        devices[f'D{pin}'] = self
        self.checkbutton = GuiCheckbutton(gui, name, checkbutton_callback)

    def get_value(self):
        with thread_lock:
            return self.state

    def set_value(self, state):
        if state == 0:
            new_state = '!selected'
        else:
            new_state = 'selected'
        def set_to_value(tk_root):
            with thread_lock:
                self.checkbutton.widget.state([new_state])
                if new_state[0] == '!':
                    self.state = 0
                else:
                    self.state = 1
        gui.dcall(set_to_value)

class AnalogReadPin:
    def __init__(self, pin, name=None, min=0, max=1023):
        self.value = min
        if name is None:
            name = f'Analog Read Pin {pin}'
        def slider_callback(value):
            with thread_lock:
                self.value = int(value)
        assert_analog_read_pin(pin)
        if analog_pins[pin]:
            raise Exception(f'Analog read pin {pin} already exists')
        analog_pins[pin] = 1
        devices[f'A{pin}'] = self
        self.checkbutton = GuiSlider(gui, name, min, max, slider_callback)

    def get_value(self):
        with thread_lock:
            return self.value

class Ultrasonic:
    def __init__(self, pin, name=None):
        self.value = 0
        def slider_callback(value):
            with thread_lock:
                self.value = int(value)
        self.pin = pin
        if name is None:
            name = f'Ultrasonic Ranger (D{pin})'
        assert_digital_pin(pin)
        if digital_pins[pin]:
            raise Exception(f'Digital pin {pin} already been defined')
        pin_name = f'Ultrasonic{pin}'
        if pin_name in devices:
            raise Exception(f'{name} already exists')
        digital_pins[pin] = 1
        devices[pin_name] = self
        self.checkbutton = GuiSlider(gui, name, 0, 500, slider_callback)

    def get_value(self):
        with thread_lock:
            return self.value

class DHT:
    def __init__(self, pin, name=None):
        self.temp_value = self.humidity_value = 0
        def temp_callback(value):
            with thread_lock:
                self.temp_value = int(value)
        def humidity_callback(value):
            with thread_lock:
                self.humidity_value = int(value)
        self.pin = pin
        if name is None:
            name = f'DHT (D{pin})'
        assert_digital_pin(pin)
        if digital_pins[pin]:
            raise Exception(f'Digital pin {pin} already been defined')
        pin_name = f'DHT{pin}'
        if pin_name in devices:
            raise Exception(f'{name} already exists')
        digital_pins[pin] = 1
        devices[pin_name] = self
        self.temp = GuiSlider(gui, name + ' temperature \xb0C', 0, 110,
                              temp_callback)
        self.temp = GuiSlider(gui, name + ' humidity %', 0, 100,
                              humidity_callback)

    def get_temp_value(self):
        with thread_lock:
            return self.temp_value

    def get_humidity_value(self):
        with thread_lock:
            return self.humidity_value