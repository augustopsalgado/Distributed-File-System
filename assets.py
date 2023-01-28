from datetime import datetime
import hashlib
import ctypes
import json
import os


Files = "C:\\Files\\"
Control = "C:\\Control\\"
Meta = "C:\\Meta\\"
usuarios = "C:\\Control\\users.txt"
# admin123
superUser = "7fcf4ba391c48784edde599889d6e3f1e47a27db36ecc050cc92f259bfac38afad2c68a1ae804d77075e8fb722503f3eca2b2c1006ee6f6c7b7628cb45fffd1d"

def Sha512Hash(Password):
    HashedPassword=hashlib.sha512(Password.encode('utf-8')).hexdigest()
    return(HashedPassword)

def cls():
    os.system('cls' if os.name=='nt' else 'clear')


def inicializa():
    if not os.path.isdir(Files):
        os.mkdir("C:\\Files")
    if not os.path.isdir(Control):
        os.mkdir('C:\\Control')
    if not os.path.isdir(Meta):
        os.mkdir('C:\\Meta')
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ret = ctypes.windll.kernel32.SetFileAttributesW(Meta, FILE_ATTRIBUTE_HIDDEN)
        ret = ctypes.windll.kernel32.SetFileAttributesW(Control, FILE_ATTRIBUTE_HIDDEN)

def imprimemenu():
    print("\n\n------------------------------------------\n\n")
    print("Opções do sistema: \n")
    print("0 - Exibir arquivos\n")
    print("1 - Abrir um arquivo\n")
    print("2 - Fechar um arquivo\n")
    print("3 - Excluir um arquivo\n")
    print("4 - Renomear um arquivo\n")
    print("5 - Adicionar ou atualizar arquivo\n")
    print("6 - Dar permissão de acesso do arquivo a outro usuário\n")
    print("7 - Retirar permissão de acesso de outro usuário\n")
    print("8 - Mostrar histórico de acessos de um arquivo\n")
    print("9 - Mostrar lista de usuários com permissão de acesso\n")
    print("10 - Mostrar lista de modificações de um arquivo\n")
    print("11 - Sair\n")

def configSessao(user):
    """
    Função responsável por criar a pasta do usuário no diretório Meta
    E por criar o arquivo de metadados do usuário
    """
    if not os.path.isdir(Meta + user):
        os.mkdir(Meta + user)
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ret = ctypes.windll.kernel32.SetFileAttributesW(Meta + user, FILE_ATTRIBUTE_HIDDEN)
    if not os.path.isdir(Files + user):
        os.mkdir(Files + user)
        
    fileAdr = Meta + user + "\\meta.json"

    # verificar se arquivo fileAdr existe
    if os.path.isfile(fileAdr):
        with open(fileAdr, "r") as f:
            meta = json.load(f)

        meta['modificado_em'] = str(datetime.now())
        meta['arquivos'] = os.listdir(Files + user)

        with open(fileAdr, "w") as f:
            json.dump(meta, f, indent=4)
    else:
        # criando dict de metadados
        meta = {}
        meta['usuario'] = user
        meta['criado_em'] = str(datetime.now())
        meta['modificado_em'] = str(datetime.now())
        arquivos = os.listdir(Files + user)
        if arquivos == None:
            meta['arquivos'] = []
        else:
            meta['arquivos'] = arquivos

        with open(fileAdr, "w+") as f:
            json.dump(meta, f, indent=4)

def listarArquivos(user):
    """
    Função responsável por listar os arquivos de um usuário
    """
    fileAdr = Meta + user + "\\meta.json"
    with open(fileAdr, "r") as f:
        meta = json.load(f)

    if meta['arquivos'] == []:
        return "Nenhum arquivo encontrado"
    else:
        return str(meta['arquivos'])
    

def carregausuarios():
    users = {}
    try:
        arquivo = open(usuarios,'r',encoding='utf8')
        for linha in arquivo:
            senha = (linha.strip()).split(' ',1)
            users[senha[0]] = senha[1]
        
    except IOError:
        arquivo = open(usuarios,'x',encoding='utf8')
    arquivo.close()
    return users

def listausuarios():
    lista = []
    users = carregausuarios()
    for user in users:
        lista.append(user[0])
    return lista

def verificausuario(user):
    users = carregausuarios()
    if user in users.keys():
        return True
    else:
        return False

def insereusuario(usuario,senha, adm):
    if(superUser == adm):
        try:
            arquivo = open(usuarios,'a',encoding='utf8')
            arquivo.write(usuario)
            arquivo.write(" ")

            arquivo.write(Sha512Hash(senha))
            arquivo.write("\n")
            arquivo.close()
            return True
        except IOError:
            print("Erro ao criar usuário!")
    else: 
        print("Senha do usuário administrador incorreta!")
        return False

def verificasenha(user,senha):
    arquivo = open(usuarios,'r',encoding='utf8')
    for linha in arquivo:
        linha = linha.strip()
        usuario = linha.split(" ",1)
        if (usuario[0] == user):
            h = Sha512Hash(senha).strip()
            if (h == usuario[1]):
                return True
            else:
                return False
            break
