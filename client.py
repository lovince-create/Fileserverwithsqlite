import socket,readline,os,time

def push(filename):
    with open(filename,"rb") as myFile:
        binaire = myFile.read()
    return binaire
    
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host,port = "127.0.0.1",8081
client_socket.connect((host,port))

nom = "a" #input("Entrez votre pseudo> ")
addresse_envoyee = 0
buffers = 4096
listening = 0
full = b""

while True:
    if listening == 0:
        message = input(f"{nom}> ")
    
    if message != "@quit":
        #ligne = f"{message}"
        if "@push" in message:
            linetab = message.split(" ")
            nomfichier = linetab[1]
            contenu = push(nomfichier)
            taille = os.path.getsize(nomfichier)
            chaine = f"{nomfichier}@{taille}@1@push"
            client_socket.sendall(chaine.encode("utf-8"))
            time.sleep(1)
            print(len(contenu))
            client_socket.sendall(contenu)
        elif "@get" in message:
            linetab = message.split(" ")
            nomfichier = linetab[1]
            chaine = f"{nomfichier}@get"
            client_socket.sendall(chaine.encode("utf-8"))
            reception = client_socket.recv(buffers)
            if 0 < len(reception) < 20:
                client_socket.sendall("OK".encode("utf-8"))
                buffers = int(reception)
                listening = 1
                full = b""
            else:
                if reception:
                    full += reception
                print(buffers,"***",len(full),"***",len(reception))
                with open(nomfichier,"wb") as myFile:
                    myFile.write(full)
                listening = 0

    else:
        break
