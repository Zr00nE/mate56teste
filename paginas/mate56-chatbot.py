import streamlit as st
from openai import OpenAI

# Configurações de API 
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

# Avatares para o usuário e assistente
avatar_user = 'arquivos/avatar.png'
avatar_assistent = 'arquivos/avatar2.png'

# Configurações de modelo e carregamento de instruções do assistente
modelo = 'gpt-4o-mini'
instrucoes = 'arquivos/assistente-python.txt'
with open(instrucoes, 'r', encoding='utf-8') as file:
    instrucoes_gpt = file.read()

# Mensagem inicial do assistente no chat
frase_inicial = 'Eu sou um instrutor personalizado de Python, focado em ensinar Python para Inteligência Artificial e Data Science. Vamos começar? 🐍'
st.chat_message('assistant', avatar=avatar_assistent).write(frase_inicial)

# Inicializa o histórico de mensagens na sessão
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": instrucoes_gpt}]

# Exibe histórico de mensagens com os avatares correspondentes
for msg in st.session_state.messages[1:]:
    avatar = avatar_user if msg['role'] == 'user' else avatar_assistent
    st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

# Captura a entrada do usuário no chat e gera uma resposta
prompt = st.chat_input()

if prompt:
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar=avatar_user).write(prompt)

    # Faz uma requisição à API OpenAI para gerar a resposta do assistente
    with st.chat_message("assistant", avatar=avatar_assistent):
        stream = client.chat.completions.create(
            model=modelo,
            messages=st.session_state.messages,
            stream=True
        )

        # Exibe a resposta em tempo real
        response = st.write_stream(stream)

    # Adiciona a resposta do assistente ao histórico
    st.session_state.messages.append({"role": "assistant", "content": response})
