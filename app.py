import streamlit as st
import pandas as pd
from io import BytesIO
import gender_guesser.detector as gender
from openpyxl.utils import get_column_letter # <- Nova ferramenta para mexer nas colunas

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

# --- INTERFACE DO STREAMLIT ---
st.set_page_config(page_title="Classificador Rápido", page_icon="⚡")
st.title("Descubra o Gênero pelo Nome ⚡")
st.write("Modo Ultra-Rápido Offline ativado.")

aba1, aba2 = st.tabs(["🔍 Consulta Única", "📁 Processar Planilha"])

with aba1:
    nome_digitado = st.text_input("Nome:")
    if st.button("Classificar Único") and nome_digitado:
        res = classificar_genero_rapido(nome_digitado)
        emoji = "👦" if res == "M" else "👧"
        st.success(f"**{nome_digitado.title()}**: {res} {emoji}")

with aba2:
    arq = st.file_uploader("Envie a planilha (.xlsx)", type=["xlsx"])
    if arq:
        df = pd.read_excel(arq)
        if "Nome" in df.columns:
            st.dataframe(df.head(3))
            
            if st.button("Processar Nomes"):
                bar = st.progress(0)
                df["Gênero Identificado"] = df["Nome"].apply(classificar_genero_rapido)
                bar.progress(100)
                st.success("Pronto! Processamento concluído.")
                
                # --- PREPARA O EXCEL COM LARGURA AUTOMÁTICA ---
                saida = BytesIO()
                with pd.ExcelWriter(saida, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Resultados')
                    
                    # Acessa a aba do Excel que acabamos de criar
                    worksheet = writer.sheets['Resultados']
                    
                    # Passa por todas as colunas para ajustar a largura
                    for i, col in enumerate(df.columns):
                        # Calcula o tamanho do maior texto na coluna (ou o título dela)
                        tamanho_maximo = max(df[col].astype(str).map(len).max(), len(str(col)))
                        # Define a largura com uma pequena margem (+ 3 espaços)
                        worksheet.column_dimensions[get_column_letter(i + 1)].width = tamanho_maximo + 3
                
                st.download_button("📥 Baixar Planilha", data=saida.getvalue(), file_name="resultado_formatado.xlsx")
        else:
            st.error("A planilha precisa de uma coluna com o cabeçalho exato 'Nome'.")
