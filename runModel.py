import argparse
import numpy as np
import pandas as pd
from joblib import load

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

#criando argumentos a serem passados junto com a execução do código
parser = argparse.ArgumentParser(description='Executa o modelo gerado do notebook criaModelo.')
parser.add_argument('-i', '--input', metavar='', required=True, help='Informa o nome do CSV com os dados da partida fechada.')
parser = parser.parse_args()

#função para normalizar os dados
def normaliza(arq, transformer):
	arq["dmg_per_death"] = arq["dmg_per_death"].apply(round, ndigits=1)
	x_teste_normal = transformer.transform(arq)

	return x_teste_normal

#inicializando os arquivos
arq = pd.read_csv(parser.input)
model = load('filename.joblib')
Transformer = load('transformer.pkl')

#predição das notas
notas = model.predict(normaliza(arq.drop('nome', axis=1), Transformer))

#associação das notas com os players
players = tuple(zip(np.array(arq["nome"]), notas))
ps = sorted(players, key=lambda x : x[1], reverse=True)
print(ps)

for e in players:
	print("{} -- {}".format(e[0], ps.index(e)+1))