import pandas as pd
import streamlit as st
from datetime import datetime
import pmdarima as pm
from pmdarima import auto_arima
import matplotlib.pyplot as plt

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

    def generar_modelo(self) -> None:
        """
            Genera un modelo ARIMA para la serie temporal.

            Utiliza la función auto_arima de la biblioteca pmdarima para generar un modelo ARIMA 
            automático basado en la serie temporal.

            No devuelve nada, pero asigna el modelo resultante a la variable modelo_arima.
        """
        serie_tiempo = self.df
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
        self.proximo_periodo = pd.date_range(start=self.df.index[-1], periods=self.periodos_predecir, freq='W')

    def imprimir_pronostico(self) -> None:  
        """
            Imprime el pronóstico generado junto con los datos reales.

            Utiliza matplotlib para trazar el pronóstico generado junto con los datos reales en un 
            gráfico.

            No devuelve nada, pero muestra el gráfico utilizando la función st.pyplot() de Streamlit.
        """

        from statsmodels.tsa.seasonal import STL
        import numpy as np

        inicio_serie_real=self.df.shape[0]-self.elementos_mostrar
        np.random.seed(0)
        indice_tiempo = pd.date_range(start='2024-01-01', periods=37, freq='W')
        serie = np.sin(np.linspace(0, 2*np.pi, 37)) + np.random.normal(0, 0.2, 37)
        df = pd.DataFrame({'valor': serie}, index=indice_tiempo)

        # Aplicamos la descomposición estacional sin especificar el período
        stl = STL(df['valor'], seasonal=3)
        result = stl.fit()

        # Graficamos los componentes
        fig, axes = plt.subplots(4, 1, figsize=(10, 8), sharex=True)

        # Serie original
        axes[0].plot(df.index, df['valor'], label='Serie Original', color='blue')
        axes[0].set_title('Serie Original')

        # Tendencia
        axes[1].plot(df.index, result.trend, label='Tendencia', color='green')
        axes[1].set_title('Tendencia')

        # Estacionalidad
        axes[2].plot(df.index, result.seasonal, label='Estacionalidad', color='red')
        axes[2].set_title('Estacionalidad')

        # Residuo
        axes[3].plot(df.index, result.resid, label='Residuo', color='purple')
        axes[3].set_title('Residuo')

        plt.tight_layout()
        plt.show()
        st.pyplot()

        '''plt.figure(figsize=(12, 6))
        plt.plot(self.df.index[inicio_serie_real:], self.df[inicio_serie_real:], label='Datos reales', color='blue')
        plt.plot(self.proximo_periodo, self.pronostico, label='Pronóstico', color='red')
        plt.fill_between(self.proximo_periodo, self.intervalo_confianza[:, 0], self.intervalo_confianza[:, 1], color='pink', alpha=0.3)
        plt.title('Comparación de pronóstico vs. datos reales')
        plt.xlabel('Fecha')
        plt.ylabel('Valor')
        plt.legend()
        st.pyplot()'''
        
    def llevar_pronostico_a_df(self):
        """
            Convierte el pronóstico generado a un DataFrame.

            Crea un DataFrame con los períodos y el pronóstico generado.

            Devuelve:
            - DataFrame: DataFrame con los períodos y el pronóstico.
        """
        df_resultado=pd.DataFrame({'Periodo':self.proximo_periodo,'Pronóstico':self.pronostico})
        df_resultado=df_resultado.set_index('Periodo')
        return df_resultado

