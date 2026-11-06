import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Coca-Cola FEMSA | DSS CAPEX", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos limpios y modernos
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
            <p style="margin: 0; font-weight: bold; color: #334155; font-size: 13px;">Liney Avendaño</p>
            <p style="margin: 0; color: #10b981; font-size: 11px; font-weight: 600;">● Sistema Activo (Colombia)</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- PANEL DE CONTROL ESTILO TARJETA ---
st.markdown("""
    <div class="corporate-card">
        <h4 style="margin-top: 0; color: #1e293b;">🎛️ Parámetros de Planificación Financiera</h4>
        <p style="color: #64748b; font-size: 13px;">Ajuste el límite de inversión para simular la asignación óptima de recursos en planta.</p>
    </div>
""", unsafe_allow_html=True)

presupuesto = st.slider("Seleccione el Presupuesto CAPEX disponible (Millones COP)", 500, 3000, 1500, 100)

# Métrica limpia de resumen
st.metric(label="Presupuesto Seleccionado para Evaluación", value=f"${presupuesto:,.0f} Millones COP", delta="Fase de Análisis")
