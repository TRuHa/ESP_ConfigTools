from web import server
import ubinascii
import network
import machine
import ujson

ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)

items = []

print('[-] Iniciando sistema.')
with open("config.json", "r") as outfile:
    data = ujson.load(outfile)
    subdata = data['config']
    for item in subdata:
        items.append(item['network'])
        items.append(item['wifi'])
        items.append(item['mqtt'])
        items.append(item['mode'])

if 'NO' in items:
    print('[!] Sistema sin configuracion.')

    mac = ubinascii.hexlify(ap_if.config('mac'), ':').decode()
    essid = 'ESP_Config_' + mac

    ap_if.active(True)
    ap_if.config(essid=essid, authmode=0)

    server.run()

    machine.reset()
