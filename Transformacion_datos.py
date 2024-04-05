import pandas as pd
import streamlit as st
from datetime import datetime

class transformacion:
    def __init__(self,df) -> None:
        self.df = df
    def combinar_partidas_reses(self) -> None:
        self.df['Periodo']=[datetime.strptime(f"{int(fila['Año'])} {int(fila['Semana'])}-1", "%Y %W-%w") for _, fila in self.df.iterrows()]
        self.df['Precio_Planta']=self.df['Cantidad_Reses']*self.df['Precio_Planta']
        
        self.df = self.df.groupby(['PERIODO']).agg({
            'Cantidad_Reses': 'sum',
            'Precio_Planta': 'sum'
        }).reset_index()
        self.df['Precio_final']=self.df[' Precio en planta']/self.df[' Cantidad de Reses Liquidadas']
        self.df=self.df[['Periodo','Precio_final']]
        self.df=self.df.set_index('Periodo')
        self.df = self.df[~self.df.index.duplicated(keep='first')]
        st.write(self.df)
