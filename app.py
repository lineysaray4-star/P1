import streamlit as st

import streamlit as st

# ------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Coca-Cola FEMSA | DSS CAPEX Planta Barranquilla",
    page_icon="🥤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# ESTILOS CORPORATIVOS
# ------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --cc-red: #E41E2B;
        --cc-red-dark: #B5121B;
        --cc-ink: #1A1A1A;
        --cc-slate: #475569;
        --cc-muted: #94A3B8;
        --cc-line: #E2E8F0;
        --cc-bg: #F6F7F9;
        --cc-ok: #15803D;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    }
    .stApp { background-color: var(--cc-bg); }

    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container { padding-top: 1.2rem; max-width: 1280px; }

    /* Encabezado */
    .cc-header {
        background: #FFFFFF;
        border-bottom: 3px solid var(--cc-red);
        border-radius: 8px;
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
        margin-bottom: 1.5rem;
    }
    .cc-brand {
        font-weight: 800;
        font-size: 1.35rem;
        color: var(--cc-red);
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .cc-badge {
        background: var(--cc-red);
        color: #FFFFFF;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 1px;
        padding: 3px 8px;
        border-radius: 3px;
    }
    .cc-title { margin: 0; color: var(--cc-ink); font-size: 1.05rem; font-weight: 700; }
    .cc-subtitle { margin: 2px 0 0 0; color: var(--cc-slate); font-size: 0.78rem; }
    .cc-user { text-align: right; }
    .cc-user-name { margin: 0; color: var(--cc-ink); font-weight: 600; font-size: 0.85rem; }
    .cc-status { margin: 2px 0 0 0; color: var(--cc-ok); font-size: 0.72rem; font-weight: 600; }
    .cc-dot {
        display: inline-block; width: 7px; height: 7px;
        background: var(--cc-ok); border-radius: 50%; margin-right: 5px;
    }

    /* Tarjetas */
    .cc-card {
        background: #FFFFFF;
        border: 1px solid var(--cc-line);
        border-left: 4px solid var(--cc-red);
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
        margin-bottom: 1rem;
    }
    .cc-card-title {
        margin: 0 0 0.25rem 0;
        color: var(--cc-ink);
        font-size: 0.95rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .cc-card-text { margin: 0; color: var(--cc-slate); font-size: 0.82rem; line-height: 1.5; }

    /* Campo numérico */
    div[data-testid="stNumberInput"] label p {
        font-weight: 600; color: var(--cc-ink); font-size: 0.85rem;
    }
    div[data-testid="stNumberInput"] input { font-weight: 600; font-size: 1.05rem; }

    /* KPI */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid var(--cc-line);
        border-radius: 8px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
    }
    div[data-testid="stMetricLabel"] p {
        color: var(--cc-slate); font-size: 0.75rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] { color: var(--cc-ink); font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# ENCABEZADO EJECUTIVO
# ------------------------------------------------------------------
st.markdown("""
<div class="cc-header">
    <div class="cc-brand">COCA-COLA <span class="cc-badge">FEMSA</span></div>
    <div>
        <p class="cc-title">Sistema de Soporte a la Decisión · CAPEX</p>
        <p class="cc-subtitle">Planta Barranquilla · Optimización y selección de portafolio de inversión</p>
    </div>
    <div class="cc-user">
        <p class="cc-user-name">Panel Gerencial</p>
        <p class="cc-status"><span class="cc-dot"></span>Sistema activo · Colombia</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# CONFIGURACIÓN DEL ESCENARIO DE INVERSIÓN
# ------------------------------------------------------------------
st.markdown("""
<div class="cc-card">
    <p class="cc-card-title">Configuración del escenario de inversión</p>
    <p class="cc-card-text">
        Ingrese el monto de presupuesto CAPEX disponible. Este valor define el límite
        superior para la selección óptima de proyectos de la planta.
    </p>
</div>
""", unsafe_allow_html=True)

col_input, col_kpi = st.columns([1, 1], gap="large")

with col_input:
    presupuesto_exacto = st.number_input(
        "Presupuesto CAPEX disponible (COP)",
        min_value=0,
        value=1_500_000_000,
        step=10_000,
        format="%d",
        help="Digite el monto exacto en pesos colombianos.",
    )

# Formato colombiano: punto como separador de miles
presupuesto_fmt = f"${presupuesto_exacto:,.0f}".replace(",", ".")

with col_kpi:
    if presupuesto_exacto > 0:
        st.metric(
            label="Tope de inversión configurado",
            value=f"{presupuesto_fmt} COP",
            delta="Listo para optimización",
        )
    else:
        st.metric(label="Tope de inversión configurado", value="— COP")
        st.warning("Ingrese un presupuesto mayor a cero para habilitar la optimización.")

