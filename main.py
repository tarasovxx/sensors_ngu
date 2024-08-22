import os
from datetime import datetime

import folium
import pandas as pd
import streamlit as st
import seaborn as sns
import plotly.express as px
import plotly
from folium import plugins
from matplotlib import pyplot as plt

# Путь к папке с файлами
folder_path = 'Nigth_renamed'

# Получение списка файлов
file_list = os.listdir(folder_path)

# Извлечение времени из названий файлов
times = sorted([file.split('_')[-2] for file in file_list])

# Создание Streamlit-приложения
st.title("Technohack 2024. Это вода - 52 | Любители Коксы.")
st.title("Карта температур")

# Выбор времени
selected_time = st.selectbox("Выберите время:", times)

# Загрузка данных для выбранного времени
selected_file = next(file for file in file_list if selected_time in file)
temp_data = pd.read_csv(os.path.join(folder_path, selected_file), delimiter=';', names=['Length', 'Temperature'], skiprows=20)

# Загрузка данных для карты
mapping_data = pd.read_csv('mapping.csv')

def find_nearest_coord(length):
    mapping_data['distance'] = abs(mapping_data['Name'] - length)
    nearest_coord = mapping_data.loc[mapping_data['distance'].idxmin()]
    return nearest_coord[['X', 'Y']]


# Создание объекта карты
m = folium.Map(location=[mapping_data['X'].mean(), mapping_data['Y'].mean()], zoom_start=18)

# Подготовка данных для тепловой карты
heat_data = []
for _, row in temp_data.iterrows():
    nearest_coord = find_nearest_coord(row['Length'])
    heat_data.append([nearest_coord['X'], nearest_coord['Y'], row['Temperature']])

# # Добавление слоя с тепловой картой
# df = pd.DataFrame(heat_data, columns=['x', 'y', 'temperature'])
# fig = px.density_mapbox(df, lat='y', lon='x', z='temperature',
#                         radius=10, center=dict(lat=2, lon=2), zoom=8,
#                         mapbox_style="stamen-terrain")
df = pd.DataFrame(heat_data, columns=['x', 'y', 'temperature'])
print(df)
# # Создание тепловой карты с использованием Plotly
# fig = px.density_mapbox(df, lat='y', lon='x', z='temperature',
#                         radius=10, center=dict(lat=mapping_data['X'].mean(), lon=mapping_data['Y'].mean()), zoom=18,
#                         mapbox_style="stamen-terrain")
#
# # Отображение карты в Streamlit
# st.plotly_chart(fig)


heat_layer = plugins.HeatMap(heat_data, radius=15)
heat_layer.add_to(m)


# Отображение карты
folium_html = m._repr_html_()
st.components.v1.html(folium_html, height=500, width=700)

st.write("Данные для тепловой карты:", heat_data[:10])

# Добавление графиков
st.header("Анализ температурных данных")

# График изменения температуры по длине
st.subheader("Изменение температуры по длине")
fig, ax = plt.subplots()
sns.lineplot(x='Length', y='Temperature', data=temp_data, ax=ax)
ax.set_xlim(2, 350)
ax.set_xlabel("Длина (м)")
ax.set_ylabel("Температура (°C)")
st.pyplot(fig)

# Гистограмма распределения температур
st.subheader("Распределение температур")
fig, ax = plt.subplots()
sns.histplot(temp_data['Temperature'], bins=30, kde=True, ax=ax)
ax.set_xlabel("Температура (°C)")
ax.set_ylabel("Частота")
st.pyplot(fig)
