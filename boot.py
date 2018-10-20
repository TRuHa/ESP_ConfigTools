from web import server

import ubinascii
import network
import machine
import os

ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)

print('[-] Iniciando sistema.')
check_file = "wifi.json" in os.listdir('config')

if not check_file:
    print('[!] Sistema sin configuracion.')

    mac = ubinascii.hexlify(ap_if.config('mac'),':').decode()
    essid = 'ESP_Config_' + mac

    ap_if.active(True)
    ap_if.config(essid=essid, authmode=0)

    server.run()

    machine.reset()
