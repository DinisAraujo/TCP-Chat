import socket, threading

# Prompt the user to input the server's IP address and their nickname
HOST = input("Type server IP: ")
nickname = input("Choose a nickname: ")
PORT = 44314

# Variables to track admin status and nickname changes
admin = False
changed_nick_as_admin = False

# Create a socket object for the client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the server using the provided IP and port
client.connect((HOST, PORT))

def receive():
    """
    Handles receiving messages from the server.
    If the server requests the client's nickname, send it.
    If the client is promoted to admin, update the admin status.
    """
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
            print("See ya later alligator!")
            client.close()
            break

def write():
    """
    Handles sending messages to the server.
    Formats messages according to the user's nickname and admin status.
    Processes commands like /nick, /kick, and /quit.
    """
    while True:
        global nickname
        global changed_nick_as_admin
        message = input()
        send = True
        if admin and not changed_nick_as_admin:
            message = f"{nickname}[ADMIN]: " + message
        else:
            message = f"{nickname}: " + message

        # Process /nick command to change nickname
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

        # Process /kick command to kick a user (admin only)
        elif message.split(" ")[1] == "/kick":
            if not admin:
                send = False
                print("You're not an Admin and can't use this command.")

        # Process /ban command to ban a user (admin only)
        elif message.split(" ")[1] == "/ban":
            if not admin:
                send = False
                print("You're not an Admin and can't use this command.")

        # Send the formatted message to the server
        if send:
            client.send(message.encode("utf-8"))

        # Process /quit command to disconnect
        if message.split(" ")[1] == "/quit":
            client.close()
            break

# Start threads to handle receiving and sending messages
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
