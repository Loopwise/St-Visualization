import streamlit as st
import pandas as pd
import numpy as np
import datetime
from utilities import *

st.set_page_config(     
    page_title="Dashboard Programación Avanzada",
    layout="wide",
)

# Creación del dataframe con los datos "preprocesados"
download_data('data.csv')
df = pd.read_csv('data.csv', encoding='utf-8')
seleccion = ['fecha_fallecimiento',
    'edad', 'sexo', 'criterio_fallecido',
    'dpt_cdc', 'cdc_positividad', 'flag_vacuna',
    'flag_hospitalizado', 'flag_uci', 'con_oxigeno',
    'con_ventilacion', 'evolucion_hosp_ultimo']

df = df[seleccion]
df['fecha_fallecimiento'] = pd.to_datetime(df['fecha_fallecimiento']).dt.date
df = add_LatLong(df)

st.markdown('## Datos de un solo departamento')
fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    set_dep = np.sort(df['dpt_cdc'].dropna().unique())
    dep_opt = st.selectbox('Departamento', set_dep)
    df_dep = df[df['dpt_cdc'] == dep_opt]

    num_filas = df_dep.shape[0]
    num_hosp = df_dep[df_dep['flag_hospitalizado'] == 1].shape[0]
    num_O2 = df_dep[df_dep['con_oxigeno'] > 0].shape[0]
    num_vacunados = df_dep[df_dep['flag_vacuna'] > 0].shape[0]
    num_ventilacion = df_dep[df_dep['con_ventilacion'] > 0].shape[0]

    st.write('Número de Fallecidos en el Departamento: ', num_filas)
    st.write('Número de Hospitalizados: ', num_hosp)
    st.write('Número de Hospitalizados con Oxígeno: ', num_O2)
    st.write('Número de Hospitalizados con Oxígeno: ', num_ventilacion)
    st.write('Número de Vacunados: ', num_vacunados)


with fig_col2:
    st.markdown("### Gráfica de fallecidos por edad en el departamento seleccionado")
    fig = px.histogram(data_frame = df_dep, x = 'edad', labels={'edad': 'Edad del Fallecido'})
    st.write(fig)


st.markdown('## Gráficas empleando límites de fechas')
fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    f_0 = st.date_input("Indique una fecha inferior: ", datetime.date(2020, 1, 1))
    f_f = st.date_input("Indique una fecha superior: ", datetime.date(2021, 1, 1))
    Lima_exclude = st.checkbox('¿Excluir a Lima del análisis de aquí en adelante?')

data = filtered_data(df, f_0, f_f, Lima_exclude)

with fig_col1:
    st.write('Número de fallecidos: ', data.shape[0])

with fig_col2:
    Distribuciones(data)

fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    plot_Criterio(data)

st.markdown("## Mapa geográfico (afecta el límite de fechas)")
fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    option = st.selectbox('Seleccione el sexo', ('Masculino', 'Femenino', 'Ambos'))
    df = data.copy()
    if option == 'Masculino':
        df = df[df['sexo'] == 'M']
    elif option == 'Femenino':
        df = df[df['sexo'] == 'F']
    hosp = st.checkbox('Restringir a Hospitalizados')
    if hosp:
        df = df[df['flag_hospitalizado'] == 1]
    oxig = st.checkbox('Restringir a los que requirieron Oxigeno')
    if oxig:
        df = df[df['con_oxigeno'] > 0]
    vent = st.checkbox('Restringir a los que requirieron Ventilación')
    if vent:
        df = df[df['con_ventilacion'] > 0]
    vac = st.checkbox('Restringir a Vacunados')
    if vac:
        df = df[df['flag_vacuna'] > 0]
    st.write('Número de fallecidos en la gráfica: ', df.shape[0])

with fig_col2:
    chart(df)