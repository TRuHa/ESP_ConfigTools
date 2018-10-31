from libreria.umqtt import MQTTClient
from time import sleep

import machine

pin = machine.Pin(0, machine.Pin.OUT)
server = "192.168.1.41"
topic = b"rele"
ID = 'ESP_Rele'

pin.on()
print('[|] Rele: ON')


def sub_cb(topic, msg):
    state = int(msg.decode())
    pin.value(state)
    if state == 1:
        state = 'ON'
    elif state == 0:
        state = 'OFF'

    print('[|] Rele:', state)


def do_connect():
    c = MQTTClient(ID, server)
    c.set_callback(sub_cb)
    print('[-] Conectando al broker...')

    while True:
        try:
            c.connect()
            break

        except OSError:
            print('[!] Imposible conectar con el servidor.')
            sleep(60)

    print('[|] Conectado correctamente.')

    c.publish(topic, str(pin.value()))
    c.subscribe(topic)
    print('[-] Subcrito al canal: rele.')

    return c


b = do_connect()

while True:
    try:
        if True:
            b.wait_msg()
        else:
            b.check_msg()
            sleep(0.1)

    except OSError:
        try:
            b.disconnect()
        except OSError:
            machine.reset()

        pin.on()
        print('[!] Desconectado del servidor')
        b = do_connect()
