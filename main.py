from time import sleep
import network
import machine
import ujson
import os

ap_if = network.WLAN(network.AP_IF)
sta_if = network.WLAN(network.STA_IF)

ap_if.active(False)
sta_if.active(True)

print('[-] Leyendo configuracion.')

with open("config.json", "r") as file:
    data = ujson.load(file)

    for item in data['network']:
        method = item['method']
        ip = item['ip']
        mask = item['mask']
        gate = item['gate']
        dns = item['dns']

    for item in data['wifi']:
        essid = item['essid']
        psk = item['psk']

    for d in data['mode']:
        model = d['model']
        type = d['type']
        gpio = d['gpio']

print('[-] Contectando a:', essid)

sta_if.connect(essid, psk)

count = 0
while True:
    if not sta_if.isconnected():
        print('[!] Imposible conectar a la WiFi, reintentando...')

        if count == 6:
            print('[!] Imposible establecer conexion. Reiniciando en modo AP.')
            os.remove('page\wifi.json')
            sleep(5)
            machine.reset()

        count += 1

        sleep(300)

    else:
        if method == 'DHCP':
            ip = sta_if.ifconfig()

        else:
            ip = sta_if.ifconfig((ip, mask, gate, dns))

        print('[-] Conexion establecida correctamente.')
        print('[|] IP: ', ip[0])
        print('[|] MASK: ', ip[1])
        print('[|] GATEWAY: ', ip[2])
        print('[|] DNS: ', ip[3])

        sleep(3)

        break

print('[-] Iniciando %s en modo: %s') % (model, type)

if model == 'ESP01':
    if type == 'Rele':
        from ESP01 import moduloRele

        moduloRele.run(gpio=gpio)

    elif type == 'DHT11':
        from ESP01 import sensorDHT11

        sensorDHT11.run(gpio=gpio)
