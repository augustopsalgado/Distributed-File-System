from datetime import datetime
import hashlib
import shutil
import ctypes
import struct
import json
import os

"""
Arquivo de configuração do sistema 
Contém as variáveis de configuração do sistema
E as funções em comum para o cliente e servidor
"""
Files = "C:\\Servidor\\Files\\" # Diretório de arquivos
Control = "C:\\Servidor\\Control\\" # Diretório de controle
Meta = "C:\\Servidor\\Meta\\" # Diretório de metadados
Share = "C:\\Servidor\\Share\\" # Diretório de compartilhamento
MetaShare = "C:\\Servidor\\Meta\\Share\\" # Diretório de metadados de compartilhamento

usuarios = "C:\\Servidor\\Control\\users.txt" # Arquivo de usuários

# admin123 - senha de administrador do sistema
superUser = "7fcf4ba391c48784edde599889d6e3f1e47a27db36ecc050cc92f259bfac38afad2c68a1ae804d77075e8fb722503f3eca2b2c1006ee6f6c7b7628cb45fffd1d"


def Sha512Hash(Password):
    """
    Função para gerar hash SHA512
    """
    HashedPassword=hashlib.sha512(Password.encode('utf-8')).hexdigest()
    return(HashedPassword)


def cls():
    """
    Função para limpar a tela
    """
    os.system('cls' if os.name=='nt' else 'clear')


def inicializa():
    """
    Função para inicializar o sistema e 
    criar os diretórios de arquivos, controle e metadados
    """
    if not os.path.isdir(Files):
        os.makedirs(Files)
    if not os.path.isdir(Control):
        os.makedirs(Control)
    if not os.path.isdir(Share):
        os.makedirs(Share)
    if not os.path.isdir(Meta):
        os.makedirs(Meta)
        os.makedirs(MetaShare)
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ret = ctypes.windll.kernel32.SetFileAttributesW(Meta, FILE_ATTRIBUTE_HIDDEN)
        ret = ctypes.windll.kernel32.SetFileAttributesW(Control, FILE_ATTRIBUTE_HIDDEN)

def imprimemenu():
    """
    Função para exibir o menu de opções do sistema
    """
    print("\n------------------------------------------\n")
    print("Opções: \n")
    print("1 - Exibir arquivos (List)\n")
    print("2 - Receber um arquivo (Get)\n") # servidor pro cliente
    print("3 - Adicionar ou atualizar arquivo (Put)\n") 
    print("4 - Excluir um arquivo (Delete)\n")
    print("5 - Renomear um arquivo \n")
    
    print("\n------------------------------------------\n")
    print("Opções de compartilhamento: \n")
    print("6 - Dar permissão de acesso dos meus arquivos a outro usuário\n") 
    print("7 - Retirar permissão de acesso de outro usuário\n")
    print("8 - Listar arquivos compartilhados comigo (List)\n")
    print("9 - Receber um arquivo compartilhado (Get)\n")
    print("10 - Adicionar ou atualizar arquivo compartilhado (Put)\n")
    print("11 - Sair\n")

def criaArquivoMetaUser(user):
    """
    Função responsável por criar o arquivo de metadados do usuário
    """
    pathFile = Meta + user + "\\MetaSessao.json" # endereço do arquivo de metadados do usuário que compartilhou o arquivo

    # criando dict de metadados
    meta = {}
    meta['nomeUsuario'] = user
    meta['criado_em'] = str(datetime.now())
    meta['modificado_em'] = str(datetime.now())
    meta['meus_Arquivos_Locais'] = []
    meta['meus_Arquivos_Compartilhados'] = []
    meta['arquivos_Compartilhados_Comigo'] = []
    meta['usando_arquivo'] = 'False'
    meta['nomeArquivo'] = ""
    meta['dataInicioLock'] = ""
    meta['dataFimLock'] = ""

    # salvando metadados no arquivo
    with open(pathFile, "w+") as f:
        json.dump(meta, f, indent=4)

def listaArquivosLocais(user):
    """
    Função responsável por listar os arquivos locais do usuário
    """
    arquivos = os.listdir(Files + user) # lista de arquivos do usuário
    if arquivos == None: # se não houver arquivos
        return []
    else: # se houver arquivos
        return arquivos

def attArquivoMetaUser(user, arquivoCompartilhado = None, arquivoCompartilhadoComigo = None):
    """
    Função responsável por atualizar o arquivo de metadados do usuário
    Atualizar modificado_em, meus_Arquivos_Locais
    """
    pathFile = Meta + user + "\\MetaSessao.json" # endereço do arquivo de metadados do usuário que compartilhou o arquivo

    # carregando metadados do arquivo
    with open(pathFile, "r") as f:
        meta = json.load(f)
    
    # atualizando metadados
    meta['modificado_em'] = str(datetime.now())
    meta['meus_Arquivos_Locais'] = listaArquivosLocais(user)

    if arquivoCompartilhado != None:
        meta['meus_Arquivos_Compartilhados'].append(arquivoCompartilhado)
    
    if arquivoCompartilhadoComigo != None:
         meta['arquivos_Compartilhados_Comigo'].append(arquivoCompartilhadoComigo)

    # salvando metadados no arquivo
    with open(pathFile, "w") as f:
        json.dump(meta, f, indent=4) 

def criaArquivoMetaShare(pathFile, user, userShare, nomeArquivo):
    """
    Função responsável por criar o arquivo de metadados do arquivo compartilhado
    """
    # criando dict de metadados
    meta = {}
    meta['owner_arquivo'] = user
    meta['nomeArquivo'] = nomeArquivo
    meta['compartilhado_em'] = str(datetime.now())
    meta['compartilhado_com'] = [userShare]
    
    meta['Lock_arquivo'] = 'False'
    meta['nomeUsuarioLock'] = ""
    meta['dataInicioLock'] = ""
    meta['dataFimLock'] = ""
   
    # salvando metadados no arquivo
    with open(pathFile, "w+") as f:
        json.dump(meta, f, indent=4)

def attArquivoMetaShare(pathFile, user, userShare):
    """
    Função responsável por atualizar o arquivo de metadados do arquivo compartilhado
    Atualizar compartilhado_com
    """
    # carregando metadados do arquivo
    with open(pathFile, "r") as f:
        meta = json.load(f)
    
    if meta['owner_arquivo'] != user: # se o usuário não for o dono do arquivo
        print("Você não é o dono do arquivo")
        return False
    else: # se o usuário for o dono do arquivo
        meta['compartilhado_com'].append(userShare) # atualizando compartilhado_com addc novo usuário

    # salvando metadados no arquivo
    with open(pathFile, "w") as f:
        json.dump(meta, f, indent=4)

def configSessao(user):
    """
    Função responsável por criar a pasta do usuário no diretório Meta
    E por criar o arquivo de metadados do usuário
    Configurando a sessão do usuário
    """
    if not os.path.isdir(Meta + user): # verificar se diretório Meta + user existe
        os.mkdir(Meta + user) # criar diretório Meta + user
        FILE_ATTRIBUTE_HIDDEN = 0x02 # atributo oculto
        ret = ctypes.windll.kernel32.SetFileAttributesW(Meta + user, FILE_ATTRIBUTE_HIDDEN) # atribuir oculto ao diretório Meta + user
    if not os.path.isdir(Files + user): # verificar se diretório Files + user existe
        os.mkdir(Files + user) # criar diretório Files + user
         
    fileAdr = Meta + user + "\\MetaSessao.json" # endereço do arquivo de metadados do usuário

    # verificar se arquivo meta do usuário existe
    if os.path.isfile(fileAdr): 
        attArquivoMetaUser(user) # atualizar registrando login no arquivo de metadados do usuário
    else:
        criaArquivoMetaUser(user)

def compartilharArquivo(user, nomeArquivo, userShare):
    """
    Função para compartilhar um arquivo com outro usuário
    """
    pathArquivo = Files + user + "\\" + nomeArquivo # endereço do arquivo 

    # verificar se arquivo existe no diretorio local do usuario, quer dizer arquivo ainda não foi compartilhado
    if os.path.isfile(pathArquivo): # se arquivo existe
        pathShareArquivo = Share  + nomeArquivo # endereço de compartilhamento do arquivo

        # verificar se já existe arquivo com este nome no diretório Share
        if os.path.isfile(pathShareArquivo):
            print("Já existe arquivo com este nome no diretório Share, renomeie o arquivo e tente novamente")
            return

        try: # mover arquivo para o diretório Share
            shutil.move(pathArquivo, pathShareArquivo)
        except Exception as e: # se não conseguir mover arquivo
            print("Erro ao mover arquivo para o diretório Share")
            print(e)
            return

        try: # atualizar o meta dos usuarios que compartilharam o arquivo
            attArquivoMetaUser(user, nomeArquivo, None) # atualizando meta do usuario que compartilhou o arquivo (owner)
            attArquivoMetaUser(userShare, None, nomeArquivo) # atualizando meta do usuario que recebeu o arquivo (compartilhado_comigo)
            
            # criar arquivo de metadados do arquivo compartilhado
            criaArquivoMetaShare(MetaShare + nomeArquivo + ".json", user, userShare, nomeArquivo)
            print("Arquivo compartilhado com sucesso")
            return True
        except Exception as e: # se não conseguir atualizar o arquivo de metadados
            print("Erro ao atualizar arquivo de metadados")
            print(e)
            return False    
    elif os.path.isfile(Share + nomeArquivo): # se arquivo existe no diretório Share, quer dizer que arquivo já foi compartilhado alguma vez
        attArquivoMetaUser(userShare, None, nomeArquivo) # atualizando meta do usuario que recebeu o arquivo (compartilhado_comigo)
        attArquivoMetaShare(MetaShare + nomeArquivo + ".json", user, userShare) # atualizando meta do arquivo compartilhado (compartilhado_com)
        print("Arquivo compartilhado com sucesso")
        return True
    else:
        print("Arquivo não encontrado")
        return False

def serializarArquivo(pathFile):
    try:
        with open(pathFile, "rb") as f:
            dadosArquivo = f.read()
            serializar = struct.Struct("{}s {}s".format(len(pathFile), len(dadosArquivo)))
            dadosUpload = serializar.pack(*[pathFile.encode(), dadosArquivo])
        
        return serializar, dadosUpload
    except FileNotFoundError:
        print("Arquivo não encontrado")
        return None

def salvarArquivo(user, pathFile, dataFile):
    """
    Função para salvar no servidor o arquivo recebido do cliente
    """ 
    nomeArquivo = pathFile.split("\\")[-1] # nome do arquivo
    nomeArquivo = Files + user + "\\" + nomeArquivo # endereço do arquivo

    try: # tentar salvar o arquivo
        try: 
            # receber o conteúdo do arquivo
            with open(nomeArquivo, 'wb') as f: 
                f.write(dataFile) 
                print("Arquivo salvo com sucesso") 
        except Exception as e : 
            print("Erro ao salvar o arquivo") 
            print(e) 
            return False 
        
        attArquivoMetaUser(user)  # atualizar o arquivo de metadados do usuário
        
        return True
    except:
        print("Erro ao salvar o arquivo") 
        return False

def excluirArquivo(user, nomeArquivo):
    nomeArquivo = Files + user + "\\" + nomeArquivo

    try:
        os.remove(nomeArquivo)
        print("Arquivo excluído com sucesso")
    except FileNotFoundError:
        print("Arquivo não encontrado")
        return False
    except Exception as e:
        print("Erro ao excluir o arquivo")
        print(e)
        return False

    # atualizar o arquivo de metadados
    fileAdr = Meta + user + "\\meta.json"
    with open(fileAdr, "r") as f:
        meta = json.load(f)

    meta['modificado_em'] = str(datetime.now())
    meta['arquivos'] = os.listdir(Files + user)

    with open(fileAdr, "w") as f:
        json.dump(meta, f, indent=4)
    
    return True

def renomearArquivo(user, nomeArquivo, novoNome):
    """
    Função para renomear um arquivo
    """
    nomeArquivo = Files + user + "\\" + nomeArquivo # endereço do arquivo
    novoNome = Files + user + "\\" + novoNome # endereço do novo nome do arquivo

    try:
        os.rename(nomeArquivo, novoNome) # renomear o arquivo
        print("Arquivo renomeado com sucesso") 
    except FileNotFoundError: # se o arquivo não for encontrado
        print("Arquivo não encontrado")
        return False
    except Exception as e:  # se ocorrer algum erro
        print("Erro ao renomear o arquivo")
        print(e)
        return False

    # atualizar o arquivo de metadados
    fileAdr = Meta + user + "\\meta.json" # endereço do arquivo de metadados do usuário
    with open(fileAdr, "r") as f:   # abrir arquivo fileAdr
        meta = json.load(f) # carregar metadados do arquivo fileAdr

    meta['modificado_em'] = str(datetime.now()) # atualizar data de modificação
    meta['arquivos'] = os.listdir(Files + user) # atualizar lista de arquivos

    with open(fileAdr, "w") as f: # abrir arquivo fileAdr
        json.dump(meta, f, indent=4) # salvar metadados no arquivo fileAdr
     
    return True

def listarArquivos(user):
    """
    Função responsável por listar os arquivos de um usuário
    """
    attArquivoMetaUser(user) # atualizar o arquivo de metadados do usuário

    pathFile = Meta + user + "\\MetaSessao.json" # endereço do arquivo de metadados do usuário que compartilhou o arquivo
    
    with open(pathFile, "r") as f: # abrir arquivo fileAdr
        meta = json.load(f) # carregar metadados do arquivo fileAdr

    if meta['meus_Arquivos_Locais'] == [] and meta['meus_Arquivos_Compartilhados'] == []: # se a lista de arquivos estiver vazia
        return "Nenhum arquivo encontrado" # retornar mensagem de erro
    elif meta['meus_Arquivos_Locais'] == [] and len(meta['meus_Arquivos_Compartilhados']) > 0: # se a lista de arquivos locais estiver vazia e compartilhados estiver arquivos
        return  "Lista de Arquivos Locais:\nNenhum arquivo encontrado" + "\nLista de Meus Arquivos Compartilhados:\n" + str(meta['meus_Arquivos_Compartilhados']) # retornar a lista de arquivos
    else:
        return  "Lista de Arquivos Locais:\n" + str(meta['meus_Arquivos_Locais']) + "\nLista de Meus Arquivos Compartilhados:\n" + str(meta['meus_Arquivos_Compartilhados']) # retornar a lista de arquivos

def carregausuarios():
    """
    Função para carregar os usuários do arquivo usuarios.txt
    """
    users = {} # dicionário para armazenar os usuários
    try:
        arquivo = open(usuarios,'r',encoding='utf8') # abrir o arquivo usuarios.txt
        for linha in arquivo: # para cada linha do arquivo
            senha = (linha.strip()).split(' ',1) # separar o usuário da senha
            users[senha[0]] = senha[1] # adicionar o usuário e a senha ao dicionário
        
    except IOError: # se o arquivo não existir
        arquivo = open(usuarios,'x',encoding='utf8') # criar o arquivo usuarios.txt
    arquivo.close() # fechar o arquivo
    return users

def verificarUsuario(user):
    """
    Função para verificar se um usuário existe
    """
    users = carregausuarios() # carregar os usuários do arquivo usuarios.txt
    if user in users.keys(): # se o usuário existir
        return True # retornar True
    else:
        return False # retornar False

def listausuarios():
    """
    Função para listar os usuário do arquivo usuarios.txt
    """
    lista = [] # lista para armazenar os usuários
    users = carregausuarios() # carregar os usuários do arquivo usuarios.txt
    for user in users: # para cada usuário no dicionário users
        lista.append(user[0])   # adicionar o usuário à lista
    return lista # retornar a lista de usuários

def insereusuario(usuario,senha, adm):
    """
    Função para inserir um usuário no arquivo usuarios.txt
    """
    if(superUser == adm): # se a senha do usuário administrador estiver correta
        try:
            arquivo = open(usuarios,'a',encoding='utf8') # abrir o arquivo usuarios.txt
            arquivo.write(usuario) # escrever o usuário no arquivo
            arquivo.write(" ")  # escrever um espaço no arquivo

            arquivo.write(Sha512Hash(senha)) # escrever a senha no arquivo em formato hash
            arquivo.write("\n") # escrever uma quebra de linha no arquivo
            arquivo.close() # fechar o arquivo
            return True
        except IOError: # se ocorrer algum erro
            print("Erro ao criar usuário!")
    else:  # se a senha do usuário administrador estiver incorreta
        print("Senha do usuário administrador incorreta!")
        return False

def verificasenha(user,senha):
    """
    Função para verificar a senha de um usuário
    """
    arquivo = open(usuarios,'r',encoding='utf8') # abrir o arquivo usuarios.txt
    for linha in arquivo: # para cada linha do arquivo
        linha = linha.strip() # remover espaços em branco
        usuario = linha.split(" ",1) # separar o usuário da senha
        if (usuario[0] == user): # se o usuário for igual ao usuário passado como parâmetro 
            h = Sha512Hash(senha).strip() # gerar o hash da senha passada como parâmetro
            if (h == usuario[1]): # se o hash da senha passada como parâmetro for igual ao hash da senha do usuário
                return True
            else:
                return False
            break
