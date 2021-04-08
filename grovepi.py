import threading, math
#from FakeDevices import *

MAX_DIGITAL_PIN = 9
MAX_ANALOG_WRITE_PIN = 9
MAX_ANALOG_READ_PIN = 2

thread_lock = threading.Lock()
digital_pins = [0,0,0,0,0,0,0,0,0,0]
analog_pins  = [0,0,0]
devices = {}

def assert_analog_write_pin(pin):
    if pin > MAX_ANALOG_WRITE_PIN or pin < 0:
        raise Exception(f'Analog write pin {pin} does not exist')

def assert_analog_read_pin(pin):
    if pin > MAX_ANALOG_READ_PIN or pin < 0:
        raise Exception(f'Analog read pin {pin} does not exist')

def assert_digital_pin(pin):
    if pin > MAX_DIGITAL_PIN or pin < 0:
        raise Exception(f'Digital pin {pin} does not exist')

def pinMode(port, mode):
    print("**config: pin {} has been set to {}**".format(port, mode))

def analogWrite(pin, value):
    assert_analog_write_pin(pin)
    print(f'analogWrite({pin}, {value})')

def analogRead(pin):
    assert_analog_read_pin(pin)
    name = f'A{pin}'
    if name not in devices:
        raise Exception(f'Analog read pin {pin} has not been configured')
    return devices[name].get_value()

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
    return "%s.%s.%s" % (1, 4, 4)

