import streamlit as st
import requests
import pandas as pd
import time
from io import BytesIO

# --- LÓGICA DO IBGE MODIFICADA ---
def classificar_genero_ibge(nome_completo):
    if not nome_completo or pd.isna(nome_completo):
        return ""
    
    primeiro_nome = str(nome_completo).strip().split()[0].lower()
    
    def obter_frequencia(sexo):
        url = f"https://servicodados.ibge.gov.br/api/v2/censos/nomes/{primeiro_nome}?sexo={sexo}"
        try:
            res = requests.get(url)
            if res.status_code == 200 and res.json():
                return sum(p['frequencia'] for p in res.json()[0]['res'])
        except:
            pass
        return 0
        
    f_m = obter_frequencia('M')
    f_f = obter_frequencia('F')
    total = f_m + f_f
    
    # Regra de desempate / Nome não encontrado
    def palpite_pela_letra(nome):
        if nome.endswith(('a', 'z', 'y', 'elly', 'ine', 'ane', 'ele')):
            return "F"
        return "M"
    
    # Se o nome não existir no IBGE, usa a regra da letra final
    if total == 0:
        return palpite_pela_letra(primeiro_nome)
        
    prob_masc = (f_m / total) * 100
    prob_fem = (f_f / total) * 100
    
    # Retorna estritamente M ou F
    if prob_masc > prob_fem:
        return "M"
    elif prob_fem > prob_masc:
        return "F"
    else:
        return palpite_pela_letra(primeiro_nome)

# --- INTERFACE DO STREAMLIT ---
st.set_page_config(page_title="Classificador", page_icon="🚻")
st.title("Descubra o Gênero pelo Nome 🚻")

aba1, aba2 = st.tabs(["🔍 Consulta Única", "📁 Processar Planilha"])

with aba1:
    nome = st.text_input("Nome:")
    if st.button("Classificar Único") and nome:
        res = classificar_genero_ibge(nome)
        if res == "M":
            st.success(f"**{nome.title()}**: {res} 👦")
        else:
            st.success(f"**{nome.title()}**: {res} 👧")

with aba2:
    arq = st.file_uploader("Envie a planilha (.xlsx)", type=["xlsx"])
    if arq:
        df = pd.read_excel(arq)
        if "Nome" in df.columns:
            st.dataframe(df.head(3))
            if st.button("Processar Nomes"):
                res = []
                bar = st.progress(0)
                for i, n in enumerate(df["Nome"]):
                    res.append(classificar_genero_ibge(n))
                    bar.progress((i + 1) / len(df))
                    time.sleep(0.1) 
                
                df["Gênero Identificado"] = res
                st.success("Pronto!")
                
                saida = BytesIO()
                with pd.ExcelWriter(saida, engine='openpyxl') as w:
                    df.to_excel(w, index=False)
                st.download_button("📥 Baixar Planilha", data=saida.getvalue(), file_name="resultado.xlsx")
        else:
            st.error("A planilha precisa de uma coluna com o cabeçalho exato 'Nome'.")
