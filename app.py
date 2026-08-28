import streamlit as st
import pandas as pd
from io import BytesIO
import gender_guesser.detector as gender
from openpyxl.utils import get_column_letter

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

# --- SVG VETORIAL OFICIAL DA SULAMÉRICA ---
FAVICON_SULAMERICA = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%20002D62'/%3E%3Cpath d='M30 65 Q 50 55 70 65 Q 50 75 30 65' fill='%23F37021'/%3E%3Ctext x='50' y='50' font-family='Arial, sans-serif' font-weight='bold' font-size='42' fill='white' text-anchor='middle' dominant-baseline='central'%3ES%3C/text%3E%3C/svg%3E"

LOGO_SVG_HTML = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 80" width="180" height="45">
  <path d="M 10 50 Q 30 40 50 50 Q 30 60 10 50" fill="#F37021"/>
  <text x="5" y="38" font-family="'Segoe UI', Helvetica, Arial, sans-serif" font-weight="900" font-size="34" fill="#002D62">SulAmérica</text>
  <text x="5" y="65" font-family="'Segoe UI', Helvetica, Arial, sans-serif" font-weight="600" font-size="16" fill="#F37021" letter-spacing="2">SEGUROS</text>
</svg>
"""

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Classificador - SulAmérica", 
    page_icon=FAVICON_SULAMERICA, 
    layout="centered"
)

# --- ESTILO CUSTOMIZADO (TRADUÇÃO DO FILE UPLOADER & ESTILOS) ---
st.markdown("""
    <style>
    /* Aumento de Fontes Globais */
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    
    /* TRADUÇÃO DO COMPONENTE DE UPLOAD DE ARQUIVOS */
    /* Esconde o texto original "Drag and drop file here" */
    [data-testid="stFileUploaderDropzoneInstructions"] div span {
        display: none !important;
    }
    /* Insere o texto em Português */
    [data-testid="stFileUploaderDropzoneInstructions"] div::after {
        content: "Arraste e solte o arquivo aqui";
        font-size: 18px !important;
        font-weight: bold;
        color: #002D62;
    }
    
    /* Esconde o limite em inglês "Limit 200MB per file • XLSX" */
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        display: none !important;
    }
    
    /* Altera o botão "Browse files" para "Procurar arquivo" */
    [data-testid="stFileUploaderDropzone"] button {
        font-size: 0px !important; /* Esconde texto em inglês */
        background-color: #002D62 !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 8px 18px !important;
    }
    [data-testid="stFileUploaderDropzone"] button::after {
        content: "Procurar arquivo";
        font-size: 16px !important;
        font-weight: bold;
        display: block;
    }

    /* Estilo dos demais Botões */
    .stButton>button {
        background-color: #F37021;
        color: white;
        border-radius: 8px;
        padding: 12px 28px;
        border: none;
        font-weight: bold;
        font-size: 18px !important;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 6px rgba(243, 112, 33, 0.2);
    }
    .stButton>button:hover {
        background-color: #D95B0F;
        color: white;
        border-color: #D95B0F;
        transform: translateY(-2px);
    }
    
    /* Botão de Download */
    .stDownloadButton>button {
        background-color: #002D62;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        font-size: 18px !important;
        padding: 12px 28px;
    }

    /* Títulos Grandes */
    .header-title {
        font-size: 36px !important;
        font-weight: 800;
        color: #002D62;
        margin-bottom: 5px;
    }
    .header-sub {
        font-size: 18px !important;
        color: #555555;
        margin-bottom: 25px;
    }
    
    /* Fontes das Abas */
    button[data-baseweb="tab"] {
        color: #002D62 !important;
        font-size: 20px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO COM LOGO NATIVO DA SULAMÉRICA ---
col_logo, col_titulo = st.columns([1.2, 2.8])

with col_logo:
    st.markdown(LOGO_SVG_HTML, unsafe_allow_html=True)

with col_titulo:
    st.markdown('<p class="header-title">Classificador de Gênero</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-sub">Ferramenta interna para identificação rápida por primeiro nome.</p>', unsafe_allow_html=True)

st.divider()

# --- ABAS DO SISTEMA ---
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
        cor_borda = "#002D62" if res == "M" else "#EC4899"
        cor_fundo = "#EFF6FF" if res == "M" else "#FDF2F8"
        cor_texto = "#1E40AF" if res == "M" else "#BE185D"
        
        st.markdown(f"""
            <div style="padding: 24px; margin-top: 18px; border-radius: 12px; background-color: {cor_fundo}; text-align: center; border-left: 8px solid {cor_borda}; box-shadow: 0 4px 10px rgba(0,0,0,0.06);">
                <h3 style="margin:0; color: #1F2937; font-size: 28px;">{nome_digitado.title()}</h3>
                <p style="font-size: 24px; margin: 10px 0 0 0; font-weight: bold; color: {cor_texto};">{emoji}</p>
            </div>
        """, unsafe_allow_html=True)

with aba2:
    st.markdown("<p style='font-size: 20px; font-weight: bold;'>Carregue seu arquivo clicando em upload</p>", unsafe_allow_html=True)
    
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
                
                # --- DASHBOARD DE RESULTADOS ---
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
                
                # --- PREPARA O EXCEL FORMATADO ---
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
