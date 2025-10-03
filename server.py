import socket
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host=socket.gethostname()
s.bind((host,5000))
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