from assets import *
import threading
import socket
import time

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        print ("Server listening")	
        while True:
            client, address = self.sock.accept()
            print ('Conexão aceita, bem vindo ' + str(address))
            client.settimeout(60)
            threading.Thread(target = execute_server , args = (client,address)).start()

def start_server():
    host = socket.gethostname()
    port = 5000

    ThreadedServer(host, port).listen()

def execute_server(conn, addr):
    conn.send('Bem vindo ao servidor de arquivos!\n'.encode())

    userAuth = login(conn)
    if(userAuth != False):
        estabeleceComunicacao(conn, userAuth)
        start_server()
    else:
        print("Erro ao fazer login")
        time.sleep(10)
        conn.close()
        start_server()

def estabeleceComunicacao(conn, user):
    configSessao(user)
    while True:
        try:
            data = conn.recv(2048)
            data = data.decode()

            if data == '0': # Exibir/Listar arquivos
                """
                O usuário tem acesso somente aos arquivos que ele criou
                """
                lista =  listarArquivos(user)
                conn.send(lista.encode())
                print("Arquivos listados com sucesso")
            elif data == '5': # Adicionar ou atualizar arquivo
                # receber o nome do arquivo e o tamanho do arquivo
                dataFile = conn.recv(2048)
                dataFile = dataFile.decode()

                # separar o nome do arquivo e o tamanho do arquivo
                dataFile = dataFile.split(" && ")
                nomeArquivo = dataFile[0]
                tamanhoArquivo = dataFile[1]

                serializar = struct.Struct("{}s {}s".format(len(nomeArquivo.split()[0]), int(tamanhoArquivo.split()[0])))
                
                conn.send("200".encode())
                print("Recebendo arquivo...")

                # receber o arquivo
                data = conn.recv(4096)
                data = data.decode()

                # deserializar o arquivo
                nome, arquivo = serializar.unpack(data.encode())

                if salvarArquivo(user, nome.decode(), arquivo):
                    print("Arquivo salvo com sucesso")
                    conn.send("200".encode())
                else:
                    print("Erro ao salvar arquivo")
                    conn.send("405".encode())    
            elif data == '11':
                print("Encerrando cliente...")
                time.sleep(5)
                conn.close()
                return False
        except Exception as e:
            print(e)
            #conn.close()
            return False

def login(conn):
    for i in range(2, -1, -1):
        cls()
        # get username
        username = conn.recv(2048)
        username = username.decode()
       
        # get password 
        password = conn.recv(2048)
        password = password.decode()

        if (verificausuario(username)):
            if (verificasenha(username,password)):
                print("Seja bem-vindo, " + username)
                conn.send("200".encode())
                print("Login efetuado com sucesso\n")
                time.sleep(5)
                return username
            else:
                print("Senha incorreta")
                print(f"Login falhou, você tem mais {i} tentativas!")
                conn.send("405".encode())
                time.sleep(5)
                continue
        else:
            # caso tenha que cadastrar um novo usuario, requisitar senha de administrador
            print("Usuário não cadastrado, inserindo novo usuário")
            conn.send("404".encode())

            adm = conn.recv(2048)
            adm = adm.decode()

            if (insereusuario(username, password, adm)):
                conn.send("200".encode())
                print("Login efetuado com sucesso\n")
                time.sleep(5)
                return username
            else:
                conn.send("405".encode())
                print("Senha de administrador incorreta\n")
                time.sleep(5)
                return False

def main():
    inicializa() # cria pastas e arquivos iniciais
    start_server()

main()