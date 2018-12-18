#importando funcoes de data e hora do python
import time
import datetime
import random

#importando a biblioteca GPIO para controle do sensor
import RPi.GPIO as GPIO

#importacao das bibliotecas IOTA 
from iota import Iota
from iota import Address

import MySQLdb

#Conexao com o Banco de dados
con = MySQLdb.connect(host="192.168.5.108", user="root", passwd="5598", db="iotaDB")
con.select_db('iotaDB')

cursor = con.cursor()

#selecionando o pino da GPIO q iremos utilizar
#PIN=4
#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
#GPIO.setup(PIN,GPIO.OUT)
#GPIO.output(PIN,GPIO.LOW)


# Utilizando o Node de teste IOTA
iotaNode = "https://nodes.devnet.thetangle.org:443"
# SEED do RASPBERRY
seed = b'99K9RSPHUTWOSZCTFJYDFXAHCECWRYRIRFOAYAPKHXSDIDVUVPLDVVLVFJVYKFFEVBOXACQTMLFHZINBW'


#criando o Objeto da API IOTA
api = Iota(iotaNode, seed)

print('IOTA PAY ESTACIONAMENTO')
print('\n \n \n Iniciando o Servico de processamento de pagamentos IOTA')

def buscaHash():
    select = "SELECT hash FROM transacoes ORDER BY id DESC LIMIT 1";

    cursor.execute(select)
    bdHash = cursor.fetchone()
    con.commit()
    
    return str(bdHash[0])



def gerarEndereco(api):

    #Gera um numero RANDOM entre 1 e 99999, q sera autilizado na hora da geracao do enderesso, onde indica um numero de indice para geracao do endereco IOTA
    n = random.randint (1,99999)
    print('\n \n Gerando endereco valido para recepcao de pagmentos')
    #Realiza a geracao das informacoes do endereco
    generate = api.get_new_addresses(security_level=2, index=n)
    address = generate['addresses']

    print("\n Endereco Gerado")
    print(address)

    print("\n Submetendo endereco ao Banco de Dados")
    #Armazena o endereco no banco de dados do sistema
    sql = "UPDATE raspberry SET endereco = '"+str(address[0])+"' WHERE id = 1;"

    cursor.execute(sql)

    con.commit()
    
    return address



def processaTransacao():
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(4,GPIO.OUT)
    print ("\n Realizando o Acionamento da GPIO, e abrindo o portao")
    GPIO.output(4,GPIO.HIGH)
    time.sleep(1)
    print ("\n\n Liberando o Pino GPIO")
    GPIO.output(4,GPIO.LOW)
    GPIO.cleanup()
    

def hashPagamento(api, endereco, aux):
    return str(api.find_transactions(addresses=endereco)['hashes'][aux])
    
    
endereco = gerarEndereco(api)    
    
# variaveis para controle dos pagamentos recebidos    
n = len(api.find_transactions(addresses=endereco)['hashes'])
new = 0


print("\n Iniciando o processamento de novos pagamentos")

while True:
    testeHash = False
    aux = 0
    
    print('\n\n Procurando Transacoes')
    print(api.find_transactions(addresses=endereco))

    
    if new > n :
        
        bdHash = buscaHash()
        
        while testeHash == False:
            
            if bdHash == hashPagamento(api, endereco, aux):
                print("\n\n\n Processando novo pagamento \n Hash do pagamento \n\n")
                print(hashPagamento(api,endereco, aux))
                processaTransacao()
                
                testeHash = True
        
            else:
                aux += 1
    
        n = new
        
        print ('\n\n\n\nTransacao processada com sucesso')
        time.sleep(5)    

    new = len(api.find_transactions(addresses=endereco)['hashes'])




