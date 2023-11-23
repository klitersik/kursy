import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client
import numpy as np
import requests

def replace_value(value):
    if isinstance(value, float):  # Sprawdzenie czy wartość jest floatem
        value = str(int(value))  # Konwersja na string

    value = value.replace(',', '')  # Usunięcie przecinka
    value = int(value)

    if value >= 1_000_000_000:  # Jeśli wartość jest większa lub równa 1 miliardowi
        return f"{value // 1_000_000_000}g"
    elif value >= 1_000_000:  # Jeśli wartość jest większa lub równa 1 milionowi
        return f"{value // 1_000_000}m"
    elif value >= 1_000:  # Jeśli wartość jest większa lub równa 1 tysiącowi
        return f"{value // 1_000}t"
    else:
        return str(value)
    

@st.cache_data
def get_data():
    anon = st.secrets["anon"]
    url = st.secrets["url"]
    key = st.secrets["key"]

    headers = {
        'Content-Type': 'application/json',
        'apikey': key,
        'Authorization': anon
    }

    response = requests.post(url, headers=headers)

    json_list = response.json()

    df = pd.DataFrame(json_list)
    df.rename(columns={'symbol_of': 'Symbol'}, inplace=True)
    df.rename(columns={'data': 'Data'}, inplace=True)
    df.rename(columns={'percent_difference': 'Difference%'}, inplace=True)
    df.rename(columns={'kurs': 'Kurs'}, inplace=True)
    df.rename(columns={'avg_wolumen': 'Wolumen_śr'}, inplace=True)
    
    return df

df = get_data()
max_date = df['Data'].max()

with st.sidebar:
    days_number = st.slider("Wybierz ilość dni",2,20)
    volumen_percentage = st.slider("Wybierz minimalny % wzrost wolumenu",25,2200)
    volume_number = st.number_input('Minimalny Wolumen',key="3",min_value=100_000,step=1000)
    min_value = st.number_input('Wybierz minimalną wartość Kursu',key="1",step=0.1)
    max_value = st.number_input('Wybierz maksymalną wartość Kursu',key="2",min_value=min_value,step=0.1)
    start_date = datetime.now().date()
    end_date = start_date - timedelta(days=days_number)

df_filtered = df[(df['Difference%'] >= volumen_percentage)]
df_filtered = df_filtered[(df['Wolumen_śr'] >= volume_number)]
df_filtered = df_filtered[(df_filtered['Kurs'] >= min_value) & (df_filtered['Kurs'] <= max_value)]
avg_value = df_filtered["Difference%"].mean()
df_filtered["Wolumen_śr"] = df_filtered["Wolumen_śr"].apply(replace_value)
df_filtered.drop("Data", axis=1, inplace=True)

st.header(f"Ostatnia aktualizacja Danych :blue[{max_date}]")

col1, col2, col3 = st.columns(3)
col1.metric("Przedział cenowy", f"{min_value:.2f}-{max_value:.2f}")
col2.metric("Średni wzrost", f"{avg_value:.2f}%")
col3.metric("Minimalny średni wolumen", f"{volume_number}")


st.write(df_filtered)
