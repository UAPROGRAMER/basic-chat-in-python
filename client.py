import socket
import threading

nickname = input("client: enter your nickname > ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('0.0.0.0', 8081))

def receive():
    global nickname
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            
            if message[0] == '~':
                command = message.split()
                if command[0] == "~nickreqv":
                    client.send(nickname.encode("utf-8"))
                elif command[0] == "~nickchange":
                    if len(command)>1:
                        nickname = command[1]
                elif command[0] == "~forsexit":
                    print("client: ~forsexit")
                    client.close()
                    break
            else:
                print(message)
        except:
            print("client: --error: <lost-connection>")
            client.close()
            break

def write():
    global nickname
    while True:
        message = f"{nickname}: "+input("")
        client.send(message.encode("utf-8"))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_tread = threading.Thread(target=write)
write_tread.start()