import streamlit as st
import requests
import pandas as pd
import time
from io import BytesIO

# --- LÓGICA DO IBGE COM MEMÓRIA (CACHE) ---
# Esse comando faz o Streamlit lembrar de nomes que já pesquisou hoje
@st.cache_data(show_spinner=False)
def classificar_genero_ibge(primeiro_nome):
    def obter_frequencia(sexo):
        url = f"https://servicodados.ibge.gov.br/api/v2/censos/nomes/{primeiro_nome}?sexo={sexo}"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200 and res.json():
                return sum(p['frequencia'] for p in res.json()[0]['res'])
        except:
            pass
        return 0
        
    f_m = obter_frequencia('M')
    f_f = obter_frequencia('F')
    total = f_m + f_f
    
    def palpite_pela_letra(nome):
        if nome.endswith(('a', 'z', 'y', 'elly', 'ine', 'ane', 'ele', 'ia')):
            return "F"
        return "M"
    
    if total == 0:
        return palpite_pela_letra(primeiro_nome)
        
    prob_masc = (f_m / total) * 100
    prob_fem = (f_f / total) * 100
    
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
    nome_digitado = st.text_input("Nome:")
    if st.button("Classificar Único") and nome_digitado:
        primeiro = str(nome_digitado).strip().split()[0].lower()
        res = classificar_genero_ibge(primeiro)
        emoji = "👦" if res == "M" else "👧"
        st.success(f"**{nome_digitado.title()}**: {res} {emoji}")

with aba2:
    arq = st.file_uploader("Envie a planilha (.xlsx)", type=["xlsx"])
    if arq:
        df = pd.read_excel(arq)
        if "Nome" in df.columns:
            st.dataframe(df.head(3))
            
            if st.button("Processar Nomes"):
                resultados = []
                bar = st.progress(0)
                
                # Memória local ultra-rápida para a planilha atual
                memoria_planilha = {}
                total_linhas = len(df["Nome"])
                
                for i, nome_completo in enumerate(df["Nome"]):
                    if pd.isna(nome_completo):
                        resultados.append("")
                    else:
                        # Limpa e pega só o primeiro nome
                        primeiro = str(nome_completo).strip().split()[0].lower()
                        
                        # Verifica se o nome já está na memória da planilha
                        if primeiro in memoria_planilha:
                            resultados.append(memoria_planilha[primeiro])
                        else:
                            # Se for um nome novo, consulta o IBGE e salva na memória
                            genero = classificar_genero_ibge(primeiro)
                            memoria_planilha[primeiro] = genero
                            resultados.append(genero)
                            time.sleep(0.05) # Pausa curtíssima apenas para nomes novos
                            
                    # Atualiza a barra
                    bar.progress((i + 1) / total_linhas)
                
                df["Gênero Identificado"] = resultados
                st.success("Pronto! Processamento concluído.")
                
                saida = BytesIO()
                with pd.ExcelWriter(saida, engine='openpyxl') as w:
                    df.to_excel(w, index=False)
                st.download_button("📥 Baixar Planilha", data=saida.getvalue(), file_name="resultado.xlsx")
        else:
            st.error("A planilha precisa de uma coluna com o cabeçalho exato 'Nome'.")
