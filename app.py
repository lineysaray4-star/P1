import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Coca-Cola FEMSA | DSS CAPEX Planta Barranquilla", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos limpios y modernos corporativos
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .corporate-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        border-left: 5px solid #E51A22;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO EJECUTIVO ---
col_logo, col_info, col_user = st.columns([1.5, 3, 1.5])

with col_logo:
    st.markdown("""
        <div style="font-weight: 900; font-style: italic; font-size: 22px; color: #E51A22; letter-spacing: -1px; padding-top: 10px;">
            COCA-COLA <span style="background: #E51A22; color: white; font-size: 11px; padding: 2px 6px; border-radius: 4px; font-style: normal;">FEMSA</span>
        </div>
    """, unsafe_allow_html=True)

with col_info:
    st.markdown("""
        <div>
            <h3 style="margin: 0; color: #1e293b; font-size: 18px;">DSS CAPEX • Planta Barranquilla</h3>
            <p style="margin: 0; color: #64748b; font-size: 12px;">Módulo de Optimización y Selección de Portafolio</p>
        </div>
    """, unsafe_allow_html=True)

with col_user:
    st.markdown("""
        <div style="text-align: right;">
            <p style="margin: 0; font-weight: bold; color: #334155; font-size: 13px;">Panel Gerencial</p>
            <p style="margin: 0; color: #10b981; font-size: 11px; font-weight: 600;">● Sistema Activo (Colombia)</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- PANEL DE CONTROL CON ENTRADA EXACTA ---
st.markdown("""
    <div class="corporate-card">
        <h4 style="margin-top: 0; color: #1e293b;">🎛️ Configuración de Escenarios de Inversión</h4>
        <p style="color: #64748b; font-size: 13px;">Ingrese el monto exacto de presupuesto CAPEX disponible para habilitar la evaluación financiera de la planta.</p>
    </div>
""", unsafe_allow_html=True)

# Campo numérico libre para que el usuario digite cualquier cifra exacta
presupuesto_exacto = st.number_input(
    "Presupuesto CAPEX disponible (COP)", 
    min_value=0, 
    value=1500000000, 
    step=10000,
    format="%d"
)

# Métrica dinámica reflejando la cifra exacta ingresada
st.metric(
    label="Tope de Inversión Configurado para el Análisis", 
    value=f"${presupuesto_exacto:,.0f} COP", 
    delta="Listo para Optimización"
)
