def show_web(html):
    header = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'.encode()
    with open("page/" + html, "rb") as file:
        body = header + file.read()

    return header, body


def save_data(web, items):
    import ujson
    if web == 'network.html':
        with open("config/config.json", "r+") as outfile:
            data = ujson.load(outfile)
            subdata = data['network']

            for item in subdata:
                item["method"] = items[0].lstrip('method=')
                item["ip"] = items[1].lstrip('ip=')
                item["mask"] = items[2].lstrip('mask=')
                item["gate"] = items[3].lstrip('gate=')
                item["dns"] = items[3].lstrip('gate=')

            outfile.seek(0)
            outfile.write(ujson.dumps(data))
            outfile.truncate()

    elif web == 'wifi.html':
        essid = items[0].lstrip('essid=')
        if '+' in essid:
            essid = essid.replace("+", " ")

        with open("config/config.json", "r+") as outfile:
            data = ujson.load(outfile)
            subdata = data['wifi']

            for item in subdata:
                item['essid'] = essid
                item['psk'] = items[1].lstrip('psk=')

            outfile.seek(0)
            outfile.write(ujson.dumps(data))
            outfile.truncate()

    elif web == 'mqtt.html':
        topic = items[5].lstrip('topic=')
        if '%2F' in topic:
            topic = topic.replace("%2F", "/")

        with open("config/config.json", "r+") as outfile:
            data = ujson.load(outfile)
            subdata = data['mqtt']

            for item in subdata:
                item['id'] = items[0].lstrip('id=')
                item['broker'] = items[1].lstrip('broker=')
                item['port'] = items[2].lstrip('port=')
                item['user'] = items[3].lstrip('user=')
                item['psw'] = items[4].lstrip('psw=')
                item['topic'] = topic

            outfile.seek(0)
            outfile.write(ujson.dumps(data))
            outfile.truncate()

    elif web == 'mode.html':
        type = items[1].lstrip('type=')
        if '+' in type:
            type = type.replace("+", " ")

        with open("config/config.json", "r+") as outfile:
            data = ujson.load(outfile)
            subdata = data['mode']

            for item in subdata:
                item['model'] = items[0].lstrip('model=')
                item['type'] = type
                item['gpio'] = items[2].lstrip('gpio=')

            outfile.seek(0)
            outfile.write(ujson.dumps(data))
            outfile.truncate()


def run():
    global last
    import socket
    import os

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
                try:
                    html = webs[last + 1]

                except IndexError:
                    print('[-] Sistema configurado correctamente, reiniciando...')
                    header = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'.encode()
                    body = '<center><h4>Configuration saved successfully.</h4><p>Rebooting the ' \
                           'system.</p></center>'.encode()

                    response = header + body

                    client.send(response)
                    client.close()
                    sock.close()

                    break

            if html in webs:
                header, body = show_web(html)
                last = webs.index(html)

            else:
                print('[-] Error: pagina no encontrada')
                header = 'HTTP/1.1 404 Not Found\n\n'.encode()
                body = '<center><h4>Error 404: File not found</h4><p>Python HTTP Server</p></center>'.encode()

        elif method == 'POST':
            msg2 = client.recv(1500).decode()
            msg2 = msg2.split('\n')

            count = len(msg2)
            answer = msg2[count - 1]
            answer = answer.split('&')

            save_data(webs[last], answer)

            print('[-] Datos %s guardados.' % webs[last])

            header = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n'.encode()
            body = '<center><h4>Configuration saved successfully.</h4><form method="get" ' \
                   'action="next.html"><button type="submit">Next</button></form></center>'.encode()

        response = header + body

        client.send(response)
        client.close()


if __name__ == '__main__':
    run()
