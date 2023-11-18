import streamlit as st
import pandas as pd
from datetime import datetime

df = pd.read_csv("data.csv")

months_dict = {
    'sty': '01', 'lut': '02', 'mar': '03', 'kwi': '04', 'maj': '05', 'cze': '06',
    'lip': '07', 'sie': '08', 'wrz': '09', 'paź': '10', 'lis': '11', 'gru': '12'
}

def konwersja_daty(row):
    day, month = row['Data'].split()  # Podzielenie na dzień i skrót miesiąca
    month_number = months_dict[month]  # Znalezienie numeru miesiąca
    year = datetime.now().year  # Możesz dodać rok zgodnie z potrzebą
    return datetime.strptime(f"{day} {month_number} {year}", "%d %m %Y")  # Tworzenie pełnej daty

# Zastosowanie funkcji do kolumny
df['Data'] = df.apply(konwersja_daty, axis=1)

with st.sidebar:
    days_number = st.slider("Wybierz ilość dni",1,25)
    volume_number = st.slider("Wybierz minimalną wielkość wolumenu braną pod uwagę",20000,70000,1000)
    start_date = pd.to_datetime(st.date_input("Data od"))
    end_date = pd.to_datetime(st.date_input("Data do"))

df['Data'] = pd.to_datetime(df['Data'])
df = df.sort_values(by='Data')
df = df[(df['Data'] >= start_date) & (df['Data'] <= end_date)]

if days_number is not None and not df.empty:
    # Sortowanie danych po dacie
    grouped = df.groupby('Nazwa')
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
    st.write(sredni_wzrost)
    st.write(new_df)