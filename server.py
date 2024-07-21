import threading, socket, time, csv

def read_file(file_path):
    """
    Reads a CSV file with two columns and returns a dictionary where the first column is the key and the second column is the value.

    :param file_path: Path to the CSV file
    :return: Dictionary with the first column as keys and the second column as values
    """
    data_dict = {}
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) != 2:
                    print(f"Skipping row with unexpected number of columns: {row}")
                    continue
                key, value = row
                data_dict[key] = value
        return data_dict
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

# Get the local machine name and IP address
HOST = socket.gethostbyname(socket.gethostname())
PORT = 44332

# Create a socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the host and port
server.bind((HOST, PORT))

# Enable the server to accept connections
server.listen()

# Lists to keep track of clients, nicknames, and admins
clients = []
nicknames = []
admins = []

# Read banned IPs from file
banned_ips = read_file("lists/bans.txt")

def broadcast(message):
    """
    Send a message to all connected clients.

    :param message: The message to send
    """
    for client in clients:
        client.send(message.encode("utf-8"))

def close_connection(client):
    """
    Close a client's connection and remove them from the chat.

    :param client: The client socket
    """
    index = clients.index(client)
    clients.remove(client)
    client.close()
    nickname = nicknames[index]
    message = f"{nickname} left the chat!"
    nicknames.remove(nickname)
    print(message)
    broadcast(message)

def kick_user(kicker, nickname):
    """
    Kick a user from the chat.

    :param kicker: The nickname of the user initiating the kick
    :param nickname: The nickname of the user to be kicked
    """
    try:
        client_to_kick = clients[nicknames.index(nickname)]
        if kicker != "SERVER" and client_to_kick in admins:
            clients[nicknames.index(kicker)].send("You can't kick/ban a fellow Admin!".encode("utf-8"))
        else:
            if client_to_kick in clients:
                message = f"{nickname} has been kicked by {kicker}!"
                print(message)
                broadcast(message)
                close_connection(client_to_kick)
            else:
                print(f"{nickname} isn't the nickname of an active user!")
    except ValueError:
        message = f"{nickname} isn't the nickname of an active user!"
        if kicker != "SERVER":
            clients[nicknames.index(kicker)].send(message.encode("utf-8"))
        else:
            print(message)

def send_secret(sender, receiver_nickname, message):
    """
    Send a private message to a specific user.

    :param sender: The client socket of the sender
    :param receiver_nickname: The nickname of the recipient
    :param message: The message to send
    """
    secret = " ".join(message.split()[3:])
    try:
        clients[nicknames.index(receiver_nickname)].send(f"{nicknames[clients.index(sender)]} whispers to you: {secret}".encode("utf-8"))
        sender.send(f"You whisper to {receiver_nickname}: {secret}".encode("utf-8"))
    except ValueError:
        sender.send(f"{receiver_nickname} isn't the nickname of an active user!".encode("utf-8"))

def handle(client):
    """
    Handle messages from a specific client.

    :param client: The client socket
    """
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            print(message)
            nickname = message.split(" ")[0][:-1]
            try:
                if message.split(" ")[1] == "/nick":
                    new_nickname = message.split(" ")[2]
                    change_nickname(nickname, new_nickname)
                elif message.split(" ")[1] == "/quit":
                    close_connection(client)
                elif message.split(" ")[1] == "/secret":
                    receiver_nickname = message.split(" ")[2]
                    send_secret(client, receiver_nickname, message)
                elif message.split(" ")[1] == "/kick":
                    nickname_to_kick = message.split(" ")[2]
                    if client in admins:
                        kick_user(nickname, nickname_to_kick)
                    else:
                        client.send(f"You can't kick '{nickname_to_kick}' because you are not an admin!".encode("utf-8"))
                else:
                    broadcast(message)
            except IndexError:
                continue
        except OSError:
            continue

def change_nickname(old_nickname, nickname):
    """
    Change a user's nickname.

    :param old_nickname: The old nickname
    :param nickname: The new nickname
    """
    print(nicknames)
    message = f"{old_nickname} changed nickname to {nickname}"
    nicknames[nicknames.index(old_nickname)] = nickname
    print(message)
    broadcast(message)

def ban_user(banner, banned):
    """
    Ban a user from the chat.

    :param banner: The nickname of the user initiating the ban
    :param banned: The nickname of the user to be banned
    """
    banned_user = clients[nicknames.index(banned)]
    banned_ip = banned_user.getsockname()[0]
    with open("lists/bans.txt", "a") as bans_list:
        bans_list.write(banned+","+banned_ip+"\n")
        bans_list.close()
    banned_ips[banned] = banned_ip
    message = f"{banned} has been banned by {banner}"
    print(message)
    print(banned_ips)
    broadcast(message)
    close_connection(clients[nicknames.index(banned)])

def promote_user(nickname):
    """
    Promote a user to an admin.

    :param nickname: The nickname of the user to be promoted
    """
    try:
        new_admin = clients[nicknames.index(nickname)]
        if new_admin not in admins:
            admins.append(new_admin)
            nicknames[nicknames.index(nickname)] = nickname + "[ADMIN]"
            new_admin.send("ADMIN".encode("utf-8"))
            print(f"{nickname} has been promoted!")
        else:
            print(f"{nickname} is already an admin!")
    except ValueError:
        print(f"{nickname} isn't the nickname of an active user!")

def receive():
    """
    Accept and handle new client connections.
    """
    while True:
        client, address = server.accept()
        banned = False
        for name in banned_ips:
            if banned_ips[name] == address[0]:
                banned = True
        if banned:
            print(f"Banned address {address[0]} tried to join!")
            client.send("You have been banned and can't join!".encode("utf-8"))
            time.sleep(1)
            client.close()
        else:
            print(f"{address[0]} connected!")
            client.send("NICK".encode("utf-8"))
            nickname = client.recv(1024).decode("utf-8")
            clients.append(client)
            nicknames.append(nickname)
            print(f"Nickname of the client with the address {address[0]} is '{nickname}'!")
            broadcast(f"{nickname} joined the chat!")
            client.send("You are now connected to the server!".encode("utf-8"))
            thread_handle = threading.Thread(target=handle, args=(client,))
            thread_handle.start()

def write():
    """
    Handle server-side commands from the administrator.
    """
    while True:
        message = input("")
        try:
            if message.startswith("/"):
                if message.split(" ")[0] == "/admin":
                    nickname = message.split(" ")[1]
                    promote_user(nickname)
                elif message.split(" ")[0] == "/kick":
                    nickname = message.split(" ")[1]
                    kick_user("SERVER",nickname)
                elif message.split(" ")[0] == "/ban":
                    nickname = message.split(" ")[1]
                    ban_user("SERVER",nickname)
                else:
                    print("Invalid command!")
        except IndexError:
            print("Invalid arguments!")

# Print server status and start the write thread
print("Server is open and listening...")
print(f"Your IP is {HOST} and all users willing to connect must enter it")
thread_write = threading.Thread(target=write)
thread_write.start()

# Start accepting client connections
receive()
