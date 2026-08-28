import streamlit as st
import requests
import pandas as pd
import time
from io import BytesIO

def classificar_genero_ibge(nome_completo):
    if not nome_completo or pd.isna(nome_completo): return "Vazio"
    primeiro_nome = str(nome_completo).strip().split()[0].lower()
    
    def obter_frequencia(sexo):
        url = f"https://servicodados.ibge.gov.br/api/v2/censos/nomes/{primeiro_nome}?sexo={sexo}"
        try:
            res = requests.get(url)
            if res.status_code == 200 and res.json():
                return sum(p['frequencia'] for p in res.json()[0]['res'])
        except: pass
        return 0
        
    f_m, f_f = obter_frequencia('M'), obter_frequencia('F')
    total = f_m + f_f
    if total == 0: return "Não encontrado"
    
    p_m, p_f = (f_m/total)*100, (f_f/total)*100
    if p_m > p_f: return f"Masculino ({p_m:.1f}%)"
    elif p_f > p_m: return f"Feminino ({p_f:.1f}%)"
    else: return "Unissex (50%)"

st.set_page_config(page_title="Classificador", page_icon="🚻")
st.title("Descubra o Gênero pelo Nome 🚻")
aba1, aba2 = st.tabs(["🔍 Consulta Única", "📁 Processar Planilha"])

with aba1:
    nome = st.text_input("Nome:")
    if st.button("Classificar Único") and nome:
        res = classificar_genero_ibge(nome)
        st.success(f"**{nome.title()}**: {res}")

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
