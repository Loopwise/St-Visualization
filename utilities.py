import streamlit as st
import pandas as pd
import numpy as np
import requests
import urllib.request
import os
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import pydeck as pdk

@st.experimental_memo
def download_data(filename = 'data.csv'):
    url = 'https://cloud.minsa.gob.pe/s/8EsmTzyiqmaySxk/download'
    opener = urllib.request.URLopener()
    opener.addheader('User-Agent', 'whatever')
    filename, headers = opener.retrieve(url, filename)

@st.experimental_memo
def add_LatLong(df):
    mapeo = pd.read_excel('Tabla_Lat_Long.xlsx')
    data = df['dpt_cdc'].copy()
    Lat_Long = dict()
    for i, element  in enumerate(mapeo['Ciudad']):
        Lat_Long[element.lower()] = [mapeo['Latitud'][i], mapeo['Longitud'][i]]

    for i, element in enumerate(data):
        if element.lower() in Lat_Long.keys():
            data[i] = Lat_Long[element.lower()]
        else:
            print(element)

    Data = pd.DataFrame((i for i in data), columns =['lat', 'lon'])
    return pd.concat([df, Data], axis = 1)

def filtered_data(data, f_0, f_f):
    df = data.copy()
    df = df[(df['fecha_fallecimiento'] >= f_0) & (df['fecha_fallecimiento'] <= f_f)]
    return df

@st.experimental_memo
def chart(data, option):
    df = data.copy()
    if option == 'M':
        df = df[df['sexo'] == 'M']
    elif option == 'F':
        df = df[df['sexo'] == 'F']
    df = df[['lat', 'lon']]

    st.write('Número de fallecidos en la gráfica: ', df.shape[0])

    st.pydeck_chart(pdk.Deck(
        map_style= None,
        initial_view_state = pdk.ViewState(
            latitude=-12.046374,
            longitude=-77.042793,
            zoom=4,
            pitch=50,
        ),
        layers = [
            pdk.Layer(
                'HexagonLayer',
                data = df,
                get_position = '[lon, lat]',
                radius = 20*1e3,
                elevation_scale=500,
                elevation_range=[0, 5000],
                pickable=True,
                extruded=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=df,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=20000,
            ),
        ],
    ))

def Distribuciones(data):
    df = data.copy()
    df_male = df['dpt_cdc'][df['sexo'] == 'M'].value_counts()
    df_female = df['dpt_cdc'][df['sexo'] == 'F'].value_counts()
    df = pd.concat([df_male, df_female], axis = 1)
    df.columns = ['Hombres', 'Mujeres']
    print(df.head())

    st.write("Fallecidos por Departamento distinguiendo Sexo")
    st.write('Número de fallecidos: ', data.shape[0])
    st.bar_chart(df)

"""
    Gráfica de Pie del Criterio
"""
def change_index_criterio(data_original):
    data = data_original.copy()
    for i, text in enumerate(data['index']):
        if 'virol' in text:
            data.loc[i, 'index'] = 'Virolágico'
        elif 'SINADEF' in text:
            data.loc[i, 'index'] = 'SINADEF'
        elif 'serol' in text:
            data.loc[i, 'index'] = 'Serolágico'
        elif 'investigaci' in text:
            data.loc[i, 'index'] = 'Investigación Epidemiológica'
        elif 'radiol' in text:
            data.loc[i, 'index'] = 'Radiológico'
        elif 'nexo' in text:
            data.loc[i, 'index'] = 'Nexo Epidemiológico'
        else:
            data.loc[i, 'index'] = 'Clínico'
    return data

def plot_Criterio(data):
    data_cf = data['criterio_fallecido'].value_counts()
    data_cf = pd.DataFrame(data_cf)
    data_cf = data_cf.reset_index()
    data_cf = change_index_criterio(data_cf)
    data_cf.columns = ['Criterio', 'Cantidad']

    fig, ax = plt.subplots()
    wedges, texts = ax.pie(data_cf['Cantidad'], wedgeprops=dict(width=0.5), shadow = True, startangle=-45)
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})

        xaux = 1.35*np.sign(x)
        yaux = 1.5*y

        if i%2:
            xaux = 1.35*np.sign(x)
            yaux = 1.25*y
        ax.annotate(data_cf['Cantidad'][i], xy=(x, y), xytext=(xaux, yaux), horizontalalignment=horizontalalignment, **kw)

    ax.legend(wedges, data_cf['Criterio'] ,title='Criterios', loc = 'center left', bbox_to_anchor = (1, 0, 0.5, 1))
    ax.axis('equal')
    st.write("Gráfica de los Criterios de Fallecimiento")
    st.pyplot(fig)