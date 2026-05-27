import asyncio
import requests
from typing import List

SYSTEM_PROMPT = (
    "Ты ассистент автодополнения текста. Твоя задача - продолжить незаконченный текст пользователя. "
    "Выведи несколько РАЗНЫХ продолжений (от 1 до 4 слов). Не повторяй то, что пользователь уже написал! "
    "Не пиши НИКАКИХ объяснений, кавычек или вводных слов. Только сами продолжения."
)


async def get_autocomplete_suggestions(current_text: str, request_id: int = 0) -> List[str]:
    """
    Асинхронная функция для получения подсказок от LLM.

    Args:
        current_text: Текст, который вводит пользователь
        request_id: ID запроса для отмены устаревших запросов

    Returns:
        Список предложенных продолжений
    """
    if not current_text.strip():
        return []

    payload = {
        "model": "/data/models+data/qwen3.5-9b-nvfp4",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f'Продолжи текст: "{current_text}". Верни 3 варианта через разделитель |',
            },
        ],
        "max_tokens": 10,
        "temperature": 0.1,
        "top_p": 0.3,
        "presence_penalty": 0.0,
        "repetition_penalty": 1.1,
    }

    try:
        # Используем thread pool для HTTP-запроса
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(
                "http://localhost:5050/v1/chat/completions", json=payload, timeout=10  # Увеличен таймаут
            ),
        )

        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            suggestions = content.split("|")
            # Очистка от мусора
            cleaned = [s.strip().replace('"', "").replace("...", "").strip() for s in suggestions]
            # Фильтруем пустые строки
            return [s for s in cleaned if s]
    except requests.exceptions.Timeout:
        print(f"[{request_id}] Request timeout")
    except requests.exceptions.ConnectionError:
        print(f"[{request_id}] Connection error to LLM server")
    except Exception as e:
        print(f"[{request_id}] Ошибка LLM: {e}")
    return []


def parse_suggestions(content: str) -> List[str]:
    """
    Парсит ответ от LLM и возвращает список подсказок.

    Args:
        content: Строка с подсказками, разделенными |

    Returns:
        Список очищенных подсказок
    """
    if not content:
        return []
    suggestions = content.split("|")
    return [s.strip().replace('"', "").replace("...", "").strip() for s in suggestions if s.strip()]
