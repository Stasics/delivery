import secrets
import os

# Генерация случайного ключа (желательно один раз при настройке)
def generate_secret_key(length=32):
    return secrets.token_hex(length) # Генерирует случайную строку из hex-символов

# Пример использования:
secret_key = generate_secret_key()
print(f"Generated Secret Key: {secret_key}")

# Использование ключа в .env (рекомендуется)
# Создай файл .env и добавь туда:
# SECRET_KEY=ТВОЙ_СГЕНЕРИРОВАННЫЙ_КЛЮЧ