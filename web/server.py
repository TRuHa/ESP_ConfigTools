def show_web(html):
    header = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'.encode()
    with open("page/network.html", "rb") as file:
        body = header + file.read()

    response = header + body

    return response


def run():
    from time import sleep
    import socket
    import ujson
    import os

    path_page = "page"

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][- 1]

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(addr)
    sock.listen(1)

    if not 'config' in os.listdir():
        os.mkdir('config')

    print('[-] Iniciado servidor WEB.')
    print('[|] Esperando cliente...')

    clients = []

    while True:
        client, addr = sock.accept()

        if not addr[0] in clients:
            clients.append(addr[0])
            print('[+] Cliente %s conectado.' % addr[0])

        msg1 = client.recv(1500).decode()
        print(msg1)
        msg1 = msg1.split('\n')

        extract = msg1[0]
        extract = extract.split(' ')
        method = extract[0]
        try:
            html = extract[1].lstrip('/')
        except IndexError:
            html = ''

        if method == 'GET':
            if 'next' in html:
                try:
                    if last == '':
                        html = 'network.html'
                    elif last == 'network':
                        html = 'wifi.html'
                    elif last == 'wifi':
                        html = 'mqtt.html'
                    elif last == 'mqtt':
                        html = 'mode.html'
                    elif last == 'mode':
                        html = 'overview.html'

                except:
                    html = ''

            if html == '' or html == 'network.html':
                last = 'network'

            elif html == 'confirmation.html':
                header = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'.encode()
                with open("page/confirmation.html", "rb") as file:
                    response = header + file.read()

            else:
                print('[-] Error: pagina no encontrada')
                header = 'HTTP/1.1 404 Not Found\n\n'.encode()
                response = '<html><head><title>Config WiFi</title></head><body><center><h2>Error 404: File not ' \
                           'found</h2><p>Python HTTP Server</p></center></body></html>'.encode()

                response = header + response

        elif method == 'POST':
            msg2 = client.recv(1500).decode()
            print(msg2)
            msg2 = msg2.split('\n')

            count = len(msg2)
            answer = msg2[count - 1]
            answer = answer.split('&')

            print(last)

            if last == '' or last == 'network':
                last = 'network'
                try:
                    method = answer[0].lstrip('method=')
                    ip = answer[1].lstrip('ip=')
                    mask = answer[2].lstrip('mask=')
                    gate = answer[3].lstrip('gate=')
                    dns = answer[4].lstrip('dns=')

                    data = {
                        'network': [
                            {
                                'method': method,
                                'ip': ip,
                                'mask': mask,
                                'gate': gate,
                                'dns': dns
                            }
                        ]
                    }

                    with open("config/network.json", "w") as outfile:
                        outfile.write(ujson.dumps(data))

                    print(os.listdir('config'))

                except IndexError:
                    print('[!] Algo salio mal')
                    last = ''

            elif last == 'wifi':
                last = 'wifi'
                try:
                    essid = answer[0].lstrip('essid=')
                    psk = answer[1].lstrip('psk=')

                    if '+' in essid:
                        essid = essid.replace("+", " ")

                    data = {
                        'wifi': [
                            {
                                'essid': essid,
                                'psk': psk,
                            }
                        ]
                    }

                    with open("config/wifi.json", "w") as outfile:
                        outfile.write(ujson.dumps(data))

                    print(os.listdir('config'))

                except IndexError:
                    print('[!] Algo salio mal')
                    last = 'network'

            elif last == 'mqtt':
                last = 'mqtt'
                try:
                    id = answer[0].lstrip('id=')
                    broker = answer[1].lstrip('broker=')
                    port = answer[2].lstrip('port=')
                    user = answer[3].lstrip('user=')
                    psw = answer[4].lstrip('psw=')
                    topic = answer[5].lstrip('topic=')

                    if '%2F' in topic:
                        topic = topic.replace("%2F", "/")

                    data = {
                        'mqtt': [
                            {
                                'id': id,
                                'broker': broker,
                                'port': port,
                                'user': user,
                                'psw': psw,
                                'topic': topic
                            }
                        ]
                    }

                    with open("config/mqtt.json", "w") as outfile:
                        outfile.write(ujson.dumps(data))

                    print(os.listdir('config'))

                except IndexError:
                    print('[!] Algo salio mal')
                    last = 'wifi'

            elif last == 'mode':
                last = 'mode'
                try:
                    model = answer[0].lstrip('model=')
                    type = answer[1].lstrip('type=')

                    if '+' in type:
                        type = type.replace("+", " ")

                    port = answer[2].lstrip('port=')

                    data = {
                        'mode': [
                            {
                                'model': model,
                                'type': type,
                                'port': port,
                            }
                        ]
                    }
                    with open("config/mode.json", "w") as outfile:
                        outfile.write(ujson.dumps(data))

                    print(os.listdir('config'))

                except IndexError:
                    print('[!] Algo salio mal')
                    last = 'mqtt'

            elif last == 'overview':
                print('[-] Reiniciando el sistema.')
                client.close()

                sleep(1)

                break

            print('[-] Datos %s guardados.' % last)

            header = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'.encode()
            with open(path_page + '/confirmation.html', "rb") as file:
                response = header + file.read()

        client.send(response)
        client.close()


if __name__ == '__main__':
    run()
