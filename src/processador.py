from configparser import ConfigParser
import xml.dom.minidom
import unidecode
import logging
import time
import csv

logging.basicConfig(filename="log/processador.log",format='%(asctime)s %(message)s',filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) #logger.error("Did you try to divide by zero")
 
def somaScore(str):
    total = 0
    for x in str:
        if x.isdigit() == True:
            z = int(x)
            total = total + z
    return total

logger.info("Leitura do arquivo de configuracao")
start = time.time()

config = ConfigParser()
config.read("config/PC.CFG")
arquivoLeitura = config["arquivos"]["LEIA"]
arquivoConsultas = config["arquivos"]["CONSULTAS"]
arquivoEsperados = config["arquivos"]["ESPERADOS"]
i = 3

end = time.time()
logger.info("Fim da leitura do arquivo de configuracao")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)
logger.info("Leu %d instrucoes", i)

logger.info("Leitura do arquivo LEIA")
start = time.time()
i = 0

domtree = xml.dom.minidom.parse(arquivoLeitura)
file = domtree.documentElement
consultas = file.getElementsByTagName("QUERY")
data1 = []
data2 = []
textoConsulta = ""
for consulta in consultas:
    i += 1
    data = []
    numeroConsulta = consulta.getElementsByTagName("QueryNumber")[0].childNodes[0].nodeValue
    textoConsulta = consulta.getElementsByTagName("QueryText")[0].childNodes[0].nodeValue
    textoConsulta = unidecode.unidecode(textoConsulta)
    textoConsulta = textoConsulta.upper()
    data = [numeroConsulta, textoConsulta]
    data1.append(data)
    items = consulta.getElementsByTagName("Item")
    for item in items:
        data = []
        numeroDocumento = item.childNodes[0].nodeValue
        data = [numeroConsulta, numeroDocumento, somaScore(item.getAttribute("score"))]
        data2.append(data)

end = time.time()
logger.info("Fim da leitura do arquivo LEIA")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)
logger.info("Leu %d consultas", i)

logger.info("Escrita dos arquivos CONSULTAS e ESPERADOS")
start = time.time()

header1 = ["NumeroConsulta","TextoConsulta"]
with open(arquivoConsultas, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(header1)
    writer.writerows(data1)

header2 = ["NumeroConsulta","NumeroDocumento","VotosDocumento"]
with open(arquivoEsperados, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(header2)
    writer.writerows(data2)

end = time.time()
logger.info("Fim escrita dos arquivos CONSULTAS e ESPERADOS")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)