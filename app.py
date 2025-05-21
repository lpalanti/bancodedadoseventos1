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

/* Labels mais visíveis */
label p {
    color: #333333 !important;
    font-weight: bold !important;
}

/* Campos de entrada com texto branco */
div[data-baseweb="input"] input,
div[data-baseweb="select"] select,
div[data-baseweb="textarea"] textarea {
    color: #FFFFFF !important;
    background-color: #666666 !important;
}

.stMultiSelect [data-baseweb="tag"] {
    color: #FFFFFF !important;
    background-color: #444444 !important;
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

# Funções principais (mantidas as mesmas)
def validar_cnpj(cnpj):
    padrao = r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$"
    return re.match(padrao, cnpj) is not None

def salvar_fornecedor(dados):
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("lpalanti/bancodedadoseventos1")
        contents = repo.get_contents("fornecedores.csv")
        
        # Converter dados para linha CSV
        campos = [
            dados['nome_fantasia'],
            dados['razao_social'],
            dados['cnpj'],
            dados['email'],
            dados['telefone'],
            dados['categoria'],
            dados['tags'],
            dados['resumo_escopo'],
            dados['instagram'],
            dados['facebook'],
            dados['linkedin']
        ]
        novo_registro = ','.join(f'"{value}"' for value in campos)
        novos_dados = contents.decoded_content.decode() + f"\n{novo_registro}"
        
        # Fazer commit
        repo.update_file(
            path=contents.path,
            message=f"Adicionar fornecedor: {dados['nome_fantasia']}",
            content=novos_dados,
            sha=contents.sha
        )
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {str(e)}")
        return False

# Interface principal
st.title("📁 Banco de Fornecedores para Eventos")

aba1, aba2 = st.tabs(["Buscar Fornecedores", "Cadastrar Novo Fornecedor"])

with aba1:
    # (Mantido igual ao anterior)

with aba2:
    st.header("Cadastro de Novo Fornecedor")
    
    with st.form(key='form_cadastro'):
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Dados Obrigatórios", divider='gray')
            nome_fantasia = st.text_input("Nome Fantasia*", help="Nome comercial da empresa")
            razao_social = st.text_input("Razão Social*", help="Nome jurídico completo")
            cnpj = st.text_input("CNPJ* (formato: XX.XXX.XXX/XXXX-XX)", help="Exemplo: 12.345.678/0001-99")
            email = st.text_input("E-mail*", help="E-mail corporativo")
            telefone = st.text_input("Telefone*", help="Telefone com DDD")
            categoria = st.selectbox(
                "Categoria do Serviço*",
                options=list(categorias_tags.keys()),
                help="Selecione a categoria principal"
            )
            
            tags_selecionadas = st.multiselect(
                "Tags* (Selecione pelo menos uma)",
                options=categorias_tags[categoria],
                help="Selecione as tags relacionadas"
            )
            
            resumo_escopo = st.text_area(
                "Resumo do Escopo do Serviço* (mínimo 20 caracteres)",
                height=100,
                help="Descreva resumidamente o serviço oferecido"
            )
        
        with c2:
            st.subheader("Dados Opcionais", divider='gray')
            instagram = st.text_input("Instagram (@usuario)", help="Perfil no Instagram")
            facebook = st.text_input("Facebook (URL ou nome)", help="Página no Facebook")
            linkedin = st.text_input("LinkedIn (URL)", help="Perfil no LinkedIn")
        
        if st.form_submit_button("Cadastrar Fornecedor"):
            erros = []
            
            # Validação de campos obrigatórios
            campos_obrigatorios = {
                "Nome Fantasia": nome_fantasia,
                "Razão Social": razao_social,
                "CNPJ": cnpj,
                "E-mail": email,
                "Telefone": telefone,
                "Tags": tags_selecionadas,
                "Resumo do Escopo": resumo_escopo
            }
            
            for campo, valor in campos_obrigatorios.items():
                if not valor:
                    erros.append(f"Campo obrigatório faltando: {campo}")
            
            if not validar_cnpj(cnpj):
                erros.append("Formato de CNPJ inválido")
            
            if len(resumo_escopo) < 20:
                erros.append("Resumo do escopo muito curto (mínimo 20 caracteres)")
            
            if erros:
                for erro in erros:
                    st.error(erro)
            else:
                dados = {
                    'nome_fantasia': nome_fantasia.strip(),
                    'razao_social': razao_social.strip(),
                    'cnpj': cnpj.strip(),
                    'email': email.strip(),
                    'telefone': telefone.strip(),
                    'categoria': categoria,
                    'tags': ", ".join(tags_selecionadas),
                    'resumo_escopo': resumo_escopo.strip(),
                    'instagram': instagram.strip(),
                    'facebook': facebook.strip(),
                    'linkedin': linkedin.strip()
                }
                
                if salvar_fornecedor(dados):
                    st.success("Fornecedor cadastrado com sucesso!")
                    st.balloons()
                else:
                    st.error("Erro ao salvar no banco de dados")
