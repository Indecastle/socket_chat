import socket, threading, time, json
from tabulate import tabulate
from typing import Dict

host = socket.gethostbyname(socket.gethostname())
# host = "localhost"
host = ''
port = 9091
clients = {}
timeout = 60  # sek

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))

quit = False
print("[ Server Started ]")


def encode_pair(dict):
    return json.dumps(dict).encode("utf-8")


def sendto(dict_message, addr):
    s.sendto(encode_pair(dict_message), addr)


def send_all(dict_message, addr=None):
    for addr_client, info in clients.items():
        if addr_client not in addr if isinstance(addr, list) else addr_client != addr:
            sendto(dict_message, addr_client)


def send_cmd(addr, cmd_type, cmd_message):
    sendto({'event': 'cmd', 'cmd': cmd_type, 'message': cmd_message}, addr)


def log_chat(addr, message):
    itsatime = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
    print(f"[{addr[0]}:{str(addr[1])}]=[{itsatime}]/", message)


def check_timeout(sock, clients):
    while not quit:
        time.sleep(1)
        for addr_client, info in list(clients.items()):
            if time.time() > info[1]:
                message = f"[{info[0]}] => timeout"
                send_all({"event": "timeout", "who": info[0], "message": message})
                log_chat(addr_client, message)
                clients.pop(addr_client)


rT = threading.Thread(target=check_timeout, args=(s, clients))
rT.start()

while not quit:
    try:
        bytes, addr = s.recvfrom(1024)
        json_string = bytes.decode("utf-8")
        data = json.loads(json_string)

        if addr not in clients:
            alias = data["name"]
            # message = f"[{alias}] => join chat "
            # send_all({"message": message})

            clients[addr] = [alias, time.time() + timeout]

        info_main = clients[addr]
        alias = info_main[0]
        info_main[1] = time.time() + timeout

        if "event" in data:
            if data["event"] == "log":
                pass
            elif data["event"] == "cmd":
                cmd = data["cmd"]
                message = f"[{alias}]-cmd => {data['cmd']}"
                if cmd == "users":
                    users_list = list(map(lambda k: [k[0], k[1][0]], list(clients.items())))
                    send_cmd(addr, data["cmd"],
                             tabulate(users_list, headers=['address', 'username'], tablefmt='github'))
                elif cmd == "pause":
                    info_main[1] = 0  # good practice :)
                elif cmd == 'resume':
                    message = f"[{alias}] => join chat "
                    send_all({"message": message})
                elif cmd == "i'm_here":
                    pass  # good practice :)
                elif cmd == 'quit':
                    clients.pop(addr)
                    send_all({"message": message}, addr)
            else:
                message = "?"
                send_cmd(addr, data["cmd"], "?")
        if "message" in data:
            message = f"[{alias}] :: {data['message']}"
            send_all({"message": message}, [addr])

        log_chat(addr, message)
    except socket.error as e:
        # print(type(e), '=', e)
        pass
    except Exception as e:
        print(type(e), '---', e)
        print("\n[ Server Stopped ]")
        quit = True

s.close()
rT.join()
