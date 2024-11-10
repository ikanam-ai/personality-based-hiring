import logging
import time

from langchain.llms.base import LLM as BaseLLM
from mongo import get_mongo_client
from pydantic import BaseModel, Field
from transformers import AutoTokenizer
from vllm import LLM as VLLM
from vllm import SamplingParams

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


client = get_mongo_client()
db = client["data_soc_type"]
collection = db["prompts"]


class QwenVLLMLangChain(BaseLLM, BaseModel):
    model_name: str = Field(default="Qwen/Qwen2.5-7B-Instruct-AWQ")
    quantization: str = Field(default="awq")
    temperature: float = Field(default=0.7)
    top_p: float = Field(default=0.8)
    repetition_penalty: float = Field(default=1.05)
    max_tokens: int = Field(default=512)
    device_map: str = Field(default="cuda:1")

    tokenizer: AutoTokenizer = None
    llm: VLLM = None
    sampling_params: SamplingParams = None

    @classmethod
    def from_pretrained(cls):
        instance = cls()
        instance.tokenizer = AutoTokenizer.from_pretrained(instance.model_name)
        instance.llm = VLLM(
            model=instance.model_name, quantization=instance.quantization
        )

        instance.sampling_params = SamplingParams(
            temperature=instance.temperature,
            top_p=instance.top_p,
            repetition_penalty=instance.repetition_penalty,
            max_tokens=instance.max_tokens,
        )

        return instance

    def _call(self, prompt: str, system_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": str(prompt)},
        ]

        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        outputs = self.llm.generate([text], self.sampling_params)
        generated_text = outputs[0].outputs[0].text
        return generated_text

    @property
    def _llm_type(self) -> str:
        return "qwen_vllm_langchain"


def consumer():
    llm = QwenVLLMLangChain.from_pretrained()
    while True:
        record = collection.find_one({"status": "pending"})
        if record:
            collection.update_one(
                {"_id": record["_id"]}, {"$set": {"status": "processing"}}
            )
            logger.info(f"Обработка запроса: {record['_id']}")

            start_time = time.time()
            response = llm._call(
                prompt=record["prompt"], system_prompt=record["system_prompt"]
            )

            collection.update_one(
                {"_id": record["_id"]},
                {"$set": {"status": "completed", "response": response}},
            )
            logger.info(
                f"Запрос {record['_id']} обработан за {time.time() - start_time:.2f} секунд."
            )
        else:
            time.sleep(5)


def producer(prompt: str, system_prompt: str):
    record = {
        "prompt": prompt,
        "system_prompt": system_prompt,
        "status": "pending",
        "response": None,
    }
    record_id = collection.insert_one(record).inserted_id
    logger.info(f"Запрос {record_id} добавлен на обработку.")
    return record_id


def wait_for_response(record_id: str, timeout: int = 60) -> str:
    """
    Функция для ожидания ответа на запрос.
    Проверяет статус запроса каждую секунду.
    Возвращает ответ, когда запрос завершен, или None, если истекло время ожидания.
    """
    start_time = time.time()
    while True:
        record = collection.find_one({"_id": record_id})
        if record and record["status"] == "completed":
            logger.info(f"Запрос {record_id} завершен.")
            return record["response"]
        elif time.time() - start_time > timeout:
            logger.warning(f"Время ожидания запроса {record_id} истекло.")
            return None
        time.sleep(1)
