import random, math

def pinMode(port, mode):
    print("**config: pin {} has been set to {}**".format(port, mode))

def analogWrite(port, value):
    print(f'analogWrite({port}, {value})')

def analogRead(port):
    return random.randint(0, 1023)
    
def digitalWrite(port, value):
    print(f'digitalWrite({port}, {value})')

def digitalRead(port):
    return random.randint(0, 1)    

# Read temp in Celsius from Grove Temperature Sensor
def temp(pin, model = '1.0'):
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
    return [random.randint(19,37), random.randint(0,100)]
    
def ultrasonicRead(pin):
    return random.randint(0, 500)
    
def version():
    return "%s.%s.%s" % (1, 4, 0)
