import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

df_corridas= pd.read_excel("data/Uber_Renan_Portfolio.xlsx", sheet_name="Corridas")
df_localidade = pd.read_excel("data/Uber_Renan_Portfolio.xlsx", sheet_name="Localidade")
df_valor = pd.read_excel("data/Uber_Renan_Portfolio.xlsx", sheet_name="Valor_Viagem")

#Merge das tabelas
df_merged = pd.merge(df_corridas,df_localidade, on="ID_viagem", how="left")
df_merged = pd.merge(df_merged, df_valor, on="ID_viagem", how="left")

#Removendo a coluna Data_x e renomeando a Data_y , que são iguais
df_merged = df_merged.drop(columns=["Data_x"])
df_merged = df_merged.rename(columns={"Data_y": "Data"})

#Padronizando
df_merged.columns = (df_merged.columns.str.strip().str.lower().str.replace(" ","_", regex=False))
df_merged.columns = (df_merged.columns.str.replace("â","a", regex=False).str.replace("ç","c", regex=False).str.replace("+","", regex=False).str.replace("ã","a", regex=False))
df_merged['data'] = pd.to_datetime(df_merged['data'], format='%d/%m/%y')
# vamos alterar as colunas municipio_embarque, bairro_embarque, municipio_desembarque e bairro_desembarque onde for 0 para 'cancelado'
df_merged[['municipio_embarque', 'bairro_embarque', 'municipio_desembarque', 'bairro_desembarque']] = df_merged[['municipio_embarque', 'bairro_embarque', 'municipio_desembarque', 'bairro_desembarque']].replace(0, 'cancelado')

#Análise Exploratória

#1 - Qual a distância total percorrida por dia ?
distancia_por_dia = df_merged.groupby("data")["distancia(km)"].sum()

#2 - Qual é o tempo total gasto em corridas por dia ?
tempo_por_dia = df_merged.groupby("data")["duracao_min"].sum()

#3 - Quantas corridas foram feitas por dia ? 
corridas_por_dia = df_merged.groupby("data")["id_viagem"].count()

#4 - Quantas corridas com Turbo+ ?
corridas_turbo = df_merged.groupby("data")["turbo"].agg(lambda x:(x != 0).sum())

#5 Quantas corridas com Dinamico:
corridas_dinamico = df_merged.groupby("data")["preco_dinamico"].agg(lambda x:(x != 0).sum())

#6 - Qual é o valor total arrecadado por dia ?
df_merged["valor_total_dia"] = df_merged["preco_dinamico"] + df_merged["turbo"] + df_merged["pg_motorista"] + np.where(df_merged["dsc_uber"] > 0, df_merged["dsc_uber"], 0)
valor_total_dia = df_merged.groupby("data")["valor_total_dia"].sum()

#7 - Qual é a média de valor por km rodado por dia?
df_merged["valor_por_km"] = df_merged["valor_total_dia"].div(df_merged["distancia(km)"]).where(df_merged["distancia(km)"] >0)
valor_por_km_dia = df_merged.groupby("data")["valor_por_km"].mean()
df_merged["valor_por_km"] = df_merged["valor_por_km"].fillna(0).round(2)

#8 - Qual é a distância total percorrida por mes ?
distancia_por_mes = df_merged.groupby(df_merged["data"].dt.to_period("M"))["distancia(km)"].sum()
print(f'Distância total percorrida por mês:{distancia_por_mes}')

#9 - Qual é o tempo total gasto em corridas por mes ?
tempo_por_mes = df_merged.groupby(df_merged["data"].dt.to_period("M"))["duracao_min"].sum()
print(f'Tempo total gasto em corridas por mês:{tempo_por_mes}')

#10 - Quantas corridas foram feitas por mes ?
corridas_por_mes = df_merged.groupby(df_merged["data"].dt.to_period("M"))["id_viagem"].count()
print(f'Número de corridas feitas por mês:{corridas_por_mes}')

#11 - Quantas corridas com Turbo+ por mes ?
corridas_turbo_mes = df_merged.groupby(df_merged["data"].dt.to_period("M"))["turbo"].agg(lambda x:(x != 0).sum())
print(f'Número de corridas com Turbo+ por mês:{corridas_turbo_mes}')

#12 - Quantas corridas com Dinamico por mes ?
corridas_dinamico_mes = df_merged.groupby(df_merged["data"].dt.to_period("M"))["preco_dinamico"].agg(lambda x:(x != 0).sum())
print(f'Número de corridas com Dinamico por mês:{corridas_dinamico_mes}')

#13 - Qual é o valor total arrecadado por mes ?
valor_total_mes = df_merged.groupby(df_merged["data"].dt.to_period("M"))["valor_total_dia"].sum().round(2)
print(f'Valor total arrecadado por mês:{valor_total_mes}')

#14 - Qual é a média de valor por km rodado por mes?
valor_por_km_mes = df_merged.groupby(df_merged["data"].dt.to_period("M"))["valor_por_km"].mean().round(2)
print(f'Valor médio por km rodado por mês:{valor_por_km_mes}')

#15 - Qual foi o bairro com maior número de corridas de embarque ?
bairro_embarque_mais_corridas = df_merged.groupby("bairro_embarque")["id_viagem"].count().idxmax()
print(f'Bairro com maior número de corridas:{bairro_embarque_mais_corridas}')

#16 - Qual foi o bairro com maior valor total arrecadado no mês?
bairro_mais_valor = df_merged.groupby("bairro_embarque")["valor_total_dia"].sum().idxmax()
print(f'Bairro com maior valor total arrecadado no mês:{bairro_mais_valor}')

#17 - Qual foi o bairro com mais corridas com Turbo+ ?
bairro_mais_turbo = df_merged[df_merged["turbo"] != 0].groupby("bairro_embarque")["id_viagem"].count().idxmax()
print(f'Bairro com mais corridas com Turbo+:{bairro_mais_turbo}')

#18 - Qual foi o bairro com mais corridas com Dinâmico ?
bairro_mais_dinamico = df_merged[df_merged["preco_dinamico"] != 0].groupby("bairro_embarque")["id_viagem"].count().idxmax()
print(f'Bairro com mais corridas com Dinâmico:{bairro_mais_dinamico}')

#19 - Qual foi o bairro com maior valor médio por km rodado ?
bairro_mais_valor_km = df_merged.groupby("bairro_embarque")["valor_por_km"].mean().idxmax()
print(f'Bairro com maior valor médio por km rodado:{bairro_mais_valor_km}')

#20 - Qual foi a melhor corrida em termos de valor por km rodado ?
melhor_corrida = df_merged.loc[df_merged["valor_por_km"].idxmax()]
print(f'Melhor corrida em termos de valor por km rodado:\n{melhor_corrida}')

#21 - Qual foi a pior corrida em termos de valor por km rodado diferente de 0 ?
pior_corrida = df_merged.loc[df_merged["valor_por_km"] != 0].loc[lambda x: x["valor_por_km"].idxmin()]
print(f'Pior corrida em termos de valor por km rodado:\n{pior_corrida}')

#22 - Qual foi a corrida com maior distância percorrida ?
maior_distancia = df_merged.loc[df_merged["distancia(km)"].idxmax()]
print(f'Corrida com maior distância percorrida:\n{maior_distancia}')

#23 - Qual foi a corrida com menor distância percorrida ?
menor_distancia = df_merged.loc[df_merged["distancia(km)"] != 0].loc[lambda x: x["distancia(km)"].idxmin()]
print(f'Corrida com menor distância percorrida:\n{menor_distancia}')

#24 - Qual foi a corrida com maior duração ?
maior_duracao = df_merged.loc[df_merged["duracao_min"].idxmax()]
print(f'Corrida com maior duração:\n{maior_duracao}')

#25 - Qual foi a corrida com menor duração ?
menor_duracao = df_merged.loc[df_merged["duracao_min"] != 0].loc[lambda x: x["duracao_min"].idxmin()]
print(f'Corrida com menor duração:\n{menor_duracao}')

#26 - Qual o tempo médio por corrida ?
tempo_medio_corrida = df_merged["duracao_min"].mean().round(2)
print(f'Tempo médio por corrida:{tempo_medio_corrida} minutos')

#27 - Qual é o valor por hora trabalhada ?
valor_por_hora = df_merged["valor_total_dia"].sum() / (df_merged["duracao_min"].sum() / 60)
print(f'Valor por hora trabalhada:{valor_por_hora.round(2)}')

#28 - Qual é o valor base (sem adicionais) médio por km rodado ? Aqui, o valor base será considerado como o valor pago ao motorista (pg_motorista) + o dsc_uber (se for maior que 0) dividido pela distância percorrida.
df_merged["valor_base"] = df_merged["pg_motorista"] + np.where(df_merged["dsc_uber"] >0, df_merged["dsc_uber"], 0)
valor_base_por_km = df_merged["valor_base"].div(df_merged["distancia(km)"]).where(df_merged["distancia(km)"] >0)
valor_base_por_km_medio = valor_base_por_km.mean().round(2)
print(f'Valor base médio por km rodado:{valor_base_por_km_medio}')

#21 - Análise de série temporal
df_merged.set_index("data", inplace=True)
decomposicao = seasonal_decompose(corridas_por_dia, model='additive', period=7)
decomposicao.plot()
plt.suptitle('Decomposição da Série Temporal - Número de Corridas por Dia', fontsize=16)
plt.show()

#22 - Vamos criar 03 gráficos : dispersão ( tempo x valor e valor/km x distancia) ; barras ( comparando bairros mais lucrativos ) ; boxplots ( variação de preços por km rodados )

#Gráfico de dispersão - Tempo x Valor
plt.figure(figsize=(10,6))
plt.scatter(df_merged["duracao_min"], df_merged["valor_total_dia"], alpha=0.5)
plt.title('Dispersão: Tempo vs Valor Total da Corrida')
plt.xlabel('Duração (minutos)')
plt.ylabel('Valor Total da Corrida (R$)')
plt.grid(True)
plt.show()

#Gráfico de dispersão - Valor/km x Distância
plt.figure(figsize=(10,6))
plt.scatter(df_merged["distancia(km)"], df_merged["valor_por_km"], alpha=0.5, color='orange')
plt.title('Dispersão: Distância vs Valor por Km')
plt.xlabel('Distância (km)')
plt.ylabel('Valor por Km (R$)')
plt.grid(True)
plt.show()

#Gráfico de barras - Bairros mais lucrativos
bairros_lucrativos = df_merged.groupby("bairro_embarque")["valor_total_dia"].sum().nlargest(10)
plt.figure(figsize=(12,6))
bairros_lucrativos.plot(kind='bar', color='green')
plt.title('Top 10 Bairros Mais Lucrativos')
plt.xlabel('Bairro de Embarque')
plt.ylabel('Valor Total Arrecadado (R$)')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.show()

## Aqui vamos fazer um gráfico comparando o valor total arrecado nas corridas com turbo+, dinamico e sem adicionais mês a mês
# Preparando os dados
df_merged['mes'] = df_merged.index.to_period('M')
valor_turbo = df_merged[df_merged['turbo'] > 0].groupby('mes')['valor_total_dia'].sum()
valor_dinamico = df_merged[df_merged['preco_dinamico'] > 0].groupby('mes')['valor_total_dia'].sum()
valor_sem_adicionais = df_merged[(df_merged['turbo'] == 0) & (df_merged['preco_dinamico'] == 0)].groupby('mes')['valor_total_dia'].sum()
valor_total = df_merged.groupby('mes')['valor_total_dia'].sum()
df_valores = pd.DataFrame({
    'Turbo+': valor_turbo,
    'Dinâmico': valor_dinamico,
    'Sem Adicionais': valor_sem_adicionais,
    'Total': valor_total
}).fillna(0)
df_valores.index = df_valores.index.to_timestamp()
# Plotando o gráfico
df_valores.plot(kind='bar',stacked=False, figsize=(12,6))
plt.title('Valor Total Arrecadado por Tipo de Corrida (Mês a Mês)')
plt.xlabel('Mês')
plt.ylabel('Valor Total Arrecadado (R$)')
plt.xticks(rotation=45)
plt.legend(title='Tipo de Corrida')
plt.grid(True)
plt.show()

# Agora, vamos responder a pergunta : " Dado um intervalo em km, qual é o valor médio por km ?"
bins = list(range(menor_distancia["distancia(km)"].astype(int), maior_distancia["distancia(km)"].astype(int) + 5, 5))
labels = [f'{i}-{i+5} km' for i in bins[:-1]]
df_merged['intervalo_km'] = pd.cut(df_merged['distancia(km)'], bins=bins, labels=labels, right=False)
valor_medio_por_km_intervalo = df_merged.groupby('intervalo_km')['valor_por_km'].mean().round(2)
print(f'Valor médio por km em cada intervalo de distância:\n{valor_medio_por_km_intervalo}')

## Gráfico de linhas - Variação de preços por km rodados
plt.figure(figsize=(12,6))
valor_medio_por_km_intervalo.plot(kind='line', marker='o', color='purple')
plt.title('Variação do Valor Médio por Km Rodado por Intervalo de Distância')
plt.xlabel('Intervalo de Distância (km)')
plt.ylabel('Valor Médio por Km (R$)')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

#salvando uma cópia do dataframe tratado
df_merged.to_excel("data/Uber_Renan_Portfolio_Tratado.xlsx", index=False) 
