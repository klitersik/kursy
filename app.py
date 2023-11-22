import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client
import numpy as np

def convert_to_date(value):
    return value.date()

@st.cache_data
def get_data():
    current_date = datetime.now()
    url = "https://iqcvodlrxlihqexxwpiv.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlxY3ZvZGxyeGxpaHFleHh3cGl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDA1NzI3MTgsImV4cCI6MjAxNjE0ODcxOH0.syaMQHi6l0_G-PBXM5VdXgd3jc-vjHzTMxJ92r2RimU"
    supabase: Client = create_client(url, key)

    response = supabase.table('indeksy').select("Nazwa","Wolumen", "Kurs","Data").execute()
    df = pd.DataFrame(response.data)
    df['Data'] = pd.to_datetime(df['Data'])
    df = df.sort_values(by='Data')
    df['Data'] = df['Data'].apply(convert_to_date)
    df = df.drop_duplicates()
    df['Kurs'] = df['Kurs'].astype(float)
    df['Wolumen'] = df['Wolumen'].astype(int)
    return df

df = get_data()
new_df = None
with st.sidebar:
    days_number = st.slider("Wybierz ilość dni",2,20)
    volume_number = st.slider("Wybierz minimalną wielkość wolumenu braną pod uwagę",500_000,300_000_000,10000)
    min_value = st.number_input('Wybierz minimalną wartość Kursu',key="1",step=0.1)
    max_value = st.number_input('Wybierz maksymalną wartość Kursu',key="2",min_value=min_value,step=0.1)
    start_date = datetime.now().date()
    end_date = start_date - timedelta(days=days_number)

df_completed = df[(df['Data'] <= start_date) & (df['Data'] >= end_date)]
df_completed = df_completed[(df['Kurs'] <= max_value) & (df['Kurs'] >= min_value)]
df_completed = df_completed[(df['Wolumen'] >= volume_number)]

if days_number is not None and not df_completed.empty:
    # Sortowanie danych po dacie
    grouped = df_completed.groupby('Nazwa')
    # Lista do przechowywania danych do nowego DataFrame
    new_data = []

    # Obliczenie zmiany wolumenu w procentach dla każdej nazwy
    for nazwa, group in grouped:
        first_volume = group.iloc[0]['Wolumen']
        last_volume = group.iloc[-1]['Wolumen']
        zmiana_wolumenu = (last_volume - first_volume)/last_volume
        new_data.append({'Nazwa': nazwa, 'zmiana_wolumenu': zmiana_wolumenu})

    # Tworzenie nowego DataFrame
    new_df = pd.DataFrame(new_data)

    # Sortowanie malejąco po zmianie wolumenu
    new_df = new_df.sort_values(by='zmiana_wolumenu', ascending=False)

    # Obliczenie średniego wzrostu dla wszystkich nazw
    sredni_wzrost = new_df['zmiana_wolumenu'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Sprawdzane dni", days_number)
    col2.metric("Przedział cenowy", f"{min_value:.2f}$ - {max_value:.2f}$")
    col3.metric("Średni wzrost", f"{sredni_wzrost:.2f}")

    #st.write(new_df)

if not new_df.empty:
    df_positve = new_df[(new_df['zmiana_wolumenu'] > 0)]
    st.header(f"Zmiana wolumenu > 0, {len(df_positve)} uniklanych wartośći")
    st.dataframe(df_positve)

    st.divider()

    df_zero = new_df[(new_df['zmiana_wolumenu'] == 0)]
    st.header(f"Zmiana wolumenu = 0, {len(df_zero)} uniklanych wartośći")
    st.dataframe(df_zero)

    st.divider()

    df_negative = new_df[(new_df['zmiana_wolumenu'] < 0)]
    st.header(f"Zmiana wolumenu < 0, {len(df_negative)} uniklanych wartośći")
    st.dataframe(df_negative)
