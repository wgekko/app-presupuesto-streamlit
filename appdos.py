import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
import streamlit.components.v1 as components

import warnings
warnings.simplefilter("ignore", category=FutureWarning)
# Suprimir advertencias ValueWarning
warnings.simplefilter("ignore")

theme_plotly = None

# Configuración inicial de la app
st.set_page_config(
    page_title="Dashboard Proyección de Gastos Proyecto Inmobiliario",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

#""" imagen de background"""
def add_local_background_image(image):
  with open(image, "rb") as image:
    encoded_string = base64.b64encode(image.read())
    st.markdown(
      f"""
      <style>
      .stApp{{
        background-image: url(data:files/{"jpg"};base64,{encoded_string.decode()});
      }}    
      </style>
      """,
      unsafe_allow_html=True
    )
add_local_background_image("img/fondo.jpg")

#""" imagen de sidebar"""
def add_local_sidebar_image(image):
  with open(image, "rb") as image:
    encoded_string = base64.b64encode(image.read())
    st.markdown(
      f"""
      <style>
      .stSidebar{{
        background-image: url(data:files/{"jpg"};base64,{encoded_string.decode()});
      }}    
      </style>
      """,
      unsafe_allow_html=True
    )

add_local_sidebar_image("img/fondo1.jpg")

#-------------- animacion con css de los botones  ------------------------
with open('asset/styles.css') as f:
        css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Carga de datos
dfDatos = pd.read_excel('datos/gastos.xlsx')

# Sidebar de filtros (sin filtro de año porque es solo 2025)
with st.sidebar:
    parMes = st.selectbox('Seleccione Mes Analizar', options=dfDatos['mes'].unique(), index=0)
    parPais = st.multiselect('Selecciones Proyecto', options=dfDatos['proyecto'].unique())

# Aplicar filtros
dfDatos = dfDatos[dfDatos['anio'] == 2025]
if parMes:
    dfDatos = dfDatos[dfDatos['mes'] <= parMes]
if len(parPais) > 0:
    dfDatos = dfDatos[dfDatos['proyecto'].isin(parPais)]

# Datos del mes actual y anterior
dfMesActual = dfDatos[dfDatos['mes'] == parMes]
if parMes > 1:
    dfMesAnterior = dfDatos[dfDatos['mes'] == parMes - 1]
else:
    dfMesAnterior = dfDatos[dfDatos['mes'] == parMes]

# Cálculo de métricas de gastos
gastos_total = dfMesActual['gastos'].sum()
gastos_pagado = dfMesActual[dfMesActual['estado'] == 'pagado']['gastos'].sum()
gastos_pendiente = dfMesActual[dfMesActual['estado'] != 'pagado']['gastos'].sum()
porcentaje_pagado = (gastos_pagado / gastos_total * 100) if gastos_total > 0 else 0
gastos_promedio = dfDatos.groupby('mes')['gastos'].sum().mean()



st.header('Tablero de control de gastos - Proyecto Inmobiliario 2025')

# 🔘 Indicador de porcentaje de Gastos pagados (tipo velocímetro)
st.subheader(f'Indicador de Ejecución de Gastos del mes # {parMes} # seleccionado')
fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=porcentaje_pagado,
    delta={'reference': 100, 'increasing': {'color': "green"}},
    gauge={
        'axis': {'range': [None, 100]},
        'bar': {'color': "blue"},
        'steps': [
            {'range': [0, 50], 'color': "lightcoral"},
            {'range': [50, 80], 'color': "orange"},
            {'range': [80, 100], 'color': "lightgreen"}
        ],
        'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 100}
    },
    title={'text': "Porcentaje de Gastos Pagados"}
))
st.plotly_chart(fig, use_container_width=True)

st.write("---")
# Métricas principales
c1, c2, c3 = st.columns(3)
with c1:
    productosAct = dfMesActual['importe'].sum()
    productosAnt = dfMesAnterior['importe'].sum()
    variacion = productosAnt - productosAct
    st.metric("Gastos totales Pesos", f'$ {productosAct:,.0f} ', f'{variacion:,.0f}')
with c2:
    ordenesAct = dfMesActual['orden'].count()
    ordenesAnt = dfMesAnterior['orden'].count()
    variacion = ordenesAct - ordenesAnt
    st.metric("Proyeccion cantidad de gastos", f'{ordenesAct:.0f}', f'{variacion:.1f}')
with c3:
    ventasAct = dfMesActual['gastos'].sum()
    ventasAnt = dfMesAnterior['gastos'].sum()
    variacion = ventasAct - ventasAnt
    st.metric("Gastos totales", f'US$ {ventasAct:,.0f}', f'{variacion:,.0f}')
    
st.write("---")

# NUEVA SECCIÓN: Gastos por pagar hasta fin de mes actual
st.subheader("📆 Gastos Pendientes Próximos Periodos por Pagar")    
# Convertir 'fecha' a datetime
dfDatos['fecha'] = pd.to_datetime(dfDatos['fecha'], errors='coerce')
# Normalizamos campos clave
dfDatos['proyecto'] = dfDatos['proyecto'].str.strip()
dfDatos['estado'] = dfDatos['estado'].str.lower().str.strip()
dfDatos['fecha'] = pd.to_datetime(dfDatos['fecha'], errors='coerce')

hoy = pd.Timestamp.today().normalize()
prox_semana = hoy + timedelta(days=7)
fin_de_mes = pd.Timestamp(hoy.year, hoy.month, 1) + pd.offsets.MonthEnd(0)

# Filtrar solo gastos pendientes con fechas válidas
dfPendiente = dfDatos[(dfDatos['estado'] == 'pendiente') & (dfDatos['fecha'].notna())]

# Gastos con vencimiento próxima semana
pendiente_semana = dfPendiente[(dfPendiente['fecha'] > hoy) & (dfPendiente['fecha'] <= prox_semana)]
pendiente_mes = dfPendiente[(dfPendiente['fecha'] > hoy) & (dfPendiente['fecha'] <= fin_de_mes)]

# Agrupamos por proyecto
dfSemana = pendiente_semana.groupby('proyecto')['gastos'].sum().reset_index(name='Pendiente Semana')
dfMes = pendiente_mes.groupby('proyecto')['gastos'].sum().reset_index(name='Pendiente Fin de Mes')

# Unimos todos los proyectos posibles
dfResumenPendiente = pd.DataFrame(dfDatos['proyecto'].unique(), columns=['proyecto'])
dfResumenPendiente = dfResumenPendiente.merge(dfSemana, on='proyecto', how='left')
dfResumenPendiente = dfResumenPendiente.merge(dfMes, on='proyecto', how='left')
dfResumenPendiente = dfResumenPendiente.fillna(0)

# Formato de dos decimales visibles
dfResumenPendiente['Pendiente Semana'] = dfResumenPendiente['Pendiente Semana'].apply(lambda x: f"{x:,.2f}")
dfResumenPendiente['Pendiente Fin de Mes'] = dfResumenPendiente['Pendiente Fin de Mes'].apply(lambda x: f"{x:,.2f}")

hoy_str = hoy.strftime("%d/%m/%Y")
# Mostrar
st.subheader(f'Gastos Pendientes Próximos Periodos desde : {hoy_str}')
st.table(dfResumenPendiente)
st.write("---")        

# Gráfico línea de Gastos por mes
c1, c2 = st.columns([60, 40])
with c1:
    dfGastosMes = dfDatos.groupby('mes').agg({'gastos': 'sum'}).reset_index()
    fig = px.line(dfGastosMes, x='mes', y='gastos', title='Gastos por mes')
    st.plotly_chart(fig, use_container_width=True)
with c2:
    dfGastosPais = dfMesActual.groupby('proyecto').agg({'gastos': 'sum'}).reset_index().sort_values(by='gastos', ascending=False)
    fig = px.bar(dfGastosPais, x='proyecto', y='gastos', title=f'Gastos por detalle Mes: {parMes}', color='proyecto', text_auto=',.0f')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.write("---")  
# Gráfico línea por unidad
c1, c2 = st.columns([60, 40])
with c1:
    dfGastosCategoria = dfDatos.groupby(['mes', 'unidad']).agg({'gastos': 'sum'}).reset_index()
    fig = px.line(dfGastosCategoria, x='mes', y='gastos', title='Gastos por mes y unidad', color='unidad')
    st.plotly_chart(fig, use_container_width=True)
with c2:
    dfGastosCategoria = dfMesActual.groupby('unidad').agg({'gastos': 'sum'}).reset_index().sort_values(by='gastos', ascending=False)
    fig = px.bar(dfGastosCategoria, x='unidad', y='gastos', title=f'Gastos por unidad Mes: {parMes}', color='unidad', text_auto=',.0f')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Gráfico tipo pie por detalle y proyecto
dfGastosPais = dfMesActual.groupby(['detalle', 'proyecto']).agg(cantidad=('orden', 'count'), gastos=('gastos', 'sum')).reset_index()
fig = px.pie(dfGastosPais, color='detalle', values='gastos', facet_col='proyecto', facet_col_wrap=4, height=800, title='Gastos por detalle y proyecto')
st.plotly_chart(fig, use_container_width=True)

# Top productos
st.write("---")  
c1, c2 = st.columns(2)

# Agrupación con proyecto, unidad y detalle
dfProductosVentas = dfMesActual.groupby(['proyecto', 'unidad', 'detalle']).agg({'gastos': 'sum'}).reset_index()

# Formatear gasto como string con 2 decimales
dfProductosVentas['gastos'] = dfProductosVentas['gastos'].apply(lambda x: f"{x:,.2f}")

with c1:
    st.subheader('Top 10 gastos más valor')
    top_mas_valor = dfProductosVentas.sort_values(by='gastos', ascending=False).head(10)
    st.table(top_mas_valor[['proyecto', 'unidad', 'detalle', 'gastos']])

with c2:
    st.subheader('Top 10 gastos menos valor')
    top_menos_valor = dfProductosVentas.sort_values(by='gastos', ascending=True).head(10)
    st.table(top_menos_valor[['proyecto', 'unidad', 'detalle', 'gastos']])

