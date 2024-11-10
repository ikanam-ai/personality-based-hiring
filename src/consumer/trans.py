import base64
import logging
import time
from datetime import timedelta

import torch
import whisper
from bson.objectid import ObjectId
from mongo import get_mongo_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("consumer_log.log")],
)

client = get_mongo_client()

db = client["data_soc_type"]
collection = db["whisper"]

device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=device)


def producer(video_path):
    try:
        with open(video_path, "rb") as video_file:
            video_base64 = base64.b64encode(video_file.read()).decode()

        record = {
            "video_data": video_base64,
            "status": "pending",
            "result": None,
        }
        record_id = collection.insert_one(record).inserted_id
        logging.info(f"Видео добавлено в очередь на обработку. ID записи: {record_id}")
        return record_id
    except Exception as e:
        logging.error(f"Ошибка при добавлении видео в MongoDB: {e}")
        return None


def wait_for_result(record_id):
    logging.info("Ожидание результата...")
    while True:
        record = collection.find_one({"_id": record_id})
        if record["status"] == "completed":
            logging.info("Результат готов.")
            return record["result"]
        else:
            time.sleep(2)


def consumer():
    processed_count = 0
    total_time = 0

    while True:
        queue_size = collection.count_documents({"status": "pending"})
        logging.info(f"Очередь: {queue_size} видео на обработку.")

        if queue_size > 0:
            record = collection.find_one({"status": "pending"})
            collection.update_one(
                {"_id": record["_id"]}, {"$set": {"status": "processing"}}
            )
            logging.info(
                f"Обработка записи: {record['_id']} (осталось в очереди: {queue_size})"
            )

            try:
                video_data = base64.b64decode(record["video_data"])
                video_path = "/tmp/temp_video.mp4"
                with open(video_path, "wb") as f:
                    f.write(video_data)

                start_time = time.time()
                result = model.transcribe(video_path)
                transcription_text = result["text"]
                processing_time = time.time() - start_time

                collection.update_one(
                    {"_id": record["_id"]},
                    {"$set": {"status": "completed", "result": transcription_text}},
                )
                logging.info(
                    f"Запись {record['_id']} обработана за {timedelta(seconds=processing_time)}"
                )

                processed_count += 1
                total_time += processing_time

                if processed_count % 5 == 0 and queue_size > 1:
                    average_time = total_time / processed_count
                    estimated_remaining_time = timedelta(
                        seconds=average_time * (queue_size - 1)
                    )
                    logging.info(
                        f"Среднее время обработки: {timedelta(seconds=average_time)}"
                    )
                    logging.info(
                        f"Примерное оставшееся время для очереди: {estimated_remaining_time}"
                    )

            except Exception as e:
                logging.error(f"Ошибка при обработке записи {record['_id']}: {e}")
        else:
            logging.info("Очередь пуста. Ожидание новых записей.")
            time.sleep(5)
