import requests

SYSTEM_PROMPT = (
    "Ты ассистент автодополнения текста. Твоя задача - продолжить незаконченный текст пользователя. "
    "Выводи ТОЛЬКО продолжение (от 1 до 4 слов). Не повторяй то, что пользователь уже написал! "
    "Не пиши НИКАКИХ объяснений, кавычек или вводных слов. Только само продолжение."
)


def get_autocomplete_suggestion(current_text: str) -> str:
    if not current_text.strip():
        return ""

    payload = {
        "model": "/data/models+data/qwen3.5-9b-nvfp4",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f'Продолжи текст: "{current_text}"'},
        ],
        "max_tokens": 10,
        "temperature": 0.1,
        "top_p": 0.3,
        "presence_penalty": 0.0,
        "repetition_penalty": 1.1,
    }

    try:
        response = requests.post("http://localhost:5050/v1/chat/completions", json=payload, timeout=2)
        if response.status_code == 200:
            suggestion = response.json()["choices"][0]["message"]["content"]
            # На всякий случай чистим от мусора
            return suggestion.strip().replace('"', "").replace("...", "")
    except Exception as e:
        print(f"Ошибка LLM: {e}")
        return ""
    return ""
