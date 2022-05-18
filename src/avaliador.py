import numpy as np
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
import logging
import time
import ast
import csv
import math

logging.basicConfig(filename="log/avaliador.log",format='%(asctime)s %(message)s',filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) 

logger.info("Leitura dos arquivos resultados esperados, com STEMMER e sem")
start = time.time()

numeroDocumentos = 1239
numeroConsulta = 0
listaResultadoEsperado = []
listaRelevancia = []
listaAuxiliar = []
listaAuxiliar2 = []
arquivoLeitura = "result/esperados.cvs"
with open(arquivoLeitura) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    next(csv_reader)
    for row in csv_reader:
        numeroConsultaAtual = int(row[0])
        if(numeroConsulta != numeroConsultaAtual):
            if(numeroConsulta!=0):
                listaResultadoEsperado.append(listaAuxiliar)
                listaRelevancia.append(listaAuxiliar2)
            listaAuxiliar = []
            listaAuxiliar2 = []
            numeroConsulta = numeroConsultaAtual    
        listaAuxiliar.append(int(row[1]))
        listaAuxiliar2.append(int(row[2]))
listaResultadoEsperado.append(listaAuxiliar)
listaRelevancia.append(listaAuxiliar2)

listaResultadoStemmer = []
arquivoLeitura = "result/resultados-STEMMER.cvs"
with open(arquivoLeitura) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    for row in csv_reader:
        listaAuxiliar = []
        linha = ast.literal_eval(row[1])
        for documento in linha:
            listaAuxiliar.append(documento[1])
        listaResultadoStemmer.append(listaAuxiliar)

listaResultadoNostemmer = []
arquivoLeitura = "result/resultados-NOSTEMMER.cvs"
with open(arquivoLeitura) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    for row in csv_reader:
        listaAuxiliar = []
        linha = ast.literal_eval(row[1])
        for documento in linha:
            listaAuxiliar.append(documento[1])
        listaResultadoNostemmer.append(listaAuxiliar)

end = time.time()
logger.info("Fim da leitura dos arquivos resultados esperados, com STEMMER e sem")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)

logger.info("Calculos das medidas de avaliacao")
start = time.time()

numeroTotalConsultas = len(listaResultadoEsperado)

totalPrecision5 = 0
totalPrecision10 = 0
totalF1 = 0
totalAP = 0
totalRR = 0
totalDCG = np.zeros(10)
totalNDCG = np.zeros(10)
RPStemmer = np.zeros(numeroTotalConsultas)
totalpontos11 = np.zeros(11)

NototalPrecision5 = 0
NototalPrecision10 = 0
NototalF1 = 0
NototalAP = 0
NototalRR = 0
NototalDCG = np.zeros(10)
NototalNDCG = np.zeros(10)
RPNostemmer = np.zeros(numeroTotalConsultas)
Nototalpontos11 = np.zeros(11)

for i in range(numeroTotalConsultas):

    numeroEsperado = len(listaResultadoEsperado[i])
    
    DCG_ideal = np.zeros(10)
    listaAuxRelevancia = sorted(listaRelevancia[i], reverse=True)
    auxCont = 0
    for relevancia in listaAuxRelevancia:
        if auxCont == 10:
            break
        if auxCont == 0:
            DCG_ideal[auxCont] = relevancia
        else:
            DCG_ideal[auxCont] = DCG_ideal[auxCont-1] + relevancia/math.log2(auxCont+1)
        auxCont +=1
    
    if auxCont < 10:
        for k in range(auxCont,10,1):
            DCG_ideal[k] = DCG_ideal[k-1]


    numeroEncontrados = len(listaResultadoStemmer[i])
    tp = 0
    auxContCerto = 0
    AP_consulta = 0
    DCG_auxiliar = np.zeros(10)
    pontos11_auxiliar = np.zeros(11)
    pontos11_auxiliar[0] = 1
    nivelRecall = 0.1
    
    for j in range( numeroEncontrados - 1, -1, -1) :

        if listaResultadoStemmer[i][j] in listaResultadoEsperado[i]:
            tp+=1
            auxContCerto +=1
            pre_aux = tp/(numeroEncontrados - j)
            AP_consulta += pre_aux
            
            rec_aux = tp/numeroEsperado
            if(rec_aux >= nivelRecall):
                indice = int(nivelRecall*10)
                pontos11_auxiliar[indice] = pre_aux
                nivelRecall+=0.1

            if numeroEncontrados - j <= 10:
                Relevancia = listaRelevancia[i][listaResultadoEsperado[i].index(listaResultadoStemmer[i][j])]
                if numeroEncontrados - j == 1:
                    DCG_auxiliar[0] = Relevancia
                else:
                    DCG_auxiliar[numeroEncontrados - j-1] = DCG_auxiliar[numeroEncontrados - j-2] + Relevancia/(math.log2(numeroEncontrados - j))

                if auxContCerto == 1:
                    totalRR += 1/(numeroEncontrados - j)
        else:
            if numeroEncontrados - j <= 10:
                if numeroEncontrados - j-1 != 0:
                    DCG_auxiliar[numeroEncontrados - j-1] = DCG_auxiliar[numeroEncontrados - j-2]


        if numeroEncontrados - j == numeroEsperado:
            RPStemmer[i] = tp/numeroEsperado
        if numeroEncontrados - j == 5:
            totalPrecision5 += tp/5
        if numeroEncontrados - j == 10: 
            totalPrecision10 += tp/10

    for x in range(11):
        pontos11_auxiliar[x] = np.max(pontos11_auxiliar[x:])

    precision = tp/numeroEncontrados
    recall = tp/numeroEsperado
    totalF1 += 2*(precision*recall)/(precision+recall)
    totalAP += AP_consulta/tp
    totalDCG = np.add(totalDCG, DCG_auxiliar)
    totalNDCG = np.add(totalNDCG, np.divide(DCG_auxiliar, DCG_ideal))
    totalpontos11 = np.add(totalpontos11, pontos11_auxiliar)

    numeroEncontrados = len(listaResultadoNostemmer[i])
    tp = 0
    auxContCerto = 0
    AP_consulta = 0
    DCG_auxiliar = np.zeros(10)
    pontos11_auxiliar = np.zeros(11)
    pontos11_auxiliar[0] = 1
    nivelRecall = 0.1

    for j in range( len(listaResultadoNostemmer[i]) - 1, -1, -1) :

        if listaResultadoNostemmer[i][j] in listaResultadoEsperado[i]:
            tp+=1
            auxContCerto +=1
            pre_aux = tp/(numeroEncontrados - j)
            AP_consulta += pre_aux
            
            rec_aux = tp/numeroEsperado
            if(rec_aux >= nivelRecall):
                indice = int(nivelRecall*10)
                pontos11_auxiliar[indice] = pre_aux
                nivelRecall+=0.1
            
            if numeroEncontrados - j <= 10:
                Relevancia = listaRelevancia[i][listaResultadoEsperado[i].index(listaResultadoNostemmer[i][j])]
                if numeroEncontrados - j == 1:
                    DCG_auxiliar[0] = Relevancia
                else:
                    DCG_auxiliar[numeroEncontrados - j-1] = DCG_auxiliar[numeroEncontrados - j-2] + Relevancia/math.log2(numeroEncontrados - j)
                if auxContCerto == 1:
                    NototalRR += 1/(numeroEncontrados - j)
        else:
            if numeroEncontrados - j <= 10:
                if numeroEncontrados - j-1 != 0:
                    DCG_auxiliar[numeroEncontrados - j-1] = DCG_auxiliar[numeroEncontrados - j-2]


        if numeroEncontrados - j == numeroEsperado:
            RPNostemmer[i] = tp/numeroEsperado
        if numeroEncontrados - j == 5:
            NototalPrecision5 += tp/5
        if numeroEncontrados - j == 10: 
            NototalPrecision10 += tp/10

    for x in range(11):
        pontos11_auxiliar[x] = np.max(pontos11_auxiliar[x:])

    precision = tp/numeroEncontrados
    recall = tp/numeroEsperado
    NototalF1 += 2*(precision*recall)/(precision+recall)
    NototalAP += AP_consulta/tp
    NototalDCG = np.add(NototalDCG, DCG_auxiliar)
    NototalNDCG = np.add(NototalNDCG, np.divide(DCG_auxiliar, DCG_ideal))
    Nototalpontos11 = np.add(Nototalpontos11, pontos11_auxiliar)

#print(NototalF1/numeroTotalConsultas)
#print(NototalAP/numeroTotalConsultas)
#print(NototalPrecision5/numeroTotalConsultas)
#print(NototalPrecision10/numeroTotalConsultas)
#print(NototalRR/numeroTotalConsultas)

#print(totalF1/numeroTotalConsultas)
#print(totalAP/numeroTotalConsultas)
#print(totalPrecision5/numeroTotalConsultas)
#print(totalPrecision10/numeroTotalConsultas)
#print(totalRR/numeroTotalConsultas)
x11 = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
x10 = [0,1,2,3,4,5,6,7,8,9]

linha1 = ["Usou Stemming",totalF1/numeroTotalConsultas,totalAP/numeroTotalConsultas,totalRR/numeroTotalConsultas,totalPrecision5/numeroTotalConsultas,totalPrecision10/numeroTotalConsultas]
linha2 = ["Nao usou Stemming",NototalF1/numeroTotalConsultas,NototalAP/numeroTotalConsultas,NototalRR/numeroTotalConsultas,NototalPrecision5/numeroTotalConsultas,NototalPrecision10/numeroTotalConsultas]
data = []
data.append(linha1)
data.append(linha2)
header = ["Se o algoritmo usou stemming","F1","MAP","MRR","Precision5","Precision10"]
with open("avalia/resultadosUnitarios-1.csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(header)
    writer.writerows(data)

#print(NototalDCG/numeroTotalConsultas)
with open("avalia/DCG-nostemmer-2.csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(NototalDCG/numeroTotalConsultas)


plt.plot(x10,NototalDCG/numeroTotalConsultas)
plt.xlabel('Ranking documento(ate 10)')
plt.ylabel('DCG')
plt.title('DCG-nostemmer')
plt.savefig("avalia/DCG-nostemmer-3.pdf")
plt.clf()

#print(NototalNDCG/numeroTotalConsultas)
with open("avalia/NDCG-nostemmer-4.csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(NototalNDCG/numeroTotalConsultas)

plt.plot(x10,NototalNDCG/numeroTotalConsultas)
plt.xlabel('Ranking documento(ate 10)')
plt.ylabel('NDCG')
plt.title('NDCG-nostemmer')
plt.savefig("avalia/NDCG-nostemmer-5.pdf")
plt.clf()

#print(Nototalpontos11/numeroTotalConsultas)
with open("avalia/11pontos-nostemmer-6.csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(Nototalpontos11/numeroTotalConsultas)

plt.plot(x11,Nototalpontos11/numeroTotalConsultas)
plt.xlabel('Nivel de recall')
plt.ylabel('Precision')
plt.title('11pontos-nostemmer')
plt.savefig("avalia/11pontos-nostemmer-7.pdf")
plt.clf()

#print(totalDCG/numeroTotalConsultas)
with open("avalia/DCG-stemmer-8.csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(totalDCG/numeroTotalConsultas)

plt.plot(x10,totalDCG/numeroTotalConsultas)
plt.xlabel('Ranking documento(ate 10)')
plt.ylabel('DCG')
plt.title('DCG-stemmer')
plt.savefig("avalia/DCG-stemmer-9.pdf")
plt.clf()

#print(totalNDCG/numeroTotalConsultas)
with open("avalia/NDCG-stemmer-10.csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(totalNDCG/numeroTotalConsultas)

plt.plot(x10,totalNDCG/numeroTotalConsultas)
plt.xlabel('Ranking documento(ate 10)')
plt.ylabel('NDCG')
plt.title('NDCG-stemmer')
plt.savefig("avalia/NDCG-stemmer-11.pdf")
plt.clf()

#print(totalpontos11/numeroTotalConsultas)
with open("avalia/11pontos-stemmer-12.csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(totalpontos11/numeroTotalConsultas)

plt.plot(x11,totalpontos11/numeroTotalConsultas)
plt.xlabel('Nivel de recall')
plt.ylabel('Precision')
plt.title('11pontos-stemmer')
plt.savefig("avalia/11pontos-stemmer-13.pdf")
plt.clf()

#print(np.subtract(RPStemmer,RPNostemmer))
histograma = np.subtract(RPStemmer,RPNostemmer)
with open("avalia/histograma-R-precision-14.csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(histograma)

x9 = [1,2,3,4,5,6,7,8,9]

pdf = matplotlib.backends.backend_pdf.PdfPages("avalia/histograma-R-precision-15.pdf")
for x in range (11):
    fig = plt.figure(x, clear = True)
    plt.scatter(x9,histograma[(x)*9:(x+1)*9])
    plt.xlabel('Consultas')
    plt.ylabel('Diferença R-Precision')
    plt.title('Histograma-R-precision '+ str(x+1) + ' grupo de consultas' )
    pdf.savefig( fig )
pdf.close()

end = time.time()
logger.info("Fim dos calculos das medidas de avaliacao")
logger.info("Executou o procedimento anterior em: %f segundos", end-start)