import pandas as pd
# from Class_Google_Sheet_STL import ConexionGoogleSheets
from Transformacion_datos import transformacion
import streamlit as st

class Visualizacion_pronostico_reses:
    def __init__(self) -> None:
        self.dataframe_serie_tiempo=None

    def pantalla_principal(self) -> None:
        st.title("Pronóstico de reses")
        self.generacion_df_muestra(['Periodo','Cantidad_Reses','Precio_Planta'])
        self.habilitar_carga_datos()
        if self.dataframe_serie_tiempo is not None:
            trans=transformacion(self.dataframe_serie_tiempo)
            trans.combinar_partidas_reses()

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