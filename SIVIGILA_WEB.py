import streamlit as st
import pandas as pd
import numpy as np
import io
import time
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="SIVIGILA ELITE WEB", page_icon="🏥", layout="wide")

# Estilo CSS para que se vea de lujo (Rojo y Premium)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        background-color: #E63946;
        color: white;
        border-radius: 20px;
        height: 3.5em;
        width: 100%;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 15px rgba(230, 57, 70, 0.3);
    }
    .stButton>button:hover {
        background-color: #D62828;
        box-shadow: 0 6px 20px rgba(230, 57, 70, 0.4);
        color: white;
    }
    h1 { color: #E63946; font-family: 'Arial'; }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🏥 SIVIGILA ELITE v5.0")
    st.subheader("Consolidador de Alta Velocidad")
    
    st.info("Sube tus archivos de Sivigila. Esta versión utiliza motor **Calamine** para lectura instantánea.")

    uploaded_files = st.file_uploader("Arrastra aquí tus archivos", accept_multiple_files=True, type=['xlsx', 'xls', 'csv'])

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} archivos cargados.")
        
        if st.button("🚀 INICIAR CONSOLIDACIÓN ULTRA"):
            if len(uploaded_files) < 2:
                st.error("Por favor sube al menos 2 archivos.")
                return

            with st.status("🚀 Procesando datos a máxima velocidad...", expanded=True) as status:
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
                        status.write(f"📖 Leyendo: {uploaded_file.name}...")
                        
                        if uploaded_file.name.endswith('.csv'):
                            # Lectura optimizada de CSV
                            df = pd.read_csv(uploaded_file, sep=None, engine='python', 
                                           encoding='latin-1', on_bad_lines='skip',
                                           dtype=str) 
                        else:
                            # MOTOR CALAMINE: 10x más rápido que openpyxl
                            try:
                                df = pd.read_excel(uploaded_file, engine='calamine', dtype=str)
                            except:
                                df = pd.read_excel(uploaded_file, dtype=str)
                        
                        # Normalización Vectorizada
                        df.columns = [str(c).lower().strip().replace(' ', '_') for c in df.columns]
                        for std, vars in mapeo.items():
                            real = next((v for v in vars if v in df.columns), None)
                            if real: df.rename(columns={real: std}, inplace=True)
                        
                        # Limpiar identificación de una vez
                        if 'num_ide_' in df.columns:
                            df = df.dropna(subset=['num_ide_'])
                            df['num_ide_'] = df['num_ide_'].str.extract(r'(\d+)')[0]
                            df = df.dropna(subset=['num_ide_'])
                        
                        dfs.append(df)

                    status.write("🧠 Ejecutando lógica de prevalencia ELITE...")
                    
                    # Consolidación MASIVA
                    df_all = pd.concat(dfs, ignore_index=True, sort=False)
                    
                    # Convertir fechas solo al final para ganar velocidad
                    if 'fec_not' in df_all.columns:
                        df_all['fec_not_dt'] = pd.to_datetime(df_all['fec_not'], errors='coerce')
                        df_all = df_all.dropna(subset=['fec_not_dt'])
                    else:
                        st.error("No se encontró columna de fecha de notificación en los archivos.")
                        return

                    # Filtro de Clasificación (Eliminar Sospechosos)
                    # Buscamos columnas de clasificación tipicamente llamadas 'clasificaci', 'clasifica', 'cla_fin'
                    col_clas = next((c for c in df_all.columns if 'clasific' in c or 'cla_fin' in c), None)
                    if col_clas:
                        status.write(f"🧹 Filtrando registros sospechosos en columna: {col_clas}...")
                        df_all = df_all[~df_all[col_clas].astype(str).str.lower().str.contains('sospecho', na=False)]

                    # Cálculo de Semana Epidemiológica (ISO year and week)
                    df_all['semana_epi'] = df_all['fec_not_dt'].dt.isocalendar().week
                    df_all['año_epi'] = df_all['fec_not_dt'].dt.isocalendar().year

                    df_all['_llave'] = (df_all['tip_ide_'].fillna('') + "-" + 
                                       df_all['num_ide_'].fillna('') + "-" + 
                                       df_all['cod_eve'].fillna(''))
                    
                    df_all = df_all.sort_values(by=['_llave', 'fec_not_dt'])
                    
                    # Lógica de episodios (4 días) optimizada
                    df_all['diff'] = df_all.groupby('_llave')['fec_not_dt'].diff().dt.days.abs()
                    es_nuevo = (df_all['_llave'] != df_all['_llave'].shift(1)) | (df_all['diff'] > 4)
                    
                    # Corrección del fillna para evitar el error de linter
                    es_nuevo_series = pd.Series(es_nuevo).fillna(True)
                    df_all['epid'] = es_nuevo_series.cumsum()
                    
                    # Grupo final
                    df_final = df_all.sort_values(by=['epid', 'fec_not_dt'], 
                                                 ascending=[True, False]).groupby('epid').first().reset_index()

                    # Eliminar columnas temporales internas pero dejamos las epi
                    df_final = df_final.drop(columns=['_llave', 'diff', 'epid', 'fec_not_dt'], errors='ignore')

                    status.write("� Generando resumen estadístico...")
                    # Crear tabla de resumen por evento
                    df_resumen = df_final.groupby('cod_eve').size().reset_index(name='total_casos_finales')
                    if 'cod_eve' in df_resumen.columns:
                        df_resumen = df_resumen.sort_values('total_casos_finales', ascending=False)

                    status.write("�💾 Generando archivo Excel final con múltiples hojas...")
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_final.to_excel(writer, index=False, sheet_name='BASE_CONSOLIDADA')
                        df_resumen.to_excel(writer, index=False, sheet_name='RESUMEN_EJECUTIVO')
                    
                    end_time = time.time()
                    total_time = end_time - start_time
                    
                    status.update(label=f"✅ ¡Fusión completa en {total_time:.1f}s!", state="complete", expanded=False)
                    st.balloons()
                    
                    st.success(f"✨ Se generaron {len(df_final):,} registros consolidados (Sospechosos eliminados).")
                    
                    st.download_button(
                        label="📥 DESCARGAR CONSOLIDADO OFICIAL v5.2",
                        data=output.getvalue(),
                        file_name=f"SIVIGILA_ELITE_PRO_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                except Exception as e:
                    status.update(label="❌ Error en el proceso", state="error")
                    st.error(f"Error técnico: {str(e)}")

    st.markdown("---")
    st.caption(f"SIVIGILA ELITE ENGINE v5.1 | {datetime.now().year}")

if __name__ == "__main__":
    main()
