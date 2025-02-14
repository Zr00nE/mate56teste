import streamlit as st
from openai import OpenAI
import numpy as np
import pandas as pd
import re
import openpyxl
from unidecode import unidecode


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
    Transforme o seguinte pedido do usuário em uma descrição estruturada, clara e organizada, com foco em garantir que os itens proibidos e os ingredientes desejados sejam identificados de forma precisa
    normalize os texto deixe-os com letra minuscula e sem acentos:

    Pedido: "{input_usuario}"

    ### **Formato de saída esperado:**  
    - Ingredientes desejados: [Lista de ingredientes específicos que o usuário quer, apenas ingredientes comestíveis; caso não haja, retorne vazio: []]  
    - Ingredientes proibidos: [Lista de ingredientes que o usuário não quer, tem alergia ou não gosta, incluindo variações do nome do alimento. 
      Exemplo: cebola deve incluir cebola roxa, cebola caramelizada, cebola branca, cebolinha; caso não haja, retorne vazio: []]  
    - Proteína desejada: [Tipo de proteína mencionada; deve ser obrigatoriamente "Vegano", "Vegetariano" ou "Carnivoro"; se não especificado, retorne "Carnivoro"]  
    - Ocasião: [jantar, almoço, lanche, café da manhã, etc.; caso não seja mencionado, retorne "não mencionada"]  
    - Preferências adicionais: [Qualquer outra observação relevante; caso não haja, retorne "nenhuma"]  

    ### **Considerações Especiais:**
    - Se o usuário mencionar "apimentado", inclua ingredientes como pimenta, pimentão, pimenta-do-reino, pimenta malagueta, etc.
    - Se o usuário mencionar "frutos do mar ou peixes", inclua ingredientes como camarão, polvo, mexilhões, lula, ostras, tipos de peixe como Atum, Tilapia, Salmao, inclua tambem o temo peixe etc.
    - Se o usuario mencionar "carne de algo", inclua ingredientes apenas esse algo.
    - Se o usuário mencionar "lactose", inclua ingredientes como leite, queijo, manteiga, creme de leite, iogurte, etc.
    - Para usuários veganos, exclua automaticamente ingredientes como carne, peixe, laticínios, ovos, mel, etc.
    - Para usuários vegetarianos, exclua automaticamente ingredientes como carne e peixe, mas permita laticínios e ovos.
    - Normalize todos os ingredientes (remova acentos e til, converta para minúsculas, etc.) para garantir compatibilidade com a função de filtro.
    - Adicione o plural de alguns ingredientes se necessario

    ### **Exemplos de Entrada e Saída:**

    **Exemplo 1:**
    - Entrada: "Quero algo vegano para o jantar, sem cebola e com abacate."
    - Saída:
      - Ingredientes desejados: [abacate]
      - Ingredientes proibidos: [cebola, cebola roxa, cebola caramelizada, cebola branca, cebolinha]
      - Proteína desejada: [Vegano]
      - Ocasião: [jantar]
      - Preferências adicionais: [nenhuma]

    **Exemplo 2:**
    - Entrada: "Estou procurando um prato com frango e sem glúten."
    - Saída:
      - Ingredientes desejados: [frango]
      - Ingredientes proibidos: [glúten, trigo, cevada, centeio]
      - Proteína desejada: [Carnivoro]
      - Ocasião: [não mencionada]
      - Preferências adicionais: [sem glúten]

    **Exemplo 3:**
    - Entrada: "Algo leve para o almoço, com quinoa e sem lactose."
    - Saída:
      - Ingredientes desejados: [quinoa]
      - Ingredientes proibidos: [lactose, leite, queijo, manteiga]
      - Proteína desejada: [Vegano]
      - Ocasião: [almoço]
      - Preferências adicionais: [leve]
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

import re

def normalizar_ingredientes(ingredientes):
    """
    Normaliza os ingredientes para um formato consistente.
    """
    ingredientes = ingredientes.lower()  # Converte para minúsculas
    ingredientes = ingredientes.strip()  # Remove espaços extras
    ingredientes = unidecode(ingredientes) 
    return ingredientes

def Filtrar_Cardapio(output_estruturado, cardapio):
    """
    Filtra o cardápio com base no output estruturado do GPT.
    """
    # Normaliza os ingredientes no cardápio
    cardapio['INGREDIENTES'] = cardapio['INGREDIENTES'].apply(normalizar_ingredientes)

    # Extrair ingredientes proibidos e normalizar
    proibidos_match = re.search(r"- Ingredientes proibidos: \[(.*?)\]", output_estruturado)
    proibidos = proibidos_match.group(1).split(", ") if proibidos_match else []
    proibidos = [normalizar_ingredientes(p) for p in proibidos if p.strip()]

    # Extrair ingredientes desejados e normalizar
    desejados_match = re.search(r"- Ingredientes desejados: \[(.*?)\]", output_estruturado)
    desejados = desejados_match.group(1).split(", ") if desejados_match else []
    desejados = [normalizar_ingredientes(d) for d in desejados if d.strip()]

    # Extrair tipo de proteína desejada
    proteina_match = re.search(r"- Proteína desejada:\s*\[(.*?)\]", output_estruturado)
    tipo_proteina = proteina_match.group(1).strip().lower() if proteina_match else None

    # Função para verificar se o item contém ingredientes proibidos
    def contem_proibidos(ingredientes):
        if not proibidos:
            return False
        ingredientes_lista = [normalizar_ingredientes(ing) for ing in re.split(r",\s*", ingredientes)]
        # Verifica se algum ingrediente proibido está contido nos ingredientes do prato
        return any(any(proibido in ingrediente for ingrediente in ingredientes_lista) for proibido in proibidos) 

    # Função para verificar se o item contém ingredientes desejados
    def contem_desejados(ingredientes):
        if not desejados:
            return True
        ingredientes_lista = [normalizar_ingredientes(ing) for ing in re.split(r",\s*", ingredientes)]
        return any(ingrediente in ingredientes_lista for ingrediente in desejados)

    # Garantir que o DataFrame não seja filtrado incorretamente
    cardapio_filtrado = cardapio.copy()

    if proibidos:
        cardapio_filtrado = cardapio_filtrado[~cardapio_filtrado['INGREDIENTES'].apply(contem_proibidos)]

    if desejados:
        cardapio_filtrado = cardapio_filtrado[cardapio_filtrado['INGREDIENTES'].apply(contem_desejados)]

    if tipo_proteina and tipo_proteina in ["vegano", "vegetariano", "carnivoro"]:
        cardapio_filtrado = cardapio_filtrado[cardapio_filtrado['PROTEINA'].str.lower() == tipo_proteina]

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
                #st.write(output_estruturado)
            else:
                st.error("Erro ao gerar embeddings. Verifique se o Cardápio foi processado corretamente.")

            st.session_state.messages.append({"role": "assistant", "content": "Recomendações enviadas!"})

        except Exception as e:
            st.error(f"Erro ao processar recomendação: {e}")
