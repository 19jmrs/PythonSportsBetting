# Importand as Bibliotecas
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

# Importando as Funções
def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

def ajustar_id_mercado(id_mercado, comprimento_decimal_desejado=9):
    id_mercado_str = str(id_mercado)
    partes = id_mercado_str.split('.')
    if len(partes) == 1:
        return id_mercado_str + '.' + '0' * comprimento_decimal_desejado
    parte_inteira, parte_decimal = partes
    zeros_para_adicionar = comprimento_decimal_desejado - len(parte_decimal)
    if zeros_para_adicionar > 0:
        parte_decimal += '0' * zeros_para_adicionar
    id_mercado_ajustado = parte_inteira + '.' + parte_decimal
    return id_mercado_ajustado

def remove_outliers(df, cols):
    for col in cols:
        Q1 = df[col].quantile(0.05)
        Q3 = df[col].quantile(0.95)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    return df

def entropy(probabilities):
    probabilities = probabilities[probabilities > 0]
    return -np.sum(probabilities * np.log2(probabilities))

# Iniciando a Tela 3
def show_tela3():
    st.title("FutPythonTrader")
    st.header("Lay 0 x 1")

    dia = st.date_input("Data de Análise", date.today())

    df = pd.read_csv(f'https://github.com/futpythontrader/YouTube/raw/main/Luke/Jogos_do_Dia/Jogos_do_Dia_Betfair_Back_Lay_{dia}.csv')
    
    odds_columns = [col for col in df.columns if 'Odd_' in col]

    df_clean = remove_outliers(df, odds_columns)
    df = drop_reset_index(df_clean)

    cs_lay_columns = [col for col in df.columns if 'CS' in col and 'Lay' in col]
    cs_lay_data = df[cs_lay_columns]
    cv_cs_lay = cs_lay_data.apply(lambda x: x.std() / x.mean(), axis=1)
    df['CV_CS'] = cv_cs_lay

    probabilities_cs = cs_lay_data.replace(0, np.nan).apply(lambda x: 1 / x, axis=1)
    entropy_cs = probabilities_cs.apply(lambda x: -np.sum(x * np.log2(x)) if x.sum() != 0 else 0, axis=1)
    df['Entropy_CS'] = entropy_cs

    flt = (df.CV_CS > 2.6) & (df.Entropy_CS > 3.6)
    df0 = df[flt]
    df0 = drop_reset_index(df0)
    Entradas = df0[['Date','Time','League','Home','Away','Odd_CS_0x1_Lay']]
       
    st.dataframe(Entradas)

    st.subheader("Entradas")
    st.text('')

    for a,b,c,d,e,f in zip(df0.League,
                           df0.Time,
                           df0.Home,
                           df0.Away,
                           df0.Odd_CS_0x1_Lay,
                           df0.IDMercado_Correct_Score):
        liga = a
        horario = b
        home = c
        away = d
        odd = e
        id_mercado = ajustar_id_mercado(f)

    
        st.write(f"Liga: {liga}")
        st.write(f"Jogo: {home} x {away}")
        st.write(f"Horário: {horario}")
        st.write(f"Odd 0 x 1: {odd}")
        link = f'<div style="text-align:left"><a href="https://bolsadeaposta.com/exchange/sport/1/market/{id_mercado}">{"Bolsa de Aposta"}</a></div>'
        st.markdown(link, unsafe_allow_html=True)
        st.write(''); st.text(''); st.text('')