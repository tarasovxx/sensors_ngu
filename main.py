import os
from datetime import datetime, timedelta

import folium
import pandas as pd
import streamlit as st
import seaborn as sns
import plotly.express as px
import plotly
from folium import plugins
from matplotlib import pyplot as plt
from branca.colormap import linear

# Путь к папке с файлами
folder_path = 'Nigth_renamed'
st.set_page_config(layout="wide")

# Получение списка файлов
file_list = os.listdir(folder_path)
#
# # Извлечение времени из названий файлов
# times = sorted([file.split('_')[-2] for file in file_list])
# times_new = sorted([file.split('_')[-2].replace('-', ':')[:5] for file in file_list])
# m_d = {}
# for i, time in enumerate(times):
#     m_d[times_new[i]] = time
#
# # Создание Streamlit-приложения
# st.title("Technohack 2024. Water.")
# st.title("Карта температур")
#
# # Выбор времени
# selected_time = st.selectbox("Выберите время:", times_new)
times = sorted([file.split('_')[-2] for file in file_list])
times_new = sorted([file.split('_')[-2].replace('-', ':')[:5] for file in file_list])
m_d = {}
for i, time in enumerate(times):
    m_d[times_new[i]] = time

# Создание Streamlit-приложения
st.title("Technohack 2024. Water.")
st.title("Карта температур")

# Выбор времени с помощью ползунка
min_time = datetime.strptime(times_new[0], '%H:%M')
max_time = datetime.strptime(times_new[-1], '%H:%M')
step = timedelta(minutes=5)
selected_time = st.slider("Выберите время", min_value=min_time, max_value=max_time, value=min_time, step=step, format="HH:mm")

# Определение ближайшего подходящего времени
nearest_time = min(times_new, key=lambda t: abs(datetime.strptime(t, '%H:%M') - selected_time))
# print(nearest_time)
selected_file = next(file for file in file_list if m_d[nearest_time] in file)

# Загрузка данных для выбранного времени
# selected_file = next(file for file in file_list if m_d[selected_time] in file)
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

# Создание цветовой шкалы для температур
min_temp = temp_data['Temperature'].min()
max_temp = temp_data['Temperature'].max()
colormap = linear.YlOrRd_09.scale(min_temp, max_temp)

# Добавление маркеров с температурой на карту
for point in heat_data:
    folium.CircleMarker(
        location=[point[0], point[1]],
        radius=5,
        fill=True,
        fill_color=colormap(point[2]),
        color=None,
        fill_opacity=0.7
    ).add_to(m)

# Добавление легенды для температур
colormap.caption = 'Температура (°C)'
colormap.add_to(m)

# Отображение карты
folium_html = m._repr_html_()
st.components.v1.html(folium_html, height=500, width=700)

# Добавление графиков
st.header("Анализ температурных данных")
#
# График изменения температуры по длине
st.subheader("Изменение температуры по длине")
fig, ax = plt.subplots()
sns.lineplot(x='Length', y='Temperature', data=temp_data, ax=ax)
ax.set_xlim(2, 350)
ax.set_xlabel("Длина (м)")
ax.set_ylabel("Температура (°C)")
st.pyplot(fig)
#
import matplotlib.patches as mpatches
#
# График изменения температуры по длине
st.subheader("Изменение температуры по длине")
fig, ax = plt.subplots()
sns.lineplot(x='Length', y='Temperature', data=temp_data, ax=ax)

# Разметка фона графика по заданным интервалам
intervals = [
    (0, 32, 'red', 'Дом'),
    (32, 105, 'green', 'Лес'),
    (105, 150, 'yellow', 'Поляна'),
    (150, 203, 'green', 'Лес'),
    (203, 234, 'yellow', 'Поляна'),
    (234, 350, 'blue', 'Вода')
]

for start, end, color, label in intervals:
    ax.axvspan(start, end, facecolor=color, alpha=0.3)

ax.set_xlim(2, 350)
ax.set_xlabel("Длина (м)")
ax.set_ylabel("Температура (°C)")

# Создание легенды
visited = set()
patches = []
for _, _, color, label in intervals:
    if color not in visited:
        patches.append(mpatches.Patch(color=color, label=label))
    visited.add(color)

ax.legend(handles=patches, loc='upper right')

st.pyplot(fig)
#
# Гистограмма распределения температур
st.subheader("Распределение температур")
fig, ax = plt.subplots()
sns.histplot(temp_data['Temperature'], bins=30, kde=True, ax=ax)
ax.set_xlabel("Температура (°C)")
ax.set_ylabel("Частота")
st.pyplot(fig)
