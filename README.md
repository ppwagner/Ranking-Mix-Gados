# Ranking-Mix-Gados

Esse repositório em o objetivo de replicar o sistema de "OPGG Score" do site OPGG com o intuito de criar um sistema ranqueado com as partidas de modo torneio do jogo League of Legends dos jogadores de uma comunidade fechada, uma vez que o site não disponibiliza a nota dessas partidas pelo fato delas não serem criadas pelo gerenciador de partidas do jogo.

## Requisitos
1. Acesso a API da Riot Games
2. Python 3.8+ instalado
3. Dependências instaladas

* O primeiro requisito serve para adquirir as partidas fechadas que foram jogadas afim de usá-las no modelo treinado para a obtenção da nota. É um método prático e oficial de obter as informações.

* O segundo requisito basta baixar no site oficial do Python o interpretador.

* O terceito requisito pode ser resolvido com o PIP que vem com o interpretador python. Basta utilizar no prompt de comando o seguinte código: `pip install -r requirements.txt`.

## Arquivos
* `getDataOPGG.py`: Serve para gerar o dataset afim de treinar e válidar o modelo feito.
* `criaModelo.ipynb`: Com o output de `getDataOPGG.py` cria e treina um modelo afim de prever o OPGG Score de uma partida.
* `getMixMatch.py`: Gera um CSV com os dados necessários para a execução do modelo a partir de uma partida de modo torneio obtida da API da Riot Games gravada em um JSON.
* `runModel.py`: Com o output dos dois últimos scripts é possível utilizá-lo para exibir os resultados esperados.
