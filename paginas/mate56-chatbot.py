import streamlit as st
from openai import OpenAI
import numpy as np
import pandas as pd
import re
import openpyxl


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

def transformar_input_usuario(input_usuario):
    """
    Usa GPT para transformar o input do usuário em um formato estruturado.
    
    :param input_usuario: Texto original do usuário.
    :return: Texto estruturado para melhor entendimento do embedding.
    """
    prompt = f"""
    Transforme o seguinte pedido do usuário em um formato estruturado, garantindo que os ingredientes proibidos, desejados e as preferências sejam corretamente identificadas.  

Caso o usuário esteja pedindo uma recomendação genérica, defina um estilo de recomendação apropriado.  

### **Entrada:**  
Pedido: "{input_usuario}"  

    ### **Formato de saída esperado:**  
    - **Tipo de Requisição:** ["Ingredientes específicos", "Estilo culinário", "Ocasião", "Sugestão genérica", "Ingredientes disponíveis"]  
      - "Ingredientes específicos" → O usuário mencionou ingredientes que deseja ou quer evitar.  
      - "Estilo culinário" → O usuário mencionou um estilo de comida (ex.: mexicana, italiana, japonesa).  
      - "Ocasião" → O usuário mencionou uma refeição específica (ex.: almoço, jantar, lanche).  
      - "Sugestão genérica" → O usuário quer apenas recomendações sem restrições específicas.  
      - "Ingredientes disponíveis" → O usuário quer recomendações baseadas no que ele tem na cozinha.  
    
    - **Ingredientes desejados:** [Lista dos ingredientes específicos mencionados pelo usuário; se não houver, retorne `[]`.]  
    - **Ingredientes proibidos:** [Lista dos ingredientes que o usuário quer evitar (incluindo sinônimos e variações); se não houver, retorne `[]`.]  
    - **Proteína desejada:** ["Vegano", "Vegetariano", "Carnívoro"; se não especificado, retorne `"Carnívoro"`.]  
    - **Estilo culinário:** [Mexicana, Italiana, Japonesa, Brasileira, etc.; se não mencionado, retorne `"Não mencionado"`.]  
    - **Ocasião:** [Jantar, Almoço, Lanche, Café da manhã, etc.; se não mencionado, retorne `"Não mencionada"`.]  
    - **Ingredientes disponíveis:** [Se o usuário mencionou o que tem em casa, liste aqui; se não, retorne `[]`.]  
    - **Preferências adicionais:** [Outros detalhes relevantes, como nível de picância, restrições alimentares, modo de preparo, etc.; se não houver, retorne `"Nenhuma"`.]  
    
    Se necessário, interprete o contexto para preencher informações ausentes.  
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente que organiza pedidos de comida de forma clara e estruturada."},
            {"role": "user", "content": prompt}
        ]
    )
    resposta = response.choices[0].message.content
    return resposta

def Embedding(texto):
    response = client.embeddings.create(
        input=texto,
        model="text-embedding-3-small")

    return response.data[0].embedding

def Filtrar_Cardapio(output_estruturado, cardapio):

    import re

import re
def Filtrar_Cardapio(output_estruturado, cardapio):
    # Extrair e normalizar ingredientes proibidos
    proibidos_match = re.search(r"- Ingredientes proibidos: \[(.*?)\]", output_estruturado)
    proibidos = proibidos_match.group(1).split(", ") if proibidos_match else []
    proibidos = [p.strip().lower() for p in proibidos if p.strip()]

    # Extrair e normalizar ingredientes desejados
    desejados_match = re.search(r"- Ingredientes desejados: \[(.*?)\]", output_estruturado)
    desejados = desejados_match.group(1).split(", ") if desejados_match else []
    desejados = [d.strip().lower() for d in desejados if d.strip()]

    # Extrair tipo de proteína desejada
    proteina_match = re.search(r"- Proteína desejada:\s*\[(.*?)\]", output_estruturado)
    tipo_proteina = proteina_match.group(1).strip().title() if proteina_match else None

    # Normalizar ingredientes do cardápio
    cardapio["INGREDIENTES"] = cardapio["INGREDIENTES"].apply(lambda x: [ing.strip().lower() for ing in re.split(r",\s*", x)])

    # Função para verificar se um item contém ingredientes proibidos (inclui substrings)
    def contem_proibidos(ingredientes):
        return any(any(p in ing for ing in ingredientes) for p in proibidos)

    # Função para verificar se um item contém ingredientes desejados (inclui substrings)
    def contem_desejados(ingredientes):
        return any(any(d in ing for ing in ingredientes) for d in desejados)

    # Criar uma cópia do cardápio para filtrar
    cardapio_filtrado = cardapio.copy()

    # Remover pratos com ingredientes proibidos
    if proibidos:
        cardapio_filtrado = cardapio_filtrado[~cardapio_filtrado["INGREDIENTES"].apply(contem_proibidos)]

    # Aplicar o filtro de desejados apenas se houver ingredientes válidos no dataset
    ingredientes_existentes = set(ing for lista in cardapio_filtrado["INGREDIENTES"] for ing in lista)
    desejados_validos = [d for d in desejados if any(d in ing for ing in ingredientes_existentes)]

    if desejados_validos:
        cardapio_filtrado = cardapio_filtrado[cardapio_filtrado["INGREDIENTES"].apply(contem_desejados)]

    # Ajustar a filtragem de proteínas para aceitar variações de nome
    proteina_mapeamento = {
        "Carnívoro": ["Carnívoro", "Carne", "Frango", "Bovina", "Suína"],
        "Vegetariano": ["Vegetariano", "Ovo-Lacto", "Ovolactovegetariano"],
        "Vegano": ["Vegano", "100% Vegetal"]
    }

    if tipo_proteina in proteina_mapeamento:
        proteinas_validas = proteina_mapeamento[tipo_proteina]
        cardapio_filtrado = cardapio_filtrado[
            cardapio_filtrado["PROTEINA"].str.title().isin(proteinas_validas)
        ]

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
            cardapio_estruturado = Filtrar_Cardapio(output_estruturado, Cardapio)
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
