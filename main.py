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

try:
    with open('config/wifi.json') as wifi:
        data = ujson.load(wifi)
        for d in data['wifi']:
            essid = d['essid']
            psk = d['psk']
except OSError:
    print('[!] Configuracion no encontrada, reiniciado...')
    sleep(2)
    machine.reset()

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
        with open('page/network.json') as ujson_network:
            data = ujson.load(ujson_network)
            for d in data['network']:
                method = d['method']
                ip = d['ip']
                mask = d['mask']
                gate = d['gate']
                dns = d['dns']

        if method == 'DHCP':
            ip = sta_if.ifconfig()

        else:
            ip = sta_if.ifconfig(ip, mask, gate, dns)

        print('[-] Conexion establecida correctamente.')
        print('[|] IP: ', ip[0])
        print('[|] MASK: ', ip[1])
        print('[|] GATEWAY: ', ip[2])
        print('[|] DNS: ', ip[3])

        sleep(3)

        break

with open('page/mode.json') as ujson_network:
    data = ujson.load(ujson_network)
    for d in data['mode']:
        model = d['model']
        type = d['type']
        port = d['port']

