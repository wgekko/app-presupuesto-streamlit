import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# Librería para manipulación y análisis de datos. Instalación: pip install pandas
import pandas as pd
# Librería para crear tablas interactivas. Instalación: pip install streamlit-aggrid
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
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
    page_icon="img/report.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# """ imagen de background"""


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

# """ imagen de sidebar"""


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

# -------------- animacion con css de los botones  ------------------------
with open('asset/styles.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


# Título con nombre del mes en lugar del número
st.header(f'Tablero de control de gastos - Proyecto Inmobiliario 2025')

st.write("---")

with st.expander("Análisis de Presupuesto filtrado por Mes/Proyecto"):
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
        st.write("---")
        st.sidebar.header("Filtros para Datos Mes/Proyecto")
        parMes = st.selectbox('Seleccione Mes Analizar', options=dfDatos['mes'].unique(
        ), index=0, format_func=lambda x: meses_nombres[x])
        parProyecto = st.multiselect(
            'Selecciones Proyecto', options=dfDatos['proyecto'].unique())

    # Aplicar filtros
    dfDatos = dfDatos[dfDatos['anio'] == 2025]
    if parMes:
        dfDatos = dfDatos[dfDatos['mes'] <= parMes]
    if len(parProyecto) > 0:
        dfDatos = dfDatos[dfDatos['proyecto'].isin(parProyecto)]

    # Datos del mes actual y anterior
    dfMesActual = dfDatos[dfDatos['mes'] == parMes]
    if parMes > 1:
        dfMesAnterior = dfDatos[dfDatos['mes'] == parMes - 1]
    else:
        dfMesAnterior = dfDatos[dfDatos['mes'] == parMes]

    # Cálculo de métricas de gastos
    gastos_total = dfMesActual['gastos'].sum()
    gastos_pagado = dfMesActual[dfMesActual['estado']
                                == 'pagado']['gastos'].sum()
    gastos_pendiente = dfMesActual[dfMesActual['estado']
                                   != 'pagado']['gastos'].sum()
    porcentaje_pagado = (gastos_pagado / gastos_total *
                         100) if gastos_total > 0 else 0
    gastos_promedio = dfDatos.groupby('mes')['gastos'].sum().mean()

    # Cálculo de métricas y visualización (sin cambios)

    # Título con nombre del mes en lugar del número
    # st.header(f'Tablero de control de gastos - Proyecto Inmobiliario 2025')
    df = pd.read_excel("datos/gastos.xlsx")

    # Preprocesamiento
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['mes'] = df['fecha'].dt.strftime('%m/%Y')

    st.subheader(
        f'Indicador de Ejecución de Gastos del mes de **{meses_nombres[parMes]}**')

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
        st.metric("Gastos totales Pesos",
                  f'$ {productosAct:,.0f} ', f'{variacion:,.0f}')
    with c2:
        ordenesAct = dfMesActual['orden'].count()
        ordenesAnt = dfMesAnterior['orden'].count()
        variacion = ordenesAct - ordenesAnt
        st.metric("Proyeccion cantidad de gastos",
                  f'{ordenesAct:.0f}', f'{variacion:.1f}')
    with c3:
        ventasAct = dfMesActual['gastos'].sum()
        ventasAnt = dfMesAnterior['gastos'].sum()
        variacion = ventasAct - ventasAnt
        st.metric("Gastos totales",
                  f'US$ {ventasAct:,.0f}', f'{variacion:,.0f}')

    st.write("---")

    # NUEVA SECCIÓN: Gastos por pagar hasta fin de mes actual
    st.subheader(
        f"Gastos Pendientes Próximos Periodos por Pagar de {meses_nombres[parMes]} ")
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
    dfPendiente = dfDatos[(dfDatos['estado'] == 'pendiente')
                          & (dfDatos['fecha'].notna())]

    # Gastos con vencimiento próxima semana
    pendiente_semana = dfPendiente[(dfPendiente['fecha'] > hoy) & (
        dfPendiente['fecha'] <= prox_semana)]
    pendiente_mes = dfPendiente[(dfPendiente['fecha'] > hoy) & (
        dfPendiente['fecha'] <= fin_de_mes)]

    # Agrupamos por proyecto
    dfSemana = pendiente_semana.groupby(
        'proyecto')['gastos'].sum().reset_index(name='Pendiente Semana')
    dfMes = pendiente_mes.groupby('proyecto')['gastos'].sum(
    ).reset_index(name='Pendiente Fin de Mes')

    # Unimos todos los proyectos posibles
    dfResumenPendiente = pd.DataFrame(
        dfDatos['proyecto'].unique(), columns=['proyecto'])
    dfResumenPendiente = dfResumenPendiente.merge(
        dfSemana, on='proyecto', how='left')
    dfResumenPendiente = dfResumenPendiente.merge(
        dfMes, on='proyecto', how='left')
    dfResumenPendiente = dfResumenPendiente.fillna(0)

    # Formato de dos decimales visibles
    dfResumenPendiente['Pendiente Semana'] = dfResumenPendiente['Pendiente Semana'].apply(
        lambda x: f"{x:,.2f}")
    dfResumenPendiente['Pendiente Fin de Mes'] = dfResumenPendiente['Pendiente Fin de Mes'].apply(
        lambda x: f"{x:,.2f}")

    hoy_str = hoy.strftime("%d/%m/%Y")
    # Mostrar
    st.subheader(f'Gastos Pendientes Próximos Periodos desde : {hoy_str}')
    st.table(dfResumenPendiente)
    st.write("---")

    # Gráfico línea de Gastos por mes
    c1, c2 = st.columns([60, 40])
    with c1:
        dfGastosMes = dfDatos.groupby('mes').agg(
            {'gastos': 'sum'}).reset_index()
        dfGastosMes['mes_nombre'] = dfGastosMes['mes'].map(meses_nombres)
        fig = px.line(dfGastosMes, x='mes_nombre',
                      y='gastos', title='Gastos por mes')
        fig.update_layout(xaxis_title='Mes', yaxis_title='Gastos')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        dfGastosPais = dfMesActual.groupby('proyecto').agg(
            {'gastos': 'sum'}).reset_index().sort_values(by='gastos', ascending=False)
        fig = px.bar(dfGastosPais, x='proyecto', y='gastos',
                     title=f'Gastos por detalle Mes: {meses_nombres[parMes]}', color='proyecto', text_auto=',.0f')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.write("---")
    # Gráfico línea por unidad
    c1, c2 = st.columns([60, 40])
    with c1:
        dfGastosCategoria = dfDatos.groupby(
            ['mes', 'unidad']).agg({'gastos': 'sum'}).reset_index()
        dfGastosCategoria['mes_nombre'] = dfGastosCategoria['mes'].map(
            meses_nombres)
        fig = px.line(dfGastosCategoria, x='mes_nombre', y='gastos',
                      title='Gastos por mes y unidad', color='unidad')
        fig.update_layout(xaxis_title='Mes', yaxis_title='Gastos')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        dfGastosCategoria = dfMesActual.groupby('unidad').agg(
            {'gastos': 'sum'}).reset_index().sort_values(by='gastos', ascending=False)
        fig = px.bar(dfGastosCategoria, x='unidad', y='gastos',
                     title=f'Gastos por unidad Mes: {meses_nombres[parMes]}', color='unidad', text_auto=',.0f')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Gráfico tipo pie por detalle y proyecto
    dfGastosPais = dfMesActual.groupby(['detalle', 'proyecto']).agg(
        cantidad=('orden', 'count'), gastos=('gastos', 'sum')).reset_index()
    fig = px.pie(dfGastosPais, color='detalle', values='gastos', facet_col='proyecto',
                 facet_col_wrap=4, height=800, title=f'Gastos por detalle y proyecto {meses_nombres[parMes]}')
    st.plotly_chart(fig, use_container_width=True)

    # Top productos
    st.write("---")
    st.subheader(
        f'Lista de Top de gastos de mayor/menor importe del mes : {meses_nombres[parMes]}')

    c1, c2 = st.columns(2)

    # Agrupación con proyecto, unidad y detalle
    dfProductosVentas = dfMesActual.groupby(['proyecto', 'unidad', 'detalle']).agg({
        'gastos': 'sum'}).reset_index()

    # Ordenar sin alterar los datos originales
    top_mas_valor = dfProductosVentas.sort_values(
        by='gastos', ascending=False).head(10).copy()
    top_menos_valor = dfProductosVentas.sort_values(
        by='gastos', ascending=True).head(10).copy()

    # Aplicar formato solo para mostrar
    top_mas_valor['gastos'] = top_mas_valor['gastos'].map(
        lambda x: f"{x:,.2f}")
    top_menos_valor['gastos'] = top_menos_valor['gastos'].map(
        lambda x: f"{x:,.2f}")

    with c1:
        st.subheader('Top 10 gastos más valor')
        st.table(top_mas_valor[['proyecto', 'unidad', 'detalle', 'gastos']])

    with c2:
        st.subheader('Top 10 gastos menos valor')
        st.table(top_menos_valor[['proyecto', 'unidad', 'detalle', 'gastos']])

st.write("---")

with st.expander("Acceso a Presupuesto con Gráfico Animado"):
    # Cargar datos
    df = pd.read_excel("datos/gastos.xlsx")

    # Preprocesamiento
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['mes'] = df['fecha'].dt.strftime('%m/%Y')

    # Filtros dinámicos en la barra lateral
    # --- Controles en barra lateral ---
    with st.sidebar:
        st.write("---")
        st.sidebar.header("Filtros para gráfico animado")
        proyecto_seleccionado = st.sidebar.selectbox(
            "Selecciona un proyecto", df['proyecto'].unique())
        modo_comparacion = st.sidebar.radio(
            "Comparar por:", ['estado', 'detalle'])
        mostrar_acumulado = st.sidebar.checkbox(
            "Mostrar totales acumulados", value=False)

    # --- Filtrado y agrupación ---
    df = df[df['proyecto'] == proyecto_seleccionado]
    columna_comparacion = modo_comparacion
    agrupado = df.groupby(['mes', 'unidad', columna_comparacion], as_index=False)[
        'gastos'].sum()

    if mostrar_acumulado:
        agrupado['gastos'] = agrupado.sort_values('mes').groupby(
            ['unidad', columna_comparacion])['gastos'].cumsum()

    # Renombrar columnas para ipyvizzu
    agrupado.columns = ['Mes', 'Unidad', 'Comparacion', 'Gastos']

    # --- Crear gráfico animado ---
    def create_chart():
        chart = Chart(width="800px", height="600px",
                      display=DisplayTarget.MANUAL)
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

st.write("---")

with st.expander("Acesso a filtado de gastos por fecha y Proyecto"):

    st.title("Dashboard Interactivo de Gastos del Proyecto")
    # Cargar los datos
    ruta_archivo = "datos/gastos.xlsx"
    dfGastos = pd.read_excel(ruta_archivo, parse_dates=["fecha"])

    # Paleta de colores
    paletacolor = px.colors.qualitative.Plotly
    color_naranja = ["orange"]

    # Agrupaciones de fecha
    def generarGruposFecha(df, columnaFecha):
        df["Trimestre"] = df[columnaFecha].dt.to_period(
            'Q').astype(str).str.replace("Q", "T")
        df["Mes"] = df[columnaFecha].dt.to_period('M').astype(str)
        df["Año"] = df[columnaFecha].dt.to_period('Y').astype(str)
        return df

    dfGastos = generarGruposFecha(dfGastos, "fecha")

    # Gráfico por fecha con botones de granularidad
    figFecha = px.bar(dfGastos.groupby("fecha")["gastos"].sum().reset_index(
    ), x="fecha", y="gastos", title="Gastos por Día", color_discrete_sequence=color_naranja)
    figFecha.update_layout(
        updatemenus=[
            {
                'type': 'buttons',
                'direction': 'left',
                'buttons': [
                    {
                        'args': [{"x": [dfGastos.groupby("fecha")["fecha"].first()],
                                  "y": [dfGastos.groupby("fecha")["gastos"].sum()],
                                  "type": "bar", "marker.color": "green"},
                                 {"title": "Gastos por Día"}],
                        'label': "Día",
                        'method': 'update'

                    },
                    {
                        'args': [{"x": [dfGastos.groupby("Mes")["Mes"].first()],
                                  "y": [dfGastos.groupby("Mes")["gastos"].sum()],
                                  "type": "bar", "marker.color": "green"},
                                 {"title": "Gastos por Mes"}],
                        'label': "Mes",
                        'method': 'update'

                    },
                    {
                        'args': [{"x": [dfGastos.groupby("Trimestre")["Trimestre"].first()],
                                  "y": [dfGastos.groupby("Trimestre")["gastos"].sum()],
                                  "type": "bar", "marker.color": "green"},
                                 {"title": "Gastos por Trimestre"}],
                        'label': "Trimestre",
                        'method': 'update',

                    },
                ],
                'showactive': True,
                'x': 0.5,
                'xanchor': 'center',
                'y': 1.2,
                'yanchor': 'top',
                'font': {'color': 'green'}
            }
        ]
    )

    # Gráfico por categorías (por ejemplo, proyecto/unidad/estado)
    figGrupo = px.bar(dfGastos.groupby("proyecto")["gastos"].sum().reset_index(
    ), x="proyecto", y="gastos", title="Gastos por Proyecto", color_discrete_sequence=color_naranja)
    figGrupo.update_layout(
        updatemenus=[
            {
                'type': 'buttons',
                'direction': 'left',
                'buttons': [
                    {
                        'args': [{"x": [dfGastos.groupby("proyecto")["proyecto"].first()],
                                  "y": [dfGastos.groupby("proyecto")["gastos"].sum()],
                                  "type": "bar", "marker.color": "orange"},
                                 {"title": "Gastos por Proyecto"}],
                        'label': "Proyecto",
                        'method': 'update'
                    },
                    {
                        'args': [{"x": [dfGastos.groupby("unidad")["unidad"].first()],
                                  "y": [dfGastos.groupby("unidad")["gastos"].sum()],
                                  "type": "bar", "marker.color": "orange"},
                                 {"title": "Gastos por Unidad"}],
                        'label': "Unidad",
                        'method': 'update'
                    },
                    {
                        'args': [{"x": [dfGastos.groupby("estado")["estado"].first()],
                                  "y": [dfGastos.groupby("estado")["gastos"].sum()],
                                  "type": "bar", "marker.color": "orange"},
                                 {"title": "Gastos por Estado"}],
                        'label': "Estado",
                        'method': 'update'
                    },
                    {
                        'args': [{"x": [dfGastos.groupby("detalle")["detalle"].first()],
                                  "y": [dfGastos.groupby("detalle")["gastos"].sum()],
                                  "type": "bar", "marker.color": "orange"},
                                 {"title": "Gastos por Detalle"}],
                        'label': "Detalle",
                        'method': 'update',

                    },
                ],
                'showactive': True,
                'x': 0.5,
                'xanchor': 'center',
                'y': 1.2,
                'yanchor': 'top',
                'font': {'color': 'orange'}
            }
        ]
    )

    # Mostrar gráficos
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.plotly_chart(figFecha, use_container_width=True)
    with c2:
        with st.container(border=True):
            st.plotly_chart(figGrupo, use_container_width=True)

    # Drill-down interactivo por categoría/detalle
    if "categoriaSeleccionada" not in st.session_state:
        st.session_state.categoriaSeleccionada = None

    @st.fragment
    def generarDrillDownGastos():
        placeholder = st.empty()
        with placeholder:
            with st.container(border=True):
                if st.session_state.categoriaSeleccionada is not None:
                    dfDetalle = dfGastos[dfGastos["proyecto"]
                                         == st.session_state.categoriaSeleccionada]
                    parDrillUp = st.button("⬆️ Regresar")
                    figDrill = px.bar(
                        dfDetalle.groupby("detalle")[
                            "gastos"].sum().reset_index(),
                        x="detalle",
                        y="gastos",
                        title=f"Gastos por detalle del proyecto {st.session_state.categoriaSeleccionada}",
                        color_discrete_sequence=color_naranja
                    )
                    if parDrillUp:
                        st.session_state.categoriaSeleccionada = None
                else:
                    dfGrupo = dfGastos.groupby("proyecto")[
                        "gastos"].sum().reset_index()
                    figDrill = px.bar(
                        dfGrupo,
                        x="proyecto",
                        y="gastos",
                        title="Gastos por proyecto",
                        color="proyecto",
                        color_discrete_sequence=paletacolor
                    )

                eventos = st.plotly_chart(
                    figDrill, use_container_width=True, on_select="rerun")
                if len(eventos.selection.points) > 0:
                    st.session_state.categoriaSeleccionada = eventos.selection.points[0]["label"]
                    colorProyecto = dfGrupo["proyecto"].unique()
                    st.session_state.colorDetalle = paletacolor[colorProyecto.tolist().index(
                        st.session_state.categoriaSeleccionada)]
                    st.rerun(scope="fragment")
                else:
                    st.session_state.categoriaSeleccionada = None

    # Mostrar el gráfico interactivo drill-down completo
    st.warning(
        "doble click sobre las barra del proyecto que desee ver el detalle de gastos")
    generarDrillDownGastos()

st.write("---")

with st.expander("Datos con la opción de hacer filtros personalizados de la información"):
    st.warning("El tablero básico incorpora la librería AgGrid, abriendo la posiblidad de personalizar los filtros")

    @st.cache_data
    def cargarDatos():
        dfDatos = pd.read_excel('datos/gastos.xlsx')
        return dfDatos

    dfDatos = cargarDatos()

    st.header('Datos para generar filtros personalizados de datos')
    tabBasico, tabGeneral, tabAgrupado = st.tabs(['Tablero-Básico', 'Tablero-Extendido', 'Tablero-Agrupado'])

    # Tablero Básico (solo AgGrid)
    with tabBasico:
        AgGrid(dfDatos, height=500, width='100%')

    # Tablero General (AgGrid extendido con opciones de filtrado)
    with tabGeneral:
        gob = GridOptionsBuilder.from_dataframe(dfDatos)
        gob.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', valueFormatter="parseFloat(value.toLocaleString()).toFixed(2)'")
        gob.configure_pagination(paginationAutoPageSize=True)
        gob.configure_grid_options(suppressAggFuncInHeader=True, autoGroupColumnDef={"cellRendererParams": {"suppressCount": True}}, pivotPanelShow='onlyWhenPivoting')
        gob.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True)
        gob.configure_side_bar()

        gob.configure_column("proyecto", header_name="Proyecto", filter=True)
        gob.configure_column("unidad", header_name="Unidad", filter=True)
        gob.configure_column("detalle", header_name="Detalle", filter=True)
        gob.configure_column(field="gastos", header_name="Total Gastos", type=["numericColumn"], valueFormatter="parseFloat(value.toLocaleString()).toFixed(2)'", cellStyle={"fontWeight": 'bold', "color": "blue"})
        gob.configure_column(field="gastos", header_name="Gastos Promedio", type=["numericColumn"], aggFunc='avg', valueFormatter="parseFloat(value.toLocaleString()).toFixed(2)'")

        gridOptions = gob.build()

        seleccion = AgGrid(
            dfDatos,
            gridOptions=gridOptions,
            height=700,
            width='100%',
            theme='material',
            update_mode=GridUpdateMode.SELECTION_CHANGED
        )

        st.write(seleccion['selected_rows'])

    # Tablero Agrupado
    with tabAgrupado:
        dfDatosGrupos = dfDatos.groupby(['proyecto', 'unidad', 'detalle']).agg({'gastos': 'sum', 'importe': 'sum'}).reset_index().round(2)
        dfDatosGrupos = dfDatosGrupos.sort_values('gastos', ascending=False)

        gob2 = GridOptionsBuilder.from_dataframe(dfDatosGrupos)
        gob2.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', valueFormatter="parseFloat(value.toLocaleString()).toFixed(2)'")

        gob2.configure_column(field="proyecto", hide=True, header_name="Proyecto", width=150, rowGroup=True)
        gob2.configure_column(field="unidad", hide=True, header_name="Unidad", width=150, rowGroup=True)
        gob2.configure_grid_options(suppressAggFuncInHeader=True, autoGroupColumnDef={"cellRendererParams": {"suppressCount": True}})

        gridOptions = gob2.build()

        AgGrid(
            dfDatosGrupos,
            gridOptions=gridOptions,
            height=500,
            width='100%',
            theme='streamlit',
            fit_columns_on_grid_load=True
        )


# --------------- footer -----------------------------
st.write("---")
with st.container():
    # st.write("---")
    st.write("&copy; - derechos reservados -  2025 -  Walter Gómez - FullStack Developer - Data Science - Business Intelligence")
    # st.write("##")
    left, right = st.columns(2, gap='medium', vertical_alignment="bottom")
    with left:
        # st.write('##')
        st.link_button(
            "Mi LinkedIn", "https://www.linkedin.com/in/walter-gomez-fullstack-developer-datascience-businessintelligence-finanzas-python/")
    with right:
       # st.write('##')
        st.link_button(
            "Mi Porfolio", "https://walter-portfolio-animado.netlify.app/")
