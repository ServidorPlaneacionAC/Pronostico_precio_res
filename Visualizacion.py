import pandas as pd
# from Class_Google_Sheet_STL import ConexionGoogleSheets
from Transformacion_datos import transformacion
import streamlit as st
from openpyxl.styles import PatternFill

class Visualizacion_pronostico_reses:
    def __init__(self) -> None:
        self.dataframe_serie_tiempo=None
        self.columnas_df=['Año','Semana','Cantidad_Reses','Precio_Planta']

    def pantalla_principal(self) -> None:
        st.title("Pronóstico de reses")
        self.generacion_df_muestra(self.columnas_df)
        self.habilitar_carga_datos()
        self.transformar_datos()

    def generacion_df_muestra(self,lista_claves) -> None:
        diccionario = {}
        
        # Iteramos sobre la lista de claves
        for clave in lista_claves:
            # Asignamos un valor inicial None a cada clave
            diccionario[clave] = ''    
        
        df=pd.DataFrame([diccionario])
        df.set_index(df.columns[0], inplace=True)
        st.write(df)
    
    def habilitar_carga_datos(self) -> None:
        data_file = st.file_uploader("Cargar información XLSX", type=["XLSX"]) 
        if data_file is not None:
            self.dataframe_serie_tiempo=pd.read_excel(data_file)

    def transformar_datos(self) -> None:
        if self.dataframe_serie_tiempo is not None:
            if all(col in self.dataframe_serie_tiempo.columns for col in self.columnas_df):
                trans=transformacion(self.dataframe_serie_tiempo)
                trans.combinar_partidas_reses()
                trans.generar_modelo()
                col1, col2 = st.columns(2)
                with col1:
                    mostrar_serie_real = st.slider("Periodos a mostrar", 10, trans.df.shape[0], trans.df.shape[0], 1)
                with col2:
                    periodos_predecir = st.slider("Periodos a pronosticar", 1, trans.df.shape[0],10, 1)
                trans.periodos_predecir=periodos_predecir
                self.elementos_mostrar=mostrar_serie_real     
                trans.generar_pronostico()
                trans.imprimir_pronostico()
                st.write(llevar_pronostico_a_df())
                st.info('El mejor modelo encontrado es')
                st.write(trans.modelo_arima.summary())

            else:
                st.error('El formato del archivo cargado no coincide con el esperado')

