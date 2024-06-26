import pandas as pd
import streamlit as st
from datetime import datetime
import pmdarima as pm
from pmdarima import auto_arima
import matplotlib.pyplot as plt
from scipy.stats import norm
import copy


class pronosticar_precio_reses:
    
    def __init__(self,df) -> None:
        """
            Inicializa la clase PronosticarPrecioReses.

            Parámetros:
            - df (DataFrame): DataFrame que contiene los datos de la serie temporal.

            Variables globales:
            - df (DataFrame): DataFrame que contiene los datos de la serie temporal.
            - modelo_arima (modelo): Mejor modelo generador
            - periodos_predecir (int): Periodos a pronosticar
            - elementos_mostrar (int): periodos de la serie original a mostrar en la gráfica
        """
        self.df = df
        self.modelo_arima=None
        self.seasonal=False
        self.trend=None
        self.periodos_predecir=10
        self.elementos_mostrar=10

    def combinar_partidas_reses(self) -> None:
        """
            Combina las partidas de reses en la serie temporal y calcula el precio final.

            Esta función agrega las partidas de reses para cada período y calcula el precio final 
            dividiendo el precio total de la planta entre la cantidad total de reses.

            No devuelve nada, pero modifica el DataFrame df.
        """
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

    def generar_modelo(self,tamano_muestra) -> None:
        """
            Genera un modelo ARIMA para la serie temporal.

            Utiliza la función auto_arima de la biblioteca pmdarima para generar un modelo ARIMA 
            automático basado en la serie temporal.

            No devuelve nada, pero asigna el modelo resultante a la variable modelo_arima.
        """
        serie_tiempo = self.df.iloc[-tamano_muestra:,:]
        self.modelo_arima = pm.auto_arima(serie_tiempo
                                            ,seasonal=self.seasonal
                                            ,trend=self.trend)

    def generar_pronostico(self) -> None: 
        """
            Genera un pronóstico utilizando el modelo ARIMA.

            Utiliza el modelo ARIMA generado previamente para generar un pronóstico para un número 
            especificado de períodos.

            No devuelve nada, pero asigna el pronóstico y el intervalo de confianza a las variables 
            pronostico y intervalo_confianza, respectivamente.
        """       
        st.set_option('deprecation.showPyplotGlobalUse', False)
        self.pronostico, self.intervalo_confianza = self.modelo_arima.predict(n_periods=self.periodos_predecir, return_conf_int=True)
        intervalo_confianza=copy.deepcopy(self.intervalo_confianza)
        nivel_confianza = 0.5
        z = norm.ppf((1 + nivel_confianza) / 2)
        ancho_intervalo_ajustado = z * (self.intervalo_confianza[:, 1] - self.intervalo_confianza[:, 0])
        intervalo_confianza[:, 0] = self.pronostico - ancho_intervalo_ajustado / 2
        intervalo_confianza[:, 1] = self.pronostico + ancho_intervalo_ajustado / 2       
        self.intervalo_confianza2=intervalo_confianza

        self.proximo_periodo = pd.date_range(start=self.df.index[-1], periods=self.periodos_predecir, freq='W')

    def imprimir_pronostico(self) -> None:  
        """
            Imprime el pronóstico generado junto con los datos reales.

            Utiliza matplotlib para trazar el pronóstico generado junto con los datos reales en un 
            gráfico.

            No devuelve nada, pero muestra el gráfico utilizando la función st.pyplot() de Streamlit.
        """
        
        inicio_serie_real=self.df.shape[0]-self.elementos_mostrar
        plt.figure(figsize=(12, 6))
        plt.plot(self.df.index[inicio_serie_real:], self.df[inicio_serie_real:], label='Datos reales', color='blue')
        plt.plot(self.proximo_periodo, self.pronostico, label='Pronóstico', color='red')
        plt.fill_between(self.proximo_periodo, self.intervalo_confianza[:, 0], self.intervalo_confianza[:, 1], color='pink', alpha=0.3)
        plt.fill_between(self.proximo_periodo, self.intervalo_confianza2[:, 0], self.intervalo_confianza2[:, 1], color='yellow', alpha=0.3)
        plt.title('Comparación de pronóstico vs. datos reales')
        plt.xlabel('Fecha')
        plt.ylabel('Valor')
        plt.legend()
        st.pyplot()
        
    def llevar_pronostico_a_df(self):
        """
            Convierte el pronóstico generado a un DataFrame.

            Crea un DataFrame con los períodos y el pronóstico generado.

            Devuelve:
            - DataFrame: DataFrame con los períodos y el pronóstico.
        """
        df_resultado=pd.DataFrame({'Periodo':self.proximo_periodo,
                                   'Pronóstico':self.pronostico,
                                   'Banda superior de confianza 95%':self.intervalo_confianza[:,1],
                                   'Banda inferior de confianza 95%':self.intervalo_confianza[:,0],
                                   'Banda superior de confianza 65%':self.intervalo_confianza2[:,1],
                                   'Banda inferior de confianza 65%':self.intervalo_confianza2[:,0],
                                   })
        df_resultado=df_resultado.set_index('Periodo')
        return df_resultado

