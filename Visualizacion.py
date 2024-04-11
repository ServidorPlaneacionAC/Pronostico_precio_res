import pandas as pd
# from Class_Google_Sheet_STL import ConexionGoogleSheets
from Transformacion_datos import pronosticar_precio_reses
import streamlit as st
from openpyxl.styles import PatternFill

class Visualizacion_pronostico_reses:
    '''
    clase que permite cargar elementos visualizar la transformación del pronostico de reses,
    se apoya en la clase transformación para generar el pronostico y transformar los datos
    '''
    def __init__(self) -> None:
        '''
        dataframe_serie_tiempo: (DataFrame) Serie de tiempo como se usa desde compras
        columnas_df: (list) Campos obligatorios para cargar y que funcione, son las columnas de dataframe_serie_tiempo
        '''
        self.dataframe_serie_tiempo=None
        self.df_regresores=None
        self.columnas_df=['Año','Semana','Cantidad_Reses','Precio_Planta']
        self.mostrar_navegabilidad()

    def pantalla_principal(self) -> None:
        '''
        Genera la pantalla principal, habilita la impresión del df de muestra, carga y trasnformación de datos
        '''
        st.title("Pronóstico de reses")
        self.dataframe_serie_tiempo=self.habilitar_carga_datos("Cargar información XLSX")
        # self.df_regresores=self.habilitar_carga_datos("Cargar regresores")
        self.transformar_datos()

    def mostrar_navegabilidad(self):
        st.sidebar.header("Navegación")
        page = st.sidebar.radio("Ir a:", ["Inicio", "Archivos de muestra","¿Cómo funciona?"])

        if page == "Inicio":
            self.pantalla_principal()
        elif page == "Archivos de muestra":
            st.title("Archivos de muestra")  
            st.write('Cargar datos de una zona en específica')          
            self.generacion_df_muestra(self.columnas_df)
            st.write('Cargar datos de una diferentes zonas indicando en la columna categoría la zona correspondiente')    
            self.generacion_df_muestra(self.columnas_df+['Categoria'])
            # self.generacion_df_muestra(['Año','Semana','Regresor_Externo1','Regresor_Externo2','Regresor_Externo3'])
        elif page=="¿Cómo funciona?":
            st.title("¿Cómo funciona?") 
            st.subheader('Carga de datos')
            st.write('''Para generar un pronóstico es necesario suministrar información 
                     que sirva de soporte para los nuevos datos a generar, en este caso es necesario 
                     cargar la historia semana a semana de las reses negociadas y su precio, el formato 
                     establecido está indicado en el segmento "Archivos de muestra", allí se muestran
                      algunas tablas que se pueden descargar como formato csv, los titulos deben ser respetados
                      y la información que se cargue debe estar revisada para generar un pronóstico aceptable, 
                      una vez se descarguen los archivos de muestra, se llenan con la información correspondiente,
                      se guardan como archvos "xlsx" y se cargan en los botones habilitados en el segmento "Inicio". 
                     Es posible cargar una serie de tiempo con distintas categorias, al hacer esto se generará un modelo
                     y un pronóstico para cada una de ellas.
                     
                      ''')
            
            st.subheader('¿Qué hay detrás?')
            st.write('''Cuando se cargan los datos, la herramienta genera el mejor modelo de serie de tiempo 
                     que se puede ajustar a los datos cargados, genera el prónostico y lo grafica con un intervalo de
                     confianza del 95%, se puede mover algunos parametros como la cantidad de datos a ver de la serie real
                     y la cantidad de datos a pronosticar; el modelo generado tambien puede ser modificado, agregandole un componente
                     estacional o un atributo de tendencia.  ''')                   
            st.write('''Siendo un poco mas técnicos, Cuando se habla del "mejor modelo" en el contexto de esta función, 
                     se refiere al modelo que mejor se ajusta a los datos de la serie temporal proporcionada. 
                     Esto significa que el modelo seleccionado tiene la capacidad de hacer predicciones precisas 
                     para valores futuros basados en el patrón histórico de los datos. El proceso de encontrar el 
                     "mejor modelo" generalmente implica probar y comparar diferentes combinaciones de parámetros 
                     del modelo (como el orden AR, el orden de diferenciación, el orden MA, etc.) y seleccionar 
                     aquel que minimiza una métrica de evaluación, como el error cuadrático medio (MSE) o el 
                     criterio de información bayesiana (BIC) - Usado actualmente -.  ''')                   
            st.write(''' Al ser una función de ajuste automático, puede generar varios tipos de modelos, algunos de los cuales son:
                     *ARIMA* (Autoregressive Integrated Moving Average): Un modelo que combina componentes autoregresivas, de media móvil y de diferenciación para capturar la estructura de la serie temporal.
                     *SARIMA* (Seasonal ARIMA): Similar a ARIMA, pero con la capacidad de modelar patrones estacionales en los datos.
                     *SARIMAX* (Seasonal ARIMA with exogenous variables): Una extensión de SARIMA que permite incluir variables exógenas que pueden influir en la serie temporal.
                     *ARIMAX* (ARIMA with exogenous variables): Similar a SARIMAX pero sin componente estacional.''')                   
            st.write('''
                     Cada uno de estos modelos tiene sus propias características y puede ser útil en diferentes 
                     situaciones dependiendo de la naturaleza de los datos y los patrones que se intenten capturar. La función usada 
                     ayuda a identificar el modelo óptimo entre estas opciones, teniendo en cuenta la complejidad de los datos y la 
                     precisión de las predicciones.  
                     ''')
            
            st.subheader('Soporte')
            st.write('''Este desarrollo fue generado por el equipo de modelación del negocio cárnico, si hay algún
                     requerimiento, duda o comentario sobre el mismo puede ser a través del líder del equipo
                     Lucas Ramirez, así mismo si se tiene alguna necesidad de desarrollo similar al presente puede
                     comunicarlo con la misma persona o a través del siguente enlace  ''')
            st.markdown('Formulario de soporte equipo modelación negocio cárnico https://docs.google.com/forms/d/e/1FAIpQLSfNVT7yFcuaWHvZ_V-wNlu02tPVvbCNA6nA0I1Bhcj5D4MRkQ/viewform')
            

    def generacion_df_muestra(self,lista_claves) -> None:
        '''
        Genera un e imprime Df a partir de una lista de campos, su indice es lista_claves[0] 
        lista_claves: (list) lista de columnas del DF
        '''
        diccionario = {}        
        for clave in lista_claves:
            diccionario[clave] = ''           
        df=pd.DataFrame([diccionario])
        df.set_index(df.columns[0], inplace=True)
        st.write(df)
     
    def habilitar_carga_datos(self,mensaje):
        '''
        Habilita el boton de carga de archivos y retorna un df con la información del archivo cargado
        '''
        data_file = st.file_uploader(mensaje, type=["XLSX"]) 
        if data_file is not None:
            return pd.read_excel(data_file)

    def transformar_datos(self) -> None:
        '''
        Valida los datos cargados por el usuario,
        usa la clase pronosticar_precio_reses para seguir su flujo, generando botones
        para manipular la vista y periodos a pronosticar
        - transformar los datos
        - generar mejor el modelo
        - generar pronostico
        - imprimir el pronostico
        - mostrar información del mejor modelo
        '''
        if self.dataframe_serie_tiempo is not None:
            if all(col in self.dataframe_serie_tiempo.columns for col in self.columnas_df+['Categoria']):
                categorias_ingresadas=self.dataframe_serie_tiempo['Categoria'].unique()
                st.info(f'Se ha cargado información para las siguientes categorías {categorias_ingresadas}')
                categoria_seleccionada = st.selectbox('Selecciona una Zona:', categorias_ingresadas)
                # st.info(operar_pronostico)
                self.operar_pronostico(categoria=categoria_seleccionada)
            else:
                if all(col in self.dataframe_serie_tiempo.columns for col in self.columnas_df):   
                    self.operar_pronostico()            
                else:
                    st.error('El formato del archivo cargado no coincide con el esperado')

    def operar_pronostico(self,categoria=None):
        if categoria is None:
            trans=pronosticar_precio_reses(self.dataframe_serie_tiempo)
        else:
            trans=pronosticar_precio_reses(self.dataframe_serie_tiempo[self.dataframe_serie_tiempo['Categoria']==categoria])     
        trans.combinar_partidas_reses()
        col1, col2 = st.columns(2)
        with col1:
            mostrar_serie_real = st.slider("Periodos a mostrar", 5, trans.df.shape[0], trans.df.shape[0], 1)
            trans.seasonal = st.selectbox('Agregar componente estacional:', [True,False])
        with col2:
            periodos_predecir = st.slider("Periodos a pronosticar", 1, trans.df.shape[0],10, 1)
            trans.trend = st.selectbox('Agregar componente de tendencia:', [None,'c','t','ct'])
        trans.generar_modelo()
        trans.periodos_predecir=periodos_predecir
        trans.elementos_mostrar=mostrar_serie_real     
        trans.generar_pronostico()
        trans.imprimir_pronostico()
        st.write(trans.llevar_pronostico_a_df())
        st.info('El mejor modelo encontrado es')
        st.write(trans.modelo_arima.summary())     
