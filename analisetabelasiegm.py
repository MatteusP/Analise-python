# -*- coding: utf-8 -*-
"""AnaliseTabelasIEGM.ipynb

Coerência entre os Resultados dos Indicadores dos Programas e das Metas das Ações
"""

import pandas as pd
import numpy as np

# Carregar as tabelas do Excel
acoes_df = pd.read_excel('/content/IEGM 2023.xlsx', sheet_name='iegm ação')
programas_df = pd.read_excel('/content/IEGM 2023.xlsx', sheet_name='iegm programa')

# Exibir as primeiras linhas de cada tabela para inspeção
print("Tabela de Ações:")
print(acoes_df.head())

print("\nTabela de Programas:")
print(programas_df.head())

# Definir funções para calcular E1 e E2
def calcular_E1(meta_alcancada, meta_estimada):
    if meta_estimada == 0:
        return 0
    return meta_alcancada / meta_estimada

def calcular_E2(valor_alcancado, valor_estimado):
    if valor_estimado == 0:
        return 0
    return valor_alcancado / valor_estimado

# Adicionar colunas para E1 e E2 nas tabelas
programas_df['E1'] = programas_df.apply(lambda row: calcular_E2(row['valor_alcancado_indicador'], row['valor_estimado_indicador_vf2025']), axis=1)
acoes_df['E2'] = acoes_df.apply(lambda row: calcular_E1(row['meta_fisica_alcancada'], row['meta_fisica_estimada']), axis=1)


# Calcular média de E1 e E2 por programa
media_E1 = programas_df.groupby('codigo_programa')['E1'].mean().reset_index()
media_E2 = acoes_df.groupby('codigo_programa')['E2'].mean().reset_index()

# Verificar códigos de programa que não aparecem em ambas as tabelas
codigos_programas_unicos = pd.merge(media_E1[['codigo_programa']], media_E2[['codigo_programa']], on='codigo_programa', how='outer', indicator=True)

# Filtrar para encontrar os códigos que estão apenas em uma das tabelas
codigos_somente_programas = codigos_programas_unicos[codigos_programas_unicos['_merge'] == 'left_only']
codigos_somente_acoes = codigos_programas_unicos[codigos_programas_unicos['_merge'] == 'right_only']

print("Códigos de Programas presentes apenas na tabela de Programas:")
print(codigos_somente_programas['codigo_programa'])

print("\nCódigos de Programas presentes apenas na tabela de Ações:")
print(codigos_somente_acoes['codigo_programa'])

# Unir as médias para calcular a diferença média, mantendo todos os registros
coerencia_df = pd.merge(media_E1, media_E2, on='codigo_programa', how='outer', suffixes=('_E1', '_E2'))

# Preencher valores NaN com 0 para os cálculos
coerencia_df['E1'] = coerencia_df['E1'].fillna(0)
coerencia_df['E2'] = coerencia_df['E2'].fillna(0)

# Calcular E e substituir 0 por 1 onde necessário
coerencia_df['E'] = abs(coerencia_df['E1'] - coerencia_df['E2'])
coerencia_df.loc[(coerencia_df['E1'] == 0) | (coerencia_df['E2'] == 0), 'E'] = 1

# Tratar casos onde o somatório A ou C são 0
coerencia_df['E'] = coerencia_df.apply(lambda row: 1 if row['E1'] == 0 or row['E2'] == 0 else row['E'], axis=1)

# Exibir resultados
print("Média de E1 por Programa:")
print(media_E1)
print("\nMédia de E2 por Ação:")
print(media_E2)
print("\nCoerência entre os Resultados dos Indicadores dos Programas e das Metas das Ações:")
coerencia_df

# Tratar casos onde o somatório A ou C são 0
print(coerencia_df['E1'].mean())
print(coerencia_df['E2'].mean())
total_A = acoes_df['meta_fisica_estimada'].sum()
print("Soma das ações = ", total_A)
total_C = programas_df['valor_estimado_indicador_vf2025'].sum()
print("Soma dos Programas = ", total_C)
if total_A == 0 or total_C == 0:
    Ef = 1
else:
    Ef = coerencia_df['E'].mean()

print("Ef =", Ef)

# Função para calcular a pontuação baseada em Ef
# Os valores de E1, E2 e E estão em %, necessário dividir por 100 para obter o real valor de Ef
Ef = Ef/100
def calcular_pontuacao(Ef):
    if Ef <= 0.20:
        return 250
    elif 0.20 < Ef < 0.40:
        return ((0.40 - Ef) / 0.20) * 250
    else:
        return 0

# Calcular a pontuação final
pontuacao_final = calcular_pontuacao(Ef)
print("Pontuação Final =", pontuacao_final)
print("Ef = ", Ef)

"""Confronto entre o Resultado Físico Alcançado pelas Metas das Ações e os Recursos Financeiros Utilizados"""

# Carregar os dados das ações
acoes_df = pd.read_excel('/content/IEGM 2023.xlsx', sheet_name='iegm ação')

# Calcular H1 e H2
acoes_df['H1'] = acoes_df.apply(lambda row: row['meta_fisica_alcancada'] / row['meta_fisica_estimada'] if row['meta_fisica_estimada'] != 0 else 0, axis=1)
acoes_df['H2'] = acoes_df.apply(lambda row: row['valor_liquido'] / row['dotacao_final'] if row['dotacao_final'] != 0 else 0, axis=1)

# Exibir as primeiras linhas para inspeção
#acoes_df

# Calcular |μH1 - μH2|
mu_H1 = acoes_df['H1'].mean()
mu_H2 = acoes_df['H2'].mean()

# Os valores de H1 estão em %, necessário dividir por 100 para obter o real valor
mu_H1 = mu_H1/100

# Exibir valores
print("H1 = ", mu_H1)
print("H2 = ", mu_H2)

# Cálculo do módulo da diferença
H = abs(mu_H1 - mu_H2)

# Tratar casos especiais
if acoes_df['meta_fisica_estimada'].sum() == 0 or acoes_df['dotacao_final'].sum() == 0:
    H = 1

print("H =", H)

# Calcular a pontuação final baseada em H
#H = H/100
print("Valor de H = ", H)
def calcular_pontuacao(H):
    if H <= 0.20:
        return 250
    elif 0.20 < H < 0.40:
        return ((0.40 - H) / 0.20) * 250
    else:
        return 0

pontuacao_final = calcular_pontuacao(H)
print("Pontuação Final =", pontuacao_final)