import re
import argparse
import requests
from selenium import webdriver

#criando argumentos a serem passados junto com a execução do código
parser = argparse.ArgumentParser(description='Coleta dados do OPGG para treinamento de modelo de Machine Learning afim de replicar o OPGGScore.')
parser.add_argument('-g', '--grandmaster', action='store_true', help='Seleciona os jogadores na liga Grão-Mestre.')
parser.add_argument('-m', '--master', action='store_true', help='Seleciona os jogadores na liga Mestre.')
parser.add_argument('-k', '--key', metavar='', required=True, help='Informa a key da API da Riot Games para a coleta dos jogadores.')

parser = parser.parse_args()

#inicialização de arquivos e variaveis
arq = open(file="databaseOPGG.csv", mode='w', encoding="utf-8")
cd = "C:/selenium_chromeDriver_teste/chromedriver"
param = "api_key=" + parser.key
nome_players = []

#fazendo request da api da Riot dos jogadores Challenger e/ou GM e/ou Mestre do server brasileiro
def getPlayersPerTier(tier):
	global param
	global nome_players

	request_game = requests.get("https://br1.api.riotgames.com/lol/league/v4/{}leagues/by-queue/RANKED_SOLO_5x5?{}".format(tier, param)).json()

	#para cada jogador do request -> coletar e tratar possiveis espaços dos nicknames deles
	for e in request_game["entries"]:
		nome_players.append(e["summonerName"].replace(" ", "+"))

#adicionando em "nome_players" jogadores dos Tiers passados por parametro
getPlayersPerTier("challenger")

if parser.grandmaster:
	getPlayersPerTier("grandmaster")

if parser.master:
	getPlayersPerTier("master")

print("Jogadores buscados, criando CSV.....")
num_player = 1

#para cada jogador coletar variaveis utilizadas para gerar a pontuação OPGGScore
for player in nome_players:
	print("Player {}  [{} de {}]".format(player, num_player, len(nome_players)+1))
	erro = 0

	#abrindo o Chrome com Selenium e coletando as variaveis desejadas
	driver = webdriver.Chrome(cd)
	driver.get("https://br.op.gg/summoner/userName={}".format(player))

	#script para que o Selenuim abra todas as abas de todos os jogos do player, apenas abrindo as abas que fica disponível os dados
	driver.execute_script("let bb = document.getElementsByClassName('Button MatchDetail'); for(let i = 0; i < bb.length; i++){bb[i].click();}")

	dados = []
	modo_partidas = []

	for e in driver.find_elements_by_class_name("GameType"):
		modo_partidas.append(e.text)

	for elem in driver.find_elements_by_class_name('GameDetail'): 
		dados += elem.text.split("\n")
		dados.append("end")

	
	driver.close()
	#fim da coleta pelo Chrome

	dados_por_partida = []
	aux = []

	for e in dados:
		if e == "end":
			dados_por_partida.append(aux)
			aux = []

		else:
			aux.append(e)

	#para cada partida coletada pelo jogador coletar os dados de todos os players da partida desse jogador
	for i in range(len(dados_por_partida)):
		#filtrando partidas indesejadas (i.e. partidas não-ranqueadas e partidas com remake)
		if modo_partidas[i] != "Ranqueada Solo":
			continue

		aux = 0
		for partida in dados_por_partida[i]:
			if "Derrota" not in partida.split() and "Vitória" not in partida.split():
				aux += 1

		if aux == len(dados_por_partida[i]):
			continue

		#fim do filtro de partidas indesejadas
		
		dados_por_partida[i] = dados_por_partida[i][8:]
		dic_de_variaveis = {}
		it = 0
		index = 0

		#passando pelos dados e pegando apenas o que é relevante para o treino do modelo
		while index < len(dados_por_partida[i]):
			dic_de_variaveis["opgg_score"] = float(dados_por_partida[i][index])
			index += 2
			
			#tratamento da variavel "kda" e das variaveis que envolvem-a (para evitar divisões por 0 e afins)
			try:
				dic_de_variaveis["kda"] = float(dados_por_partida[i][index].split(":")[0])
			except:
				erro = 1

			index += 1
			kda_list = re.split("/|\(|%", dados_por_partida[i][index])
			dic_de_variaveis["kills"] = int(kda_list[0])
			dic_de_variaveis["deaths"] = int(kda_list[1])
			if dic_de_variaveis["deaths"] == 0:
				dic_de_variaveis["deaths"] = 1

			dic_de_variaveis["assists"] = int(kda_list[2])
			if erro == 1:
				dic_de_variaveis["kda"] = dic_de_variaveis["kills"] + dic_de_variaveis["assists"]

			#fim do tratamento da variavel "kda"

			dic_de_variaveis["kill_participation"] = int(kda_list[3])
			index += 1
			dic_de_variaveis["Dmg_per_death"] = int(dados_por_partida[i][index].replace(",",""))/dic_de_variaveis["deaths"]
			index += 2
			dic_de_variaveis["vision"] = sum(list(map(int, dados_por_partida[i][index].split(" / "))))
			index += 1
			dic_de_variaveis["CS"] = int(dados_por_partida[i][index])
			index += 1
			dic_de_variaveis["CS_per_min"] = float(dados_por_partida[i][index].split(" /")[0])
			index += 4
			dic_de_variaveis["role"] = it%5
			it += 1

			#quando terminar os cinco players do "lado azul" entao pular nove posições para pegar os players do "lado vermelho"
			if it%5 == 0:
				index += 9

			#adicionando as variaveis no output final
			arq.write(str(dic_de_variaveis["opgg_score"])+","+str(dic_de_variaveis["kda"])+","+str(dic_de_variaveis["kill_participation"])+","+str(dic_de_variaveis["Dmg_per_death"])+",")
			arq.write(str(dic_de_variaveis["vision"])+","+str(dic_de_variaveis["CS_per_min"])+","+str(dic_de_variaveis["role"])+"\n")

	num_player += 1

arq.close()