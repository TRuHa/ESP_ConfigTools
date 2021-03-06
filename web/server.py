import machine
import socket
import os


def show_web(html):
    with open("web/" + html, "rb") as file:
        body = file.read()

    return body


def save_data(web, items):
    if web == 'network.html':
        with open("config.json", "r+") as outfile:
            data = ujson.load(outfile)
            subdata = data['network']
            for item in subdata:
                item["method"] = items[0].lstrip('method=')
                item["ip"] = items[1].lstrip('ip=')
                item["mask"] = items[2].lstrip('mask=')
                item["gate"] = items[3].lstrip('gate=')
                item["dns"] = items[3].lstrip('gate=')
            subdata = data['config']
            for item in subdata:
                item['network'] = 'YES'

            outfile.seek(0)
            outfile.write(ujson.dumps(data))
            outfile.truncate()

    elif web == 'wifi.html':
        essid = items[0].lstrip('essid=')
        if '+' in essid:
            essid = essid.replace("+", " ")

        with open("config.json", "r+") as outfile:
            data = ujson.load(outfile)
            subdata = data['wifi']

            for item in subdata:
                item['essid'] = essid
                item['psk'] = items[1].lstrip('psk=')
            subdata = data['config']
            for item in subdata:
                item['wifi'] = 'YES'

            outfile.seek(0)
            outfile.write(ujson.dumps(data))
            outfile.truncate()

    elif web == 'mqtt.html':
        topic = items[5].lstrip('topic=')
        if '%2F' in topic:
            topic = topic.replace("%2F", "/")

        with open("config.json", "r+") as outfile:
            data = ujson.load(outfile)
            subdata = data['mqtt']

            for item in subdata:
                item['id'] = items[0].lstrip('id=')
                item['broker'] = items[1].lstrip('broker=')
                item['port'] = items[2].lstrip('port=')
                item['user'] = items[3].lstrip('user=')
                item['psw'] = items[4].lstrip('psw=')
                item['topic'] = topic
            subdata = data['config']
            for item in subdata:
                item['mqtt'] = 'YES'

            outfile.seek(0)
            outfile.write(ujson.dumps(data))
            outfile.truncate()

    elif web == 'mode.html':
        type = items[1].lstrip('type=')
        if '+' in type:
            type = type.replace("+", " ")

        with open("config.json", "r+") as outfile:
            data = ujson.load(outfile)
            subdata = data['mode']

            for item in subdata:
                item['model'] = items[0].lstrip('model=')
                item['type'] = type
                item['gpio'] = items[2].lstrip('gpio=')
            subdata = data['config']
            for item in subdata:
                item['mode'] = 'YES'

            outfile.seek(0)
            outfile.write(ujson.dumps(data))
            outfile.truncate()

    elif web == 'mqtt.html':
        topic = items[5].lstrip('topic=')
        if '%2F' in topic:
            topic = topic.replace("%2F", "/")

        with open("config.json", "r+") as outfile:
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

        with open("config.json", "r+") as outfile:
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
    webs = ['network.html', 'wifi.html', 'mqtt.html', 'mode.html', 'end']

    while True:
        client, addr = sock.accept()

        if not addr[0] in clients:
            clients.append(addr[0])
            print('[+] Cliente %s conectado.' % addr[0])

        msg = client.recv(1500).decode()
        msg = msg.split('\n')

        extract = msg[0]
        extract = extract.split(' ')
        method = extract[0]

        try:
            html = extract[1].lstrip('/')
            if html == '':
                html = 'network.html'
        except IndexError:
            html = 'network.html'

        if method == 'GET':
            if '?' in html:
                html = html.rstrip('?')

            if html == 'end':
                print('[-] Sistema configurado correctamente, reiniciando...')
                body = '<html><center><h4>Configuration saved successfully.</h4><p>Rebooting the ' \
                       'system.</p></center></html>'.encode()

                client.send(body)
                client.close()
                sock.close()

                machine.reset()

                break

            elif html in webs:
                body = show_web(html)
                last = webs.index(html)

            else:
                print('[-] Error: pagina no encontrada')
                body = '<html><center><h4>Error 404: File not found</h4><p>Python HTTP '\
                       'Server</p></center></html>'.encode()

        elif method == 'POST':
            msg = client.recv(1500).decode()
            msg = msg.split('\n')

            count = len(msg)
            answer = msg[count - 1]
            answer = answer.split('&')

            save_data(webs[last], answer)

            print('[-] Datos %s guardados.' % webs[last])

            body = '<html><center><h4>Configuration saved successfully.</h4><form method="get" ' \
                   'action=%s><button type="submit">Next</button></form></center></html>' % (webs[last + 1])
            body = body.encode()

        client.send(body)
        client.close()


if __name__ == '__main__':
    run()
