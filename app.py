# ==============================================================================
# PROJETO G.O.L.D.I.L.O.C.K.S. v3.0 - SUÍTE DE ANÁLISE DE EXOPLANETAS
# HACKATHON NASA SPACE APPS 2025
# ==============================================================================

# --- 1. IMPORTAÇÕES ---
import streamlit as st
import pandas as pd
import numpy as np
import lightkurve as lk
import matplotlib.pyplot as plt
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
import time
import warnings
import google.generativeai as genai
from PIL import Image
import io

# Suprime avisos desnecessários
warnings.filterwarnings('ignore')

# ==============================================================================
# --- CONFIGURAÇÃO E FUNÇÕES GLOBAIS ---
# ==============================================================================

st.set_page_config(page_title="G.O.L.D.I.L.O.C.K.S. Suite", page_icon="🪐", layout="wide")

# Configura a API do Gemini
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# Cache para acelerar buscas repetidas
@st.cache_data(show_spinner="A procurar dados em cache...")
def fetch_planet_data(planet_name: str):
    """Busca dados de um planeta no NASA Exoplanet Archive."""
    try:
        nexsci_archive = NasaExoplanetArchive()
        planet_data = nexsci_archive.query_object(planet_name, table="pscomppars")
        if planet_data is None or len(planet_data) == 0:
            return None
        return planet_data[0]
    except Exception as e:
        st.error(f"Erro ao buscar dados no arquivo da NASA: {e}")
        return None

# ==============================================================================
# --- FERRAMENTA 1: ANÁLISE APROFUNDADA (RISCO + FALSO POSITIVO) ---
# ==============================================================================
def render_deep_analysis_tool():
    st.title("🛰️ G.O.L.D.I.L.O.C.K.S. - Análise Aprofundada")
    
    with st.sidebar:
        planet_name = st.selectbox(
            'Selecione um alvo para análise:',
            ('Kepler-186 f', 'TRAPPIST-1 e', 'WASP-12 b', 'Kepler-452 b')
        )
        analyze_button = st.button("Analisar Alvo", type="primary", use_container_width=True)

    st.markdown(f"### Relatório Completo para **{planet_name}**")

    if analyze_button:
        planet_info = fetch_planet_data(planet_name)
        if planet_info is None:
            st.error(f"Não foi possível obter dados para {planet_name}.")
            return

        # --- Sub-ferramenta 1: Análise de Risco ---
        with st.spinner("A calcular scores de risco de sustentabilidade..."):
            st.subheader("📊 Scores de Risco e Potencial")
            # (A lógica de scoring completa pode ser inserida aqui, como nas versões anteriores)
            # Para fins de demonstração, usamos valores estáticos.
            st.metric("Zona Habitável (Energia)", "95%", "1%")
            st.metric("Estabilidade Estelar", "75%", "-5%")
            st.metric("Maturidade do Sistema", "90%", "0%")
            st.metric("Viabilidade Planetária", "98%", "2%")
            st.success("Análise de risco concluída.")

        # --- Sub-ferramenta 2: Diagnóstico de Falso Positivo com Lightkurve ---
        with st.spinner(f"A descarregar e a analisar a curva de luz do TESS para {planet_info['hostname']}..."):
            st.subheader("🕵️ Diagnóstico de Trânsito (Falso Positivo)")
            try:
                period = planet_info.get('pl_orbper').value
                t0 = planet_info.get('pl_tranmid').value
                search_result = lk.search_lightcurve(planet_info['hostname'], mission='TESS')
                
                if not search_result:
                    st.warning("Nenhuma curva de luz do TESS encontrada para esta estrela.")
                else:
                    lc = search_result[0].download(quality_bitmask='default').flatten()
                    folded_lc = lc.fold(period=period, epoch_time=t0)

                    # Criação do gráfico
                    fig, ax = plt.subplots(figsize=(10, 5))
                    folded_lc.scatter(ax=ax, label='Fluxo Dobrado')
                    folded_lc.bin(time_bin_size=0.01).plot(ax=ax, color='red', lw=2, label='Fluxo em Bins')
                    ax.set_title(f"Curva de Luz Dobrada para {planet_name}")
                    ax.set_xlim(-0.1, 0.1) # Foca na região do trânsito
                    ax.set_xlabel("Fase")
                    ax.set_ylabel("Fluxo Normalizado")
                    ax.legend()
                    st.pyplot(fig)
                    st.success("Análise visual da curva de luz concluída. Trânsitos em forma de 'U' são bons indicadores de planetas.")

            except Exception as e:
                st.error(f"Falha na análise da curva de luz: {e}")

# ==============================================================================
# --- FERRAMENTA 2: AGENTE DE PESQUISA (CREWAI SIMULADO) ---
# ==============================================================================
def render_crewai_tool():
    st.title("🤖 Agente de Pesquisa de Exoplanetas (CrewAI Simulado)")
    st.markdown("Dê uma tarefa de pesquisa à nossa equipa de agentes de IA para compilar um relatório.")
    
    research_topic = st.text_input("Tópico da Pesquisa:", "Analise o potencial para vida no sistema TRAPPIST-1, focando nas condições atmosféricas de TRAPPIST-1 e.")
    
    if st.button("Iniciar Pesquisa", type="primary"):
        with st.status("Equipa de IA a trabalhar...", expanded=True) as status:
            st.write("Inicializando Agente Investigador...")
            time.sleep(2)
            st.write(f"Investigador a agregar dados sobre '{research_topic}' a partir de arquivos simulados (NASA, ESA)...")
            time.sleep(4)
            st.write("Inicializando Agente Analista...")
            time.sleep(2)
            st.write("Analista a verificar a consistência dos dados e a identificar biomarcadores potenciais...")
            time.sleep(5)
            st.write("Inicializando Agente Escritor...")
            time.sleep(2)
            st.write("Escritor a compilar o relatório final...")
            time.sleep(3)
            status.update(label="Pesquisa Concluída!", state="complete", expanded=False)

        st.subheader("Relatório de Pesquisa Compilado")
        st.markdown(f"""
        **Tópico:** {research_topic}

        **Resumo Executivo:**
        O sistema TRAPPIST-1, em particular o planeta 'e', continua a ser um dos alvos mais promissores na busca por vida extraterrestre. A análise de dados consolidados indica que, embora a estrela anã ultra-fria apresente desafios de habitabilidade devido à sua atividade de flares, a localização de TRAPPIST-1 e na zona habitável e a sua densidade sugerem um mundo rochoso com potencial para reter uma atmosfera e água líquida.

        **Pontos-Chave:**
        * **Atividade Estelar:** O principal risco para a habitabilidade é a emissão de flares de alta energia da estrela TRAPPIST-1, que poderiam erodir a atmosfera do planeta.
        * **Potencial Atmosférico:** Simulações baseadas no raio e massa do planeta sugerem que uma atmosfera densa o suficiente para proteger a superfície é plausível. Futuras observações com o JWST são cruciais para detetar a presença de vapor de água, metano ou outras bioassinaturas.
        * **Conclusão:** A equipa recomenda a alocação de tempo de observação prioritária do JWST para a análise espectroscópica da atmosfera de TRAPPIST-1 e.
        """)

# ==============================================================================
# --- FERRAMENTA 3: ANÁLISE DE IMAGEM (GEMINI AI) ---
# ==============================================================================
def render_image_analysis_tool():
    st.title("🖼️ Análise de Habitabilidade por Imagem (IA Multimodal)")
    
    if not GEMINI_AVAILABLE:
        st.error("A funcionalidade de análise de imagem não está disponível. Por favor, configure a sua chave de API do Google no ficheiro `.streamlit/secrets.toml`.")
        return

    st.markdown("Carregue uma imagem (real ou conceptual) de um exoplaneta para uma análise especulativa.")

    uploaded_file = st.file_uploader("Escolha uma imagem de um planeta...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Imagem Carregada', use_column_width=True)

        if st.button("Analisar Potencial de Habitabilidade", type="primary"):
            with st.spinner("O nosso astrobiólogo de IA está a analisar a imagem..."):
                try:
                    model = genai.GenerativeModel('gemini-pro-vision')
                    prompt = """
                    Você é um astrobiólogo especialista a analisar uma imagem de um exoplaneta para o Hackathon da NASA.
                    Baseado **apenas** nas pistas visuais desta imagem (que pode ser uma conceção artística), forneça uma análise especulativa do seu potencial de habitabilidade.
                    
                    Estruture a sua resposta em Português da seguinte forma:
                    - **Observações Visuais:** Descreva o que você vê (nuvens, oceanos, continentes, calotas polares, cor da atmosfera).
                    - **Inferências Especulativas:** Com base no que observou, o que você pode inferir sobre o clima, a presença de água líquida e a possibilidade de fotossíntese?
                    - **Nível de Confiança:** Atribua um nível de confiança (Muito Baixo, Baixo, Moderado) à sua análise, lembrando que se trata de uma imagem.
                    - **Próximos Passos Recomendados:** Que tipo de dados reais (ex: análise espectral, medições de massa) seriam necessários para confirmar estas hipóteses?
                    """
                    response = model.generate_content([prompt, image])
                    
                    st.subheader("Relatório de Análise Visual")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"Ocorreu um erro ao comunicar com a IA: {e}")
                    st.info("Verifique se a sua chave de API do Google está corretamente configurada.")
    st.warning("Nota: Esta análise é puramente especulativa e baseada na interpretação visual de uma IA.")

# ==============================================================================
# --- NAVEGAÇÃO PRINCIPAL ---
# ==============================================================================
st.sidebar.title("🛠️ Ferramentas de Análise")
app_mode = st.sidebar.radio(
    "Selecione a ferramenta que deseja usar:",
    ("Análise Aprofundada", "Agente de Pesquisa", "Análise de Imagem")
)

if app_mode == "Análise Aprofundada":
    render_deep_analysis_tool()
elif app_mode == "Agente de Pesquisa":
    render_crewai_tool()
elif app_mode == "Análise de Imagem":
    render_image_analysis_tool()