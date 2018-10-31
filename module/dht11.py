from libreria.umqtt import MQTTClient
from time import sleep

import machine
import dht


def pub(server, temp, humd):
    c = MQTTClient("client_DHT11", server)
    while True:
        try:
            c.connect()
            print('[-] Conectado correctamente al broker.')
            c.publish(b"esp_temp", str(temp))
            print('[|] Temperatura: ', str(temp), 'ºC')
            c.publish(b"esp_humd", str(humd))
            print('[|] Humedad: ', str(humd), '%')
            c.disconnect()
            print('[-] Desconectado.')
            break

        except:
            print('[*] Fallo de conexion, reintentando..."')
            sleep(10)
            continue


dht11 = dht.DHT11(machine.Pin(2))

while True:
    server = "192.168.1.41"

    dht11.measure()

    temp = dht11.temperature()
    #print('Temperatura: ', str(temp), 'ºC')
    humd = dht11.humidity()
    #print('Humedad: ', str(humd), '%')

    pub(server, temp, humd)

    sleep(300)
