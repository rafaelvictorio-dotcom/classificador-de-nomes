import streamlit as st
import pandas as pd
from io import BytesIO
import gender_guesser.detector as gender

# --- INICIALIZA O MOTOR OFFLINE ---
# O cache impede que ele recarregue o dicionário toda vez que você clica em um botão
@st.cache_resource
def carregar_motor_offline():
    return gender.Detector(case_sensitive=False)

detector = carregar_motor_offline()

def classificar_genero_rapido(nome_completo):
    if not nome_completo or pd.isna(nome_completo):
        return ""
    
    # Pega o primeiro nome e capitaliza (ex: MARIA -> Maria)
    primeiro_nome = str(nome_completo).strip().split()[0].title()
    
    # Busca na biblioteca offline
    resultado = detector.get_gender(primeiro_nome)
    
    # Converte o resultado gringo para M ou F
    if resultado in ['male', 'mostly_male']:
        return "M"
    elif resultado in ['female', 'mostly_female']:
        return "F"
    else:
        # Se a biblioteca não conhecer o nome, usa a regra brasileira da última letra
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
                # Barra de progresso visual (vai ser tão rápido que talvez você mal veja carregar)
                bar = st.progress(0)
                
                # Aplica a regra em todos os nomes instantaneamente
                df["Gênero Identificado"] = df["Nome"].apply(classificar_genero_rapido)
                
                bar.progress(100)
                st.success("Pronto! Processamento concluído em menos de 1 segundo.")
                
                saida = BytesIO()
                with pd.ExcelWriter(saida, engine='openpyxl') as w:
                    df.to_excel(w, index=False)
                
                st.download_button("📥 Baixar Planilha", data=saida.getvalue(), file_name="resultado_rapido.xlsx")
        else:
            st.error("A planilha precisa de uma coluna com o cabeçalho exato 'Nome'.")
