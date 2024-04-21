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

        import numpy as np
        import statsmodels.api as sm

        
        inicio_serie_real=self.df.shape[0]-self.elementos_mostrar
        explicacion=None
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Ver ACF de mis datos'):
                explicacion='ACF'
        
        with col2:
            if st.button('Ver gráfico de diferenciación de mis datos'):
                explicacion='gráfico de diferenciación'
        if explicacion=='gráfico de diferenciación':

            st.write('''El componente de tendencia de una serie de tiempo se refiere a la dirección general en la que cambian los datos a lo largo del tiempo. Es como observar si una serie de tiempo está subiendo, bajando o permaneciendo relativamente constante en el largo plazo, esta puede ser de 4 tipos:''')
            st.write('''**None:** Quiere decir que nuestra serie no tiene ninguna tendencia ''')
            st.write('''**Constante (c):** En una tendencia constante, los datos muestran un cambio uniforme en una dirección específica a lo largo del tiempo, este cambio no necesariamente sigue una línea recta, pero crece un valor constante''')
            st.write('''**Lineal (t):** En una tendencia lineal, los datos muestran un cambio permanente en una dirección específica a lo largo del tiempo, y este cambio sigue una razon de crecimiento ''')
            st.write('''**Constante y lineal (ct):** Usado en movimientos que contienen ambos tipos de tendencia ''')

            from statsmodels.tsa.stattools import adfuller, kpss

            # Aplicar la prueba ADF
            adf_result = adfuller(self.df['Precio_final'])
            st.write(f'Al realizar la prueba estadistica Prueba de Dickey-Fuller Aumentada (ADF) obtenemos un valor-p de {adf_result[1]}, concluyendo:')
            if adf_result[1]<0.05:
                st.write('**La serie no tiene tendencia se sugiere no agregar componente estacional**')
            else:
                st.write('**La serie si tiene tendencia se sugiere evaluar el componente estacional que mas se ajuste según las definiciones anteriores**')
            

        elif explicacion=='ACF':
            acf = sm.tsa.acf(self.df['Precio_final'], nlags=len(self.df)-1)
            # Graficamos el ACF
            plt.figure(figsize=(10, 6))
            plt.stem(acf)
            plt.xlabel('Lag')
            plt.ylabel('Autocorrelación')
            plt.title('Gráfico de Autocorrelación (ACF)')
            plt.show()
            st.pyplot()
            st.write('''La ACF te ayuda a ver si hay un patrón que se repite en ciertos momentos, como si hubiera un evento especial que ocurre en la misma época cada cierto periodo de tiempo. Si ves picos en ciertos momentos en la ACF, eso podría significar que hay un componente estacional en esos momentos, entonces se recomienda activar el componente estacional con la alternativa TRUE''')
        plt.figure(figsize=(12, 6))
        plt.plot(self.df.index[inicio_serie_real:], self.df[inicio_serie_real:], label='Datos reales', color='blue')
        plt.plot(self.proximo_periodo, self.pronostico, label='Pronóstico', color='red')
        plt.fill_between(self.proximo_periodo, self.intervalo_confianza[:, 0], self.intervalo_confianza[:, 1], color='pink', alpha=0.3)
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
        df_resultado=pd.DataFrame({'Periodo':self.proximo_periodo,'Pronóstico':self.pronostico})
        df_resultado=df_resultado.set_index('Periodo')
        return df_resultado

