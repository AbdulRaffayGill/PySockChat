import socket
import os
import threading

lock = threading.Lock()

def safe_print(msg):
    with lock:
        print(msg)

def direct_chat():
    choice = input("Enter 1 to host chat, 2 to connect to peer:\n")

    if choice == "1":
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '0.0.0.0'
        s.bind((host, 6000))
        s.listen(1)
        safe_print("Waiting for peer to connect...\n")
        conn, addr = s.accept()

        name_peer = conn.recv(100).decode().strip()
        name_me = input("Enter your name:\n")
        conn.sendall(name_me.encode('utf-8'))
        os.system("cls")

        safe_print(f"Connected with {name_peer}\n")

        while True:
            msg = input(name_me + " : ")
            if msg == ";":
                conn.sendall(msg.encode('utf-8'))
                safe_print("You ended the chat.")
                conn.close()
                break
            conn.sendall(msg.encode('utf-8'))

            r = conn.recv(5000).decode().strip()
            if r == ";":
                safe_print(f"{name_peer} ended the chat.")
                conn.close()
                break
            safe_print(f"{name_peer} : {r}")

        return

    else:
        ip = input("Enter peer IP:\n")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, 6000))

        name_me = input("Enter your name:\n")
        s.sendall(name_me.encode('utf-8'))
        name_peer = s.recv(100).decode().strip()
        os.system("cls")

        safe_print(f"Connected with {name_peer}\n")

        while True:
            r = s.recv(5000).decode().strip()
            if r == ";":
                safe_print(f"{name_peer} ended the chat.")
                s.close()
                break
            safe_print(f"{name_peer} : {r}")

            msg = input(name_me + " : ")
            if msg == ";":
                s.sendall(msg.encode('utf-8'))
                safe_print("You ended the chat.")
                s.close()
                break
            s.sendall(msg.encode('utf-8'))

        return

def Group():
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host=str(input("Enter the Private Ip of server\n"))
    if not host:
        host=socket.gethostname()
    s.connect((host,5000))
    r='0'
    arr=['/','*',':',';','!','@','#','$','%','^','&','?','|','\\']
    name=str(input("Enter your name\n"))
    while True:
        if name not in arr:
            break
        else:
            safe_print("Only special chracters not allowed\n")
            name=str(input("Enter your name:\n"))
    s.sendall(name.encode('utf-8'))
    name_r=s.recv(100).decode().strip()
    os.system("cls")

    def send():
        while True:
            with lock:
                i=str(input(name+" : "))
            if i==";":
                safe_print("You have closed the chat\n")
                s.close()
                break
            i=(name+":"+i).encode('utf-8')
            s.sendall(i)
        
    def recv():
        while True:
            try:
                r = s.recv(5100)
            except ConnectionResetError:
                safe_print("Connection closed by server.")
                break
            except:
                break

            if not r:
                safe_print("Server closed the connection.")
                break

            r = r.decode().strip()

            if not r.strip(name_r):
                safe_print(f"{name_r} : (Empty message received)\n")
            elif r.strip(name_r) == ';':
                safe_print("Chat ended by the other person:\nQuitting\n")
                s.close()
                break
            else:
                safe_print(f"\n{r}")

    threading.Thread(target=recv).start()              
    threading.Thread(target=send).start()
    
print("1) Direct Chat (peer to peer)")
print("2) Group Chat (via server)")
mode = input("Choose mode:")

if mode == "1":
    direct_chat()
else:
    Group()
