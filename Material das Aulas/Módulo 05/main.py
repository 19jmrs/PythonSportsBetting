import streamlit as st

from tela1 import show_tela1
from tela2 import show_tela2
from tela3 import show_tela3

### Criação de Aplicativo ###

st.set_page_config(
    page_title="Meu Dashboard", layout="wide"
)

paginas = ['Lay Home', 'Lay Away', 'Lay 0 x 1']

escolha = st.sidebar.radio('', paginas)

if escolha == 'Lay Home':
    show_tela1()
elif escolha == 'Lay Away':
    show_tela2()
elif escolha == 'Lay 0 x 1':
    show_tela3()