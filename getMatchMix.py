import json
import argparse

#criando argumentos a serem passados junto com a execução do código
parser = argparse.ArgumentParser(description='Seleciona as informações necessarias de uma partida desejada afim de serem utilizadas no modelo treinado.')
parser.add_argument('-i', '--input', metavar='', required=True, help='Informa o nome do JSON com os dados da partida fechada disponibilizados pela API da Riot Games.')
parser.add_argument('-o', '--output', metavar='', required=True, help='Informa o nome do arquivo final a ser escrito as informações.')
parser = parser.parse_args()

#função para somar dados (pois algumas variaveis são a media de dados)
def somaDado(path, dado):
	resp = 0
	for i in range(5):
		aux = path[i]
		for f in dado:
			aux = aux[f]
		resp = resp + aux

	return resp

request_game = json.load(open(parser.input, 'r'))
arq = open(parser.output, 'w')

#para cada jogador da partida recolher as variaveis necessarias
for k in range(10):
	#name = request_game["participantIdentities"][k]["name"]
	name = request_game["participantIdentities"][k]["player"]["summonerName"]

	root_path = request_game["participants"][k]["stats"]

	if root_path["deaths"] == 0:
		root_path["deaths"] = 1

	#kda
	kda = (root_path["kills"] + root_path["assists"])/root_path["deaths"]

	#kill_participation
	kill_participation = (root_path["kills"] + root_path["assists"])/somaDado(request_game["participants"], ["stats", "kills"])		

	#damage_per_death
	damage_per_death = root_path["totalDamageDealtToChampions"]/root_path["deaths"]

	root_path = request_game["participants"][k]["timeline"]

	#vision_score_per_hour
	vision_score_per_hour = request_game["participants"][k]["stats"]["visionScore"]

	#cs_per_minute
	cs_per_minute = (request_game["participants"][k]["stats"]["totalMinionsKilled"] + request_game["participants"][k]["stats"]["neutralMinionsKilled"])/(request_game["gameDuration"]/60)

	#name,kda,kill_participation,dmg_per_death,vision,CS_per_min,role
	arq.write("{},{},{},{},{},{}\n".format(name,kda,kill_participation,damage_per_death,vision_score_per_hour,cs_per_minute))

arq.close()