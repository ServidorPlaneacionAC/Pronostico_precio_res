import pandas as pd
import streamlit as st
from datetime import datetime
import pmdarima as pm
from pmdarima import auto_arima
import matplotlib.pyplot as plt

class transformacion:
    def __init__(self,df) -> None:
        self.df = df
        self.modelo_arima=None

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

    def generar_pronostico(self, periodos_predecir=70):        
        st.set_option('deprecation.showPyplotGlobalUse', False)

        pronostico, intervalo_confianza = self.modelo_arima.predict(n_periods=periodos_predecir, return_conf_int=True)
        proximo_periodo = pd.date_range(start=self.df.index[-1], periods=periodos_predecir)

        plt.figure(figsize=(12, 6))
        plt.plot(self.df.index, self.df, label='Datos reales', color='blue')
        plt.plot(proximo_periodo, pronostico, label='Pronóstico', color='red')
        plt.fill_between(proximo_periodo, intervalo_confianza[:, 0], intervalo_confianza[:, 1], color='pink', alpha=0.3)
        plt.title('Comparación de pronóstico vs. datos reales')
        plt.xlabel('Fecha')
        plt.ylabel('Valor')
        plt.legend()
        st.pyplot()
        
        df2=pd.DataFrame({'Periodo':proximo_periodo,'Pronostico':pronostico})
        df2=df2.set_index('Periodo')

        st.info('El mejor modelo encontrado es')
        st.write(self.modelo_arima.summary())