import streamlit as st
import pandas as pd
from io import BytesIO
import gender_guesser.detector as gender
from openpyxl.utils import get_column_letter
import os

# --- INICIALIZA O MOTOR OFFLINE ---
@st.cache_resource
def carregar_motor_offline():
    return gender.Detector(case_sensitive=False)

detector = carregar_motor_offline()

def classificar_genero_rapido(nome_completo):
    if not nome_completo or pd.isna(nome_completo):
        return ""
    
    primeiro_nome = str(nome_completo).strip().split()[0].title()
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
    page_title="Classificador - SulAmérica", 
    page_icon="logo.png" if os.path.exists("logo.png") else "💙", 
    layout="centered"
)

# --- ESTILO CUSTOMIZADO (FORCE BRANCO NOS TEXTOS CIRCULADOS) ---
st.markdown("""
    <style>
    /* Fundo Gradiente Azul SulAmérica */
    .stApp {
        background: linear-gradient(135deg, #001A3B 0%, #002D62 50%, #0B4B8A 100%);
        background-attachment: fixed;
    }

    /* FORÇA TODOS OS TEXTOS PADRÃO E RÓTULOS PARA BRANCO */
    html, body, p, span, label, h1, h2, h3, h4, .stMarkdown {
        color: #FFFFFF !important;
        font-size: 18px;
    }
    
    /* Subtítulo do topo */
    .header-sub {
        color: #E2E8F0 !important;
        font-size: 18px !important;
        margin-bottom: 20px;
    }

    /* Rótulo "Digite o nome do cliente" e outros labels de campo em Branco */
    .stTextInput label p, .stFileUploader label p {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }

    /* Campo de Texto de Entrada */
    .stTextInput input {
        font-size: 18px !important;
        padding: 12px !important;
        background-color: #FFFFFF !important;
        border: 2px solid #CBD5E1 !important;
        color: #0F172A !important;
    }

    /* TEXTO E ÍCONES DAS ABAS EM BRANCO PURO */
    button[data-baseweb="tab"] div p, 
    button[data-baseweb="tab"] p, 
    button[data-baseweb="tab"] span {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }
    
    /* Aba Selecionada (Laranja com indicador visível) */
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 3px solid #F37021 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] div p {
        color: #F37021 !important; /* Destaque laranja apenas na aba ativa */
    }

    /* TRADUÇÃO E ESTILO DO UPLOAD DE ARQUIVOS */
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

    /* Estilo dos Botões */
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

    /* TÍTULO PRINCIPAL (LARANJA SULAMÉRICA) */
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
    st.markdown('<p class="header-title">Classificador de Gênero</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-sub">Ferramenta interna para identificação rápida por primeiro nome.</p>', unsafe_allow_html=True)

st.divider()

# Abas
aba1, aba2 = st.tabs(["🔍 Consulta Rápida", "📁 Processamento em Lote (Excel)"])

with aba1:
    st.markdown("### Consultar um único nome")
    
    col1, col2 = st.columns([2.8, 1.2])
    with col1:
        nome_digitado = st.text_input("Digite o nome do cliente:")
    with col2:
        st.write("")
        st.write("")
        btn_consultar = st.button("Classificar Único")
        
    if btn_consultar and nome_digitado:
        res = classificar_genero_rapido(nome_digitado)
        
        emoji = "👨‍💼 Masculino (M)" if res == "M" else "👩‍💼 Feminino (F)"
        cor_borda = "#002D62" if res == "M" else "#DB2777"
        cor_fundo = "#EFF6FF" if res == "M" else "#FDF2F8"
        cor_texto = "#1E40AF" if res == "M" else "#9D174D"
        
        st.markdown(f"""
            <div style="padding: 24px; margin-top: 18px; border-radius: 12px; background-color: {cor_fundo}; text-align: center; border: 2px solid {cor_borda}; border-left: 10px solid {cor_borda}; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                <h3 style="margin:0; color: #0F172A !important; font-size: 28px;">{nome_digitado.title()}</h3>
                <p style="font-size: 24px; margin: 10px 0 0 0; font-weight: 800; color: {cor_texto} !important;">{emoji}</p>
            </div>
        """, unsafe_allow_html=True)

with aba2:
    st.markdown("### Carregue seu arquivo clicando em upload")
    
    arq = st.file_uploader("", type=["xlsx"])
    
    if arq:
        df = pd.read_excel(arq)
        
        if "Nome" in df.columns:
            st.write("📋 **Pré-visualização dos dados:**")
            st.dataframe(df.head(3), use_container_width=True)
            
            if st.button("🚀 Processar Todos os Nomes"):
                with st.spinner("Analisando nomes..."):
                    df["Gênero Identificado"] = df["Nome"].apply(classificar_genero_rapido)
                
                st.success("✅ Processamento concluído com sucesso!")
                st.balloons()
                
                st.divider()
                st.write("📊 **Resumo da Classificação:**")
                
                total = len(df)
                total_m = (df["Gênero Identificado"] == "M").sum()
                total_f = (df["Gênero Identificado"] == "F").sum()
                
                colA, colB, colC = st.columns(3)
                colA.metric("Total de Clientes", total)
                colB.metric("Masculino (M)", total_m)
                colC.metric("Feminino (F)", total_f)
                
                st.divider()
                
                saida = BytesIO()
                with pd.ExcelWriter(saida, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Resultados')
                    worksheet = writer.sheets['Resultados']
                    for i, col in enumerate(df.columns):
                        tamanho_maximo = max(df[col].astype(str).map(len).max(), len(str(col)))
                        worksheet.column_dimensions[get_column_letter(i + 1)].width = tamanho_maximo + 3
                
                st.download_button("📥 Baixar Planilha Final Formatada", data=saida.getvalue(), file_name="clientes_classificados.xlsx")
        else:
            st.error("⚠️ A planilha precisa de uma coluna com o cabeçalho exato 'Nome'.")
