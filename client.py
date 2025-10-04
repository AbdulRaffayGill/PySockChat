import socket
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
while True:
    i=str(input(name+" : "))
    i=i.encode('utf-8')
    send=s.sendall(i)
    if i==";":
        print("You have closed the chat\n")
        s.close()
        break
    r=s.recv(5000)
    r=r.decode().strip()
    if not r:
        print(name_r," : ","(Empty message received\n)")
    elif r==';':
        print("Chat ended by the other person:\nQuitting\n")
        s.close()
        break
    else:
        print(name_r," : ",r,'\n')

        
