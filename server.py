import socket
import threading

NICK_SYMBOLS = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","-","_"]

ADMIN_PASSWORD = 'admin'

HOST = "0.0.0.0"
PORT = 8081

print(f"server: ~start --host: {HOST} --port: {PORT}")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []
admins = set()

def valid_nick(nick):
    nickl = nick.lower()
    for i in nickl:
        if i in NICK_SYMBOLS:
            continue
        return False
    if nick in nicknames:
        return False
    return True

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if message.decode("utf-8").split(':')[1][1] == '~':
                command = message.decode("utf-8").split(':')[1].split()
                index = clients.index(client)
                if command[0] == "~admin":
                    if len(command)>1:
                        if command[1] == ADMIN_PASSWORD:
                            print(f"server: ~admin {client} {nicknames[index]} --success")
                            broadcast(f"server: {nicknames[index]} is now admin".encode('utf-8'))
                            admins.add(client)
                        else:
                            print(f"server: ~admin {client} {nicknames[index]} --fail: <wrong-password>")
                            client.send(f"server: ~admin --error: <wrong-password>".encode("utf-8"))
                    else:
                        print(f"server: ~admin {client} {nicknames[index]} --fail: <wrong-password>")
                        client.send(f"server: ~admin --error: <wrong-password>".encode("utf-8"))
                elif command[0] == "~deadmin":
                    if client in admins:
                        print(f"server: ~deadmin {client} {nicknames[index]} --success")
                        broadcast(f"server: {nicknames[index]} is no longer admin".encode('utf-8'))
                        admins.remove(client)
                elif command[0] == "~quit" or command[0] == "~exit":
                    print(f"server: ~quit/exit {client} {nicknames[index]} --success")
                    if client in admins:
                        admins.remove(client)
                    clients.remove(client)
                    client.close()
                    nickname = nicknames[index]
                    broadcast(f"server: {nickname} --disconnected".encode('utf-8'))
                    nicknames.remove(nickname)
                    break
                elif command[0] == "~nickchange":
                    nickname = command[1]

                    if not valid_nick(nickname):
                        print(f"server: ~nickchange {client} {nicknames[index]} --error: <bad-nick>")
                        client.send(f"server: ~nickchange --error: <bad-nick>".encode("utf-8"))
                        continue

                    print(f"server: ~nickchange {client} {nicknames[index]} --success: {command[1]}")
                    broadcast(f"server: {nicknames[index]} changed name to {command[1]}".encode("utf-8"))
                    nicknames[index] = command[1]
                    client.send(f"~nickchange {nickname}".encode("utf-8"))
                else:
                    print(f"server: {command[0]} {client} {nicknames[index]} --error: <wrong-command>")
                    client.send(f"server: {command[0]} --error: <wrong-command>".encode("utf-8"))
            else:
                broadcast(message)
        except:
            index = clients.index(client)
            print(f"server: {client} {nicknames[index]} --disconnected: <exeption>")
            if client in admins:
                admins.remove(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f"server: {nickname} --disconnected".encode('utf-8'))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"server: --client: {client} --address: {str(address)} --connected")

        client.send("~nickreqv".encode('utf-8'))
        nickname = client.recv(1024).decode("utf-8")

        if not valid_nick(nickname):
            print(f"server: ~nickreqv {client} --error: <bad-nick>")
            client.send(f"server: --error: <bad-nick>".encode("utf-8"))
            client.send(f"~forsexit".encode("utf-8"))
            continue

        nicknames.append(nickname)
        clients.append(client)

        print(f"server: ~nickreqv {client} --result: {nickname}")
        broadcast(f"server: {nickname} --connected".encode("utf-8"))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()