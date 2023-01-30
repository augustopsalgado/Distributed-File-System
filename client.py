from assets import *
import socket 
import time

"""
Arquivo cliente do sistema de arquivos distribuídos
Responsável por fazer a conexão com o servidor e enviar os comandos

"""

def cria_socket_client():
    """
    Função responsável por criar o socket do cliente
    """
    for i in range(1, 10): # Cliente tenta conectar 10 vezes
        try:  # Tenta conectar com o servidor
            host = socket.gethostname() # Pega o nome do host
            port = 5000 # Porta do servidor
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Cria o socket
            client_socket.connect((host, port)) # Conecta com o servidor
            print("Conectado com o servidor!")  
            return client_socket  # Retorna o socket
        except: # Não conseguiu conectar com o servidor
            print(f"Erro ao conectar com o servidor, tentando novamente... {i}/10") # Mostra mensagem de erro, tenta mais uma vez
            time.sleep(10)
            continue
    # Tentou conectar 10 vezes e não conseguiu
    return False 

def login(client_socket):
    """
    Função responsável por fazer o login do usuário
    """
    # Recebe mensagem de boas vindas do servidor
    print(client_socket.recv(1024).decode()) 
    tentativas = 3 # Número de tentativas para login
    while True: # Loop para login
        # Envia username para o servidor
        username = input("Digite seu username:") 
        while (" " in username):  # Verifica se o username tem espaços    
            username = input("Não é permitido o uso de espaços no nome de usuário, digite novamente:")
        client_socket.send(username.encode()) # Envia username para o servidor

        # Envia password para o servidor
        password = input("Digite sua senha:")
        password = Sha512Hash(password)
        client_socket.send(password.encode())

        # Recebe mensagem de login efetuado ou falhou
        data = client_socket.recv(2048).decode()

        if (data == "200"): # Login efetuado com sucesso
            print("Login efetuado com sucesso!")
            time.sleep(2)
            print("Seja bem-vindo, " + username + "! \n")
            time.sleep(5)
            return True
        elif (data == "405"):  # Senha incorreta, tenta 3 vezes
            tentativas -= 1
            print(f"Senha incorreta para o usuário {username}, você tem mais {tentativas} tentativas!") 
            time.sleep(5)
            if (tentativas == 0):   # Número de tentativas esgotado
                print("Número de tentativas esgotado, encerrando programa...")
                time.sleep(5)
                return False
            continue
        elif (data == "404"): # Usuário não cadastrado
            print("Usuário não cadastrado, necessário inserir novo usuário...")
            adm = input("Digite a senha de administrador:") # Recebe senha de administrador
            adm = Sha512Hash(adm) # Envia senha de administrador para o servidor
            client_socket.send(adm.encode()) # Envia senha de administrador para o servidor

            data = client_socket.recv(2048).decode() # Recebe mensagem de senha de administrador incorreta ou usuário cadastrado com sucesso
            if (data == "200"): # Usuário cadastrado com sucesso
                print("Usuário cadastrado com sucesso!") 
                time.sleep(2)
                print("Seja bem-vindo, " + username + "! \n")
                time.sleep(5)
                return True
            else: # Senha de administrador incorreta
                print("Senha de administrador incorreta!")
                return False

def estabeleceComunicacao(conn):
    """
    Função responsável por estabelecer a comunicação com o servidor
    Recebendo os comandos do usuário e enviando para o servidor
    """
    while True:
        try: # Tenta receber mensagem do servidor
            imprimemenu() # Imprime o menu
            opcao = input("Digite a opção desejada: ") # Recebe a opção do usuário
            conn.send(opcao.encode()) # Envia a opção para o servidor

            if opcao == '2': #  Receber um arquivo (Get) - Cliente recebe arquivo do servidor
                # Enviar o nome do arquivo que deseja receber
                FileName = input("Digite o nome do arquivo: ")
                conn.send(FileName.encode()) 

                # receber resposta do servidor
                response = conn.recv(2048)
                response = response.decode()

                if response == "404": # Arquivo não encontrado
                    print("Arquivo não encontrado!")
                    continue
                else: # Arquivo encontrado
                    print("Arquivo encontrado!")
                    # receber o nome do arquivo e o tamanho do arquivo
                    dataFile = conn.recv(2048)
                    dataFile = dataFile.decode()

                    # separar o nome do arquivo e o tamanho do arquivo
                    dataFile = dataFile.split(" && ")
                    nomeArquivo = dataFile[0]
                    tamanhoArquivo = dataFile[1]

                    # serializar o nome do arquivo e o tamanho do arquivo
                    serializar = struct.Struct("{}s {}s".format(len(nomeArquivo.split()[0]), int(tamanhoArquivo.split()[0])))
                    
                    # enviar resposta para o servidor
                    conn.send("200".encode())
                    print("Recebendo arquivo...")

                    # receber o arquivo
                    data = conn.recv(4096)
                    data = data.decode()

                    # deserializar o arquivo
                    nome, arquivo = serializar.unpack(data.encode())

                    while True: # Loop para salvar o arquivo
                        # Recebe o caminho para salvar o arquivo
                        path = input("Digite o caminho para salvar o arquivo.  Exemplo:(C:\FileClient) \n") 
                        
                    
                        if not os.path.isdir(path): # Verifica se o caminho existe
                            print("Caminho não existe, tente novamente!")
                            continue
                        else: # Caminho existe
                            break
                    
                    # Salvar o arquivo
                    path = path + "\\" + FileName
                    try: # Tenta salvar o arquivo
                        # receber o conteúdo do arquivo
                        with open(path, 'wb') as f:
                            f.write(arquivo) # Salvar o arquivo
                            print("Arquivo salvo com sucesso")
                            time.sleep(2)
                    except Exception as e : # Erro ao salvar o arquivo
                        print("Erro ao salvar o arquivo")
                        print(e)
                        time.sleep(2)
                    continue
            
            elif opcao == '4': # Excluir arquivo do servidor
                # Enviar o nome do arquivo que deseja excluir
                FileName = input("Digite o nome do arquivo: ")
                conn.send(FileName.encode())

                # receber resposta do servidor
                response = conn.recv(2048)
                response = response.decode()

                if response == "404": # Arquivo não encontrado
                    print("Arquivo não encontrado!")
                    continue
                else: # Arquivo encontrado
                    print("Arquivo encontrado!")
                    print("Excluindo arquivo...")
                    time.sleep(2)
                    print("Arquivo excluído com sucesso!")
                    time.sleep(2)
                    continue
            
            elif opcao == '5': # Renomear arquivo do servidor
                # Enviar o nome do arquivo que deseja renomear
                FileName = input("Digite o nome do arquivo: ")
                conn.send(FileName.encode())

                # Enviar novo nome do arquivo
                newFileName = input("Digite o novo nome do arquivo: ")
                conn.send(newFileName.encode())

                # receber resposta do servidor
                response = conn.recv(2048)
                response = response.decode()

                if response == "405": # Arquivo não encontrado
                    print("Arquivo não encontrado!")
                    continue
                else: # Arquivo encontrado
                    print("Arquivo encontrado!")
                    print("Renomeando arquivo...")
                    time.sleep(2)
                    print("Arquivo renomeado com sucesso!")
                    time.sleep(2)
                    continue

            elif opcao == '3': # Adicionar ou atualizar arquivo (Put)
                while True: # Loop para receber o caminho do arquivo
                    pathFile = input("Digite o caminho do arquivo: ") # Recebe o caminho do arquivo
                    if not os.path.isfile(pathFile): # Verifica se o arquivo existe
                        print("Arquivo não encontrado, tente novamente!") 
                        continue 
                    else: # Arquivo existe
                        break

                serializar, dadosUpload = serializarArquivo(pathFile) # Serializa o arquivo
                # Envia o nome do arquivo e o tamanho do arquivo
                msg = pathFile + " && " + str(len(serializar.unpack(dadosUpload)[1]))  
                conn.send(msg.encode()) # Envia o nome do arquivo e o tamanho do arquivo

                # Aguarda mensagem de confirmação do servidor
                response = conn.recv(2048).decode()
                if (response == "200"): # Servidor está pronto para receber o arquivo
                    print("Enviando arquivo...") 
                    time.sleep(5)
                    conn.send(dadosUpload) # Envia o arquivo
                    
                    # Recebe mensagem de confirmação do servidor
                    response = conn.recv(2048).decode() 
                    if (response == "200"): # Arquivo enviado com sucesso
                        print("Arquivo enviado com sucesso!")
                        time.sleep(5)
                        continue
                    else: # Erro ao enviar arquivo
                        print("Erro ao enviar arquivo! Servidor retornou: " + response)
                        time.sleep(5)
                        continue

            elif opcao == '6': # Dar permissão de acesso do arquivo a outro usuário (Compartilhar)
                # Enviar o nome do arquivo que deseja compartilhar
                FileName = input("Digite o nome do arquivo: ")
                conn.send(FileName.encode())

                # Enviar o nome do usuário que deseja compartilhar o arquivo
                UserName = input("Digite o nome do usuário: ")
                conn.send(UserName.encode())

                # receber resposta do servidor
                response = conn.recv(2048)
                response = response.decode()

                if response == "404": # Arquivo não encontrado
                    print("Arquivo não encontrado!")
                    continue
                elif response == "406": # Usuário não encontrado
                    print("Usuário não encontrado!")
                    continue
                else: # Arquivo encontrado
                    print("Arquivo encontrado!")
                    print("Compartilhando arquivo...")
                    time.sleep(2)
                    print("Arquivo compartilhado com sucesso!")
                    time.sleep(2)
                    continue
            
            elif opcao == '11': # Encerrar conexão
                print("Encerrando cliente...")
                time.sleep(5)
                conn.close()
                return False # Encerra o loop de comunicação com o servidor
            
            # recebe resposta do servidor
            data = conn.recv(2048)
            data = data.decode()

            print(data) # Imprime a resposta do servidor
            time.sleep(2)

        except KeyboardInterrupt: # Encerra o cliente
            print("Encerrando cliente...")
            conn.close()
            return False

def main():
    #inicializa() # Inicializa o cliente 
    
    client_socket = cria_socket_client() # Cria o socket do cliente
    if not client_socket: # Erro ao criar o socket
        print("Não foi possível conectar com o servidor!")
        return
    else: # Socket criado com sucesso
        if (login(client_socket)):  # Faz login no servidor
            estabeleceComunicacao(client_socket) # Estabelece comunicação com o servidor
        else: # Erro ao fazer login
            print("Erro ao fazer login, encerrando cliente...")
            time.sleep(10)
            client_socket.close() # Encerra o socket do cliente

main()
