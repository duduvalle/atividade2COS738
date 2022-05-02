from configparser import RawConfigParser
from configparser import ConfigParser
from collections import OrderedDict
from nltk.tokenize import word_tokenize
import xml.dom.minidom
import unidecode
import logging
import time
import csv
import ast
import math
 
logging.basicConfig(filename="log/geradorLista-indexador.log",format='%(asctime)s %(message)s',filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.info("Leitura do arquivo de configuracao")
start = time.time()

class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
           self[key].extend(value)
        else:
            super(OrderedDict, self).__setitem__(key, value)

config = RawConfigParser(dict_type=MultiOrderedDict, strict=False)
config.read("config/GLI.CFG")
arquivosLeitura = config["arquivos"]["LEIA"]
arquivoListas = config["arquivos"]["ESCREVA"]
i = 7

end = time.time()
logger.info("Fim da leitura do arquivo de configuracao")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)
logger.info("Leu %d instrucoes", i)

logger.info("Leitura dos arquivos LEIA e criacao das listas invertidas")
start = time.time()

dicionarioListaInvertida = {}
palavrasDocumento = []
i=0
for arquivoLeitura in arquivosLeitura:
    domtree = xml.dom.minidom.parse(arquivoLeitura)
    file = domtree.documentElement
    artigos = file.getElementsByTagName("RECORD")
    i+=len(artigos)
    for artigo in artigos:
        numeroDocumento = artigo.getElementsByTagName("RECORDNUM")[0].childNodes[0].nodeValue
        texto = ""
        if(len(artigo.getElementsByTagName("ABSTRACT"))!=0):
            texto = artigo.getElementsByTagName("ABSTRACT")[0].childNodes[0].nodeValue
        else: 
            if(len(artigo.getElementsByTagName("EXTRACT"))!=0):
                texto = artigo.getElementsByTagName("EXTRACT")[0].childNodes[0].nodeValue
            else:
                texto = artigo.getElementsByTagName("TITLE")[0].childNodes[0].nodeValue
        texto = unidecode.unidecode(texto)
        texto = texto.upper()
        words = word_tokenize(texto)
        palavrasDocumento.append(len(words))
        for word in words: 
            if word in dicionarioListaInvertida:
                dicionarioListaInvertida[word].append(numeroDocumento)
            else:
                dicionarioListaInvertida[word] = [numeroDocumento]

totalDocumentos = i
end = time.time()
logger.info("Fim da leitura dos arquivos LEIA e criacao das listas invertidas")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)
logger.info("Leu %d artigos", i)

logger.info("Escrita do arquivo ESCREVA")
start = time.time()

data = []
for chave in dicionarioListaInvertida:
    daux = [chave, dicionarioListaInvertida[chave]]
    data.append(daux)

with open(arquivoListas[0], 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerows(data)

end = time.time()
logger.info("Fim escrita do arquivo ESCREVA")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)

#-------------------------------------Indexador----------------------------------------------------

logger.info("INICIA INDEXADOR")
logger.info("Leitura do arquivo de configuracao")
start = time.time()

config = ConfigParser()
config.read("config/INDEX.CFG")
arquivoLeitura = config["arquivos"]["LEIA"]
arquivoModelo = config["arquivos"]["ESCREVA"]
i = 2

end = time.time()
logger.info("Fim da leitura do arquivo de configuracao")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)
logger.info("Leu %d instrucoes", i)

logger.info("Leitura do arquivo LEIA")
start = time.time()
line_count = 0
palavrasSelecionadas = 0
dicionarioListas = {}
with open(arquivoLeitura) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    for row in csv_reader:
        line_count += 1
        if(row[0].isalpha() and len(row[0]) > 2):
            dicionarioListas[row[0]] = ast.literal_eval(row[1])
            palavrasSelecionadas +=1

end = time.time()
logger.info("Leitura do arquivo LEIA")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)
logger.info("Leu %d palavras", line_count)
logger.info("Mas apenas %d palavras foram selecionadas", palavrasSelecionadas)

logger.info("Criacao da estrutura do modelo")
start = time.time()

dicionarioModelo = {}

for key in dicionarioListas:
    numeroDocumentosDistintos = 0
    aux = [0] * totalDocumentos
    elementosUnicos = []
    dicionarioModelo[key] = aux
    for presenca in dicionarioListas[key]:
        dicionarioModelo[key][int(presenca)-1] += 1
        if presenca not in elementosUnicos:
            numeroDocumentosDistintos +=1
            elementosUnicos.append(presenca)

    for peso in elementosUnicos:
        dicionarioModelo[key][int(peso)-1] = (dicionarioModelo[key][int(peso)-1]/palavrasDocumento[int(peso)-1])*math.log(totalDocumentos/len(elementosUnicos))

end = time.time()
logger.info("Fim da criacao da estrutura do modelo")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)

logger.info("Escrita do arquivo MODELO")
start = time.time()

data = []
for chave in dicionarioModelo:
    daux = [chave, dicionarioModelo[chave]]
    data.append(daux)

with open(arquivoModelo, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerows(data)

end = time.time()
logger.info("Fim da Escrita do arquivo MODELO")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)