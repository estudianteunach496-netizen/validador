import streamlit as st
import pandas as pd
import numpy as np
import io
import time
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="SIVIGILA ELITE PRO",
    page_icon="🏥",
    layout="wide"
)

# --- DISEÑO LIMPIO Y PREMIUM (Sin cajas vacías) ---
st.markdown("""
    <style>
        /* Fondo Global */
        .stApp {
            background-color: #050505 !important;
            background-image: radial-gradient(circle at 50% -20%, #1e1e1e 0%, #050505 80%) !important;
        }

        /* Título Centrado y Elegante */
        .main-header {
            text-align: center;
            padding: 60px 0 20px 0;
        }
        
        .main-header h1 {
            font-size: 5rem !important;
            font-weight: 800 !important;
            letter-spacing: -3px !important;
            margin-bottom: 0px !important;
            background: linear-gradient(135deg, #FF3B30 0%, #FF9500 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .main-header p {
            color: #8E8E93;
            font-size: 1.2rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 10px;
        }

        /* Estilo del Cargador de Archivos */
        [data-testid="stFileUploader"] {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 24px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* Botón de Fusión Gigante */
        .stButton button {
            background: linear-gradient(135deg, #FF3B30 10%, #D72C21 90%) !important;
            color: white !important;
            border: none !important;
            border-radius: 20px !important;
            height: 80px !important;
            font-size: 1.5rem !important;
            font-weight: 800 !important;
            box-shadow: 0 15px 40px rgba(255, 59, 48, 0.3) !important;
            transition: 0.3s all ease;
            max-width: 800px;
            margin: 20px auto !important;
            display: block !important;
        }

        .stButton button:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 50px rgba(255, 59, 48, 0.5) !important;
        }

        /* Módulos de Información */
        .info-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .info-card h2 { color: #ffffff; font-size: 3rem; margin: 0; }
        .info-card p { color: #8E8E93; text-transform: uppercase; font-size: 0.8rem; margin: 0; }

        /* Arreglos de Streamlit */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    
    <div class="main-header">
        <h1>SIVIGILA ELITE PRO</h1>
        <p>Intelligence Data Consolidation</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Contenedor central
    cont = st.container()
    
    with cont:
        col1, col2, col3 = st.columns([1, 4, 1])
        
        with col2:
            st.markdown('<h3 style="text-align:center; color:white; margin-bottom:20px;">� CARGAR REPORTES SIVIGILA</h3>', unsafe_allow_html=True)
            uploaded_files = st.file_uploader(
                "Sivigila Upload", 
                accept_multiple_files=True, 
                type=['xlsx', 'xls', 'csv'],
                label_visibility="collapsed"
            )

            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} archivos listos para el motor ELITE.")
                
                if st.button("🚀 INICIAR CONSOLIDACIÓN"):
                    start_time = time.time()
                    
                    with st.status("💎 Procesando con motor SIVIGILA ELITE...", expanded=False) as status:
                        try:
                            mapeo = {
                                'num_ide_': ['num_ide_', 'num_ide', 'identificacion', 'documento'],
                                'tip_ide_': ['tip_ide_', 'tip_ide', 'tipo_id', 'tipo_doc'],
                                'cod_eve': ['cod_eve', 'evento', 'codigo_evento'],
                                'fec_not': ['fec_not', 'fecha_notificacion'],
                            }
                            
                            dfs = []
                            for f in uploaded_files:
                                if f.name.endswith('.csv'):
                                    df = pd.read_csv(f, sep=None, engine='python', encoding='latin-1', on_bad_lines='skip', dtype=str)
                                else:
                                    try:
                                        df = pd.read_excel(f, engine='calamine', dtype=str)
                                    except:
                                        df = pd.read_excel(f, dtype=str)
                                
                                df.columns = [str(c).lower().strip().replace(' ', '_') for c in df.columns]
                                for std, vars in mapeo.items():
                                    real = next((v for v in vars if v in df.columns), None)
                                    if real: df.rename(columns={real: std}, inplace=True)
                                
                                if 'num_ide_' in df.columns:
                                    df = df.dropna(subset=['num_ide_'])
                                    df['num_ide_'] = df['num_ide_'].str.extract(r'(\d+)')[0]
                                    df = df.dropna(subset=['num_ide_'])
                                
                                dfs.append(df)

                            # Proceso
                            df_all = pd.concat(dfs, ignore_index=True, sort=False)
                            if 'fec_not' in df_all.columns:
                                df_all['fec_not_dt'] = pd.to_datetime(df_all['fec_not'], errors='coerce')
                                df_all = df_all.dropna(subset=['fec_not_dt'])
                            
                            # Filtro sospechosos
                            col_clas = next((c for c in df_all.columns if 'clasific' in c or 'cla_fin' in c), None)
                            if col_clas:
                                df_all = df_all[~df_all[col_clas].astype(str).str.lower().str.contains('sospecho', na=False)]

                            df_all['semana_epi'] = df_all['fec_not_dt'].dt.isocalendar().week
                            df_all['año_epi'] = df_all['fec_not_dt'].dt.isocalendar().year

                            df_all['_llave'] = (df_all['tip_ide_'].fillna('') + "-" + df_all['num_ide_'].fillna('') + "-" + df_all['cod_eve'].fillna(''))
                            df_all = df_all.sort_values(by=['_llave', 'fec_not_dt'])
                            df_all['diff'] = df_all.groupby('_llave')['fec_not_dt'].diff().dt.days.abs()
                            es_nuevo = (df_all['_llave'] != df_all['_llave'].shift(1)) | (df_all['diff'] > 4)
                            df_all['epid'] = pd.Series(es_nuevo).fillna(True).cumsum()
                            
                            df_final = df_all.sort_values(by=['epid', 'fec_not_dt'], ascending=[True, False]).groupby('epid').first().reset_index()
                            df_final = df_final.drop(columns=['_llave', 'diff', 'epid', 'fec_not_dt'], errors='ignore')
                            
                            df_resumen = df_final.groupby('cod_eve').size().reset_index(name='total_casos')

                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                df_final.to_excel(writer, index=False, sheet_name='BASE_CONSOLIDADA')
                                df_resumen.to_excel(writer, index=False, sheet_name='RESUMEN')
                            
                            status.update(label="✅ FUSIÓN COMPLETADA", state="complete")
                            st.balloons()
                            
                            # Métricas
                            st.markdown('<div style="margin-top:40px;"></div>', unsafe_allow_html=True)
                            m1, m2 = st.columns(2)
                            with m1:
                                st.markdown(f'<div class="info-card"><h2>{len(df_final):,}</h2><p>Casos Consolidados</p></div>', unsafe_allow_html=True)
                            with m2:
                                st.markdown(f'<div class="info-card"><h2>{len(dfs)}</h2><p>Fuentes Unidas</p></div>', unsafe_allow_html=True)
                            
                            st.download_button(
                                label="📥 DESCARGAR CONSOLIDADO (.XLSX)",
                                data=output.getvalue(),
                                file_name=f"SIVIGILA_ELITE_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                        except Exception as e:
                            st.error(f"Falla: {str(e)}")

    st.markdown('<div style="margin-top:100px; text-align:center; color:#333; font-size:0.8rem;">SIVIGILA ELITE v5.2 | PRO ENGINE</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
