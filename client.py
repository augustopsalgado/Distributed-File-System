from assets import *
import socket 
import time

def cria_socket_client():
    for i in range(1, 10):
        try: 
            host = socket.gethostname()
            port = 5000
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            print("Conectado com o servidor!")
            return client_socket 
        except:
            print(f"Erro ao conectar com o servidor, tentando novamente... {i}/10")
            time.sleep(10)
            continue
    # Tentou conectar 10 vezes e não conseguiu
    return False 

def login(client_socket):
    # Recebe mensagem de boas vindas do servidor
    print(client_socket.recv(1024).decode())
    tentativas = 3
    while True:
        
        # Envia username para o servidor
        username = input("Digite seu username:")
        while (" " in username):    
            username = input("Não é permitido o uso de espaços no nome de usuário, digite novamente:")
        client_socket.send(username.encode())

        # Envia password para o servidor
        password = input("Digite sua senha:")
        password = Sha512Hash(password)
        client_socket.send(password.encode())

        # Recebe mensagem de login efetuado ou falhou
        data = client_socket.recv(2048).decode()

        if (data == "200"):
            print("Login efetuado com sucesso!")
            time.sleep(2)
            print("Seja bem-vindo, " + username + "! \n")
            time.sleep(5)
            return True
        elif (data == "405"): 
            tentativas -= 1
            print(f"Senha incorreta para o usuário {username}, você tem mais {tentativas} tentativas!") 
            time.sleep(5)
            if (tentativas == 0):
                print("Número de tentativas esgotado, encerrando programa...")
                time.sleep(5)
                return False
            continue
        elif (data == "404"):
            print("Usuário não cadastrado, necessário inserir novo usuário...")
            adm = input("Digite a senha de administrador:")
            adm = Sha512Hash(adm)
            client_socket.send(adm.encode())

            data = client_socket.recv(2048).decode()
            if (data == "200"):
                print("Usuário cadastrado com sucesso!")
                time.sleep(2)
                print("Seja bem-vindo, " + username + "! \n")
                time.sleep(5)
                return True
            else:
                print("Senha de administrador incorreta!")
                return False

def estabeleceComunicacao(conn):
    
    while True:
        try:
            imprimemenu()
            opcao = input("Digite a opção desejada: ")
            conn.send(opcao.encode())

            if opcao == '11':
                print("Encerrando cliente...")
                time.sleep(5)
                conn.close()
                return False
            
            # recebe resposta do servidor
            data = conn.recv(2048)
            data = data.decode()

            print(data)
            time.sleep(5)

        except KeyboardInterrupt:
            print("Encerrando cliente...")
            conn.close()
            return False

    

def main():
    inicializa()
    
    client_socket = cria_socket_client()
    if not client_socket:
        print("Não foi possível conectar com o servidor!")
        return
    else:
        if (login(client_socket)):

            estabeleceComunicacao(client_socket)
        else:
            print("Erro ao fazer login, encerrando cliente...")
            time.sleep(10)
            client_socket.close()

main()
