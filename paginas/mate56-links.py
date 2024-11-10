import streamlit as st
  
st.title('🔗 Links')  
st.write('Segue uma seleção de canais e vídeos no YouTube que eu entendo que são conteúdos que vocês, meus alunos queridos, deveriam assistir.')
st.divider()
 
st.subheader('Canais do YouTube')


st.write("**Canal do Sandeco**") 
st.video("https://youtu.be/GA2m-1m4zxk?si=gVcsvA_cwTumBwBt") 
st.write("Sandeco é professor na federal de Goias e grande pesquisador e entusiasta na área de IA. Tem MUITO conteúdo legal no canal dele.")

st.write("**Canal do Guanabara**") 
st.video("https://www.youtube.com/watch?v=jQMbuK6URws&list=PLHz_AreHm4dm24MhlWJYiR_Rm7TFtvs6S") 
st.write("Guanabara	é um grande professor do YouTube, com muito conteúdo em tecnologia. Recentemente tem soltado videos nessa playlist de IA. Os vídeos são para pessoas BEMM iniciantes. Esse é o perfil dele. Algumas pessoas podem achar um pouco devagar as aulas. No entanto, o conteúdo é muito bom. ")


st.divider()
 


st.subheader('Vídeos')

st.write("Vídeo: **Por que você não deveria CONFIAR em IAs**") 
col1, col2 = st.columns([2,1])
with col1: 
	st.video("https://youtu.be/-3VK7qF-6dY?si=s4UU8QQs74ycmPnV")     
with col2:
	st.write("Muitos bons conselhos sobre quando IA deve ser usada e quando não deve. Muito atencioso aos detalhes. Gostei muito desse vídeo.")



st.write("Vídeo: **ChatGPT: 30 Year History | How AI Learned to Talk**") 
col1, col2 = st.columns([2,1])
with col1: 
	st.video("https://youtu.be/OFS90-FX6pg?si=T4A-_pF6H18-52M9")     
with col2:
	st.write("Um excelente mini documentário sobre os modelos de linguagem. Vale a pena conferir.")



st.write("Vídeo: **How Intelligence Evolved | A 600 million year story.**") 
col1, col2 = st.columns([2,1])
with col1: 
	st.video("https://www.youtube.com/watch?v=5EcQ1IcEMFQ")     
with col2:
	st.write("Mais um mini documentário que dá alguns insights sobre o próprio entendimento do que é inteligência e suas adaptações computacionais.")




st.write("Vídeo: **How large language models work, a visual intro to transformers.**") 
col1, col2 = st.columns([2,1])
with col1: 
	st.video("https://youtu.be/wjZofJX0v4M?si=9bLsaTuLR30d55mR")     
with col2:
	st.write("Video de um canal bem famoso por fazer excelentes visualizações de conceitos matemáticos. Bem legal para se ter uma ideia de como os grandes modelos de linguagem funcionam.")


 
 


st.write("Vídeo: **Attention in transformers, visually explained.**") 
col1, col2 = st.columns([2,1])
with col1: 
	st.video("https://youtu.be/eMlx5fFNoYc?si=a1yuKvO4bQy3GeyP")     
with col2:
	st.write("A sequência do vídeo anterior, dando enfoque no funcionamento do mecânismo de atenção, que faz parte da rede a qual o ChatGPT foi criada.")


 
 
