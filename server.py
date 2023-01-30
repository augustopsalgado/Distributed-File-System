from assets import *
import threading
import socket
import time

"""
Arquivo responsável por iniciar o servidor e receber as requisições dos clientes

"""

class ThreadedServer(object):
    """
    Classe responsável por iniciar o servidor e receber as requisições dos clientes
    """
    def __init__(self, host, port): 
        """
        Construtor da classe
        """
        self.host = host # Endereço do servidor
        self.port = port # Porta do servidor
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Cria o socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Configura o socket
        self.sock.bind((self.host, self.port)) # Associa o socket ao endereço e porta

    def listen(self):
        """
        Método responsável por iniciar o servidor e receber as requisições dos clientes
        """ 
        self.sock.listen(5) # Inicia o servidor
        print ("Server listening")	
        while True: # Loop infinito para receber as requisições dos clientes
            client, address = self.sock.accept()  # Aceita a conexão do cliente
            print ('Conexão aceita, bem vindo ' + str(address)) # Exibe mensagem de boas vindas
            client.settimeout(600) # Configura o tempo de timeout
            threading.Thread(target = execute_server , args = (client,address)).start() # Inicia uma thread para atender o cliente

def start_server():
    """
    Função responsável por iniciar o servidor
    """
    host = socket.gethostname() # Pega o nome do host
    port = 5000 # Porta do servidor

    ThreadedServer(host, port).listen() # Inicia o servidor criando uma instância da classe ThreadedServer

def execute_server(conn, addr):
    """
    Função responsável por receber as requisições dos clientes gerenciando as threads
    E também é responsável por enviar as mensagens de boas vindas
    Estabelendo a comunicação com o cliente
    """
    conn.send('Bem vindo ao servidor de arquivos!\n'.encode())

    userAuth = login(conn) # Faz o login do usuário
    if(userAuth != False): # Se o usuário foi autenticado
        estabeleceComunicacao(conn, userAuth) # Estabelece a comunicação com o cliente
        start_server() # Inicia o servidor
    else: # Se o usuário não foi autenticado
        print("Erro ao fazer login") 
        time.sleep(10) 
        conn.close() # Fecha a conexão
        start_server() # Inicia o servidor novamente

def estabeleceComunicacao(conn, user):
    """
    Função responsável por estabelecer a comunicação com o cliente
    """
    configSessao(user) # Configura a sessão do usuário

    while True: # Loop infinito para receber as requisições do cliente
        try:  # Tenta receber a requisição do cliente
            data = conn.recv(2048) # Recebe a requisição do cliente
            data = data.decode()

            if data == '0': # Exibir/Listar arquivos (cliente lista os arquivos do servidor)
                lista =  listarArquivos(user) # Lista os arquivos do usuário
                conn.send(lista.encode()) # Envia a lista de arquivos para o cliente
                print("Arquivos listados com sucesso")
            
            elif data == '1': # Receber arquivo (cliente recebe arquivo do servidor)
                # receber o nome do arquivo
                dataFile = conn.recv(2048)
                dataFile = dataFile.decode()

                # editar pra possibilitar receber arquivos compartilhados
                pathFile = "C:\\Files\\" + user + "\\" + dataFile # Path do arquivo

                # Verifica se o arquivo existe no servidor
                if (not os.path.exists(pathFile)): # Se o arquivo não existe
                    conn.send("404".encode()) # Envia mensagem de erro para o cliente
                    print("Arquivo não encontrado")
                    continue # Volta para o início do loop
                else: # Se o arquivo existe
                    conn.send("200".encode()) # Envia mensagem de sucesso para o cliente
                    print("Enviando arquivo...") 
                    
                    serializar, dadosUpload = serializarArquivo(pathFile) # Serializa o arquivo
                    # Envia o nome do arquivo e o tamanho do arquivo
                    msg = pathFile + " && " + str(len(serializar.unpack(dadosUpload)[1]))  # Monta a mensagem
                    conn.send(msg.encode()) # Envia a mensagem para o cliente
 
                    # Aguarda mensagem de confirmação do cliente
                    response = conn.recv(2048).decode()
                    if (response == "200"): # Se o cliente retornou 200
                        print("Enviando arquivo...")
                        time.sleep(5)
                        conn.send(dadosUpload) # Envia o arquivo para o cliente
                        
                        # Recebe mensagem de confirmação do servidor
                        response = conn.recv(2048).decode()
                        if (response == "200"): # Se o cliente retornou 200
                            print("Arquivo enviado com sucesso!")
                            time.sleep(5)
                            continue
                        else: # Se o cliente retornou 404
                            print("Erro ao receber arquivo! cliente retornou: " + response)
                            time.sleep(5)
                            continue

            elif data == '3': # Excluir arquivo
                # receber o nome do arquivo
                dataFile = conn.recv(2048)
                dataFile = dataFile.decode()

                if excluirArquivo(user, dataFile): # Exclui o arquivo
                    print("Arquivo excluído com sucesso")
                    conn.send("200".encode()) # Envia mensagem de sucesso para o cliente
                else: # Se o arquivo não existe
                    print("Erro ao excluir arquivo") 
                    conn.send("405".encode()) # Envia mensagem de erro para o cliente

            elif data == '4': # Renomear arquivo
                # receber o nome do arquivo
                dataFile = conn.recv(2048)
                dataFile = dataFile.decode()

                # receber o novo nome do arquivo
                newNameFile = conn.recv(2048)
                newNameFile = newNameFile.decode()

                if renomearArquivo(user, dataFile, newNameFile): # Renomeia o arquivo
                    print("Arquivo renomeado com sucesso") 
                    conn.send("200".encode()) # Envia mensagem de sucesso para o cliente
                else: # Se o arquivo não existe
                    print("Erro ao renomear arquivo")
                    conn.send("405".encode()) # Envia mensagem de erro para o cliente

            elif data == '5': # Adicionar ou atualizar arquivo
                # receber o nome do arquivo e o tamanho do arquivo
                dataFile = conn.recv(2048)
                dataFile = dataFile.decode()

                # separar o nome do arquivo e o tamanho do arquivo
                dataFile = dataFile.split(" && ")
                nomeArquivo = dataFile[0]
                tamanhoArquivo = dataFile[1]

                # serializar o arquivo
                serializar = struct.Struct("{}s {}s".format(len(nomeArquivo.split()[0]), int(tamanhoArquivo.split()[0])))
                 
                conn.send("200".encode()) # Envia mensagem de sucesso para o cliente
                print("Recebendo arquivo...")

                # receber o arquivo
                data = conn.recv(4096)
                data = data.decode()

                # deserializar o arquivo
                nome, arquivo = serializar.unpack(data.encode())

                if salvarArquivo(user, nome.decode(), arquivo): # Salva o arquivo
                    print("Arquivo salvo com sucesso")
                    conn.send("200".encode()) # Envia mensagem de sucesso para o cliente
                else: # Se o arquivo não existe
                    print("Erro ao salvar arquivo")
                    conn.send("405".encode())    # Envia mensagem de erro para o cliente 
            
            elif data == '6': # Compartilhar arquivo
                # receber o nome do arquivo
                dataFile = conn.recv(2048)
                dataFile = dataFile.decode()

                # receber o nome do usuário
                dataUser = conn.recv(2048)
                dataUser = dataUser.decode()

                # verificar se o usuário existe
                if not verificarUsuario(dataUser):
                    print("Usuário não existe")
                    conn.send("406".encode())
                    continue
                else: # Se o usuário existe
                    if compartilharArquivo(user, dataFile, dataUser): # Compartilha o arquivo
                        print("Arquivo compartilhado com sucesso")
                        conn.send("200".encode()) # Envia mensagem de sucesso para o cliente
                    else: # Se o arquivo não existe
                        print("Erro ao compartilhar arquivo")
                        conn.send("404".encode()) # Envia mensagem de erro para o cliente
                    

            elif data == '11': # Encerrar conexão
                print("Encerrando cliente...")
                time.sleep(5)
                conn.close() # Encerra a conexão com o cliente
                return False # Encerra o loop
            
        except Exception as e: # Se ocorrer algum erro
            print(e) # Imprime o erro
            return False # Encerra o loop

def login(conn):
    """
    Função que realiza o login do usuário
    """
    for i in range(2, -1, -1): # 3 tentativas
        cls() # Limpa a tela
        # get username
        username = conn.recv(2048) 
        username = username.decode()
       
        # get password 
        password = conn.recv(2048)
        password = password.decode()

        if (verificausuario(username)): # Verifica se o usuário existe
            if (verificasenha(username,password)): # Verifica se a senha está correta
                print("Seja bem-vindo, " + username) 
                conn.send("200".encode()) # Envia mensagem de sucesso para o cliente
                print("Login efetuado com sucesso\n") 
                time.sleep(5)
                return username # Retorna o nome do usuário
            else: # Se a senha está incorreta
                print("Senha incorreta")
                print(f"Login falhou, você tem mais {i} tentativas!") 
                conn.send("405".encode()) # Envia mensagem de erro para o cliente
                time.sleep(5) 
                continue # Continua o loop
        else: # Se o usuário não existe
            # caso tenha que cadastrar um novo usuario, requisitar senha de administrador
            print("Usuário não cadastrado, inserindo novo usuário")
            conn.send("404".encode()) # Envia mensagem de usuário inexistente para o cliente

            # Recebe a senha de administrador
            adm = conn.recv(2048) 
            adm = adm.decode() 

            if (insereusuario(username, password, adm)): # Insere o novo usuário
                conn.send("200".encode()) # Envia mensagem de sucesso para o cliente
                print("Login efetuado com sucesso\n")
                time.sleep(5)
                return username # Retorna o nome do usuário
            else: # Se a senha de administrador está incorreta
                conn.send("405".encode()) # Envia mensagem de erro para o cliente
                print("Senha de administrador incorreta\n")
                time.sleep(5)
                return False # Encerra o loop

def main():
    """
    Função principal
    """
    inicializa() # cria pastas e arquivos iniciais
    start_server() # inicia o servidor

main()