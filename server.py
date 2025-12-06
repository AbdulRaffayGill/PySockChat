import socket
import os
import threading
import time
import sqlite3

clients_lock = threading.Lock()
auth_lock = threading.Lock()
def init_db():
    conn = sqlite3.connect('chat_system.db', check_same_thread=False)
    c = conn.cursor()
    
    # We are using 2 databases here, Database 1: Registered Users, Database 2:Online status
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS online_status 
                 (username TEXT PRIMARY KEY, is_online INTEGER, time_stamp TEXT)''')
    
    # If the Database is created first time , it will create the admin account for these credentials , else admin is required to sign in
    c.execute("SELECT username FROM users WHERE username = '_h4ck3er_'")
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?, ?)", ('_h4ck3er_', 'p4ssw0rd_1s_5tr0ng'))
        print("Admin account created.")
        
    conn.commit()
    return conn
db_conn = init_db()
def handle_auth_client(conn, addr):
    try:
        msg = conn.recv(1024).decode().strip()
        parts = msg.split('|')
        command = parts[0]

        cursor = db_conn.cursor()

        if command == "SIGNUP":
            user, pwd = parts[1], parts[2]
            try:
                with auth_lock:
                    cursor.execute("INSERT INTO users VALUES (?, ?)", (user, pwd))
                    cursor.execute("INSERT INTO online_status VALUES (?, ?, ?)", (user, 0, ""))
                    db_conn.commit()
                conn.sendall("1".encode()) 
            except sqlite3.IntegrityError:
                conn.sendall("0".encode()) 

        elif command == "LOGIN":
            user, pwd = parts[1], parts[2]
            with auth_lock:
                cursor.execute("SELECT password FROM users WHERE username=?", (user,))
                record = cursor.fetchone()
                
                if record and record[0] == pwd:
                    if user != "_h4ck3er_":
                        cursor.execute("UPDATE online_status SET is_online = 1, time_stamp = ? WHERE username = ?", (time.ctime(), user))
                        db_conn.commit()
                    conn.sendall("1".encode())
                else:
                    conn.sendall("0".encode())

        elif command == "LOGOUT":
            user = parts[1]
            with auth_lock:
                if user != "_h4ck3er_":
                    cursor.execute("UPDATE online_status SET is_online = 0, time_stamp = ? WHERE username = ?", (time.ctime(), user))
                    db_conn.commit()
            conn.sendall("1".encode())

        elif command == "GET_ONLINE":
            with auth_lock:
                cursor.execute("SELECT username, time_stamp FROM online_status WHERE is_online = 1")
                users = cursor.fetchall()

                if users:
                    online_list = ", ".join([f"{u[0]} ({u[1]})" for u in users])
                    conn.sendall(online_list.encode())

    except Exception as e:
        print(f"Auth Error: {e}")
    finally:
        conn.close()

def start_auth_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 6001))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_auth_client, args=(conn, addr))
        t.start()

def client_soc(client, i, m, stop_event):
    while not stop_event.is_set():
        try:
            r = client[i][0].recv(5100).decode().strip()
            if not r:
                stop_event.set()
                break
            if r == ';':
                stop_event.set()
                break
            print(r, '\n')
            with clients_lock:
                for j in range(len(client)):
                    if client[i][0] != client[j][0]:
                        try:
                            client[j][0].sendall(("\n" + r).encode('utf-8'))
                        except:
                            continue
        except Exception:
            stop_event.set()
            break

    with clients_lock:
        if i < len(client):
            disconnected_client = client.pop(i)
            print(f"{disconnected_client[1]} left the chat")
            disconnected_client[0].close()

def GroupChat():
    auth_thread = threading.Thread(target=start_auth_server, daemon=True)
    auth_thread.start()

    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host='0.0.0.0'
    s.bind((host,5000))
    print("Server listening for Group Chat connections (Port 5000)\n")
    s.listen(10)
    clients=[]
    arr=['/','*',':',';','!','@','#','$','%','^','&','?','|','\\']
    
    name_me=str(input("Enter your name (Server Admin Name):\n"))
    while True:
        if name_me not in arr:
            break
        else:
            print("Single special chracters not allowed\n")
            name_me=str(input("Enter your name:\n"))
            
    m=int(input("Enter the number of clients that are allowed to connect:\n(Max allowed 10):\n"))
    for i in range(0,m):
        soc,l=s.accept()
        name=soc.recv(100).decode().strip()
        soc.sendall(name_me.encode('utf-8'))
        clients.append((soc,name,name_me))
        print("Client ",i,"'"+name+"'"," entered the Chat")
    
    for i in range(0,m):
        stop_event=threading.Event()
        threading.Thread(target=client_soc,args=(clients,i,m,stop_event)).start()


print("Welcome Admin , Login to start Group Chat\n")
c = input("Username: ")
p = input("\nPassword: ")

cursor = db_conn.cursor()
cursor.execute(
    "SELECT 1 FROM users WHERE username = ? AND password = ?",
    (c, p)
)

if not cursor.fetchone():
    print("Username or Password didn't match\n")
    time.sleep(3)
    os.system("cls")
else:
    print("Admin Login successful\n")
    time.sleep(2)
    os.system("cls")
    GroupChat()