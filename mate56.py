import streamlit as st


st.set_page_config(
    page_title="Assistente ChatBot",
    page_icon='arquivos/avatar2.png',
    layout="centered",
    initial_sidebar_state="expanded")

st.logo("arquivos/logo.png") 

paginas = {
    "Conteúdos": [
        st.Page("paginas/mate56-inicial.py", title="Página Inicial", icon = '', default = True), 
        st.Page("paginas/mate56-materiais.py", title="Materiais de Aula", icon = ''), 
        st.Page("paginas/mate56-links.py", title="Links e Referências", icon = ''), 
    ], 

    "Aplicativos para os Alunos": [
        st.Page("paginas/mate56-chatbot.py", title="Instrutor de Python", icon='🐍'), 
    ],
}

pg = st.navigation(paginas)
pg.run()
  