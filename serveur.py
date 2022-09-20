import socket,select,sqlite3,time

serveur = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host,port = "127.0.0.1",8081
serveur.bind((host,port))
serveur.listen(2)
cont =  True
socket_objs = [serveur]
active = 0
buffers = 4096
addresse_recue = 0
full = ""
code = 0
connect = sqlite3.connect("fichiers.db")
cursor = connect.execute("""CREATE TABLE IF NOT EXISTS stockage(id INTEGER PRIMARY KEY AUTOINCREMENT, chemin varchar(100), contenu BLOB)""")
query1 = """INSERT INTO stockage(chemin) VALUES (?)"""
query2 = """INSERT INTO stockage(contenu) VALUES (?)"""
query3 = """INSERT INTO stockage(chemin,contenu) VALUES (?,?)"""
query4 = """SELECT contenu,length(contenu) from stockage WHERE chemin = (?)"""
full = b""
querytimes = 0

while cont:
    outread,outwrite,outerror = select.select(socket_objs,[],socket_objs)

    for socket_obj in outread:
        if socket_obj is serveur:
            client,addresse = serveur.accept()
            print("Nouvelle connexion")
            socket_objs.append(client)
            active += 1
        else:
            reception = socket_obj.recv(buffers)
            if 0 < len(reception) < 60 and b"@push" in reception:
                print("**",reception)
                reception = reception.decode("utf-8")
                recept =  reception.split("@")
                nomfichier = recept[0]
                buffers = int(recept[1])
                code = int(recept[2])
                addresse_recue = 0
                #full = b""
            elif len(reception) > 60:
                if reception:
                    full += reception
                addresse_recue = 0
                code = 0
                querytimes += 1
                    #with open(nomfichier,"wb") as myFile:
                    #        myFile.write(full)
                if len(reception) == buffers:
                    cursor.execute(query3,(nomfichier,reception,))
                    connect.commit()
            elif b"@get" in reception:
                reception = reception.decode("utf-8")
                print("&&",reception)
                if len(reception) > 2:
                    reception = reception.replace("OK","")
                    recept = reception.split("@")
                    nomfichier = recept[0]
                    cursor.execute(query4,(recept[0],))
                    results = cursor.fetchall()
                    contenu = results[0][0]
                    taille = results[0][1]
                    print("**",taille)
                if code == 0:
                    client.sendall(str(taille).encode("utf-8"))
                    reception2 = client.recv(buffers).decode("utf-8")
                    if reception2 == "OK":
                        client.sendall(contenu)
                        code = 0
            if not reception:
                    cont = False

            """elif b"@pull" in reception:
                reception = reception.decode("utf-8")
                cursor.execute(query4,(reception,))
                print(cursor)
                

            #if reception.count(b"@") == 1:
             #   reception_taille = reception.decode("utf-8")
              #  recept = reception_taille.split("@")
              #  print(recept)
             #   buffers = int(recept[1])
              #  nomfichier = recept[0]
            #elif reception.count(b"+") == 0:
               # reception_taille = reception
                    
              #  if reception_taille:
               #     with open(nomfichier,"wb") as myFile:
              #          myFile.write(reception_taille)
           # else:
              #  print(f"Deconnexion: {active} restants")
               # active -= 1
               # if active < 0:
               #     cont = False"""
