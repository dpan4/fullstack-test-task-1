import json
import urllib.request
import urllib.error

API_KEY = "sk-xt-8327032cc2ebcc0a0fc3e3a95ff99ef7459ad3587a25668d"
BASE_URL = "https://api.xkiro.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("--- Проверка списка моделей ---")
try:
    req = urllib.request.Request(f"{BASE_URL}/models", headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode())
        models = [m["id"] for m in data.get("data", [])]
        print(f"Доступные модели: {models}\n")
except Exception as e:
    print(f"Ошибка получения списка моделей: {e}\n")
    models = ["qwen/qwen3.8-max:free"]

print("--- Тестирование chat/completions ---")
for model in models:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "ping"}]
    }).encode("utf-8")

    req = urllib.request.Request(f"{BASE_URL}/chat/completions", data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = json.loads(response.read().decode())
            print(f"Модель [{model}]: Успешно!")
            print(f"  -> Ответ: {res_body['choices'][0]['message']['content']}\n")
    except urllib.error.HTTPError as e:
        print(f"Модель [{model}]: Ошибка HTTP {e.code}")
        print(f"  -> Ответ сервера: {e.read().decode()}\n")
    except Exception as e:
        print(f"Модель [{model}]: Ошибка -> {e}\n")