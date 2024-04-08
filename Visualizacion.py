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
        self.columnas_df=['Año','Semana','Cantidad_Reses','Precio_Planta']

    def pantalla_principal(self) -> None:
        '''
        Genera la pantalla principal, habilita la impresión del df de muestra, carga y trasnformación de datos
        '''
        st.title("Pronóstico de reses")
        self.generacion_df_muestra(self.columnas_df)
        self.generacion_df_muestra(self.columnas_df+['Categoria'])
        self.habilitar_carga_datos()
        self.transformar_datos()

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
    
    def habilitar_carga_datos(self) -> None:
        '''
        Habilita el boton de carga de archivos e inicializa la variable global dataframe_serie_tiempo
        '''
        data_file = st.file_uploader("Cargar información XLSX", type=["XLSX"]) 
        if data_file is not None:
            self.dataframe_serie_tiempo=pd.read_excel(data_file)

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
                categoria_seleccionada = st.selectbox('Selecciona una opción:', categorias_ingresadas)
                # st.info(operar_pronostico)
                self.operar_pronostico(categoria=categoria_seleccionada)
                # trans=pronosticar_precio_reses(self.dataframe_serie_tiempo[self.dataframe_serie_tiempo['Categoria']==categoria_seleccionada])
                # trans.combinar_partidas_reses()
                # trans.generar_modelo()
                # col1, col2 = st.columns(2)
                # with col1:
                #     mostrar_serie_real = st.slider("Periodos a mostrar", 5, trans.df.shape[0], trans.df.shape[0], 1)
                # with col2:
                #     periodos_predecir = st.slider("Periodos a pronosticar", 1, trans.df.shape[0],10, 1)
                # trans.periodos_predecir=periodos_predecir
                # trans.elementos_mostrar=mostrar_serie_real     
                # trans.generar_pronostico()
                # trans.imprimir_pronostico()
                # st.write(trans.llevar_pronostico_a_df())
                # st.info('El mejor modelo encontrado es')
                # st.write(trans.modelo_arima.summary())

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
        trans.generar_modelo()
        col1, col2 = st.columns(2)
        with col1:
            mostrar_serie_real = st.slider("Periodos a mostrar", 5, trans.df.shape[0], trans.df.shape[0], 1)
        with col2:
            periodos_predecir = st.slider("Periodos a pronosticar", 1, trans.df.shape[0],10, 1)
        trans.periodos_predecir=periodos_predecir
        trans.elementos_mostrar=mostrar_serie_real     
        trans.generar_pronostico()
        trans.imprimir_pronostico()
        st.write(trans.llevar_pronostico_a_df())
        st.info('El mejor modelo encontrado es')
        st.write(trans.modelo_arima.summary())     
