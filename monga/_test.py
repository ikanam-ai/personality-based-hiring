import os
from pymongo import MongoClient

# Загрузка переменных окружения из .env файла
from dotenv import load_dotenv

load_dotenv()

# Получение данных для подключения из переменных окружения
MONGO_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
MONGO_HOST = 'localhost'
MONGO_PORT = os.getenv('MONGO_INITDB_ROOT_PORT')

# Формирование URI для подключения к MongoDB
mongo_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"

# Подключение к MongoDB
client = MongoClient(mongo_uri)

# Выбор базы данных и коллекции
db = client.test_db
collection = db.test_collection

# Пример документа
test_document = {
    "name": "Test User",
    "email": "testuser@example.com",
    "age": 30
}

# Вставка документа в коллекцию
result = collection.insert_one(test_document)
print(f"Inserted document id: {result.inserted_id}")

# Извлечение документа из коллекции
retrieved_document = collection.find_one({"name": "Test User"})
print("Retrieved document:")
print(retrieved_document)

# Закрытие подключения
client.close()
