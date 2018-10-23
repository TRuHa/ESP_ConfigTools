def show_web(html):
    header = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'.encode()
    with open("page/" + html, "rb") as file:
        body = header + file.read()

    return header, body


def run():
    global last
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
    webs = ['network.html', 'wifi.html', 'mqtt.html', 'mode.html']

    while True:
        client, addr = sock.accept()

        if not addr[0] in clients:
            clients.append(addr[0])
            print('[+] Cliente %s conectado.' % addr[0])

        msg1 = client.recv(1500).decode()
        msg1 = msg1.split('\n')

        extract = msg1[0]
        extract = extract.split(' ')
        method = extract[0]

        try:
            html = extract[1].lstrip('/')
            if html == '':
                html = 'network.html'
        except IndexError:
            html = 'network.html'

        if method == 'GET':
            if 'index' in html:
                html = webs[last+1]

            if html in webs:
                header, body = show_web(html)

            elif html == 'confirmation.html':
                header = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'.encode()
                body = '<center><h4>Configuration saved successfully.</h4><form method="get" ' \
                       'action="next.html"><button type="submit">Next</button></form></center>'.encode()

            else:
                print('[-] Error: pagina no encontrada')
                header = 'HTTP/1.1 404 Not Found\n\n'.encode()
                body = '<center><h4>Error 404: File not found</h4><p>Python HTTP Server</p></center>'.encode()

            last = webs.index(html)

        elif method == 'POST':
            msg2 = client.recv(1500).decode()
            msg2 = msg2.split('\n')

            count = len(msg2)
            answer = msg2[count - 1]
            answer = answer.split('&')

            if last == '' or last == 'network':
                last = 'network'

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

            elif last == 'wifi':
                last = 'wifi'

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

            elif last == 'mqtt':
                last = 'mqtt'

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

            elif last == 'mode':
                last = 'mode'

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

            elif last == 'overview':
                print('[-] Reiniciando el sistema.')
                client.close()

                sleep(1)

                break

            print('[-] Datos %s guardados.' % last)

            header = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'.encode()
            with open(path_page + '/confirmation.html', "rb") as file:
                response = header + file.read()

        response = header + body

        client.send(response)
        client.close()


if __name__ == '__main__':
    run()
