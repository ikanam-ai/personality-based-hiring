import logging
import time
from concurrent.futures import ThreadPoolExecutor

from llm import consumer as llm_consumer
from photo import consumer as photo_consumer
from trans import consumer as whisper_consumer

# Инициализация логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат вывода
    handlers=[
        logging.StreamHandler(),  # Логирование в консоль
        logging.FileHandler("consumer_log.log"),  # Логирование в файл
    ],
)


def start_consumers():
    logging.info("Запуск потребителей...")

    # Создаем пул потоков
    with ThreadPoolExecutor(max_workers=3) as executor:
        logging.info("Запуск потока для LLM потребителя")
        executor.submit(llm_consumer)

        logging.info("Запуск потока для Photo потребителя")
        executor.submit(photo_consumer)

        logging.info("Запуск потока для Whisper потребителя")
        executor.submit(whisper_consumer)

        # Даем время на выполнение (опционально)
        time.sleep(10)
        logging.info("Все потребители запущены, ожидаем завершения...")


if __name__ == "__main__":
    start_consumers()
