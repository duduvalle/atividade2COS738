# Atividade 3 de COS738
Eduardo Vieira Marques Pereira do Valle
evalle@cos.ufrj.br 09/05/2022

## Bibliotecas de python utilizadas:

- word_tokenize de nltk.tokenize
- RawConfigParser de configparser
- ConfigParser de configparser
- OrderedDict de collections 
- matplotlib.pyplot 
- matplotlib.backends.backend_pdf
- distance de scipy.spatial
- xml.dom.minidom
- numpy
- unidecode
- logging
- math
- time
- ast
- csv

## Execução

O código foi implementado seguindo as instruções estabelecidas em InstrucoesAtividade4.pdf. Para executar a atividade basta rodar os arquivos a seguir na ordem que são apresentados: processador.py, geradorLista-indexador.py, buscador.py e avaliador.py.

Para selecionar Stemming de Porter ou remove-lo, basta trocar o valor de USASTEMMER para STEMMER e NOSTEMMER respectivamente nos arquivos BUSCA.CFG e GLI.CFG.

Para diminuir a quantidade de resultados da busca, são separados apenas os documentos que tiveram o cosseno entre seu vetor e o vetor da consulta maiores que 0,9.

