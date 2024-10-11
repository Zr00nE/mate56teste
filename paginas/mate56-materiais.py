import streamlit as st
  
st.title('📚 Materiais')   

git = 'https://github.com/ricardorocha86/mate56'
st.link_button('**📂 Github desse App**', url = git,  help=None, type="primary", disabled=False, use_container_width=False)


st.write('#### Minicurso Python para IA')

colab = 'https://colab.research.google.com/drive/1G55vxN9IL6ASUZ9_7lq3O-7-vjKDduQS?usp=sharing'
st.link_button('**👨‍💻 Script Minicurso Python para IA**', url = colab,  help=None, type="primary", disabled=False, use_container_width=False)


st.write('#### Aula 1 - 04/10/2024')
c1, c2 = st.columns(2)

with c1:
	colab = 'https://colab.research.google.com/drive/1kvNAWirEsw20pr3qMicVDCKUvv5JbXyg?usp=sharing'
	st.link_button('**👨‍💻 Script Google Colab**', url = colab,  help=None, type="primary", disabled=False, use_container_width=True)

with c2:
	slides = 'https://colab.research.google.com/drive/19TJ3Vme9w60NY0W58STBnYVUCmREx92q?usp=sharing'
	st.link_button('**👨🏽‍🏫 Slides**', url = slides,  help=None, type="primary", disabled=False, use_container_width=True)
 

st.write('#### Aula 2 - 11/10/2024')
c1, c2 = st.columns(2)

with c1:
	colab = 'https://colab.research.google.com/drive/19TJ3Vme9w60NY0W58STBnYVUCmREx92q?usp=sharing'
	st.link_button('**👨‍💻 Script Google Colab**', url = colab,  help=None, type="primary", disabled=False, use_container_width=True)

with c2:
	slides = 'https://drive.google.com/file/d/12ITiEyXHnSkmNCdPfTNWeLUEBQpHKZbJ/view?usp=sharing'
	st.link_button('**Slides**', url = slides,  help=None, type="primary", disabled=True, use_container_width=True)
