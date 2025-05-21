import streamlit as st
import pandas as pd
import re
import json
from github import Github

# Configuração da página
st.set_page_config(
    page_title="Banco de Fornecedores para Eventos",
    page_icon="📁",
    layout="wide"
)

# CSS Customizado
st.markdown("""
<style>
.stApp {
    background-color: #FFFFFF !important;
    color: #000000 !important;
}
[data-testid="stHeader"] {
    background-color: #F0F2F6;
}
.st-b7 {
    color: #000000;
}
</style>
""", unsafe_allow_html=True)

# Carregar categorias e tags
try:
    with open("categorias_tags.json") as f:
        categorias_tags = json.load(f)
except FileNotFoundError:
    st.error("Arquivo categorias_tags.json não encontrado!")
    st.stop()

# Funções principais
def validar_cnpj(cnpj):
    padrao = r
