import pandas as pd
import streamlit as st
from datetime import datetime
import pmdarima as pm
from pmdarima import auto_arima
import matplotlib.pyplot as plt

class pronosticar_precio_reses:
    def __init__(self,df) -> None:
        self.df = df
        self.modelo_arima=None
        self.periodos_predecir=10
        self.elementos_mostrar=10

    def combinar_partidas_reses(self) -> None:
        self.df['Periodo']=[datetime.strptime(f"{int(fila['Año'])} {int(fila['Semana'])}-1", "%Y %W-%w") for _, fila in self.df.iterrows()]
        self.df['Precio_Planta']=self.df['Cantidad_Reses']*self.df['Precio_Planta']
        
        self.df = self.df.groupby(['Periodo']).agg({
            'Cantidad_Reses': 'sum',
            'Precio_Planta': 'sum'
        }).reset_index()
        self.df['Precio_final']=self.df['Precio_Planta']/self.df['Cantidad_Reses']
        self.df=self.df[['Periodo','Precio_final']]
        self.df=self.df.set_index('Periodo')
        self.df = self.df[~self.df.index.duplicated(keep='first')]        

    def generar_modelo(self) -> None:
        serie_tiempo = self.df
        self.modelo_arima = pm.auto_arima(serie_tiempo)

    def generar_pronostico(self) -> None:        
        st.set_option('deprecation.showPyplotGlobalUse', False)
        self.pronostico, self.intervalo_confianza = self.modelo_arima.predict(n_periods=self.periodos_predecir, return_conf_int=True)
        self.proximo_periodo = pd.date_range(start=self.df.index[-1], periods=self.periodos_predecir, freq='W')

    def imprimir_pronostico(self) -> None:   
        inicio_serie_real=self.df.shape[0]-self.elementos_mostrar
        plt.figure(figsize=(12, 6))
        plt.plot(self.df.index[inicio_serie_real:], self.df[inicio_serie_real:], label='Datos reales', color='blue')
        plt.plot(self.proximo_periodo, self.pronostico, label='Pronóstico', color='red')
        plt.fill_between(self.proximo_periodo, self.intervalo_confianza[:, 0], self.intervalo_confianza[:, 1], color='pink', alpha=0.3)
        plt.title('Comparación de pronóstico vs. datos reales')
        plt.xlabel('Fecha')
        plt.ylabel('Valor')
        plt.legend()
        st.pyplot()
        
    def llevar_pronostico_a_df(self) -> DataFrame:
        df_resultado=pd.DataFrame({'Periodo':self.proximo_periodo,'Pronóstico':self.pronostico})
        df_resultado=df_resultado.set_index('Periodo')
        return df_resultado

