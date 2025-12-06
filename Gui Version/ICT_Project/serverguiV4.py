import socket
import threading
import sqlite3
from tkinter import *
from tkinter import scrolledtext



root=Tk()
root.geometry("540x540")
root.title("PySocket_Chat")

Label(root, text = "PYSOCKET CHAT SERVER", font = ("century Gothic", 20, "bold")).pack(pady=50)
Label(root, text = "Welcome Admin , Login to start Group Chat\n", font = ("century gothic", 13)).pack()

Label(root, text = "Username ", font=("century gothic", 10)).pack()
userrr = Entry(root, font=("century gothic", 10))
userrr.pack()

Label(root, text="Password", font=("century gothic", 10)).pack()
pass_enter = Entry(root, show="*")
pass_enter.pack()

Label(root, text = "Name of the Server Admin", font=("century gothic", 10)).pack()
s_n_e = Entry(root, font = ("century gothic", 10))
s_n_e.pack()

Label(root, text = "Max number of Clients (1-10)", font = ("century gothic", 10)).pack()
max_cli = Entry(root, font = ("century gothic", 10))
max_cli.pack()

Label(root, text = "\n").pack()

clients_lock = threading.Lock()
auth_lock = threading.Lock()



def clear_window():
    for widget in root.winfo_children():
        widget.destroy()



def create_label(message):
    Label(root, text=message, font = ("century gothic", 10), anchor="w").pack()

def disp_mes(message):
    root.after(0, create_label, message)


scrolling = None

def scrolling_func(message):
    def enter():
        scrolling.config(state = "normal")
        scrolling.insert(END, message + "\n")
        scrolling.see(END)
        scrolling.config(state = "disabled")
    root.after(0, enter)



def init_db():
    conn = sqlite3.connect('chat_system.db', check_same_thread=False)
    c = conn.cursor()
    
    # We are using 2 databases here, Database 1: Registered Users, Database 2:Online status
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS online_status 
                 (username TEXT PRIMARY KEY, is_online INTEGER)''')
    
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
                    cursor.execute("INSERT INTO online_status VALUES (?, ?)", (user, 0))
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
                        cursor.execute("UPDATE online_status SET is_online = 1 WHERE username = ?", (user,))
                        db_conn.commit()
                    conn.sendall("1".encode())
                else:
                    conn.sendall("0".encode())

        elif command == "LOGOUT":
            user = parts[1]
            with auth_lock:
                if user != "_h4ck3er_":
                    cursor.execute("UPDATE online_status SET is_online = 0 WHERE username = ?", (user,))
                    db_conn.commit()
            conn.sendall("1".encode())

        elif command == "GET_ONLINE":
            with auth_lock:
                cursor.execute("SELECT username FROM online_status WHERE is_online = 1")
                users = cursor.fetchall()
            
            if users:
                online_list = ", ".join([u[0] for u in users])
                conn.sendall(online_list.encode())
            else:
                conn.sendall("No users online.".encode())

    except Exception as e:
        Label(root, text = f"Auth Error: {e}", font = ("century gothic")).pack()
    finally:
        conn.close()





def start_auth_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 6001))
    s.listen(5)
    disp_mes("Auth Server running on port 6001...")

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
            scrolling_func(r +"\n")
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
            msg = f"{disconnected_client[1]} left the chat"
            scrolling_func(msg)
            disconnected_client[0].close()





def GroupChat():
    Label(root, text = "CHAT VIEW", font = ("century gothic", 20, "bold", "underline")).pack(pady=25)

    global scrolling
    scrolling = scrolledtext.ScrolledText(root, width=50, height = 16, font = ("century gothic", 10), state = "disabled")
    scrolling.pack(pady=10)

    adm_name = ad_name_glob
    mx_cli = mx_cli_glob

    auth_thread = threading.Thread(target=start_auth_server, daemon=True)
    auth_thread.start()

    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host='0.0.0.0'
    s.bind((host,5000))
    disp_mes("Server listening for Group Chat connections (Port 5000)\n")
    s.listen(10)

    Button(root, text = "End Group Chat", command=root.quit, font=("century gothic", 10, "italic")).pack(pady=10)

    clients=[]
    arr=['/','*',':',';','!','@','#','$','%','^','&','?','|','\\']

    if adm_name in arr or adm_name.strip() == "":
        Label(root, text="Such characters are not allowed. Default set to Admin").pack()
        adm_name = "Admin"


    for i in range(mx_cli):
        soc,l=s.accept()
        name=soc.recv(100).decode().strip()
        soc.sendall(adm_name.encode('utf-8'))
        clients.append((soc,name,adm_name))
        msg = f"Client '{name}' has entered the chat ({i+1}/{mx_cli})"
        stop_event=threading.Event()
        threading.Thread(target=client_soc,args=(clients,i,mx_cli,stop_event)).start()
        scrolling_func(msg)    



def guiii():

    global ad_name_glob, mx_cli_glob

    USER = userrr.get().strip()
    PAZWRD = pass_enter.get().strip()
    ad_name_glob = s_n_e.get().strip() or "Admin"
    MAXCLIENTS = max_cli.get().strip()

    if MAXCLIENTS.isdigit() == False:
        disp_mes("This is an invalid number for max clients")
        return
    
    mx_cli_glob = int(MAXCLIENTS)

    if mx_cli_glob < 1 or mx_cli_glob > 10:
        disp_mes("Number of clients should not exceed the constraints (1-10)")
        return

    cursor=db_conn.cursor()
    cursor.execute(("SELECT username,password FROM users WHERE username = ? and password = ? "),(USER,PAZWRD))
    if not cursor.fetchone():
        disp_mes("Username or Password did not match\n")
    else:
        disp_mes("Admin login successful. Initializing Group Chat...\n")
        root.after(2000, clear_window)
        root.after(2050, lambda: threading.Thread(target=GroupChat, daemon=True).start())



Button(root, text="Login and Create the chat", font = ("century gothic", 10, "italic"), command=guiii).pack()

root.mainloop()
        