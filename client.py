import socket
import os
import threading
import time

lock = threading.Lock()

def safe_print(msg):
    with lock:
        print(msg)
def send_auth_request(ip, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, 6001)) 
        s.sendall(message.encode('utf-8'))
        response = s.recv(1024).decode().strip()
        s.close()
        return response
    except ConnectionRefusedError:
        return "ERROR: Server not running"

def login_system(server_ip):
    while True:
        os.system("cls")
        print("1. Login")
        print("2. Signup")
        print("3. Back to Main Menu")
        choice = input("Select: ")

        if choice == "1":
            # Login
            user = input("Username: ")
            pwd = input("Password: ")
            msg = f"LOGIN|{user}|{pwd}"
            resp = send_auth_request(server_ip, msg)
            
            if resp == "1":
                safe_print("Successful login.")
                time.sleep(1)
                return user # Return verified username
            elif resp == "0":
                safe_print("Incorrect username or password.")
                time.sleep(2)
            else:
                safe_print(f"Error: {resp}")
                time.sleep(2)

        elif choice == "2":
            # Signup
            user = input("New Username: ")
            pwd = input("New Password: ")
            msg = f"SIGNUP|{user}|{pwd}"
            resp = send_auth_request(server_ip, msg)
            
            if resp == "1":
                safe_print("Signup Successful! Please Login.")
            elif resp == "0":
                safe_print("Username already exists.")
            else:
                safe_print(f"Error: {resp}")
            time.sleep(2)
            
        elif choice == "3":
            return None # Back to main

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
                time.sleep(3)
                s.close()
                break
            safe_print(f"{name_peer} : {r}")

            msg = input(name_me + " : ")
            if msg == ";":
                s.sendall(msg.encode('utf-8'))
                safe_print("You ended the chat.")
                time.sleep(3)
                s.close()
                break
            s.sendall(msg.encode('utf-8'))

        return

def Group(server_ip, logged_in_user):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host = server_ip
    
    s.connect((host,5000))
    r='0'
    name = logged_in_user
    
    s.sendall(name.encode('utf-8'))
    name_r=s.recv(100).decode().strip()
    os.system("cls")
    def send():
        while True:
            
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

    t1 = threading.Thread(target=recv)
    t2 = threading.Thread(target=send)
    t1.start()
    t2.start()
    
    t2.join() 


def group_chat_controller():
    server_ip = input("Enter the Private Ip of server: ")
    if not server_ip:
        server_ip = socket.gethostname()

    while True:
        current_user = login_system(server_ip)
        
        if current_user is None:
            break 
        while True:
            os.system("cls")
            print(f"Welcome, {current_user}!")
            print("1. Join Group Chat")
            print("2. Check Online Users")
            print("3. Logout")
            
            dash_choice = input("Select: ")
            
            if dash_choice == "1":
                Group(server_ip, current_user)
                
            elif dash_choice == "2":
                resp = send_auth_request(server_ip, "GET_ONLINE")
                print(f"\n--- Online Users ---\n{resp}\n")
                input("Press Enter to continue...")
                
            elif dash_choice == "3":
                
                send_auth_request(server_ip, f"LOGOUT|{current_user}")
                print("Logging out...")
                time.sleep(1)
                break 
                

while True:
    os.system("cls")
    print("1) Direct Chat (peer to peer)")
    print("2) Group Chat (via server)")
    print("3) Exit")
    mode = input("Choose mode: ")

    if mode == "1":
        direct_chat()
    elif mode == "2":
        group_chat_controller()
    elif mode == "3":
        break