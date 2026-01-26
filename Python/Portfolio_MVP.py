## Importando os pacotes necessários
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose

## Carregando as tabelas
df_corridas= pd.read_excel("data/Uber_Renan_Portfolio.xlsx", sheet_name="Corridas")
df_localidade = pd.read_excel("data/Uber_Renan_Portfolio.xlsx", sheet_name="Localidade")
df_valor = pd.read_excel("data/Uber_Renan_Portfolio.xlsx", sheet_name="Valor_Viagem")

## Merge das tabelas : Aqui, faremos o merge das 3 tabelas do dataframe para que seja possível fazer a análise exploratória dos dados
df_merged = pd.merge(df_corridas,df_localidade, on=["ID_local", "ID_local"], how="left")
df_merged = pd.merge(df_merged, df_valor, on="ID_valor", how="left")

## Removendo a coluna Data_x e renomeando a Data_y , que são iguais, foram duplicadas devido ao merge
df_merged = df_merged.drop(columns=["Data_x"])
df_merged = df_merged.rename(columns={"Data_y": "Data"})

## Padronizando: vamos padronizar os nomes das colunas para facilitar a manipulação
def remover_acentos(series):
    return (
        series
        .str.normalize('NFKD')
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
    )
df_merged.columns = remover_acentos(df_merged.columns.str.lower().str.replace(' ', '_')).str.replace('+',"").str.replace('-', '_')

## Convertendo a coluna 'data' para o formato datetime
df_merged['data'] = pd.to_datetime(df_merged['data'], format='%d/%m/%y')

## Vamos alterar as colunas municipio_embarque, bairro_embarque, municipio_desembarque e bairro_desembarque onde for 0 para 'cancelado' devido a coluna ser do tipo object (categórica)
df_merged[['municipio_embarque', 'bairro_embarque', 'municipio_desembarque', 'bairro_desembarque']] = df_merged[['municipio_embarque', 'bairro_embarque', 'municipio_desembarque', 'bairro_desembarque']].replace(0, 'cancelado')

## Análise Exploratória dos Dados (EDA)
# Análise 1 : Ganho por dia da semana, vamos analisar o ganho total por dia da semana, isso inclui os valores preco_dinamico e turbo, sendo assim vamos adicionar uma nova coluna chamada 'valor_total' que será a soma dos valores 'preco_dinamico' e 'turbo' e 'pg_motorista'
df_merged['valor_total'] = df_merged['preco_dinamico'] + df_merged['turbo'] + df_merged['pg_motorista']
ganho_dia_semana = df_merged.groupby(df_merged['data'].dt.day_name())['valor_total'].sum().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
plt.figure(figsize=(10,6))
sns.barplot(x=ganho_dia_semana.index, y=ganho_dia_semana.values, palette='viridis')
plt.title('Ganho Total por Dia da Semana')
plt.xlabel('Dia da Semana')
plt.ylabel('Ganho Total (R$)')
plt.show()

## Análise 2: Ganho por faixa horária - A partir da coluna 'horario' do dataframe, vamos criar uma nova coluna chamada 'faixa_horaria' que categoriza os horarios em faixas: 'Madrugada' (00:00 - 05:59), 'Manhã' (06:00 - 11:59), 'Tarde' (12:00 - 17:59), 'Noite' (18:00 - 23:59)

df_merged['horario'] = (
    df_merged['horario']
    .astype(str)
    .str.strip()
    .str.replace(r'\s+', '', regex=True)
)
df_merged['horario'] = pd.to_datetime(
    df_merged['horario'],
    format='%H:%M:%S',
    errors='raise'
)
df_merged['hora'] = df_merged['horario'].dt.hour
def categorizar_faixa_horaria(hora):
    if 0 <= hora < 6:
        return 'Madrugada'
    elif 6 <= hora < 12:
        return 'Manhã'
    elif 12 <= hora < 18:
        return 'Tarde'
    else:
        return 'Noite'
df_merged['faixa_horaria'] = df_merged['hora'].apply(categorizar_faixa_horaria)

df_merged['ganho_total'] = (
    df_merged['preco_dinamico'].fillna(0) +
    df_merged['turbo'].fillna(0) +
    df_merged['pg_motorista'].fillna(0)
)
ganho_por_faixa = (
    df_merged
    .groupby('faixa_horaria', as_index=False)['ganho_total']
    .sum()
)
ordem = ['Madrugada', 'Manhã', 'Tarde', 'Noite']

ganho_por_faixa['faixa_horaria'] = pd.Categorical(ganho_por_faixa['faixa_horaria'], categories=ordem, ordered=True)

ganho_por_faixa = ganho_por_faixa.sort_values('faixa_horaria')

plt.figure(figsize=(8,5))
sns.barplot(x='faixa_horaria', y='ganho_total', data=ganho_por_faixa, palette='magma')
plt.title('Ganho Total por Faixa Horária')
plt.xlabel('Faixa Horária')
plt.ylabel('Ganho Total (R$)')
plt.show()

## Aqui, foi preciso lidar com o formato da coluna 'horario' que estava como string, convertendo-a para datetime para extrair a hora corretamente. 

## Análise 3: Ganhos por Quilometragem - Vamos analisar o ganho total por faixa de quilometragem percorrida. Primeiro, criaremos faixas de quilometragem e depois somaremos os ganhos em cada faixa.
## A coluna distancia_corridA(km) tem o status : cancelado e por isso, está com o formato object, vamos converter para numérico, transformando os valores ' cancelado ' em NaN
df_merged['distancia_corrida(km)'] = pd.to_numeric(df_merged['distancia_corrida(km)'], errors='coerce')
df_merged['distancia_embarque(km)'] = pd.to_numeric(df_merged['distancia_embarque(km)'], errors='coerce')
## validando a transformação : 
# print(df_merged[['distancia_corrida(km)', 'distancia_embarque(km)']].dtypes)

## Quantidade total de cancelamentos:
total_cancelamentos = df_merged['distancia_corrida(km)'].isna().sum()
print(f'Total de cancelamentos: {total_cancelamentos}')

## Criando a coluna de km total
df_merged['km_total'] = df_merged['distancia_corrida(km)'].fillna(0) + df_merged['distancia_embarque(km)'].fillna(0)
df_merged['ganho_sem_bonus'] = df_merged['pg_motorista'].fillna(0)

## Vamos analisar o ganho por km rodado, incluindo os ganhos de preco_dinamico e turbo
df_merged['ganho_km_valor_total'] = df_merged['valor_total'] / df_merged['km_total'].replace(0 , np.nan)

## Vamos analisar o ganho por km rodado, apenas com o valor base do motorista entitulado como 'pg_motorista'
df_merged['ganho_km_base'] = df_merged['ganho_sem_bonus'] / df_merged['km_total'].replace(0 , np.nan)

## Criando faixas de quilometragem
bins = [ 0, 2, 5, 10, 15, 20, 30, 50]

labels = ['0-2 km', '2-5 km', '5-10 km', '10-15 km', '15-20 km', '20-30 km', '30-50 km']

df_merged['faixa_km'] = pd.cut(df_merged['km_total'], bins=bins, labels=labels, right=False)

analise_km = df_merged.groupby('faixa_km').agg({
    'ganho_km_valor_total': 'mean',
    'ganho_km_base': 'mean',
    'km_total': 'count'
})

analise_km.rename(columns={'km_total': 'quantidade_corridas'}, inplace=True)

## Plotando os resultados
x = np.arange(len(analise_km))
largura = 0.35

plt.figure()
plt.bar( x - largura/2, analise_km['ganho_km_valor_total'], width=largura, label='Ganho por km (Valor Total)', color='b')

plt.bar( x + largura/2, analise_km['ganho_km_base'], width=largura, label='Ganho por km (Base)', color='g')

plt.xticks(x, analise_km.index)
plt.xlabel('Faixa de KM')
plt.ylabel('Ganho Médio por KM (R$)')
plt.title('Comparação: Ganho por KM - Valor Total vs Base')
plt.legend()
plt.tight_layout()
plt.show()

## Análise 4: Ganho por hora - Vamos analisar o ganho total por hora do dia, para isso, precisamos incluir uma informação que não há nos dados que é tempo de deslocamento para cada corrida. Nessa situação , o valor base será de 6 minutos, que é o tempo médio de deslocamento para cada corrida levando em consideração fatores como : engarrafamentos, vias locais, semáforos, etc.
df_merged['tempo_deslocamento_min'] = 6
df_merged['duracao_total_min'] = df_merged['tempo_deslocamento_min'] + df_merged['duracao_min'].fillna(0)
df_merged['duracao_total_hora'] = df_merged['duracao_total_min'] / 60
df_merged['ganho_hora'] = df_merged['valor_total'] / df_merged['duracao_total_hora'].replace(0 , np.nan)

analise_hora = df_merged.groupby('faixa_horaria').agg({
    'valor_total': 'sum',
    'duracao_total_hora': 'sum'
})

analise_hora['ganho_hora_real'] = (analise_hora['valor_total'] / analise_hora['duracao_total_hora']).replace(0 , np.nan)
analise_hora = analise_hora.reindex(ordem)

plt.figure()
plt.bar(
    analise_hora.index,
    analise_hora['ganho_hora_real']
)

plt.xlabel('Faixa Horária')
plt.ylabel('Ganho por Hora (R$)')
plt.title('Ganho por Hora Real por Faixa Horária')
plt.show()

## Análise 5: