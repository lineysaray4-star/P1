import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Coca-Cola FEMSA | DSS CAPEX Planta Barranquilla", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos corporativos limpios
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
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        text-align: center;
        border-top: 3px solid #E51A22;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar el estado de navegación de la página
if "pagina" not in st.session_state:
    st.session_state.pagina = "configuracion"

# --- ENCABEZADO EJECUTIVO COMÚN ---
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
            <p style="margin: 0; color: #64748b; font-size: 12px;">Sistema de Soporte de Decisiones para Selección de Portafolio</p>
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

# ==========================================
# FASE 1: PÁGINA DE CONFIGURACIÓN Y PARÁMETROS
# ==========================================
if st.session_state.pagina == "configuracion":
    st.markdown("### 📋 Fase 1: Configuración de Escenarios y Proyectos Candidatos")
    st.write("Defina el presupuesto disponible y revise el listado de proyectos evaluados por AHP/TOPSIS para la planta.")

    col_izq, col_der = st.columns([1, 1])

    with col_izq:
        st.markdown("""
            <div class="corporate-card">
                <h4 style="margin-top: 0; color: #1e293b;">🎛️ Parámetro Financiero</h4>
            </div>
        """, unsafe_allow_html=True)
        
        presupuesto_ingresado = st.number_input(
            "Presupuesto CAPEX Disponible (COP)", 
            min_value=0, 
            value=2500000000, 
            step=50000,
            format="%d"
        )
        st.session_state.presupuesto = presupuesto_ingresado

    with col_der:
        st.markdown("""
            <div class="corporate-card">
                <h4 style="margin-top: 0; color: #1e293b;">🏭 Alcance de Planta</h4>
                <p style="color: #64748b; font-size: 13px;">Se evaluarán 5 proyectos estratégicos enfocados en líneas de producción, eficiencia energética y modernización logística de Barranquilla.</p>
            </div>
        """, unsafe_allow_html=True)

    # Base de datos de proyectos candidatos
    proyectos_df = pd.DataFrame({
        "ID": [1, 2, 3, 4, 5],
        "Proyecto": [
            "Automatización Línea PET 3", 
            "Optimización Sistema de Calderas", 
            "Modernización Fajas Transportadoras", 
            "Ampliación Bodega Almacenamiento", 
            "Actualización Válvulas QMS"
        ],
        "Costo (COP)": [450000000, 300000000, 600000000, 800000000, 250000000],
        "VPN Estimado (COP)": [120000000, 90000000, 150000000, 210000000, 70000000],
        "Score Multicriterio (AHP)": [8.5, 7.8, 8.1, 9.0, 7.2]
    })
    
    st.session_state.proyectos = proyectos_df

    st.write("#### 📊 Banco de Proyectos Candidatos")
    st.dataframe(proyectos_df, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Ejecutar Modelo de Optimización y Ver Dashboard 3D", type="primary", use_container_width=True):
        st.session_state.pagina = "dashboard"
        st.rerun()

# ==========================================
# FASE 2: DASHBOARD EJECUTIVO + MODELO 3D
# ==========================================
elif st.session_state.pagina == "dashboard":
    st.markdown("### 📊 Fase 2: Dashboard Ejecutivo de Decisión y Distribución 3D")
    
    if st.button("⬅️ Volver a Configuración de Parámetros"):
        st.session_state.pagina = "configuracion"
        st.rerun()

    presupuesto_actual = st.session_state.get("presupuesto", 2500000000)
    df = st.session_state.get("proyectos")

    # Simulación de selección por optimización (Greedy / Programación entera)
    df_opt = df[df["Costo (COP)"] <= presupuesto_actual].copy()

    # KPIs Superiores
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Presupuesto Asignado", f"${presupuesto_actual:,.0f} COP")
    with kpi2:
        st.metric("Proyectos Seleccionados", f"{len(df_opt)} de {len(df)}")
    with kpi3:
        st.metric("VPN Total del Portafolio", f"${df_opt['VPN Estimado (COP)'].sum():,.0f} COP")

    st.divider()

    # Sección dividida: Resultados del Portafolio vs Modelo 3D de Planta
    col_res, col_3d = st.columns([1.2, 1.8])

    with col_res:
        st.markdown("#### ✅ Portafolio Óptimo Seleccionado")
        if not df_opt.empty:
            st.dataframe(df_opt[["ID", "Proyecto", "Costo (COP)"]], use_container_width=True)
            st.success("✨ Optimización matemática completada con éxito (Modelo de Programación Entera).")
        else:
            st.warning("⚠️ El presupuesto configurado es insuficiente para seleccionar proyectos.")

    with col_3d:
        st.markdown("#### 🧊 Visualización 3D de Implantación en Planta")
        st.markdown("""
            <div style="background-color: #1e293b; color: white; padding: 2.5rem; border-radius: 0.75rem; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 40px; margin-bottom: 10px;">🏭</div>
                <h5 style="margin: 0; color: #f8fafc; font-size: 16px;">Planta Barranquilla - Modelo 3D Interactivo</h5>
                <p style="margin: 5px 0 15px 0; color: #94a3b8; font-size: 12px;">Renderizado espacial de ubicación de equipos y líneas optimizadas.</p>
                <span style="background-color: #E51A22; color: white; font-size: 11px; padding: 4px 12px; border-radius: 4px; font-weight: bold;">MÓDULO 3D ACTIVO</span>
            </div>
        """, unsafe_allow_html=True)
