# Importando as Bibliotecas
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import plotly.graph_objects as go

# Importando as Funções
def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

# Iniciando a Tela 01
def show_tela_02():
    st.title("Dashboard Mentoria FutPythonTrader")
    st.header("Resultados")

    base = pd.read_csv("https://github.com/futpythontrader/YouTube/raw/main/Bases_de_Dados/Betfair/Base_de_Dados_Betfair_Exchange_Back_Lay.csv")
    base = base[['Date','League','Home','Away','Goals_H','Goals_A','Goals_Min_H','Goals_Min_A',
                'Odd_H_Back','Odd_H_Lay','Odd_A_Back','Odd_A_Lay','Odd_D_Back','Odd_D_Lay',
                'Odd_Over25_FT_Back','Odd_Under25_FT_Back','Odd_BTTS_Yes_Back','Odd_BTTS_No_Back',
                'Odd_CS_0x0_Lay','Odd_CS_0x1_Lay','Odd_CS_1x0_Lay','Odd_CS_Goleada_H_Lay','Odd_CS_Goleada_A_Lay']]
    base.columns = ['Date','League','Home','Away','Goals_H','Goals_A','Goals_Min_H','Goals_Min_A',
                    'Odd_H','Odd_H_Lay','Odd_A','Odd_A_Lay','Odd_D','Odd_D_Lay',
                    'Odd_Over25','Odd_Under25','Odd_BTTS_Yes','Odd_BTTS_No',
                    'Odd_0x0','Odd_0x1','Odd_1x0','Odd_Gol_H','Odd_Gol_A']
    base = drop_reset_index(base)

    df = base.copy()

    df['VAR'] = np.abs(df['Odd_D'] - df['Odd_A'])
    df['Lay_0x0'] = np.where(((df['Goals_H'] == 0) & (df['Goals_A'] == 0)), 0, 1)

    flt = ((df.VAR >= 2) & (df.Odd_0x0 > 1) & (df.Odd_0x0 <= 21))
    df0 = df[flt]
    df0 = drop_reset_index(df0)
    
    Stake = 1
    # Lucro Fixo e Responsabilidade Variável
    green = (Stake * 0.944)
    red = Stake * (1 - df0['Odd_0x0'])

    df0['Profit'] = np.where((df0['Lay_0x0'] == 1), green, red)
    df0['Investimento'] = df0['Odd_0x0'] - 1
    df0['Profit_acu'] = df0['Profit'].cumsum()

    # st.dataframe(df0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df0.index, y=df0['Profit_acu'], mode='lines'))

    fig.update_layout(
        title = 'Profit Acumulado',
        xaxis_title = 'Entradas',
        yaxis_title = 'Stakes'
    )

    st.plotly_chart(fig)


    