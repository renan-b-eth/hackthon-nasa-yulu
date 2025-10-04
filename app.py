# ==============================================================================
# PROJETO G.O.L.D.I.L.O.C.K.S. - AVALIADOR DE RISCO PLANETÁRIO
# VERSÃO FINAL OTIMIZADA v2.2 - HACKATHON NASA SPACE APPS 2025
# ==============================================================================

# --- 1. IMPORTAÇÕES ---
import streamlit as st
import pandas as pd
import numpy as np
import lightkurve as lk
# Importação corrigida para a versão mais recente do astroquery
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
import time
import warnings

# Suprime avisos desnecessários para uma apresentação mais limpa no console
warnings.filterwarnings('ignore')

# ==============================================================================
# --- 2. MÓDULO DE DADOS (O CORAÇÃO) ---
# ==============================================================================
@st.cache_data(show_spinner="A procurar dados em cache...") # Adiciona cache para acelerar buscas repetidas
def fetch_real_data_from_archives(planet_name: str) -> dict:
    """
    Busca e consolida dados realistas de um exoplaneta e da sua estrela hospedeira.
    """
    try:
        nexsci_archive = NasaExoplanetArchive()
        planet_data = nexsci_archive.query_object(planet_name, table="pscomppars")
        
        if planet_data is None or len(planet_data) == 0:
            st.error(f"ERRO: Planeta '{planet_name}' não encontrado no arquivo. Tente um nome alternativo.")
            return None

        planet_info = planet_data[0]
        
        # --- CORREÇÃO PARA O ERRO UnitConversionError ---
        # Esta função agora extrai o .value das quantidades Astropy, tornando-as números puros.
        def get_value(series, key, default=0.0):
            val = series.get(key)
            if pd.isna(val):
                return default
            # Se o valor for uma quantidade com unidades (comum em AstroPy), pegamos apenas o valor numérico.
            if hasattr(val, 'value'):
                return val.value
            return val
        # -----------------------------------------------

        consolidated_data = {
            'planet_name': planet_name, 'star_name': get_value(planet_info, 'hostname', 'N/A'),
            'discovery_method': get_value(planet_info, 'discoverymethod', 'N/A'),
            'orbital_period_days': get_value(planet_info, 'pl_orbper'),
            'orbit_semi_major_axis_au': get_value(planet_info, 'pl_orbsmax'),
            'planet_radius_earth': get_value(planet_info, 'pl_rade'),
            'planet_mass_earth': get_value(planet_info, 'pl_masse'),
            'star_temp_k': get_value(planet_info, 'st_teff'),
            'star_radius_sun': get_value(planet_info, 'st_rad'),
            'star_mass_sun': get_value(planet_info, 'st_mass'),
            'star_age_gyr': get_value(planet_info, 'st_age'),
        }

        st.write(f"🔍 A procurar dados de observação para a estrela {consolidated_data['star_name']} (TESS)...")
        search_result = lk.search_lightcurve(consolidated_data['star_name'], mission='TESS')
        
        consolidated_data['stellar_flux_std_ppm'] = 0.0
        consolidated_data['stellar_flare_outliers_count'] = 0
        
        if search_result:
            try:
                st.write("✅ Dados de observação encontrados. A descarregar o conjunto de dados primário...")
                lc = search_result[0].download(download_dir='lc_cache', quality_bitmask='default')
                
                if lc:
                    st.write("⚙️ A processar a curva de luz para análise de atividade...")
                    lc = lc.flatten()
                    flux_std_ppm = lc.flux.std().value * 1e6 # Adicionado .value aqui também por segurança
                    consolidated_data['stellar_flux_std_ppm'] = round(flux_std_ppm, 2)
                    _, outlier_mask = lc.remove_outliers(sigma=3, return_mask=True)
                    consolidated_data['stellar_flare_outliers_count'] = np.sum(outlier_mask)
            except Exception:
                st.warning("⚠️ Não foi possível processar os dados da curva de luz do TESS.")
                pass

        return consolidated_data
    except Exception as e:
        st.error(f"ERRO GERAL na busca de dados: {e}")
        return None

# ==============================================================================
# --- 3. MÓDULO DE LÓGICA (O CÉREBRO) ---
# ==============================================================================
def _normalize_score(score):
    return max(0, min(100, int(score)))

def _calculate_habitable_zone_score(star_temp_k, star_radius_sun, orbit_semi_major_axis_au):
    if star_temp_k <= 0 or star_radius_sun <= 0 or orbit_semi_major_axis_au <= 0: return 0
    relative_luminosity = (star_radius_sun ** 2) * ((star_temp_k / 5778) ** 4)
    relative_flux = relative_luminosity / (orbit_semi_major_axis_au ** 2)
    score = 100 * np.exp(-((relative_flux - 1.0) ** 2) / 0.5)
    return _normalize_score(score)

def _calculate_stellar_stability_score(flare_outliers_count, stellar_flux_std_ppm):
    score = 100
    if flare_outliers_count > 100: score -= 80
    elif flare_outliers_count > 20: score -= 50
    elif flare_outliers_count > 5: score -= 25
    if stellar_flux_std_ppm > 10000: score -= 20
    elif stellar_flux_std_ppm > 5000: score -= 10
    return _normalize_score(score)

def _calculate_system_maturity_score(star_age_gyr):
    if star_age_gyr <= 0: return 20
    if 2.0 < star_age_gyr < 8.0: score = 100
    elif 1.0 < star_age_gyr <= 2.0: score = 70
    elif star_age_gyr >= 8.0: score = 60
    else: score = 30
    return _normalize_score(score)

def _calculate_planet_viability_score(planet_radius_earth):
    if planet_radius_earth <= 0: return 0
    if 0.8 < planet_radius_earth < 1.8: score = 100
    elif 0.5 < planet_radius_earth <= 0.8: score = 60
    elif 1.8 <= planet_radius_earth < 2.5: score = 70
    else: score = 10
    return _normalize_score(score)

def calculate_risk_scores(planet_data: dict) -> dict:
    if planet_data is None: return {}
    final_scores = {
        "Zona Habitável (Energia)": _calculate_habitable_zone_score(
            planet_data.get('star_temp_k'), planet_data.get('star_radius_sun'), planet_data.get('orbit_semi_major_axis_au')),
        "Estabilidade Estelar": _calculate_stellar_stability_score(
            planet_data.get('stellar_flare_outliers_count'), planet_data.get('stellar_flux_std_ppm')),
        "Maturidade do Sistema": _calculate_system_maturity_score(planet_data.get('star_age_gyr')),
        "Viabilidade Planetária": _calculate_planet_viability_score(planet_data.get('planet_radius_earth'))
    }
    return final_scores

def generate_narrative_report(planet_data: dict, scores: dict) -> str:
    stability_score = scores.get("Estabilidade Estelar", 0)
    if stability_score > 80: risk_level, risk_desc = "BAIXO", "A estrela hospedeira é notavelmente calma, similar ao Sol."
    elif stability_score > 50: risk_level, risk_desc = "MODERADO", "A estrela apresenta atividade esporádica de flares, requerendo monitorização."
    else: risk_level, risk_desc = "ALTO", "A estrela é altamente ativa, representando um risco significativo para a manutenção de uma atmosfera."

    return f"""
    ### **RELATÓRIO DE SUSTENTABILIDADE PLANETÁRIA**
    **ALVO:** {planet_data.get('planet_name', 'N/A').upper()} | **ESTRELA:** {planet_data.get('star_name', 'N/A')}
    ---
    #### **AVALIAÇÃO GERAL:**
    O sistema apresenta um potencial de sustentabilidade que justifica uma análise mais aprofundada. A viabilidade planetária e a maturidade do sistema são favoráveis, com o principal ponto de atenção a ser a estabilidade da estrela hospedeira.

    #### **ANÁLISE DOS FATORES:**
    * **Energia (`{scores.get("Zona Habitável (Energia)", 0)}%`):** O planeta recebe um fluxo de energia estelar compatível com a manutenção de água líquida.
    * **Estabilidade (`{stability_score}%`):** RISCO **{risk_level}**. {risk_desc}
    * **Maturidade (`{scores.get("Maturidade do Sistema", 0)}%`):** Com {planet_data.get('star_age_gyr', 'N/A')} mil milhões de anos, o sistema é maduro e estável.
    * **Viabilidade (`{scores.get("Viabilidade Planetária", 0)}%`):** Com {planet_data.get('planet_radius_earth', 'N/A')}x o raio da Terra, o planeta tem o tamanho ideal para ser rochoso e reter uma atmosfera.

    **RECOMENDAÇÃO PARA OBSERVAÇÃO FUTURA (JWST):** **Prioridade { 'ALTA' if stability_score > 70 else 'MÉDIA' }.**
    """

# ==============================================================================
# --- 4. INTERFACE DO UTILIZADOR (O ROSTO) ---
# ==============================================================================
st.set_page_config(page_title="Projeto G.O.L.D.I.L.O.C.K.S.", page_icon="🪐", layout="wide")

with st.sidebar:
    st.image("nasa_logo.png")
    st.image("esa_logo.jpg")
    
    st.title("Projeto G.O.L.D.I.L.O.C.K.S.")
    st.info("Uma ferramenta para avaliar o risco e a sustentabilidade de exoplanetas, auxiliando investigadores na priorização de alvos para o JWST.")
    st.markdown("---")
    
    planet_name = st.selectbox(
        'Selecione um alvo para análise:',
        ('Kepler-186 f', 'TRAPPIST-1 e', 'Kepler-452 b', 'Proxima Centauri b')
    )

st.title("🛰️ Painel de Controlo de Risco Planetário")
st.markdown(f"### Análise de Sustentabilidade para **{planet_name}**")

if st.sidebar.button("Analisar Alvo", type="primary", use_container_width=True):
    if not planet_name:
        st.error("Por favor, selecione um planeta.")
    else:
        # A busca de dados agora acontece dentro do spinner,
        # e as mensagens de progresso aparecerão no painel principal.
        with st.spinner("A iniciar análise..."):
            planet_data = fetch_real_data_from_archives(planet_name)
        
        if planet_data is None:
            st.error(f"Falha na obtenção de dados para '{planet_name}'. Verifique o terminal para mais detalhes.")
        else:
            scores = calculate_risk_scores(planet_data)
            report = generate_narrative_report(planet_data, scores)
            
            st.success(f"Análise de {planet_name} concluída!")
            st.subheader("Índices de Risco e Potencial")
            
            cols = st.columns(len(scores))
            for i, (score_name, score_value) in enumerate(scores.items()):
                cols[i].metric(score_name, f"{score_value}%")
            
            st.markdown("---")
            st.subheader("Relatório de Análise Detalhada")
            st.markdown(report, unsafe_allow_html=True)
else:
    st.info("Selecione um planeta na barra lateral e clique em 'Analisar Alvo' para começar.")

