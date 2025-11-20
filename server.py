import socket
import os
import threading
import time       
clients_lock = threading.Lock()

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
            if i <= len(client) - 1 and i - 1 >= 0:
                i -= 1
def GroupChat():
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host='0.0.0.0'
    s.bind((host,5000))
    print("Server listening for Group Chat connections\n")
    s.listen(10)
    clients=[]
    arr=['/','*',':',';','!','@','#','$','%','^','&','?','|','\\']
    name_me=str(input("Enter your name:\n"))
    while True:
        if name_me not in arr:
            break
        else:
            print("Single special chracters not allowed\n")
            name_me=str(input("Enter your name:\n"))
    m=int(input("Enter the number of clients that are allowed to connect:\n(Max allowed 10)"))
    for i in range(0,m):
        soc,l=s.accept()
        name=soc.recv(100).decode().strip()
        soc.sendall(name_me.encode('utf-8'))
        clients.append((soc,name,name_me))
        print("Client ",i,"'"+name+"'"," entered the Chat")
       # for j in range(0,i):
          #  clients[j][0].sendall(("\nClient "+i+"'"+name+"' entered the Chat").encode('utf-8'))
    for i in range(0,m):
        stop_event=threading.Event()
        threading.Thread(target=client_soc,args=(clients,i,m,stop_event)).start()    

        
while True:
    print("Welcome")
    time.sleep(2)
    c=str(input("Would you like a Group Chat or a Single Chat?\nEnter 1 or 2 respectively\n"))
    if c=="1":
        os.system("cls")
        GroupChat()
        break
    elif c=="2":
        os.system("cls")
        peer_chat()
        break
    else:
        print("Invalid\n")
        time.sleep(2)
        print("You will be redirected to Main Menu in 3 seconds\n")
        time.sleep(3)
        os.system("cls")        