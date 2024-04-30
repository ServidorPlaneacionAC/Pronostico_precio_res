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
        self.df_regresores=None 

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

    def agregar_regresores(self,df_regresores):
        self.df_regresores=df_regresores
        self.df_regresores['Periodo']=[datetime.strptime(f"{int(fila['Año'])} {int(fila['Semana'])}-1", "%Y %W-%w") for _, fila in df_regresores.iterrows()]
        self.df_regresores=self.df_regresores.set_index('Periodo')
        self.df_regresores = self.df_regresores[~self.df_regresores.index.duplicated(keep='first')]     
        faltantes_regresores = self.df[~self.df.index.isin(self.df_regresores.index)]
        indices_a_eliminar = self.df_regresores[~self.df_regresores.index.isin(self.df.index)].index
        self.df_regresores = self.df_regresores.drop(indices_a_eliminar)
        if faltantes_regresores.shape[0]>0:
            st.error("por favor validar, los siguientes periodos no tienen año y semana asiciada en los regresores externos, los regresores no se tendrán en cuenta para generar el modelo")
            st.write(faltantes_regresores)  
            self.df_regresores=None      

    def generar_modelo(self,tamano_muestra) -> None:
        # self.otro()
        """
            Genera un modelo ARIMA para la serie temporal.

            Utiliza la función auto_arima de la biblioteca pmdarima para generar un modelo ARIMA 
            automático basado en la serie temporal.

            No devuelve nada, pero asigna el modelo resultante a la variable modelo_arima.
        """
        serie_tiempo = self.df.iloc[-tamano_muestra:,:]
        if self.df_regresores is not None:
            regresores = self.df_regresores.iloc[-tamano_muestra:,2:]
            serie_tiempo_con_regresores=pd.concat([serie_tiempo,regresores], axis=1)
            self.modelo_arima = pm.auto_arima(serie_tiempo_con_regresores['Precio_final']
                                                ,exogenous=serie_tiempo_con_regresores.drop(columns=['Precio_final'])
                                                ,seasonal=self.seasonal
                                                ,trend=self.trend)
        else:
            self.modelo_arima = pm.auto_arima(serie_tiempo
                                            ,seasonal=self.seasonal
                                            ,trend=self.trend)
    def otro(self):
        import numpy as np
        import pandas as pd
        import pmdarima as pm
        import matplotlib.pyplot as plt

        # Generar una serie temporal sintética
        np.random.seed(42)
        serie_tiempo = pd.Series(np.random.normal(loc=0, scale=1, size=100), index=pd.date_range(start='2022-01-01', periods=100))

        # Generar regresores sintéticos
        regresores = pd.DataFrame({
            'regresor_1': np.random.normal(loc=0, scale=1, size=100),
            'regresor_2': np.random.normal(loc=0, scale=1, size=100)
        }, index=serie_tiempo.index)

        # Agregar regresores a la serie temporal
        serie_tiempo_con_regresores = serie_tiempo + regresores.sum(axis=1)
        st.write('serie_tiempo eje')
        st.write(serie_tiempo)
        st.write('regresores eje')
        st.write(regresores)
        st.write('serie_tiempo_con_regresores eje')
        st.write(serie_tiempo_con_regresores)
        # Entrenar modelo ARIMA sin regresores
        modelo_sin_regresores = pm.auto_arima(serie_tiempo, seasonal=True, m=12)

        # Entrenar modelo ARIMA con regresores
        modelo_con_regresores = pm.auto_arima(serie_tiempo_con_regresores, exogenous=regresores, seasonal=True, m=12)

        # Imprimir los modelos
        st.write("Modelo sin regresores:")
        st.write(modelo_sin_regresores.summary())
        st.write("\nModelo con regresores:")
        st.write(modelo_con_regresores.summary())


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

