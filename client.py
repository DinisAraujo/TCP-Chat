import socket, threading

#HOST = input("Type server IP: ")
HOST = "192.168.1.101"
nickname = input("Choose a nickname: ")
PORT = 4431
admin = False
changed_nick_as_admin = False
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
        global changed_nick_as_admin
        message = input()
        send = True
        if admin and not changed_nick_as_admin:
            message = f"{nickname}[ADMIN]: " + message
        else:
            message = f"{nickname}: " + message
        if message.split(" ")[1] == "/nick":
            try:
                new_nickname = message.split(" ")[2]
                if admin:
                    changed_nick_as_admin = True
                    new_nickname += "[ADMIN]"
                    message += "[ADMIN]"
                if new_nickname != nickname:
                    nickname = message.split(" ")[2]
                else:
                    send = False
                    print("You must select a new nickname!")
            except IndexError:
                send = False
                print("You must select a new nickname!")
        elif message.split(" ")[1] == "/kick":
            if not admin:
                send = False
                print("You're not an Admin and can't use this command.")
        if send:
            client.send(message.encode("utf-8"))
        if message.split(" ")[1] == "/quit":
            client.close()
            break


receive_thread = threading.Thread(target=receive)
receive_thread.start()
write_thread = threading.Thread(target=write)
write_thread.start()