import time, ubinascii, machine
from machine import UART, Pin, SoftI2C
from micropython import const
from micropyGPS import MicropyGPS
from cayennelpp import CayenneLPP

stop = False
LED_GPIO = const(2)  # define a constant
led = machine.Pin(LED_GPIO, mode=machine.Pin.OUT)  # GPIO output
led = Pin(2, Pin.OUT)
relay1 = Pin(12, Pin.OUT)
uart1 = machine.UART(1, baudrate=9600, rx=25, tx=12, timeout=10)
uart2 = UART(2, 9600, timeout=300)
my_gps = MicropyGPS(+7)
rstr = ""

def sendATcommand(ATcommand):
    print("Command: {0}\r\n".format(ATcommand))
    print(ATcommand)
    uart2.write("{0}\r\n".format(ATcommand))
    rstr = uart2.read().decode("utf-8")
    print(rstr)
    return rstr

sendATcommand("AT+CADR=0")
sendATcommand("AT+CDATARATE=2")
sendATcommand("AT+CULDLMODE=1")
sendATcommand("AT+CDEVEUI?")
sendATcommand("AT+CAPPKEY?")
sendATcommand("AT+CAPPEUI?")
sendATcommand("AT+CJOIN=1,0,8,1")
time.sleep(20.0)
arstr = ""
arstr = sendATcommand("AT+CSTATUS?")

while "+CSTATUS:04" not in arstr:
    print("Retry OTAA Continue")
    sendATcommand("AT+CJOIN=1,0,8,2")
    time.sleep(20.0)
    arstr = ""
    arstr = sendATcommand("AT+CSTATUS?")

    if "+CSTATUS:04" in arstr:
        print("++++OTAA OK+++++")
        break
if "+CSTATUS:04" in arstr:
    print("++++OTAA OK+++++")
    # Send Sample data
    sendATcommand("AT+DTRX=0,2,6,445566")
cnt = 1
relay1 = Pin(12, Pin.OUT)
button = Pin(4, Pin.IN)
button.value()
###LOOP OTAA
print("Join Success")
###END LOOP OTAA
time.sleep(5.0)
cnt = 1
while True:
    print("\r\n\r\nPacket No #{}".format(cnt))
    my_sentence = uart1.readline()
    print(my_sentence)
    for x in str(my_sentence):
        my_gps.update(x)
    print("---------------------------  ")
    print("Date:", my_gps.date_string("s_dmy"))
    print("Time:", my_gps.timestamp)
    print(
        "Time: {}:{}:{}".format(
            my_gps.timestamp[0], my_gps.timestamp[1], my_gps.timestamp[2]
        )
    )
    print("Direction:", my_gps.course)
    print("satellites_in_use", my_gps.satellites_in_use)
    print("my_gps.altitude", my_gps.altitude)
    lat1 = my_gps.latitude[0] + my_gps.latitude[1] / 60
    lon1 = my_gps.longitude[0] + my_gps.longitude[1] / 60
    alt = my_gps.altitude
    print("LATITUDE %2.6f" % float(lat1))
    print("LONGIITUDE %2.6f" % float(lon1))
    print("ALTITUDE %f" % float(my_gps.altitude))
    print("Speed (Km/hr):", my_gps.speed_string("kph"))
    print("Speed (mph):", my_gps.speed_string("mph"))
    print("Speed (mph):", my_gps.speed[1])
    speed = my_gps.speed[1]
    print(speed)
    print("---------------------------  ")

    c = CayenneLPP()
    #c.addTemperature(1, 50.0)
    c.addGPS(7, lat1, lon1, alt)
    b = ubinascii.hexlify(c.getBuffer())

    print("")
    print("************    Sending Data Status   **************")
    led.value(1)
    sendATcommand("AT+DTRX=0,1,{0},{1}".format(int(len(b)), (b.decode("utf-8"))))

    print("********Finish Sending & Receiving Data Status******")
    led.value(0)
    cnt = cnt + 1
    time.sleep(5.0)
