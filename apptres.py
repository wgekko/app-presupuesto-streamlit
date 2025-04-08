import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd  # Librería para manipulación y análisis de datos. Instalación: pip install pandas
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode # Librería para crear tablas interactivas. Instalación: pip install streamlit-aggrid
from datetime import datetime, timedelta
import base64
import streamlit.components.v1 as components
from streamlit.components.v1 import html
from ipyvizzu import Chart, Data, Config, DisplayTarget,  Style  
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

# Diccionario de nombres de meses
meses_nombres = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

# Sidebar de filtros
with st.sidebar:
    parMes = st.selectbox('Seleccione Mes Analizar', options=dfDatos['mes'].unique(), index=0, format_func=lambda x: meses_nombres[x])
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


# Cálculo de métricas y visualización (sin cambios)

# Título con nombre del mes en lugar del número
st.header(f'Tablero de control de gastos - Proyecto Inmobiliario 2025')

# Cargar datos
df = pd.read_excel("datos/gastos.xlsx")

# Preprocesamiento
df['fecha'] = pd.to_datetime(df['fecha'])
df['mes'] = df['fecha'].dt.strftime('%m/%Y')

# Filtros dinámicos en la barra lateral
# --- Controles en barra lateral ---
st.sidebar.header("Filtros para gráfico animado")
proyecto_seleccionado = st.sidebar.selectbox("Selecciona un proyecto", df['proyecto'].unique())
modo_comparacion = st.sidebar.radio("Comparar por:", ['estado', 'detalle'])
mostrar_acumulado = st.sidebar.checkbox("Mostrar totales acumulados", value=False)

# --- Filtrado y agrupación ---
df = df[df['proyecto'] == proyecto_seleccionado]
columna_comparacion = modo_comparacion
agrupado = df.groupby(['mes', 'unidad', columna_comparacion], as_index=False)['gastos'].sum()

if mostrar_acumulado:
    agrupado['gastos'] = agrupado.sort_values('mes').groupby(['unidad', columna_comparacion])['gastos'].cumsum()

# Renombrar columnas para ipyvizzu
agrupado.columns = ['Mes', 'Unidad', 'Comparacion', 'Gastos']

# --- Crear gráfico animado ---
def create_chart():
    chart = Chart(width="800px", height="600px", display=DisplayTarget.MANUAL)
    data = Data()
    data.add_df(agrupado)
    chart.animate(data)

    # Configuración inicial
    chart.animate(
        Config({
            "x": "Unidad",
            "y": "Gastos",
            "label": "Gastos",
            "color": "Comparacion",
            "title": f"Gastos por Unidad ({modo_comparacion})"
        })
    )

    chart.feature("tooltip", True)

    # Animación por cada mes
    for mes in sorted(agrupado['Mes'].unique()):
        chart.animate(
            Data.filter(f'record.Mes == "{mes}"')
        )
        chart.animate(
            Config({
                "x": "Unidad",
                "y": "Gastos",
                "label": "Comparacion",
                "color": "Comparacion",
                "geometry": "rectangle",
                "split": True,
                "title": f"Gastos - Mes: {mes}"
            })
        )

    return chart._repr_html_()

# --- Mostrar en Streamlit ---
st.title("Visualización Animada de Gastos")
st.subheader(f"Proyecto seleccionado: {proyecto_seleccionado}")
CHART = create_chart()
html(CHART, width=950, height=700)

st.warning("---")

        
st.subheader(f'Indicador de Ejecución de Gastos del mes de **{meses_nombres[parMes]}**')

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
st.subheader(f"📆 Gastos Pendientes Próximos Periodos por Pagar de {meses_nombres[parMes]} ")    
st.warning("importante el detalle de los gastos pendientes para el próximo periodo siempre lo hace desde la fecha actual, en adelante si de decide cambiar el mes a desplegar, la proyeccion de gastos a pagar por semana o mensual no cambia")
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
    dfGastosMes['mes_nombre'] = dfGastosMes['mes'].map(meses_nombres)
    fig = px.line(dfGastosMes, x='mes_nombre', y='gastos', title='Gastos por mes')
    fig.update_layout(xaxis_title='Mes', yaxis_title='Gastos')
    st.plotly_chart(fig, use_container_width=True)

with c2:
    dfGastosPais = dfMesActual.groupby('proyecto').agg({'gastos': 'sum'}).reset_index().sort_values(by='gastos', ascending=False)
    fig = px.bar(dfGastosPais, x='proyecto', y='gastos', title=f'Gastos por detalle Mes: {meses_nombres[parMes]}', color='proyecto', text_auto=',.0f')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.write("---")  
# Gráfico línea por unidad
c1, c2 = st.columns([60, 40])
with c1:
    dfGastosCategoria = dfDatos.groupby(['mes', 'unidad']).agg({'gastos': 'sum'}).reset_index()
    dfGastosCategoria['mes_nombre'] = dfGastosCategoria['mes'].map(meses_nombres)
    fig = px.line(dfGastosCategoria, x='mes_nombre', y='gastos', title='Gastos por mes y unidad', color='unidad')
    fig.update_layout(xaxis_title='Mes', yaxis_title='Gastos')
    st.plotly_chart(fig, use_container_width=True)

with c2:
    dfGastosCategoria = dfMesActual.groupby('unidad').agg({'gastos': 'sum'}).reset_index().sort_values(by='gastos', ascending=False)
    fig = px.bar(dfGastosCategoria, x='unidad', y='gastos', title=f'Gastos por unidad Mes: {meses_nombres[parMes]}', color='unidad', text_auto=',.0f')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# Gráfico tipo pie por detalle y proyecto
dfGastosPais = dfMesActual.groupby(['detalle', 'proyecto']).agg(cantidad=('orden', 'count'), gastos=('gastos', 'sum')).reset_index()
fig = px.pie(dfGastosPais, color='detalle', values='gastos', facet_col='proyecto', facet_col_wrap=4, height=800, title= f'Gastos por detalle y proyecto {meses_nombres[parMes]}')
st.plotly_chart(fig, use_container_width=True)

# Top productos
st.write("---")  
st.subheader(f'Lista de Top de gastos de mayor/menor importe del mes : {meses_nombres[parMes]}')

c1, c2 = st.columns(2)

# Agrupación con proyecto, unidad y detalle
dfProductosVentas = dfMesActual.groupby(['proyecto', 'unidad', 'detalle']).agg({'gastos': 'sum'}).reset_index()

# Ordenar sin alterar los datos originales
top_mas_valor = dfProductosVentas.sort_values(by='gastos', ascending=False).head(10).copy()
top_menos_valor = dfProductosVentas.sort_values(by='gastos', ascending=True).head(10).copy()

# Aplicar formato solo para mostrar
top_mas_valor['gastos'] = top_mas_valor['gastos'].map(lambda x: f"{x:,.2f}")
top_menos_valor['gastos'] = top_menos_valor['gastos'].map(lambda x: f"{x:,.2f}")

with c1:
    st.subheader('Top 10 gastos más valor')
    st.table(top_mas_valor[['proyecto', 'unidad', 'detalle', 'gastos']])

with c2:
    st.subheader('Top 10 gastos menos valor')
    st.table(top_menos_valor[['proyecto', 'unidad', 'detalle', 'gastos']])


# trabajando con el concepto de AgGrid 
# se busca que el usuario realice los filtros de manera personalizada 
st.write("---")

st.warning("el item que sigue tiene distintas librerias como AgGrid, DataFrame, para generar distintos filtros de los datos para poder analisis la información en crudo")


with st.expander("Datos con la opción de hacer filtros personalizados de la información "):
    @st.cache_data # Decorador para guardar en caché la función y evitar recargas innecesarias
    def cargarDatos():
        dfDatos = pd.read_excel('datos/gastos.xlsx') 
        return dfDatos

    dfDatos=cargarDatos() # Llamamos a la función para cargar los datos


    st.header('Datos para generar filtros personalizados de datos') # Título de la aplicación
    # Creamos dos pestañas para mostrar diferentes configuraciones de AgGrid
    tabBasico,tabGeneral,tabAgrupado = st.tabs(['Tablero-Básico','Tablero-Extendido','Tablero-Agrupado']) # Creamos dos pestañas


    # Configuraciones para la pestaña "AgGrid Básico"
    with tabBasico:
        c1,c2 = st.columns(2) # Creamos dos columnas
        with c1: # Columna 1
            # Creamos la tabla AgGrid    
            AgGrid(dfDatos, # Dataframe a mostrar
                height=500, # Altura de la tabla
                width='100%', # Ancho de la tabla
                )
        with c2:
            st.dataframe(dfDatos,height=500,use_container_width=True) # Mostramos el dataframe en una tabla de Pandas

    # Configuraciones para la pestaña "AgGrid General"
    with tabGeneral:
        # Creamos un objeto GridOptionsBuilder a partir del dataframe
        gob = GridOptionsBuilder.from_dataframe(dfDatos)
        
        gob.configure_default_column(groupable=True, # Habilita la agrupación de columnas
                                    value=True, # Habilita la visualización de valores
                                    enableRowGroup=True,  # Habilita la agrupación por filas
                                    aggFunc='sum', # Función de agregación para las columnas agrupadas (suma)
                                    valueFormatter="parseFloat(value.toLocaleString()).toFixed(2)'", # Formato para los valores numéricos                             
                                    )
        gob.configure_pagination(paginationAutoPageSize=True) # Habilita la paginación automática
        gob.configure_grid_options(suppressAggFuncInHeader = True, # Elimina el nombre de la función de agregación del encabezado
                                    autoGroupColumnDef = {"cellRendererParams": {"suppressCount": True}}, # Desactiva el contador de filas en los grupos
                                    pivotPanelShow= 'onlyWhenPivoting', # Muestra el panel de pivote solo cuando se realiza un pivote
                )
        
        gob.configure_selection(
            'multiple', # Permite la selección múltiple de filas
            use_checkbox=True, # Habilita las casillas de verificación para la selección
            groupSelectsChildren=True,  # Selecciona todos los elementos de un grupo al seleccionar el grupo
            groupSelectsFiltered=True # Selecciona los elementos filtrados de un grupo
        )
        gob.configure_side_bar() # Habilita la barra lateral
        

        # Configuraciones específicas para algunas columnas
        gob.configure_column("proyecto", header_name="Proyecto", filter=True) # Configura la columna "proyecto" con filtro habilitado
        gob.configure_column("unidad", header_name="Unidad", filter=True) # Configura la columna "unidad" con filtro habilitado
        gob.configure_column("detalle", header_name="Detalle", filter=True) # Configura la columna "detalle" con filtro habilitado

        gob.configure_column(
            field="gastos", # Nombre del campo
            header_name="Total Gastos",  # Nombre del encabezado
            type=["numericColumn"], # Tipo de columna (numérica)
            valueFormatter="parseFloat(value.toLocaleString()).toFixed(2)'", # Formato de los valores
            cellStyle= { "fontWeight": 'bold',"color":"blue" } # Estilo de la celda (negrita y color azul)
        )
        gob.configure_column(
            field="gastos", # Nombre del campo
            header_name="Gastos Promedio", # Nombre del encabezado
            type=["numericColumn"], # Tipo de columna
            aggFunc='avg',  # Función de agregación (promedio)
            valueFormatter="parseFloat(value.toLocaleString()).toFixed(2)'" # Formato de los valores
        )
        gridOptions = gob.build() # Construye las opciones de la grilla

        # Crea la tabla AgGrid
        seleccion = AgGrid(
            dfDatos, # Dataframe a mostrar
            gridOptions=gridOptions, # Opciones de la grilla
            height=700, # Altura de la tabla
            width='100%', # Ancho de la tabla
            theme='material',  # Tema de la tabla
            update_mode=GridUpdateMode.SELECTION_CHANGED # Modo de actualización
        )
        
        st.write(seleccion['selected_rows']) # Muestra las filas seleccionadas

    # Configuraciones para la pestaña "AgGrid Agrupado"
    with tabAgrupado:
        # Agrupamos los datos por país, categoría y producto
        dfDatosGrupos = dfDatos.groupby(['proyecto','unidad','detalle']).agg({'gastos':'sum','importe':'sum'}).reset_index().round(2) 
        dfDatosGrupos = dfDatosGrupos.sort_values('gastos',ascending=False) # Ordenamos los datos
        gob2 = GridOptionsBuilder.from_dataframe(dfDatosGrupos) # Creamos un nuevo objeto GridOptionsBuilder para la tabla agrupada
        
        gob2.configure_default_column(groupable=True, # Habilita la agrupación de columnas
                                    value=True, # Habilita la visualización de valores
                                    enableRowGroup=True,  # Habilita la agrupación por filas
                                    aggFunc='sum', # Función de agregación para las columnas agrupadas (suma)
                                    valueFormatter="parseFloat(value.toLocaleString()).toFixed(2)'", # Formato para los valores numéricos                             
                                    )
        # Configuraciones para las columnas
        gob2.configure_column(
            field="proyecto", # Nombre del campo
            hide=True, # Oculta la columna
            header_name="Proyecto", # Nombre del encabezado
            width=150,  # Ancho de la columna
            rowGroup=True,  # Habilita la agrupación por filas para esta columna    
        )
        
        gob2.configure_column(
            field="unidad", # Nombre del campo
            hide=True, # Oculta la columna
            header_name="Unidad", # Nombre del encabezado
            width=150,  # Ancho de la columna
            rowGroup=True,   # Habilita la agrupación por filas para esta columna 
        )
        

        gob2.configure_grid_options(suppressAggFuncInHeader = True, # Elimina el nombre de la función de agregación del encabezado
                                    autoGroupColumnDef = {"cellRendererParams": {"suppressCount": True}}, # Desactiva el contador de filas en los grupos                                
                )
        gridOptions = gob2.build() # Construye las opciones de la grilla
        AgGrid(
            dfDatosGrupos, # Dataframe a mostrar
            gridOptions=gridOptions, # Opciones de la grilla        
            height=500, # Altura de la tabla
            width='100%',  # Ancho de la tabla
            theme='streamlit',  # Tema de la tabla
            fit_columns_on_grid_load=True,  # Ajusta las columnas al cargar la grilla      
        )# Configuraciones para la pestaña "AgGrid Básico"


# --------------- footer -----------------------------
st.write("---")
with st.container():
  #st.write("---")
  st.write("&copy; - derechos reservados -  2025 -  Walter Gómez - FullStack Developer - Data Science - Business Intelligence")
  #st.write("##")
  left, right = st.columns(2, gap='medium', vertical_alignment="bottom")
  with left:
    #st.write('##')
    st.link_button("Mi LinkedIn", "https://www.linkedin.com/in/walter-gomez-fullstack-developer-datascience-businessintelligence-finanzas-python/",use_container_width=True)
  with right: 
     #st.write('##') 
    st.link_button("Mi Porfolio", "https://walter-portfolio-animado.netlify.app/", use_container_width=True)
      