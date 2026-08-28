import streamlit as st
import pandas as pd
from io import BytesIO
import gender_guesser.detector as gender
from openpyxl.utils import get_column_letter
import os
import unicodedata
import re
import streamlit.components.v1 as components

# --- INICIALIZA O MOTOR OFFLINE ---
@st.cache_resource
def carregar_motor_offline():
    return gender.Detector(case_sensitive=False)

detector = carregar_motor_offline()

# --- FUNÇÕES DE BUSCA DE COLUNAS ---
def encontrar_coluna_nome(columns):
    for col in columns:
        col_clean = str(col).strip().upper()
        if col_clean in ["NOME", "NOME COMPLETO", "NOME_COMPLETO", "NOME CLIENTE", "CLIENTE"]:
            return col
    for col in columns:
        if "NOME" in str(col).strip().upper():
            return col
    return None

def encontrar_coluna_cpf(columns):
    for col in columns:
        col_clean = str(col).strip().upper()
        if col_clean in ["CPF", "CPF/CNPJ", "CPF_CNPJ", "DOCUMENTO", "DOC"]:
            return col
    for col in columns:
        if "CPF" in str(col).strip().upper():
            return col
    return None

# --- FUNÇÃO DE HIGIENIZAÇÃO DE NOMES (MAIÚSCULAS) ---
def limpar_nome(nome):
    if not nome or pd.isna(nome):
        return ""
    
    # Remove acentos e cedilhas
    nome_normalizado = unicodedata.normalize('NFD', str(nome))
    nome_sem_acentos = ''.join(c for c in nome_normalizado if unicodedata.category(c) != 'Mn')
    
    # Remove pontuações, traços e caracteres especiais
    nome_limpo = re.sub(r'[^a-zA-Z\s]', '', nome_sem_acentos)
    
    # Espaços simples e em MAIÚSCULAS
    return ' '.join(nome_limpo.split()).upper()

# --- FUNÇÃO DE LIMPEZA DE CPF (SEM PONTOS, TRAÇOS E ZEROS À ESQUERDA) ---
def limpar_cpf(cpf):
    if pd.isna(cpf) or cpf is None:
        return ""
    
    cpf_str = str(cpf).split('.')[0].strip()
    cpf_limpo = re.sub(r'[\.\-]', '', cpf_str)
    return cpf_limpo.lstrip('0')

# --- FUNÇÃO DE CLASSIFICAÇÃO DE GÊNERO ---
def classificar_genero_rapido(nome_completo):
    if not nome_completo or pd.isna(nome_completo):
        return ""
    
    nome_limpo = limpar_nome(nome_completo)
    if not nome_limpo:
        return ""
        
    primeiro_nome = nome_limpo.split()[0].title()
    resultado = detector.get_gender(primeiro_nome)
    
    if resultado in ['male', 'mostly_male']:
        return "M"
    elif resultado in ['female', 'mostly_female']:
        return "F"
    else:
        nome_min = primeiro_nome.lower()
        if nome_min.endswith(('a', 'z', 'y', 'elly', 'ine', 'ane', 'ele', 'ia', 'ce', 'te', 'is')):
            return "F"
        else:
            return "M"

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Processador Inteligente - SulAmérica", 
    page_icon="logo.png" if os.path.exists("logo.png") else "💙", 
    layout="centered"
)

# --- ESTILO CUSTOMIZADO ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #001A3B 0%, #002D62 50%, #0B4B8A 100%);
        background-attachment: fixed;
    }

    html, body, p, span, label, h1, h2, h3, h4, .stMarkdown {
        color: #FFFFFF !important;
        font-size: 18px;
    }
    
    .header-sub {
        color: #E2E8F0 !important;
        font-size: 18px !important;
        margin-bottom: 20px;
    }

    .stTextInput label p, .stFileUploader label p {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }

    .stTextInput input {
        font-size: 18px !important;
        padding: 12px !important;
        background-color: #FFFFFF !important;
        border: 2px solid #CBD5E1 !important;
        color: #0F172A !important;
    }

    button[data-baseweb="tab"] div p, 
    button[data-baseweb="tab"] p, 
    button[data-baseweb="tab"] span {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 3px solid #F37021 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] div p {
        color: #F37021 !important;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] div span {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] div::after {
        content: "Arraste e solte o arquivo aqui";
        font-size: 18px !important;
        font-weight: bold;
        color: #FFFFFF !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 2px dashed #FFFFFF !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        font-size: 0px !important;
        background-color: #F37021 !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 8px 18px !important;
    }
    [data-testid="stFileUploaderDropzone"] button::after {
        content: "Procurar arquivo";
        font-size: 16px !important;
        font-weight: bold;
        display: block;
        color: #FFFFFF !important;
    }

    .stButton>button {
        background-color: #F37021;
        border-radius: 8px;
        padding: 12px 28px;
        border: none;
        box-shadow: 0 4px 6px rgba(243, 112, 33, 0.3);
    }
    .stButton>button div p {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }
    .stButton>button:hover {
        background-color: #D95B0F;
        transform: translateY(-2px);
    }
    
    .stDownloadButton>button {
        background-color: #002D62;
        border-radius: 8px;
        padding: 12px 28px;
    }
    .stDownloadButton>button div p {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }

    .header-title {
        font-size: 34px !important;
        font-weight: 800;
        color: #F37021 !important;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho com Logo
col_logo, col_titulo = st.columns([1.2, 2.8])

with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=160)

with col_titulo:
    st.markdown('<p class="header-title">Processador de Dados</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-sub">Higienização de Nome/CPF e Classificação de Gênero Unificadas.</p>', unsafe_allow_html=True)

st.divider()

# --- ABAS DO SISTEMA ---
aba1, aba2 = st.tabs(["🔍 Consulta Única", "📁 Processamento Unificado (Excel)"])

with aba1:
    st.markdown("### Processamento Individual")
    
    c1, c2 = st.columns(2)
    with c1:
        nome_input = st.text_input("Nome do cliente:", key="input_unico_nome")
    with c2:
        cpf_input = st.text_input("CPF do cliente:", key="input_unico_cpf")
        
    if st.button("⚡ Processar Cliente") and (nome_input or cpf_input):
        nome_limpo = limpar_nome(nome_input) if nome_input else "-"
        cpf_limpo = limpar_cpf(cpf_input) if cpf_input else "-"
        genero = classificar_genero_rapido(nome_input) if nome_input else "-"
        
        emoji = "👨‍💼 Masculino (M)" if genero == "M" else ("👩‍💼 Feminino (F)" if genero == "F" else "-")
        
        st.markdown(f"""
            <div style="padding: 24px; margin-top: 18px; border-radius: 12px; background-color: #EFF6FF; border: 2px solid #002D62; border-left: 10px solid #002D62; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                <p style="margin:0; font-size: 18px; color: #002D62 !important;"><b>Nome Higienizado:</b> {nome_limpo}</p>
                <p style="margin:8px 0 0 0; font-size: 18px; color: #002D62 !important;"><b>CPF Higienizado (Geral):</b> {cpf_limpo}</p>
                <p style="margin:8px 0 0 0; font-size: 20px; font-weight: bold; color: #F37021 !important;"><b>Gênero Identificado:</b> {emoji}</p>
            </div>
        """, unsafe_allow_html=True)

with aba2:
    st.markdown("### Carregue sua planilha completa")
    st.write("O sistema irá higienizar o Nome, tratar o CPF (Geral/Sem zeros), identificar o Gênero e remover as colunas antigas.")
    
    arq = st.file_uploader("", type=["xlsx"], key="uploader_unificado")
    
    if arq:
        df_bruto = pd.read_excel(arq, dtype=str)
        col_nome = encontrar_coluna_nome(df_bruto.columns)
        col_cpf = encontrar_coluna_cpf(df_bruto.columns)
        
        if col_nome or col_cpf:
            st.write(f"📋 **Colunas identificadas:** Nome = `{col_nome}` | CPF = `{col_cpf}`")
            st.dataframe(df_bruto.head(3), use_container_width=True)
            
            if st.button("🚀 Processar e Higienizar Tudo"):
                with st.spinner("Higienizando dados e identificando gênero..."):
                    df_final = pd.DataFrame()
                    
                    if col_nome:
                        df_final["Nome"] = df_bruto[col_nome].apply(limpar_nome)
                        df_final["Gênero Identificado"] = df_bruto[col_nome].apply(classificar_genero_rapido)
                    if col_cpf:
                        df_final["CPF"] = df_bruto[col_cpf].apply(limpar_cpf)
                
                st.success("✅ Processamento e Higienização concluídos com sucesso!")
                st.snow()
                components.html("""
                    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.min.js"></script>
                    <script>
                        confetti({
                            particleCount: 50,
                            spread: 60,
                            origin: { y: 0.7 },
                            colors: ['#F37021', '#002D62', '#FFFFFF']
                        });
                    </script>
                """, height=0)
                
                st.divider()
                st.write("📊 **Resumo dos Dados:**")
                
                total = len(df_final)
                total_m = (df_final["Gênero Identificado"] == "M").sum() if "Gênero Identificado" in df_final.columns else 0
                total_f = (df_final["Gênero Identificado"] == "F").sum() if "Gênero Identificado" in df_final.columns else 0
                
                colA, colB, colC = st.columns(3)
                colA.metric("Total de Linhas", total)
                colB.metric("Masculino (M)", total_m)
                colC.metric("Feminino (F)", total_f)
                
                st.divider()
                st.dataframe(df_final.head(5), use_container_width=True)
                
                saida_unificada = BytesIO()
                with pd.ExcelWriter(saida_unificada, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False, sheet_name='Base_Tratada')
                    worksheet = writer.sheets['Base_Tratada']
                    
                    for i, col in enumerate(df_final.columns):
                        tamanho_maximo = max(df_final[col].astype(str).map(len).max(), len(str(col)))
                        worksheet.column_dimensions[get_column_letter(i + 1)].width = tamanho_maximo + 3
                        
                        # Formatação Geral para todas as células
                        for cell in worksheet[get_column_letter(i + 1)]:
                            cell.number_format = 'General'
                
                st.download_button("📥 Baixar Planilha Final Higienizada", data=saida_unificada.getvalue(), file_name="base_trabalhada.xlsx")
        else:
            st.error("⚠️ Nenhuma coluna válida de Nome ou CPF foi identificada na planilha.")
