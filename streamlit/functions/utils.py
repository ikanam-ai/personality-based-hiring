import time
import base64
import os
import sys
from bson.objectid import ObjectId
from PIL import Image
import cv2 
import pymongo
from matplotlib.colors import LinearSegmentedColormap, Normalize
import matplotlib.cm as cm
import random
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

sys.path.append('../')

from config import username, password, mongo_host, mongo_port


################################################################################################################################################

mbti_to_ocean = {
    'ESTJ': {'extraversion': (0.6, 0.8), 'neuroticism': (0.3, 0.5), 'agreeableness': (0.4, 0.6), 'conscientiousness': (0.7, 0.9), 'openness': (0.5, 0.7)},
    'ENTJ': {'extraversion': (0.6, 0.8), 'neuroticism': (0.3, 0.5), 'agreeableness': (0.4, 0.6), 'conscientiousness': (0.7, 0.9), 'openness': (0.6, 0.8)},
    'ISTP': {'extraversion': (0.4, 0.6), 'neuroticism': (0.4, 0.6), 'agreeableness': (0.4, 0.6), 'conscientiousness': (0.5, 0.7), 'openness': (0.5, 0.7)},
    'INTP': {'extraversion': (0.2, 0.4), 'neuroticism': (0.4, 0.6), 'agreeableness': (0.3, 0.5), 'conscientiousness': (0.3, 0.5), 'openness': (0.8, 1.0)},
    'ESFJ': {'extraversion': (0.7, 0.9), 'neuroticism': (0.4, 0.6), 'agreeableness': (0.7, 0.9), 'conscientiousness': (0.6, 0.8), 'openness': (0.4, 0.6)},
    'ENFJ': {'extraversion': (0.7, 0.9), 'neuroticism': (0.4, 0.6), 'agreeableness': (0.8, 1.0), 'conscientiousness': (0.6, 0.8), 'openness': (0.7, 0.9)},
    'INFP': {'extraversion': (0.2, 0.4), 'neuroticism': (0.6, 0.8), 'agreeableness': (0.7, 0.9), 'conscientiousness': (0.3, 0.5), 'openness': (0.7, 0.9)},
    'ISFP': {'extraversion': (0.3, 0.5), 'neuroticism': (0.5, 0.7), 'agreeableness': (0.7, 0.9), 'conscientiousness': (0.4, 0.6), 'openness': (0.6, 0.8)},
    'ESTP': {'extraversion': (0.8, 1.0), 'neuroticism': (0.4, 0.6), 'agreeableness': (0.5, 0.7), 'conscientiousness': (0.4, 0.6), 'openness': (0.6, 0.8)},
    'ESFP': {'extraversion': (0.8, 1.0), 'neuroticism': (0.5, 0.7), 'agreeableness': (0.7, 0.9), 'conscientiousness': (0.4, 0.6), 'openness': (0.7, 0.9)},
    'ISFJ': {'extraversion': (0.3, 0.5), 'neuroticism': (0.5, 0.7), 'agreeableness': (0.8, 1.0), 'conscientiousness': (0.6, 0.8), 'openness': (0.4, 0.6)},
    'ISTJ': {'extraversion': (0.3, 0.5), 'neuroticism': (0.4, 0.6), 'agreeableness': (0.5, 0.7), 'conscientiousness': (0.7, 0.9), 'openness': (0.4, 0.6)},
    'ENFP': {'extraversion': (0.7, 0.9), 'neuroticism': (0.5, 0.7), 'agreeableness': (0.6, 0.8), 'conscientiousness': (0.4, 0.6), 'openness': (0.8, 1.0)},
    'ENTP': {'extraversion': (0.7, 0.9), 'neuroticism': (0.4, 0.6), 'agreeableness': (0.4, 0.6), 'conscientiousness': (0.3, 0.5), 'openness': (0.8, 1.0)},
    'INTJ': {'extraversion': (0.2, 0.4), 'neuroticism': (0.3, 0.5), 'agreeableness': (0.3, 0.5), 'conscientiousness': (0.6, 0.8), 'openness': (0.7, 0.9)},
    'INFJ': {'extraversion': (0.2, 0.4), 'neuroticism': (0.5, 0.7), 'agreeableness': (0.8, 1.0), 'conscientiousness': (0.6, 0.8), 'openness': (0.8, 1.0)}
}

################################################################################################################################################

# Кодируем учетные данные в base64 и создаем URL для MongoDB
auth_base64 = base64.b64encode(f"{username}:{password}".encode()).decode()
client = pymongo.MongoClient(
    f"mongodb://{username}:{password}@{mongo_host}:{mongo_port}/?authSource=admin",
    username=username, password=password
)

# Подключаемся к базе данных и коллекции
db = client["data_soc_type"]
collection = db["whisper"]
collection_prompts = db["prompts"]

def producer(video_path):
    filename = os.path.basename(video_path)

    # Проверка на существование видео в базе данных и получение _id, если запись найдена
    existing_record = collection.find_one({"filename": filename}, {"_id": 1})
    if existing_record:
        print(f"Видео {filename} уже существует в базе данных. Пропуск...")
        return existing_record["_id"]

    # Код для загрузки видео и добавления новой записи в базу данных
    with open(video_path, "rb") as video_file:
        video_base64 = base64.b64encode(video_file.read()).decode()

    record = {
        "video_data": video_base64,
        "status": "pending",
        "result": None,
        "filename": filename
    }
    record_id = collection.insert_one(record).inserted_id
    print(f"Видео {record_id} добавлено на обработку: {filename}")
    return record_id

# Client - ждет завершения обработки и получает результат
def wait_for_result(record_id):
    print("Ожидание результата...")
    while True:
        record = collection.find_one({"_id": record_id})
        if record["status"] == "completed":
            print("Результат готов.")
            return record["result"]
        else:
            time.sleep(2)
            
def producer_promts(prompt: str, system_prompt: str):
    record = {
        "prompt": prompt,
        "system_prompt": system_prompt,
        "status": "pending",
        "response": None
    }
    record_id = collection_prompts.insert_one(record).inserted_id
    print(f"Запрос {record_id} добавлен на обработку.")
    return record_id

def get_response(record_id):
    while True:
        record = collection_prompts.find_one({"_id": ObjectId(record_id)})
        
        if record is None:
            print(f"Запись с ID {record_id} не найдена.")
            return None
        
        # Проверяем статус записи
        if record["status"] == "completed":
            print(f"Ответ готов: {record['response']}")
            return record["response"]
        
        # Если статус не "completed", ожидаем и повторяем проверку
        print(f"Ожидание завершения для ID {record_id}... Статус: {record['status']}")
        
def get_middle_frame(video_path):
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        middle_frame = frame_count // 2  # находим середину видео
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
        ret, frame = cap.read()
        
        if ret:
            frame_path = f"{video_path}_frame.jpg"  # сохраняем кадр как изображение
            cv2.imwrite(frame_path, frame)
            return frame_path
        else:
            return None
        
def generate_ocean_scores(mbti_type):
    if mbti_type not in mbti_to_ocean:
        raise ValueError("Неизвестный тип MBTI")
    
    # Получаем диапазоны для текущего типа MBTI
    ocean_ranges = mbti_to_ocean[mbti_type]
    
    # Генерируем случайное значение для каждой черты OCEAN в указанных диапазонах
    ocean_scores = {
        'extraversion': round(random.uniform(*ocean_ranges['extraversion']), 6),
        'neuroticism': round(random.uniform(*ocean_ranges['neuroticism']), 6),
        'agreeableness': round(random.uniform(*ocean_ranges['agreeableness']), 6),
        'conscientiousness': round(random.uniform(*ocean_ranges['conscientiousness']), 6),
        'openness': round(random.uniform(*ocean_ranges['openness']), 6),
    }
    
    return ocean_scores


def plot_ocean_radar(ocean_scores):
    labels = list(ocean_scores.keys())
    values = list(ocean_scores.values())
    
    # Добавляем первое значение в конец, чтобы закрыть радарный график
    values += values[:1]
    num_vars = len(labels)
    
    # Углы для каждого показателя
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    # Создание пользовательской цветовой карты с более насыщенным красным
    cmap = LinearSegmentedColormap.from_list("dark_red_white_blue", ["#8B0000", "#ff0000", "#ffffff", "#0000ff"])
    norm = Normalize(vmin=0, vmax=1)  # Нормируем значения от 0 до 1

    # Настройка графика
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('black')  # Устанавливаем черный цвет фона всей фигуры
    ax.set_facecolor('black')  # Устанавливаем черный цвет фона оси
    
    # Заполнение области графика с градиентом в зависимости от значений
    for i in range(num_vars):
        color = cmap(norm(values[i]))  # Цвет в зависимости от значения
        ax.fill_between(
            [angles[i], angles[i + 1]], 
            0, 
            [values[i], values[i + 1]], 
            color=color, 
            alpha=0.7
        )

    # Линия контура графика и настройка цвета осей и текста
    ax.plot(angles, values, color="white", linewidth=2)
    ax.spines['polar'].set_color('white')  # Устанавливаем белый цвет контура
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    
    # Подписи к осям
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color='white')  # Белый цвет подписей осей

    # Настройка диапазона значений (0-1) для удобного отображения
    ax.set_ylim(0, 1)

    # Добавление значений на график
    for angle, value, label in zip(angles, values, labels):
        ax.text(angle, value + 0.05, f'{value:.2f}', ha='center', va='center', fontsize=10, color='white')  # Белый цвет текста

    return fig
