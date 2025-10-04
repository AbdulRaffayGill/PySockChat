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
            print("Only special chracters not allowed\n")
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
def client_soc(client,i,m):
    while True:
        r=client[i][0].recv(5000).decode().strip()
        if not r:
            print(client[i][1]," : ","(Empty message received)\n")
        elif r==';':
            print("Chat ended by the other person:\nQuitting\n")
            client[i][0].close()
            break
        else:
            print(client[i][1]," : ",r,'\n')
            for i in range(0,m):
                client[i][0].sendall("\n"+r)
        h=str(input(client[i][2] +" : ")).encode('utf-8')
        send=client[i][0].sendall(h)
        if h.decode()==";":
            print("You have closed the chat\n")
            client[i][0].close()
            break
def GroupChat():
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host=socket.gethostname()
    s.bind((host,5000))
    print("Server listening for Group Chat connections\n")
    s.listen(5)
    clients=[]
    arr=['/','*',':',';','!','@','#','$','%','^','&','?','|','\\']
    name_me=str(input("Enter your name:\n"))
    while True:
        if name_me not in arr:
            break
        else:
            print("Only special chracters not allowed\n")
            name_me=str(input("Enter your name:\n"))
    m=int(input("Enter the number of clients that are allowed to connect:\n(Max allowed 5)"))
    for i in range(0,m):
        soc,l=s.accept()
        name=soc.recv(100).decode().strip()
        soc.sendall(name_me.encode('utf-8'))
        clients.append((soc,name,name_me))
    for i in range(0,m):
        threading.Thread(target=client_soc,args=(clients,i,m)).start()    

        
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