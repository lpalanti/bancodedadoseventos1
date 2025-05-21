import streamlit as st
import pandas as pd
import re
import json
import requests
import base64

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker

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

/* Toast customization */
.st-emotion-cache-1n6lq0l {
    background-color: #4CAF50 !important;
    color: white !important;
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

# Configuração do banco de dados PostgreSQL usando a URL fornecida do Heroku
DATABASE_URL = "postgresql://u4d0g10bap3vp2:pb779825107188fe08afab88c6451add2551c6b9b7efa685cf2a29d1cf86d12bf@ccpa7stkruda3o.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/db6jbtlveansek"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Definir a tabela do banco de dados
class Fornecedor(Base):
    __tablename__ = 'fornecedores'
    
    id = Column(Integer, primary_key=True)
    nome_fantasia = Column(String(100))
    razao_social = Column(String(100))
    cnpj = Column(String(18))
    email = Column(String(100))
    telefone = Column(String(20))
    categoria = Column(String(50))
    tags = Column(Text)
    resumo_escopo = Column(Text)
    instagram = Column(String(100))
    facebook = Column(String(100))
    linkedin = Column(String(100))

# Criar as tabelas no banco de dados, se não existirem
Base.metadata.create_all(engine)

# Função para validar o CNPJ
def validar_cnpj(cnpj):
    padrao = r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$"
    return re.match(padrao, cnpj) is not None

# Função para salvar o fornecedor no banco de dados
def salvar_fornecedor(dados):
    try:
        # Criar uma sessão com o banco de dados
        session = Session()
        
        # Criar o novo fornecedor
        novo_fornecedor = Fornecedor(
            nome_fantasia=dados['nome_fantasia'],
            razao_social=dados['razao_social'],
            cnpj=dados['cnpj'],
            email=dados['email'],
            telefone=dados['telefone'],
            categoria=dados['categoria'],
            tags=dados['tags'],
            resumo_escopo=dados['resumo_escopo'],
            instagram=dados['instagram'],
            facebook=dados['facebook'],
            linkedin=dados['linkedin']
        )
        
        # Adicionar e salvar no banco de dados
        session.add(novo_fornecedor)
        session.commit()
        
        # Fechar a sessão
        session.close()
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {str(e)}")
        return False

# Função para enviar o arquivo para o GitHub
def upload_to_github(file_path, github_token, repo_name, branch="main"):
    # Carregar o arquivo CSV
    with open(file_path, "rb") as f:
        file_content = f.read()

    # Codifica o conteúdo do arquivo em base64
    file_content_b64 = base64.b64encode(file_content).decode('utf-8')

    # URL da API para enviar o arquivo para o repositório
    api_url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"

    # Obtenha o SHA se o arquivo já existir
    headers = {
        "Authorization": f"token {github_token}"
    }
    
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        sha = file_info['sha']
    else:
        sha = None

    # Dados do commit
    commit_data = {
        "message": "Atualizando o arquivo fornecedores.csv",
        "content": file_content_b64,
        "branch": branch
    }
    
    if sha:
        commit_data["sha"] = sha

    # Enviar o arquivo para o GitHub
    response = requests.put(api_url, headers=headers, data=json.dumps(commit_data))

    if response.status_code == 201 or response.status_code == 200:
        st.success("Arquivo atualizado no GitHub com sucesso!")
    else:
        st.error(f"Erro ao atualizar o arquivo: {response.status_code} - {response.text}")

# Interface principal
st.title("📁 Banco de Fornecedores para Eventos")

aba1, aba2 = st.tabs(["Buscar Fornecedores", "Cadastrar Novo Fornecedor"])

with aba1:
    st.header("Busca de Fornecedores")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        categoria_filtro = st.selectbox(
            "Selecione a Categoria",
            options=["TODAS"] + list(categorias_tags.keys()),
            index=0
        )
        
        if categoria_filtro != "TODAS":
            tags_disponiveis = categorias_tags[categoria_filtro]
        else:
            tags_disponiveis = []
            for cat in categorias_tags.values():
                tags_disponiveis.extend(cat)
            tags_disponiveis = sorted(list(set(tags_disponiveis)))
            
        tags_filtro = st.multiselect(
            "Filtrar por Tags",
            options=tags_disponiveis
        )

    with col2:
        # Consultar o banco de dados PostgreSQL
        session = Session()
        if categoria_filtro != "TODAS":
            fornecedores = session.query(Fornecedor).filter_by(categoria=categoria_filtro).all()
        else:
            fornecedores = session.query(Fornecedor).all()
        
        if fornecedores:
            st.write(f"**Fornecedores encontrados:** {len(fornecedores)}")
            for fornecedor in fornecedores:
                with st.expander(f"{fornecedor.nome_fantasia} - {fornecedor.categoria}", expanded=False):
                    st.markdown(f"""
                    **Razão Social:** {fornecedor.razao_social}  
                    **CNPJ:** {fornecedor.cnpj}  
                    **Contato:** {fornecedor.telefone} | {fornecedor.email}  
                    **Tags:** {fornecedor.tags}  
                    **Escopo do Serviço:**  
                    {fornecedor.resumo_escopo}  
                    **Redes Sociais:**  
                    {', '.join(filter(None, [fornecedor.instagram, fornecedor.facebook, fornecedor.linkedin]))}
                    """)
        else:
            st.info("Nenhum fornecedor cadastrado ainda")
        
        session.close()

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
        
        submitted = st.form_submit_button("Cadastrar Fornecedor")
        
        if submitted:
            erros = []
            
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
                    st.toast(f"❌ {erro}", icon="⚠️")
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
                    st.toast("✅ Fornecedor cadastrado com sucesso!", icon="🎉")
                    st.balloons()

                    # Salvar e enviar o CSV para o GitHub
                    # Gerar o CSV
                    fornecedores_df = pd.DataFrame([{
                        'nome_fantasia': dados['nome_fantasia'],
                        'razao_social': dados['razao_social'],
                        'cnpj': dados['cnpj'],
                        'email': dados['email'],
                        'telefone': dados['telefone'],
                        'categoria': dados['categoria'],
                        'tags': dados['tags'],
                        'resumo_escopo': dados['resumo_escopo'],
                        'instagram': dados['instagram'],
                        'facebook': dados['facebook'],
                        'linkedin': dados['linkedin']
                    }])
                    fornecedores_df.to_csv("fornecedores.csv", index=False)

                    # Chamar função para fazer upload do CSV para o GitHub
                    upload_to_github(
                        'fornecedores.csv',
                        github_token="ithub_pat_11BRRDQHA0ispg8koxszxD_tAjrwNBvo7aGAjVrglawkSeDUJBJIo7kv0bj4eLCECtY2MPGTXHztplVavE",
                        repo_name="nome_do_repositorio"
                    )

                else:
                    st.toast("❌ Erro ao salvar no banco de dados", icon="⚠️")
