import streamlit as st
import pymongo
from bson import ObjectId
import time

from config import MONGO_HOST, MONGO_PASSWORD, MONGO_PORT, MONGO_USERNAME


# Настройка подключения к MongoDB
client = pymongo.MongoClient(
    f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin",
    username=MONGO_USERNAME, password=MONGO_PASSWORD
)
db = client["data_soc_type"]
collection = db["prompts"]

# Функция добавления запроса в MongoDB (producer)
def producer(prompt: str, system_prompt: str):
    record = {
        "prompt": prompt,
        "system_prompt": system_prompt,
        "status": "pending",
        "response": None,
        "timestamp": time.time()
    }
    record_id = collection.insert_one(record).inserted_id
    print(f"Запрос {record_id} добавлен на обработку.")
    return record_id

# Функция получения ответа из MongoDB (consumer)
def get_response(record_id):
    while True:
        record = collection.find_one({"_id": ObjectId(record_id)})
        if record is None:
            print(f"Запись с ID {record_id} не найдена.")
            return None
        
        if record["status"] == "completed":
            print(f"Ответ готов: {record['response']}")
            return record["response"]
        
        print(f"Ожидание завершения для ID {record_id}... Статус: {record['status']}")
        time.sleep(2)  # Интервал проверки

st.title("В продакшен Chat-bot")

# Системное сообщение о типах личности
system_message = (
    'Ты бот-помощник, который должен отвечать на вопросы по типам личности. Ты должен помогать определить тип личности. Индикатор типа личности Майерс-Бриггс (MBTI) — это метод психологической оценки, разработанный для выявления личностных особенностей. С помощью специальных вопросов тест определяет сильные и слабые стороны человека, его предпочтения, мотивацию и особенности поведения. В результате тестирования участнику присваивается один из 16 типов личности, который помогает лучше понять себя и других. Считается, что знание своего типа и понимание типов окружающих способствует улучшению общения, помогает преодолевать конфликты, управлять стрессом и определять профессиональные предпочтения.\n\nМетод MBTI был создан Кэтрин Бриггс и её дочерью Изабель Майерс в 1942 году на основе теории психологических типов Карла Юнга. Юнг выделял два типа восприятия информации (через ощущения и интуицию) и два типа принятия решений (через мышление и чувство), а также делил людей на экстравертов и интровертов, в зависимости от источника энергии. Опросник MBTI предназначен для того, чтобы определить ключевые черты личности и предложить подходящие сферы деятельности. Во время Второй мировой войны этот метод помогал людям находить работу, которая подходила им по личным качествам.\n\nТест MBTI оценивает ответы по четырём категориям характеристик: интроверсия или экстраверсия, ощущение или интуиция, мышление или чувство, суждение или восприятие. Конечный тип личности составляется из комбинации доминирующих качеств и может, например, быть ENTP (экстравертный, интуитивный, думающий, восприимчивый). Считается, что каждый тип уникален, и не существует «лучших» комбинаций.\n\nТипология MBTI включает 16 типов личности, каждый из которых описан определёнными характеристиками. ISTJ (логист) — сдержанный и надёжный; ISFJ (защитник) — преданный и ответственный; INFJ (адвокат) — рациональный и сострадательный; INTJ (архитектор) — независимый и уверенный в себе логик; ISTP (мастер) — бесстрашный и целеустремлённый; ISFP (художник) — дружелюбный и чувствительный; INFP (посредник) — творческий и заботливый; INTP (мыслитель) — сдержанный и аналитичный; ESTP (делец) — спонтанный и общительный; ESFP (артист) — оптимистичный и импульсивный; ENFP (чемпион) — активный и общительный; ENTP (спорщик) — смелый и энергичный; ESTJ (режиссёр) — трудолюбивый и практичный; ESFJ (воспитатель) — ответственный и отзывчивый; ENFJ (главный герой) — целеустремлённый и преданный; ENTJ (командир) — инициативный и любящий структуру.'
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение сообщений в чате
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Получаем ввод пользователя
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Формируем последние 3 сообщения для объединенного запроса
    combined_prompt = " ".join(
        [msg["content"] for msg in st.session_state.messages[-10:] if msg["role"] == "user"]
    )

    # Добавляем запрос в MongoDB и получаем его ID
    record_id = producer(combined_prompt, system_message)

    # Ожидание и получение ответа
    response = get_response(record_id)
    
    if response:
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.error("Ошибка при получении ответа.")
