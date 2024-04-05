import pandas as pd
import streamlit as st

class transformacion:
    def __init__(self,df) -> None:
        self.df = df
    def combinar_partidas_reses(self) -> None:
        st.write(self.df)