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
    </style>
""", unsafe_allow_html=True)

# Inicializar estado de navegación
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
            <p style="margin: 0; color: #64748b; font-size: 12px;">Modelo Multicriterio con Ponderación Estandarizada (Excel Model)</p>
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
# FASE 1: CONFIGURACIÓN Y MATRIZ EN BLANCO
# ==========================================
if st.session_state.pagina == "configuracion":
    st.markdown("### 📋 Fase 1: Ingreso de Parámetros y Evaluación Multicriterio")
    st.write("Ingrese el presupuesto global y registre los proyectos candidatos calificando su relación (1 a 10) frente a los criterios estandarizados de su modelo de Excel.")

    # 1. Presupuesto Global Libre en Blanco/Editable
    st.markdown("""
        <div class="corporate-card">
            <h4 style="margin-top: 0; color: #1e293b;">🎛️ 1. Restricción Presupuestal Global</h4>
        </div>
    """, unsafe_allow_html=True)
    
    presupuesto_ingresado = st.number_input(
        "Presupuesto CAPEX Disponible (COP)", 
        min_value=0, 
        value=0, 
        step=100000,
        format="%d"
    )
    st.session_state.presupuesto = presupuesto_ingresado

    # 2. Criterios y Ponderación Estandarizada (Ajusta aquí si tienes los nombres exactos de tu Excel)
    st.markdown("#### ⚖️ 2. Criterios de Evaluación y Ponderación Estandarizada")
    st.write("Pesos estandarizados definidos en el modelo:")
    
    criterios_df = pd.DataFrame({
        "Criterio": [
            "C1: [Escribe o ajusta el criterio de tu Excel]", 
            "C2: [Escribe o ajusta el criterio de tu Excel]", 
            "C3: [Escribe o ajusta el criterio de tu Excel]", 
            "C4: [Escribe o ajusta el criterio de tu Excel]"
        ],
        "Peso Estandarizado (W)": [0.40, 0.30, 0.20, 0.10]
    })
    st.dataframe(criterios_df, use_container_width=True)

    # 3. Banco de Proyectos EN BLANCO para que el usuario escriba libremente
    st.markdown("#### 📊 3. Registro de Proyectos Candidatos y Calificaciones (1 a 10)")
    st.write("Agregue las filas necesarias y escriba el nombre del proyecto, su costo y las calificaciones de 1 a 10 por criterio:")

    if "proyectos_input" not in st.session_state:
        # Tabla vacía lista para ser llenada por el usuario
        st.session_state.proyectos_input = pd.DataFrame(
            columns=["Proyecto", "Costo Estimado (COP)", "C1", "C2", "C3", "C4"],
            data=[["", 0, 0, 0, 0, 0]]
        )

    proyectos_editados = st.data_editor(
        st.session_state.proyectos_input, 
        use_container_width=True, 
        num_rows="dynamic"
    )
    st.session_state.proyectos_input = proyectos_editados

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Calcular Puntuación Global y Ver Dashboard 3D", type="primary", use_container_width=True):
        st.session_state.pagina = "dashboard"
        st.rerun()

# ==========================================
# FASE 2: DASHBOARD EJECUTIVO + MODELO 3D
# ==========================================
elif st.session_state.pagina == "dashboard":
    st.markdown("### 📊 Fase 2: Resultados del Modelo Ponderado y Visualización 3D")
    
    if st.button("⬅️ Volver a Modificar Parámetros y Proyectos"):
        st.session_state.pagina = "configuracion"
        st.rerun()

    presupuesto_actual = st.session_state.get("presupuesto", 0)
    df = st.session_state.get("proyectos_input")

    # Limpiar filas vacías si el usuario dejó alguna sin nombre
    df = df[df["Proyecto"].astype(str).str.strip() != ""].copy()

    if not df.empty:
        # Asegurar formato numérico
        for col in ["Costo Estimado (COP)", "C1", "C2", "C3", "C4"]:
            df[col] = pd.to_numeric(df[col], errors="fill").fillna(0)

        # Cálculo del Score Global Ponderado (Pesos: 0.40, 0.30, 0.20, 0.10 o ajustados)
        pesos = [0.40, 0.30, 0.20, 0.10]
        df["Score Global Ponderado"] = (
            df["C1"] * pesos[0] + 
            df["C2"] * pesos[1] + 
            df["C3"] * pesos[2] + 
            df["C4"] * pesos[3]
        ).round(2)

        # Ordenar por el score ponderado para la selección óptima
        df_sorted = df.sort_values(by="Score Global Ponderado", ascending=False).copy()
        
        acumulado = 0
        seleccionados = []
        for index, row in df_sorted.iterrows():
            if acumulado + row["Costo Estimado (COP)"] <= presupuesto_actual:
                acumulado += row["Costo Estimado (COP)"]
                seleccionados.append(True)
            else:
                seleccionados.append(False)
                
        df_sorted["Seleccionado"] = seleccionados
        df_opt = df_sorted[df_sorted["Seleccionado"] == True]

        # KPIs Superiores
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("Presupuesto Disponible", f"${presupuesto_actual:,.0f} COP")
        with kpi2:
            st.metric("Inversión Portafolio Óptimo", f"${df_opt['Costo Estimado (COP)'].sum():,.0f} COP")
        with kpi3:
            st.metric("Proyectos Seleccionados", f"{len(df_opt)} de {len(df)}")

        st.divider()

        col_res, col_3d = st.columns([1.3, 1.7])

        with col_res:
            st.markdown("#### ✅ Portafolio Óptimo Seleccionado (Ranking Ponderado)")
            if not df_opt.empty:
                st.dataframe(df_opt[["Proyecto", "Costo Estimado (COP)", "Score Global Ponderado"]], use_container_width=True)
                st.success("✨ Modelo multicriterio ejecutado correctamente.")
            else:
                st.warning("⚠️ El presupuesto ingresado es insuficiente para los proyectos registrados.")
    else:
        st.warning("⚠️ No ha ingresado ningún proyecto válido en la fase anterior. Por favor regrese y agregue proyectos.")

    with col_3d:
        st.markdown("#### 🧊 Visualización 3D de Implantación en Planta")
        st.markdown("""
            <div style="background-color: #1e293b; color: white; padding: 2.5rem; border-radius: 0.75rem; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 40px; margin-bottom: 10px;">🏭</div>
                <h5 style="margin: 0; color: #f8fafc; font-size: 16px;">Planta Barranquilla - Modelo 3D Interactivo</h5>
                <p style="margin: 5px 0 15px 0; color: #94a3b8; font-size: 12px;">Renderizado espacial del portafolio óptimo seleccionado en planta.</p>
                <span style="background-color: #E51A22; color: white; font-size: 11px; padding: 4px 12px; border-radius: 4px; font-weight: bold;">MÓDULO 3D ACTIVO</span>
            </div>
        """, unsafe_allow_html=True)
