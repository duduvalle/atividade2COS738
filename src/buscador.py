from nltk.tokenize import word_tokenize
from configparser import ConfigParser
import numpy as np
from scipy.spatial import distance
import logging
import time
import ast
import csv

logging.basicConfig(filename="log/buscador.log",format='%(asctime)s %(message)s',filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) #logger.error("Did you try to divide by zero")

logger.info("Leitura do arquivo de configuracao")
start = time.time()

config = ConfigParser()
config.read("config/BUSCA.CFG")
arquivoModelo = config["arquivos"]["MODELO"]
arquivoConsultas = config["arquivos"]["CONSULTAS"]
arquivoResultado = config["arquivos"]["RESULTADOS"]
i = 3

end = time.time()
logger.info("Fim da leitura do arquivo de configuracao")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)
logger.info("Leu %d instrucoes", i)

logger.info("Leitura do arquivo do modelo")
start = time.time()
matrixVetoresAux = []
termos = []
i = 0
with open(arquivoModelo) as csv_file1:
    csv_reader = csv.reader(csv_file1, delimiter=';')
    for row in csv_reader:
        i+=1
        termos.append(row[0])
        matrixVetoresAux.append(ast.literal_eval(row[1]))

matrixVetores = np.array(matrixVetoresAux)
matrixVetores = matrixVetores.T

end = time.time()
logger.info("Fim da leitura do arquivo do modelo")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)
logger.info("Leu %d palavras e seus vetores", i)

logger.info("Leitura do arquivo das consultas")
start = time.time()
i = 0
tamanhoVetor = len(matrixVetores[0])

dicionarioConsulta = {}
with open(arquivoConsultas) as csv_file2:
    csv_reader = csv.reader(csv_file2, delimiter=';')
    next(csv_reader)
    for row in csv_reader:
        i += 1
        dicionarioConsulta[int(row[0])] = word_tokenize(row[1])
        aux = np.zeros(len(matrixVetores[0]))
        for word in dicionarioConsulta[int(row[0])]:
            if word in termos:
                aux[termos.index(word)] = 1
        dicionarioConsulta[int(row[0])] = aux

end = time.time()
logger.info("Fim da leitura do arquivo das consultas")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)
logger.info("Leu %d consultas", i)

logger.info("Escrita do arquivo resultados.csv")
start = time.time()

data = []
for key in dicionarioConsulta:
    matrizResultado = []
    tuplasConsulta = []
    for i in range(len(matrixVetores)):
        distanceDocumento = distance.cosine(dicionarioConsulta[key], matrixVetores[i])
        if distanceDocumento > 0.9:
            matrizResultado.append([distanceDocumento,i])
    matrizResultado.sort()
    for i in range(len(matrizResultado)):
        auxTuple = (len(matrizResultado)-i,matrizResultado[i][1],matrizResultado[i][0])
        tuplasConsulta.append(auxTuple)
    daux = [key, tuplasConsulta]
    data.append(daux)

with open(arquivoResultado, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerows(data)

end = time.time()
logger.info("Fim da escrita do arquivo resultados.csv")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)