import streamlit as st
from tela1 import show_tela_01
from tela2 import show_tela_02

# Criação do Aplicativo
st.set_page_config(page_title='Dashboard Mentoria', layout='wide')

paginas = ['Lay 0 x 0', 'Resultados']

escolha = st.sidebar.radio('', paginas)

if escolha == 'Lay 0 x 0':
    show_tela_01()
elif escolha == 'Resultados':
    show_tela_02()