import base64
import logging
import os
import time

import pymongo
import torch
from bson.objectid import ObjectId
from mongo import get_mongo_client
from PIL import Image
from transformers import AutoModelForImageClassification, AutoProcessor, pipeline

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = get_mongo_client()
db = client["data_soc_type"]
collection = db["photos"]

device = "cuda:0" if torch.cuda.is_available() else "cpu"


def producer(image_path):
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode()

    record = {
        "image_data": image_base64,
        "status": "pending",
        "gender": None,
        "ethnicity": None,
    }

    record_id = collection.insert_one(record).inserted_id
    logger.info(f"Изображение добавлено в очередь на обработку. ID записи: {record_id}")
    return record_id


def consumer():
    gender_model = AutoModelForImageClassification.from_pretrained(
        "rizvandwiki/gender-classification"
    ).to(device)
    gender_processor = AutoProcessor.from_pretrained(
        "rizvandwiki/gender-classification"
    )

    ethnicity_pipe = pipeline(
        "image-classification",
        model="cledoux42/Ethnicity_Test_v003",
        device=0 if device == "cuda:0" else -1,
    )

    def predict_image_class(image_path):
        image = Image.open(image_path).convert("RGB")
        gender_inputs = gender_processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            gender_outputs = gender_model(**gender_inputs)
            gender_logits = gender_outputs.logits
            predicted_gender_class = gender_logits.argmax(-1).item()

        gender = "male" if predicted_gender_class == 0 else "female"
        ethnicity_result = ethnicity_pipe(image)
        predicted_ethnicity = ethnicity_result[0]["label"]

        return gender, predicted_ethnicity

    while True:
        queue_size = collection.count_documents({"status": "pending"})

        if queue_size > 0:
            record = collection.find_one({"status": "pending"})
            collection.update_one(
                {"_id": record["_id"]}, {"$set": {"status": "processing"}}
            )
            logger.info(
                f"Обработка записи: {record['_id']} (осталось в очереди: {queue_size})"
            )

            image_data = base64.b64decode(record["image_data"])
            image_path = "/tmp/temp_image.jpg"
            with open(image_path, "wb") as f:
                f.write(image_data)

            predicted_gender, predicted_ethnicity = predict_image_class(image_path)

            collection.update_one(
                {"_id": record["_id"]},
                {
                    "$set": {
                        "status": "completed",
                        "gender": predicted_gender,
                        "ethnicity": predicted_ethnicity,
                    }
                },
            )
            logger.info(
                f"Запись {record['_id']} обработана. Гендер: {predicted_gender}, Этническая принадлежность: {predicted_ethnicity}"
            )

        else:
            logger.info("Очередь пуста. Ожидание новых изображений...")
            time.sleep(5)


def wait_for_result(record_id):
    logger.info("Ожидание результата...")
    while True:
        record = collection.find_one({"_id": record_id})
        if record["status"] == "completed":
            logger.info(
                f"Результат готов: Гендер: {record['gender']}, Этническая принадлежность: {record['ethnicity']}"
            )
            return record["gender"], record["ethnicity"]
        else:
            time.sleep(2)
