import streamlit as st
from openai import OpenAI
import numpy as np
import pandas as pd
import re
import openpyxl
import json


# Configurações de API 
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

# Avatares para o usuário e assistente e Cardapio
avatar_user = 'arquivos/avatar.png'
avatar_assistent = 'arquivos/avatar2.jpeg'
card = 'arquivos/CARDAPIO_TOPICOS.xlsx'
Cardapio = pd.read_excel(card)

# Configurações de modelo e carregamento de instruções do assistente
modelo = 'gpt-4o-mini'
instrucoes = 'arquivos/assistente-python.txt'
with open(instrucoes, 'r', encoding='utf-8') as file:
    instrucoes_gpt = file.read()

# Mensagem inicial do assistente no chat
frase_inicial = 'Eu sou um instrutor personalizado, focado em te ajudar a escolher o melhor prato para o seu momento atual. Vamos começar?'
st.chat_message('assistant', avatar=avatar_assistent).write(frase_inicial)

# Inicializa o histórico de mensagens na sessão
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": instrucoes_gpt}]

# Exibe histórico de mensagens com os avatares correspondentes
for msg in st.session_state.messages[1:]:
    avatar = avatar_user if msg['role'] == 'user' else avatar_assistent
    st.chat_message(msg["role"], avatar=avatar).write(msg["content"])


################################################## Funções ##########################################################

def gerar_embeddings(dataframe, colunas):
    """
    Gera embeddings para colunas específicas de um DataFrame.

    :param dataframe: O DataFrame contendo os dados.
    :param colunas: Lista de nomes das colunas que serão usadas para gerar embeddings.
    :return: Um DataFrame com os embeddings como colunas adicionais.
    """
    # Combina o texto das colunas selecionadas
    textos = dataframe[colunas].astype(str).apply(lambda row: " ".join(row), axis=1)

    # Gera embeddings para os textos combinados
    response = client.embeddings.create(
        input=textos.tolist(),  # Passa a lista de textos do DataFrame
        model="text-embedding-3-small"
    )

    # Adiciona os embeddings ao DataFrame
    dataframe["embeddings"] = [item.embedding for item in response.data]
    return dataframe

def similaridade_cosseno(vetor1, vetor2):
    # Calcula o produto escalar entre os vetores
    produto_escalar = np.dot(vetor1, vetor2)
    norma_vetor1 = np.linalg.norm(vetor1)
    norma_vetor2 = np.linalg.norm(vetor2)
    # Calcula a similaridade do cosseno
    similaridade = produto_escalar / (norma_vetor1 * norma_vetor2)
    return similaridade

def transformar_input_usuario(input_usuario, client):
    """
    Usa GPT para transformar o input do usuário em um formato estruturado.
    
    :param input_usuario: Texto original do usuário.
    :param client: Cliente da API GPT (OpenAI, etc.).
    :return: Dicionário com as preferências do usuário.
    """
    prompt = f"""
    Transforme o seguinte pedido do usuário em uma descrição estruturada, clara e organizada, garantindo que:  
    - Todos os ingredientes (desejados e proibidos) sejam convertidos para minúsculas e estejam em um formato consistente para comparação direta.  
    - Ingredientes proibidos incluam sinônimos e variações conhecidas e suas variações no plural (ex.: "peixe" deve incluir "tilápia", "salmão", "atum", etc.).  
    - Ingredientes desejados sejam expandidos para incluir variações conhecidas (ex.: "queijo" deve incluir "muçarela", "cheddar", "parmesão").  
    - Termos subjetivos (como "apimentado", "doce", "leve") sejam convertidos para ingredientes específicos.  
    - Preferências de estilo culinário e ocasião sejam identificadas com palavras-chave padronizadas.  
    - A estrutura de saída seja fácil de extrair usando expressões regulares na função de filtragem.  
    
    Pedido: "{input_usuario}"
    
    ### **Formato de saída esperado:**  
    - ingredientes_desejados: [lista de ingredientes mencionados ou inferidos, todos em minúsculas e normalizados]  
    - ingredientes_proibidos: [lista de ingredientes que o usuário não quer, incluindo variações e sinônimos em minúsculas]  
    - proteina: ["vegano", "vegetariano" ou "carnívoro"; se não especificado, retorne "carnívoro"]  
    - ocasiao: ["jantar", "almoço", "lanche", "café da manhã", etc.; se não mencionado, retorne "não mencionada"]  
    - preferencias: ["nenhuma" ou outras observações importantes, como nível de dificuldade, tempo de preparo, etc.]  
    - estilo_culinario: ["mexicano", "indiano", "mediterrâneo", etc.; se não especificado, retorne "não mencionado"]  
    
    ### **Conversão e Normalização de Termos Subjetivos:**  
    - "apimentado" → adicionar ingredientes como "pimenta dedo-de-moça", "jalapeño", "pimenta caiena".  
    - "doce" → adicionar ingredientes como "mel", "açúcar mascavo", "frutas caramelizadas".  
    - "leve" → priorizar ingredientes como "frango", "peixe", "folhas verdes", evitando frituras.  
    - "confortável" → priorizar pratos quentes e cremosos, como "massas", "ensopados".  
    - "frutos do mar" → incluir ingredientes como "camarão", "lagosta", "siri", "lula", "polvo", "mariscos", "mexilhão".  
    - "lactose" → incluir ingredientes como "leite", "queijo", "manteiga", "nata", "creme de leite", "iogurte".  
    
    ### **Regras de Normalização para Compatibilidade com o Filtro:**  
    - Todos os ingredientes devem estar em minúsculas para comparação direta.  
    - Ingredientes proibidos devem incluir variações e sinônimos conhecidos.  
    - Ingredientes desejados devem incluir variações conhecidas para aumentar as correspondências.  
    - Utilize palavras-chave padronizadas para proteínas e ocasiões.  
    - Se o usuário solicitar apenas uma recomendação genérica, preencha "sugestao_generica" na seção de tipo de requisição.  """

    response = client.chat.completions.create(
        model="gpt-4",  # Atualize para o modelo correto
        messages=[
            {"role": "system", "content": "Você é um assistente que organiza pedidos de comida de forma clara e estruturada."},
            {"role": "user", "content": prompt}
        ]
    )
    resposta = response.choices[0].message.content
    
    # Converter a resposta para JSON
    try:
        resposta_json = json.loads(resposta)
    except json.JSONDecodeError:
        # Se a resposta não for JSON válido, criar um dicionário padrão
        resposta_json = {
            "ingredientes_desejados": [],
            "ingredientes_proibidos": [],
            "proteina": "carnívoro",
            "ocasiao": "não mencionada",
            "preferencias": "nenhuma",
            "estilo_culinario": "não mencionado"
        }
    
    return resposta_json

def Embedding(texto):
    response = client.embeddings.create(
        input=texto,
        model="text-embedding-3-small")

    return response.data[0].embedding


def Filtrar_Cardapio(input_json, cardapio):
    """
    Filtra o cardápio com base nas preferências do usuário, recebendo um JSON estruturado como input.
    
    :param input_json: Dicionário contendo preferências de ingredientes, proteínas, ocasião, etc.
    :param cardapio: DataFrame contendo o cardápio completo.
    :return: DataFrame filtrado de acordo com as preferências do usuário.
    """
    
    # Extrair informações do JSON de input
    ingredientes_desejados = [i.strip().lower() for i in input_json.get("ingredientes_desejados", [])]
    ingredientes_proibidos = [i.strip().lower() for i in input_json.get("ingredientes_proibidos", [])]
    tipo_proteina = input_json.get("proteina", "carnívoro").strip().lower()

    # Normalizar ingredientes do cardápio
    cardapio["INGREDIENTES"] = cardapio["INGREDIENTES"].apply(lambda x: [ing.strip().lower() for ing in x.split(",")])

    # Função para verificar se um prato contém ingredientes proibidos
    def contem_proibidos(ingredientes):
        return any(p in ingredientes for p in ingredientes_proibidos)

    # Função para verificar se um prato contém ingredientes desejados
    def contem_desejados(ingredientes):
        return any(d in ingredientes for d in ingredientes_desejados)

    # Criar uma cópia do cardápio para filtrar
    cardapio_filtrado = cardapio.copy()

    # Remover pratos com ingredientes proibidos
    if ingredientes_proibidos:
        cardapio_filtrado = cardapio_filtrado[~cardapio_filtrado["INGREDIENTES"].apply(contem_proibidos)]

    # Aplicar o filtro de desejados apenas se houver ingredientes válidos no dataset
    ingredientes_existentes = set(ing for lista in cardapio_filtrado["INGREDIENTES"] for ing in lista)
    desejados_validos = [d for d in ingredientes_desejados if d in ingredientes_existentes]

    if desejados_validos:
        cardapio_filtrado = cardapio_filtrado[cardapio_filtrado["INGREDIENTES"].apply(contem_desejados)]

    # Ajustar a filtragem de proteínas para aceitar as categorias do dataset
    proteina_mapeamento = {
        "carnívoro": ["carnívoro"],
        "vegetariano": ["vegetariano"],
        "vegano": ["vegano"]
    }

    if tipo_proteina in proteina_mapeamento:
        proteinas_validas = proteina_mapeamento[tipo_proteina]
        cardapio_filtrado = cardapio_filtrado[
            cardapio_filtrado["PROTEINA"].isin(proteinas_validas)
        ]

    # Retornar o cardápio filtrado
    return cardapio_filtrado


##############################################################################################################################################################################

#Captura a entrada do usuário no chat e gera uma resposta
prompt = st.chat_input()

Colunas = ["INGREDIENTES", "OCASIAO", "PROTEINA","GLUTEN"]

Cardapio = gerar_embeddings(Cardapio, Colunas)

if prompt:
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar=avatar_user).write(prompt)

    # Faz uma requisição à API OpenAI para gerar a resposta do assistente
    with st.chat_message("assistant", avatar=avatar_assistent):
        
        try:
            output_estruturado = transformar_input_usuario(st.session_state.messages[-1]["content"])
            input_json = json.loads(output_estruturado) if isinstance(output_estruturado, str) else output_estruturado
            cardapio_estruturado = Filtrar_Cardapio(input_json, Cardapio)
            input_embedding = Embedding(output_estruturado)

            if "embeddings" in cardapio_estruturado.columns:
                cardapio_estruturado["Indicações"] = cardapio_estruturado["embeddings"].apply(lambda x: similaridade_cosseno(input_embedding, x))
                resultados = cardapio_estruturado.sort_values(by="Indicações", ascending=False).reset_index(drop=True)
                st.dataframe(resultados[["PRATO","INGREDIENTES"]].head(10))
                st.write(output_estruturado)
            else:
                st.error("Erro ao gerar embeddings. Verifique se o Cardápio foi processado corretamente.")

            st.session_state.messages.append({"role": "assistant", "content": "Recomendações enviadas!"})

        except Exception as e:
            st.error(f"Erro ao processar recomendação: {e}")
