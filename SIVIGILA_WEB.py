import streamlit as st
import pandas as pd
import numpy as np
import io
import time
import os
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="OBSERVATORIO DE SALUD | Norte de Santander",
    page_icon="🏥",
    layout="wide"
)

# --- DISEÑO OFICIAL IDS (Rojo y Blanco) ---
st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff !important;
            color: #1a1a1a !important;
        }

        /* Título IDS */
        .header-container {
            text-align: center;
            padding: 40px 0;
            background-color: #ffffff;
            border-bottom: 4px solid #E63946;
            margin-bottom: 30px;
        }
        
        .header-container h1 {
            color: #E63946 !important;
            font-size: 3.5rem !important;
            font-weight: 900 !important;
            margin: 0 !important;
            letter-spacing: -2px;
        }

        .header-container p {
            color: #48484A;
            font-size: 1.1rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 5px;
        }

        /* Cargador de Archivos */
        [data-testid="stFileUploader"] {
            max-width: 900px;
            margin: 0 auto;
            background: #f8f9fa;
            border-radius: 20px;
            padding: 25px;
            border: 2px dashed #E63946;
        }
        
        .stMarkdown h3 {
            color: #1a1a1a !important;
            font-weight: 800 !important;
        }

        /* Botón de Fusión IDS */
        .stButton button {
            background-color: #E63946 !important;
            color: white !important;
            border: none !important;
            border-radius: 15px !important;
            height: 65px !important;
            font-size: 1.4rem !important;
            font-weight: 800 !important;
            box-shadow: 0 8px 20px rgba(230, 57, 70, 0.2) !important;
            transition: 0.3s all ease;
            max-width: 900px;
            margin: 30px auto !important;
            display: block !important;
        }

        .stButton button:hover {
            background-color: #D62828 !important;
            transform: translateY(-2px);
            box-shadow: 0 12px 25px rgba(230, 57, 70, 0.3) !important;
        }

        /* Info Cards */
        .info-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            border-left: 5px solid #E63946;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        
        .info-card h2 { color: #E63946; font-size: 2.5rem; margin: 0; }
        .info-card p { color: #48484A; text-transform: uppercase; font-size: 0.8rem; font-weight: 700; margin: 0; }

        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def main():
    # --- HEADER CON LOGO ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Intento cargar el logo si existe en la carpeta
        if os.path.exists("logo.png"):
            st.image("logo.png", width=250, use_container_width=False)
        else:
            # Si no hay logo, mostramos un icono
            st.markdown("<h1 style='text-align:center; font-size: 80px;'>🏥</h1>", unsafe_allow_html=True)
            
    st.markdown("""
        <div class="header-container">
            <h1>SIVIGILA ELITE PRO</h1>
            <p>Instituto Departamental de Salud de Norte de Santander</p>
            <p style="font-size: 0.9rem; color: #E63946;">OBSERVATORIO DE SALUD PÚBLICA</p>
        </div>
    """, unsafe_allow_html=True)

    # --- CUERPO PRINCIPAL ---
    col_a, col_b, col_c = st.columns([1, 8, 1])
    
    with col_b:
        st.markdown('<h3 style="text-align:center;">📦 CARGA DE ARCHIVOS EPIDEMIOLÓGICOS</h3>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Cargar archivos", 
            accept_multiple_files=True, 
            type=['xlsx', 'xls', 'csv'],
            label_visibility="collapsed"
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} archivos listos para consolidación oficial.")
            
            if st.button("🚀 INICIAR CONSOLIDACIÓN DEPARTAMENTAL"):
                start_time = time.time()
                
                with st.status("💎 Motor SIVIGILA IDS en ejecución...", expanded=False) as status:
                    try:
                        mapeo = {
                            'num_ide_': ['num_ide_', 'num_ide', 'identificacion', 'documento'],
                            'tip_ide_': ['tip_ide_', 'tip_ide', 'tipo_id', 'tipo_doc'],
                            'cod_eve': ['cod_eve', 'evento', 'codigo_evento'],
                            'fec_not': ['fec_not', 'fecha_notificacion'],
                        }
                        
                        dfs = []
                        for f in uploaded_files:
                            status.write(f"📖 Leyendo: **{f.name}**")
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

                        # Proceso Maestro
                        df_all = pd.concat(dfs, ignore_index=True, sort=False)
                        if 'fec_not' in df_all.columns:
                            df_all['fec_not_dt'] = pd.to_datetime(df_all['fec_not'], errors='coerce')
                            df_all = df_all.dropna(subset=['fec_not_dt'])
                        
                        # Filtro oficiales (Sin sospechosos)
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
                            df_resumen.to_excel(writer, index=False, sheet_name='RESUMEN_EVENTOS')
                        
                        status.update(label="✅ PROCESO COMPLETADO EXITOSAMENTE", state="complete")
                        st.balloons()
                        
                        # Resultados
                        st.markdown('<div style="margin-top:30px;"></div>', unsafe_allow_html=True)
                        m1, m2 = st.columns(2)
                        with m1:
                            st.markdown(f'<div class="info-card"><h2>{len(df_final):,}</h2><p>Casos Finales Consolidados</p></div>', unsafe_allow_html=True)
                        with m2:
                            st.markdown(f'<div class="info-card"><h2>{len(dfs)}</h2><p>Fuentes Originales</p></div>', unsafe_allow_html=True)
                        
                        st.download_button(
                            label="📥 DESCARGAR CONSOLIDADO OFICIAL IDS (.XLSX)",
                            data=output.getvalue(),
                            file_name=f"MAESTRO_SIVIGILA_IDS_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                    except Exception as e:
                        st.error(f"Falla en el motor: {str(e)}")

    st.markdown(
        f'<div style="margin-top:100px; text-align:center; color:#E63946; font-size:0.9rem; font-weight:700;">'
        f'SIVIGILA ELITE v5.2 | IDS NORTE DE SANTANDER | {datetime.now().year}'
        f'</div>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
