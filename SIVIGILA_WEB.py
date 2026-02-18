import streamlit as st
import pandas as pd
import numpy as np
import io
import time
from datetime import datetime

# Configuración de página con SEO y título Elite
st.set_page_config(
    page_title="SIVIGILA ELITE PRO | Intelligence Hub",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SISTEMA DE DISEÑO PREMIUM (Glassmorphism + Apple Aesthetic) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;600;800&family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        /* Global Styles */
        .main {
            background: radial-gradient(circle at top right, #1a1a1a, #050505);
            color: #ffffff;
            font-family: 'SF Pro Display', 'Outfit', sans-serif;
        }
        
        /* Ocultar elementos de Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Glassmorphism Card Content */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 32px;
            padding: 40px;
            margin-bottom: 25px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        
        /* Typography */
        h1 {
            font-size: 4rem !important;
            font-weight: 800 !important;
            letter-spacing: -2px !important;
            background: linear-gradient(135deg, #FF3B30 0%, #FF9500 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0px !important;
        }
        
        .elite-subtitle {
            font-size: 1.2rem;
            color: #8E8E93;
            font-weight: 400;
            margin-bottom: 40px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        
        /* Custom Button */
        .stButton>button {
            background: linear-gradient(135deg, #FF3B30 0%, #D72C21 100%);
            color: white !important;
            border-radius: 18px !important;
            border: none !important;
            height: 70px !important;
            width: 100% !important;
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
            box-shadow: 0 10px 30px rgba(255, 59, 48, 0.3) !important;
            margin-top: 20px !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-4px);
            box-shadow: 0 15px 40px rgba(255, 59, 48, 0.5) !important;
            filter: brightness(1.1);
        }
        
        /* Custom File Uploader */
        .uploadedFileName {
            color: #34C759 !important;
        }
        
        .stFileUploader section {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 2px dashed rgba(255, 255, 255, 0.1) !important;
            border-radius: 24px !important;
            padding: 30px !important;
        }
        
        /* Status & Progress */
        .stStatus {
            border-radius: 20px !important;
            background: rgba(0, 122, 255, 0.1) !important;
            border: 1px solid rgba(0, 122, 255, 0.2) !important;
        }

        /* Metrics */
        .metric-container {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            text-align: center;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 800;
            color: #ffffff;
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #8E8E93;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    # --- HEADER SECTION ---
    st.markdown('<div style="text-align: center; padding-top: 50px;">', unsafe_allow_html=True)
    st.markdown('<h1>SIVIGILA ELITE PRO</h1>', unsafe_allow_html=True)
    st.markdown('<p class="elite-subtitle">Intelligence Hub & Data Consolidation Engine</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- MAIN UI CONTAINER ---
    col1, col2, col3 = st.columns([1, 8, 1])
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        # --- UPLOAD SECTION ---
        st.markdown('<h3 style="color:#ffffff; font-weight:600; margin-bottom:20px;">📦 Fuentes de Información</h3>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Cargue múltiples reportes Sivigila (CSV, XLSX, XLS)", 
            accept_multiple_files=True, 
            type=['xlsx', 'xls', 'csv'],
            label_visibility="collapsed"
        )

        if uploaded_files:
            st.markdown(f'<div style="color:#34C759; font-weight:600; margin-bottom:10px;">✅ {len(uploaded_files)} archivos en cola para procesamiento.</div>', unsafe_allow_html=True)
            
            # --- ACTION BUTTON ---
            if st.button("🚀 INICIAR FUSIÓN E INTELIGENCIA"):
                if len(uploaded_files) < 2:
                    st.error("Se requieren al menos 2 archivos para realizar la consolidación.")
                    return

                with st.status("� SIVIGILA ENGINE v5.2 | Procesando a alta fidelidad...", expanded=True) as status:
                    try:
                        start_time = time.time()
                        
                        mapeo = {
                            'num_ide_': ['num_ide_', 'num_ide', 'identificacion', 'documento'],
                            'tip_ide_': ['tip_ide_', 'tip_ide', 'tipo_id', 'tipo_doc'],
                            'cod_eve': ['cod_eve', 'evento', 'codigo_evento'],
                            'fec_not': ['fec_not', 'fecha_notificacion'],
                        }
                        
                        dfs = []
                        for uploaded_file in uploaded_files:
                            status.write(f"� Cargando fuente: **{uploaded_file.name}**")
                            
                            if uploaded_file.name.endswith('.csv'):
                                df = pd.read_csv(uploaded_file, sep=None, engine='python', 
                                               encoding='latin-1', on_bad_lines='skip',
                                               dtype=str) 
                            else:
                                try:
                                    df = pd.read_excel(uploaded_file, engine='calamine', dtype=str)
                                except:
                                    df = pd.read_excel(uploaded_file, dtype=str)
                            
                            # Normalización Express
                            df.columns = [str(c).lower().strip().replace(' ', '_') for c in df.columns]
                            for std, vars in mapeo.items():
                                real = next((v for v in vars if v in df.columns), None)
                                if real: df.rename(columns={real: std}, inplace=True)
                            
                            if 'num_ide_' in df.columns:
                                df = df.dropna(subset=['num_ide_'])
                                df['num_ide_'] = df['num_ide_'].str.extract(r'(\d+)')[0]
                                df = df.dropna(subset=['num_ide_'])
                            
                            dfs.append(df)

                        status.write("� Aplicando filtros de depuración avanzada...")
                        df_all = pd.concat(dfs, ignore_index=True, sort=False)
                        
                        # Fechas y Filtros
                        if 'fec_not' in df_all.columns:
                            df_all['fec_not_dt'] = pd.to_datetime(df_all['fec_not'], errors='coerce')
                            df_all = df_all.dropna(subset=['fec_not_dt'])
                        
                        # Quitar sospechosos
                        col_clas = next((c for c in df_all.columns if 'clasific' in c or 'cla_fin' in c), None)
                        if col_clas:
                            df_all = df_all[~df_all[col_clas].astype(str).str.lower().str.contains('sospecho', na=False)]

                        # Cálculo Epi
                        df_all['semana_epi'] = df_all['fec_not_dt'].dt.isocalendar().week
                        df_all['año_epi'] = df_all['fec_not_dt'].dt.isocalendar().year

                        status.write("🧠 Ejecutando algoritmos de prevalencia...")
                        df_all['_llave'] = (df_all['tip_ide_'].fillna('') + "-" + 
                                           df_all['num_ide_'].fillna('') + "-" + 
                                           df_all['cod_eve'].fillna(''))
                        
                        df_all = df_all.sort_values(by=['_llave', 'fec_not_dt'])
                        df_all['diff'] = df_all.groupby('_llave')['fec_not_dt'].diff().dt.days.abs()
                        es_nuevo = (df_all['_llave'] != df_all['_llave'].shift(1)) | (df_all['diff'] > 4)
                        
                        es_nuevo_series = pd.Series(es_nuevo).fillna(True)
                        df_all['epid'] = es_nuevo_series.cumsum()
                        
                        df_final = df_all.sort_values(by=['epid', 'fec_not_dt'], 
                                                     ascending=[True, False]).groupby('epid').first().reset_index()

                        df_final = df_final.drop(columns=['_llave', 'diff', 'epid', 'fec_not_dt'], errors='ignore')

                        # Resumen
                        df_resumen = df_final.groupby('cod_eve').size().reset_index(name='total_casos')

                        status.write("� Generando reporte ELITE...")
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_final.to_excel(writer, index=False, sheet_name='BASE_CONSOLIDADA')
                            df_resumen.to_excel(writer, index=False, sheet_name='RESUMEN')
                        
                        total_time = time.time() - start_time
                        status.update(label=f"🌟 Motor SIVIGILA ELITE: Fusión Exitosa en {total_time:.1f}s", state="complete")
                        
                        st.balloons()
                        
                        # --- RESULTS SECTION ---
                        st.markdown('<div style="margin-top: 30px;">', unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.markdown(f'<div class="metric-container"><div class="metric-value">{len(df_final):,}</div><div class="metric-label">Casos Consolidados</div></div>', unsafe_allow_html=True)
                        with m2:
                            st.markdown(f'<div class="metric-container"><div class="metric-value">{len(dfs)}</div><div class="metric-label">Fuentes Fusionadas</div></div>', unsafe_allow_html=True)
                        with m3:
                            st.markdown(f'<div class="metric-container"><div class="metric-value">{total_time:.1f}s</div><div class="metric-label">Tiempo de Respuesta</div></div>', unsafe_allow_html=True)
                        
                        st.download_button(
                            label="📥 DESCARGAR RESULTADOS ELITE (.XLSX)",
                            data=output.getvalue(),
                            file_name=f"SIVIGILA_RESULT_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)

                    except Exception as e:
                        status.update(label="❌ Fallo en el motor de inteligencia", state="error")
                        st.error(f"Error crítico: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

    # --- FOOTER ---
    st.markdown(
        f'<div style="text-align: center; color: #48484A; padding: 40px; font-size: 0.8rem;">'
        f'SIVIGILA ELITE ENGINE v5.2 PRO | {datetime.now().year} | High-Performance Epidemiological Intelligence'
        f'</div>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
