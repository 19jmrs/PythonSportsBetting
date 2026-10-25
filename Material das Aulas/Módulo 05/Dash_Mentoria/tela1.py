# Importando as Bibliotecas
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

# Iniciando a Tela 01
def show_tela_01():
    st.title("Dashboard Mentoria FutPythonTrader")
    st.header("Lay 0 x 0")

    dia = st.date_input("Data de Análise", date.today())

    df = pd.read_csv(f'https://github.com/futpythontrader/YouTube/raw/main/Jogos_do_Dia/Betfair/Jogos_do_Dia_Betfair_Back_Lay_{dia}.csv')

    df = df[['Date','Time','League','Home','Away','IDMercado_Correct_Score',
    'Odd_H_Back','Odd_A_Back','Odd_D_Back','Odd_Under25_FT_Back','Odd_Over25_FT_Back','Odd_BTTS_Yes_Back','Odd_BTTS_No_Back',
    'Odd_CS_0x0_Lay','Odd_CS_0x1_Lay','Odd_CS_1x0_Lay']]
    df.columns = ['Date','Time','League','Home','Away','IDMercado_Correct_Score',
    'Odd_H','Odd_A','Odd_D','Odd_Under25','Odd_Over25','Odd_BTTS_Yes','Odd_BTTS_No',
    'Odd_CS_0x0_Lay','Odd_CS_0x1_Lay','Odd_CS_1x0_Lay']

    df['VAR'] = np.abs(df['Odd_D'] - df['Odd_A'])
    flt = ((df.VAR >= 2.0) & (df.Odd_CS_0x0_Lay > 1) & (df.Odd_CS_0x0_Lay <= 21))
    df0 = df[flt]
    df0 = drop_reset_index(df0)
    Entradas1 = df0[['Date','Time','League','Home','Away','Odd_CS_0x0_Lay','IDMercado_Correct_Score']]
    Entradas1.columns = ['Date','Time','League','Home','Away','Odd_0x0','IDMercado_Correct_Score']

    df = pd.read_csv(f'https://github.com/futpythontrader/YouTube/raw/main/Jogos_do_Dia/Betfair/Jogos_do_Dia_Betfair_Back_Lay_{dia}.csv')

    df = df[['Date','Time','League','Home','Away','IDMercado_Correct_Score',
    'Odd_H_Back','Odd_A_Back','Odd_D_Back','Odd_Under25_FT_Back','Odd_Over25_FT_Back','Odd_BTTS_Yes_Back','Odd_BTTS_No_Back',
    'Odd_CS_0x0_Lay','Odd_CS_0x1_Lay','Odd_CS_1x0_Lay']]
    df.columns = ['Date','Time','League','Home','Away','IDMercado_Correct_Score',
    'Odd_H','Odd_A','Odd_D','Odd_Under25','Odd_Over25','Odd_BTTS_Yes','Odd_BTTS_No',
    'Odd_0x0','Odd_0x1','Odd_1x0']

    df['p_Under'] = 1 / df['Odd_Under25']
    df['p_0x0'] = 1 / df['Odd_0x0']

    df['VAR'] = df['p_0x0'] / df['p_Under']

    flt = ((df.VAR > 0.121) & (df.VAR <= 0.124)
            & (df.Odd_0x0 > 1) & (df.Odd_0x0 <= 21))
    df0 = df[flt]
    df0 = drop_reset_index(df0)
    Entradas2 = df0[['Date','Time','League','Home','Away','Odd_0x0','IDMercado_Correct_Score']]

    Entradas = pd.concat([Entradas1, Entradas2])
    Entradas = Entradas.sort_values(by='Time')
    Entradas = Entradas.drop_duplicates(subset=['Home', 'Away'])
    Entradas = drop_reset_index(Entradas)

    df0 = Entradas[['Date','Time','League','Home','Away','Odd_0x0']]

    st.dataframe(df0)

    st.subheader("Entradas")
    st.text('')

    for a,b,c,d,e,f in zip(Entradas.League,
                           Entradas.Time,
                           Entradas.Home,
                           Entradas.Away,
                           Entradas.Odd_0x0,
                           Entradas.IDMercado_Correct_Score):
        
        liga = a
        hora = b
        home = c
        away = d
        odd = e 
        id_mercado = f

        st.write(f"Liga: {liga}")
        st.write(f"Jogo: {home} x {away}")
        st.write(f"Horário: {hora}")
        st.write(f"Odd: {odd}")
        link1 = f'<div style="text-align:left"><a href="https://bolsadeaposta.com/exchange/sport/1/market/{id_mercado}">{"Bolsa de Aposta"}</a></div>'
        st.markdown(link1, unsafe_allow_html=True)
        link2 = f'<div style="text-align:left"><a href="https://fulltbet.com/exchange/sport/1/market/{id_mercado}">{"Fulltbet"}</a></div>'
        st.markdown(link2, unsafe_allow_html=True)
        st.text('');st.text('')


