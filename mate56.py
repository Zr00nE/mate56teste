import streamlit as st


st.set_page_config(
    page_title="Assistente ChatBot",
    page_icon='arquivos/avatar2.jpeg',
    layout="centered",
    initial_sidebar_state="expanded")

st.logo("arquivos/avatar2.jpeg") 

paginas = {
    "Conteúdos": [
        st.Page("paginas/mate56-inicial.py", title="Página Inicial", icon = '', default = True), 
    ], 

    "Aplicativos para os Alunos": [
        st.Page("paginas/mate56-chatbot.py", title="Instrutor de Python", icon='🐍'), 
    ],
}

pg = st.navigation(paginas)
pg.run()
  
