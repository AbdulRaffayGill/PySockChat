import socket
import os
import threading
import time
from tkinter import *
from tkinter import simpledialog, messagebox, scrolledtext

root = Tk()
root.geometry("540x350")
root.title("PySocket Chat")

# Global vars
current_chat_area = None 
lock = threading.Lock()

def safe_print(msg):
    with lock:
        if current_chat_area:
            current_chat_area.configure(state='normal')
            current_chat_area.insert(END, msg + "\n")
            current_chat_area.see(END)
            current_chat_area.configure(state='disabled')
        else:
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


# 1. DIRECT CHAT (Fixed: Non-blocking Connection)

def direct_chat():
    root.withdraw()

    chat_win = Toplevel(root)
    chat_win.geometry("450x500")
    chat_win.title("Direct Chat - Select Mode")

    frame_mode_select = Frame(chat_win)
    frame_chat_ui = Frame(chat_win)

    # Variables for connection
    conn = None
    s = None
    stop_event = threading.Event()
    name_me = ""

    def on_close():
        stop_event.set()
        # Closing the socket 's' here breaks the blocking s.accept() loop
        if s: 
            try: s.close()
            except: pass
        if conn: 
            try: conn.close()
            except: pass
        chat_win.destroy()
        root.deiconify()

    chat_win.protocol("WM_DELETE_WINDOW", on_close)

    global current_chat_area
    chat_box = scrolledtext.ScrolledText(frame_chat_ui, height=20, width=50, state='disabled')
    chat_box.pack(padx=10, pady=10)
    
    msg_entry = Entry(frame_chat_ui, width=40)
    msg_entry.pack(side=LEFT, padx=10, pady=10)

  
    def setup_chat_screen():
       
        frame_mode_select.pack_forget()
        frame_chat_ui.pack()
        chat_win.title(f"Direct Chat - {name_me}")
        global current_chat_area
        current_chat_area = chat_box

    def recv_loop(sock, peer_name):
        while not stop_event.is_set():
            try:
                r = sock.recv(5000).decode().strip()
                if not r: break
                if r == ";":
                    safe_print(f"{peer_name} ended chat.")
                    sock.close()
                    break
                safe_print(f"{peer_name} : {r}")
            except: break

    def send_msg():
        msg = msg_entry.get()
        msg_entry.delete(0, END)
        target = conn if conn else s
        if msg and target:
            if msg == ";":
                target.sendall(msg.encode('utf-8'))
                target.close()
                on_close()
                return
            target.sendall(msg.encode('utf-8'))
            safe_print(f"{name_me} : {msg}")

    send_btn = Button(frame_chat_ui, text="Send", command=send_msg)
    send_btn.pack(side=LEFT)
    back_btn = Button(frame_chat_ui, text="Back", command=on_close)
    back_btn.pack(side=RIGHT, padx=10)

    
    def mode_host():
        nonlocal name_me
        name_me = simpledialog.askstring("Name", "Enter your name:")
        if not name_me: return
        
        setup_chat_screen() 
        
        def run_host():
            nonlocal s, conn
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('0.0.0.0', 6000))
                s.listen(1)
                safe_print("Waiting for peer to connect...")
                
             
                conn, addr = s.accept() 
                
                name_peer = conn.recv(100).decode().strip()
                conn.sendall(name_me.encode('utf-8'))
                safe_print(f"Connected with {name_peer}")
                threading.Thread(target=recv_loop, args=(conn, name_peer), daemon=True).start()
            except OSError:
                pass # This happens when you click "Back" and s.close() is called
            except Exception as e:
                safe_print(f"Error: {e}")

        
        threading.Thread(target=run_host, daemon=True).start()

    def mode_connect():
        nonlocal name_me
        ip = simpledialog.askstring("IP", "Enter peer IP:")
        if not ip: return
        name_me = simpledialog.askstring("Name", "Enter your name:")
        if not name_me: return

        setup_chat_screen() 

        def run_client():
            nonlocal s
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ip, 6000)) # This blocks if IP is unreachable, so we thread it
                s.sendall(name_me.encode('utf-8'))
                name_peer = s.recv(100).decode().strip()
                safe_print(f"Connected with {name_peer}")
                threading.Thread(target=recv_loop, args=(s, name_peer), daemon=True).start()
            except OSError:
                pass # Socket closed by "Back"
            except Exception as e:
                safe_print(f"Error: {e}")

        threading.Thread(target=run_client, daemon=True).start()

    Label(frame_mode_select, text="Select Mode", font=("Arial", 14)).pack(pady=20)
    Button(frame_mode_select, text="Host a Chat", command=mode_host, height=2, width=20).pack(pady=10)
    Button(frame_mode_select, text="Connect to Peer", command=mode_connect, height=2, width=20).pack(pady=10)
    Button(frame_mode_select, text="Cancel", command=on_close).pack(pady=20)
    
    frame_mode_select.pack()

# 2. GROUP CHAT & AUTH SYSTEM

def start_group_chat_interface(server_ip, current_user):
    # This creates the actual Chat Window
    grp_win = Toplevel(root)
    grp_win.geometry("450x500")
    grp_win.title(f"Group Chat - {current_user}")

    global current_chat_area
    current_chat_area = scrolledtext.ScrolledText(grp_win, height=20, width=50, state='disabled')
    current_chat_area.pack(padx=10, pady=10)
    
    msg_entry = Entry(grp_win, width=40)
    msg_entry.pack(side=LEFT, padx=10, pady=10)

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    try:
        s.connect((server_ip, 5000))
        s.sendall(current_user.encode('utf-8'))
        # Try receive server name
        try: name_r = s.recv(100).decode().strip()
        except: name_r = "Server"
        safe_print(f"Connected to {name_r}")
    except:
        messagebox.showerror("Error", "Could not connect to Group Server")
        grp_win.destroy()
        return

    def on_group_close():
        try: s.close()
        except: pass
        grp_win.destroy()
        

    grp_win.protocol("WM_DELETE_WINDOW", on_group_close)

    def send_msg():
        i = msg_entry.get()
        msg_entry.delete(0, END)
        if i:
            if i==";":
                s.close()
                on_group_close()
                return
            s.sendall((current_user+":"+i).encode('utf-8'))
            # --- FIX: Display the sent message locally ---
            safe_print(f"{current_user} : {i}")

    Button(grp_win, text="Send", command=send_msg).pack(side=LEFT)
    Button(grp_win, text="Close", command=on_group_close).pack(side=RIGHT, padx=10)

    def recv_thread():
        while True:
            try:
                r = s.recv(5100)
                if not r: break
                r = r.decode().strip()
                safe_print(f"\n{r}")
            except: break

    threading.Thread(target=recv_thread, daemon=True).start()


def group_system_entry():
    # 1. Ask for Server IP first
    server_ip = simpledialog.askstring("Server IP", "Enter Server IP (Leave empty for localhost):")
    if server_ip is None: return # Cancelled
    if not server_ip: server_ip = socket.gethostname()

    root.withdraw()
    
    # 2. Login/Signup Window
    auth_win = Toplevel(root)
    auth_win.geometry("300x300")
    auth_win.title("Authentication")

    def back_to_main():
        auth_win.destroy()
        root.deiconify()

    auth_win.protocol("WM_DELETE_WINDOW", back_to_main)

    def perform_login():
        user = simpledialog.askstring("Login", "Username:")
        if not user: return
        pwd = simpledialog.askstring("Login", "Password:", show='*')
        
        resp = send_auth_request(server_ip, f"LOGIN|{user}|{pwd}")
        if resp == "1":
            messagebox.showinfo("Success", "Login Successful")
            auth_win.destroy()
            open_dashboard(server_ip, user)
        elif resp == "0":
            messagebox.showerror("Failed", "Incorrect credentials")
        else:
            messagebox.showerror("Error", resp)

    def perform_signup():
        user = simpledialog.askstring("Signup", "New Username:")
        if not user: return
        pwd = simpledialog.askstring("Signup", "New Password:", show='*')
        
        resp = send_auth_request(server_ip, f"SIGNUP|{user}|{pwd}")
        if resp == "1":
            messagebox.showinfo("Success", "Signup Successful! Please Login.")
        elif resp == "0":
            messagebox.showerror("Fail", "Username exists.")
        else:
            messagebox.showerror("Error", resp)

    Label(auth_win, text="Group Chat Auth", font=("Arial", 12)).pack(pady=20)
    Button(auth_win, text="Login", command=perform_login, width=20).pack(pady=5)
    Button(auth_win, text="Signup", command=perform_signup, width=20).pack(pady=5)
    Button(auth_win, text="Back", command=back_to_main, width=20).pack(pady=20)

def open_dashboard(server_ip, user):
    dash_win = Toplevel(root)
    dash_win.geometry("300x400")
    dash_win.title(f"Dashboard - {user}")

    def do_logout():
        send_auth_request(server_ip, f"LOGOUT|{user}")
        dash_win.destroy()
        root.deiconify() # Go back to main app menu

    dash_win.protocol("WM_DELETE_WINDOW", do_logout)

    def join_chat():
        start_group_chat_interface(server_ip, user)

    def check_online():
        resp = send_auth_request(server_ip, "GET_ONLINE")
        messagebox.showinfo("Online Users", resp)

    Label(dash_win, text=f"Welcome, {user}", font=("Arial", 14)).pack(pady=20)
    
    Button(dash_win, text="Join Group Chat", command=join_chat, height=2, width=25).pack(pady=10)
    Button(dash_win, text="Check Online Users", command=check_online, height=2, width=25).pack(pady=10)
    Button(dash_win, text="Logout", command=do_logout, height=2, width=25, bg="#ffcccc").pack(pady=30)


# MAIN MENU

def main():
    Label(root,text="Welcome to PySocket",font=("Arial", 18, "bold")).pack(pady=20)
    
    Button(root,text="Direct Chat (Peer to Peer)", command=direct_chat, height=2, width=30).pack(pady=10)
    Button(root,text="Group Chat (via server)", command=group_system_entry, height=2, width=30).pack(pady=10)
    Button(root,text="Exit", command=root.quit, height=2, width=30).pack(pady=10)

if __name__ == "__main__":
    main()
    root.mainloop()