import socket, threading

#HOST = input("Type server IP: ")
HOST = "192.168.1.101"
nickname = input("Choose a nickname: ")
PORT = 1112
admin = False
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((HOST,PORT))

def receive():
    global admin
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if message == "NICK":
                client.send(nickname.encode("utf-8"))
            elif message == "ADMIN":
                admin = True
                print("You have been promoted to an Admin!")
            else:
                print(message)
        except:
            print("See ya later aligator!")
            client.close()
            break

def write():
    while True:
        global nickname
        message = input()
        if admin == True:
            message = f"{nickname}[ADMIN]: " + message
        else:
            message = f"{nickname}: " + message
        if message.split(" ")[1] == "/nick":
            nickname = message.split(" ")[2]
        client.send(message.encode("utf-8"))
        if message.split(" ")[1] == "/quit":
            client.close()
            break


receive_thread = threading.Thread(target=receive)
receive_thread.start()
write_thread = threading.Thread(target=write)
write_thread.start()