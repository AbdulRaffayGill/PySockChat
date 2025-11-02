import socket
import os
import threading
import time       
def peer_chat():
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host=socket.gethostname()
    s.bind((host,5000))
    print("Server listening for Receiver Connection\n")
    s.listen()
    b,j=s.accept()
    arr=['/','*',':',';','!','@','#','$','%','^','&','?','|','\\']
    name_r=b.recv(100).decode().strip()
    name=str(input("Enter your name:\n"))
    while True:
        if name not in arr:
            break
        else:
            print("Single special chracters not allowed\n")
            name=str(input("Enter your name:\n"))
    b.sendall(name.encode('utf-8'))
    os.system("cls")
    while True:
        r=b.recv(5000)
        r=r.decode().strip()
        if not r:
            print(name_r," : ","(Empty message received)\n")
        elif r==';':
            print("Chat ended by the other person:\nQuitting\n")
            b.close()
            break
        else:
            print(name_r," : ",r,'\n')
        i=str(input( name +" : ")).encode('utf-8')
        send=b.sendall(i)
        if i==";":
            print("You have closed the chat\n")
            s.close()
            break
def client_soc(client,i,m,stop_event):
    while not stop_event.is_set():
        r=client[i][0].recv(5100).decode().strip()
        if not r.strip(client[i][1]+":"):
            print(client[i][1]," : ","(Empty message received)\n")
        elif r.strip(client[i][1]+":")==';':
            stop_event.set()
            break
        else:
            print(r,'\n')
            for j in range(0,m):
                if(client[i][0]!=client[j][0]):
                    client[j][0].sendall(("\n"+r).encode('utf-8'))
    if(stop_event.is_set()):
        print(client[i][1]," left the chat")
        client[i][0].stop()
        client[i][0].join()
                 
            
def GroupChat():
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host=socket.gethostname()
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
        peer_chat()
        break
    elif c=="2":
        os.system("cls")
        GroupChat()
        break
    else:
        print("Invalid\n")
        time.sleep(2)
        print("You will be redirected to Main Menu in 3 seconds\n")
        time.sleep(3)
        os.system("cls")        