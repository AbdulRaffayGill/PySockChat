import socket
import os
import threading
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
        print("Only special chracters not allowed\n")
        name=str(input("Enter your name:\n"))
s.sendall(name.encode('utf-8'))
name_r=s.recv(100).decode().strip()
os.system("cls")
def send():
    while True:
        i=str(input(name+" : "))
        if i==";":
            print("You have closed the chat\n")
            s.close()
            break
        i=(name+":"+i).encode('utf-8')
        send=s.sendall(i)
    
def recv():
    while True:   
        r=s.recv(5100)
        r=r.decode().strip()
        if not r.strip(name_r):
            print(name_r," : ","(Empty message received\n)")
        elif r.strip(name_r)==';':
            print("Chat ended by the other person:\nQuitting\n")
            s.close()
            break
        else:
            print('\n',r,'\n')
threading.Thread(target=recv).start()            
threading.Thread(target=send).start()



    
    
        
