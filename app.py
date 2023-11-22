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
    url = st.secrets["url"]
    key = st.secrets["key"]
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

with st.sidebar:
    days_number = st.slider("Wybierz ilość dni",2,20)
    volume_number = st.number_input('Minimalny Wolumen',key="3",min_value=100_000,step=1000)
    min_value = st.number_input('Wybierz minimalną wartość Kursu',key="1",step=0.1)
    max_value = st.number_input('Wybierz maksymalną wartość Kursu',key="2",min_value=min_value,step=0.1)
    start_date = datetime.now().date()
    end_date = start_date - timedelta(days=days_number)

df_completed = df[(df['Data'] <= start_date) & (df['Data'] >= end_date)]

if days_number is not None and not df_completed.empty:
    # Sortowanie danych po dacie
    grouped = df_completed.groupby('Nazwa')
    # Lista do przechowywania danych do nowego DataFrame
    new_data = []
    # Obliczenie zmiany wolumenu w procentach dla każdej nazwy
    for nazwa, group in grouped:
        first_volume = group.iloc[0]['Wolumen']
        last_volume = group.iloc[-1]['Wolumen']
        mean_volume = group['Wolumen'].mean()
        zmiana_wolumenu = (mean_volume - first_volume)/mean_volume
        max_date_row = group[group['Data'] == group['Data'].max()]  # Wiersz z maksymalną datą
        if not max_date_row.empty:
            kurs = max_date_row.iloc[0, -2]
            wolumen = max_date_row.iloc[0, -3]
            new_data.append({
                'Nazwa': nazwa,
                'Zmiana_wolumenu': zmiana_wolumenu,
                'Kurs': kurs,
                'Wolumen_śr': mean_volume
            })

    # Tworzenie nowego DataFrame
    new_df = pd.DataFrame(new_data)

    # Sortowanie malejąco po zmianie wolumenu
    new_df = new_df.sort_values(by='Zmiana_wolumenu', ascending=False)

    # Obliczenie średniego wzrostu dla wszystkich nazw
    sredni_wzrost = new_df['Zmiana_wolumenu'].mean()

    new_df = new_df[(new_df['Kurs'] <= max_value) & (df['Kurs'] >= min_value)]
    new_df = new_df[(new_df['Wolumen_śr'] >= volume_number)]
   

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sprawdzane dni", days_number)
    col2.metric("Przedział cenowy", f"{min_value:.2f}-{max_value:.2f}")
    col3.metric("Średni wzrost", f"{sredni_wzrost:.2f}")
    col4.metric("Minimalny wolumen", f"{volume_number}")
    #st.write(new_df)
    
    if not new_df.empty:
        df_positve = new_df[(new_df['Zmiana_wolumenu'] > 0)]
        df_positve['Zmiana_wolumenu'] = df_positve['Zmiana_wolumenu'].apply(lambda x: f"{x * 100:.4f}%")
        st.header(f"Zmiana wolumenu > 0, {len(df_positve)} uniklanych wartośći")
        st.dataframe(df_positve)

        st.divider()

        df_zero = new_df[(new_df['Zmiana_wolumenu'] == 0)]
        df_zero['Zmiana_wolumenu'] = df_zero['Zmiana_wolumenu'].apply(lambda x: f"{x * 100:.4f}%")
        st.header(f"Zmiana wolumenu = 0, {len(df_zero)} uniklanych wartośći")
        st.dataframe(df_zero)

        st.divider()

        df_negative = new_df[(new_df['Zmiana_wolumenu'] < 0)]
        df_negative['Zmiana_wolumenu'] = df_negative['Zmiana_wolumenu'].apply(lambda x: f"{x * 100:.4f}%")
        st.header(f"Zmiana wolumenu < 0, {len(df_negative)} uniklanych wartośći")
        st.dataframe(df_negative)

