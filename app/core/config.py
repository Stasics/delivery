from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    SECRET_KEY: str = "a788ad13d21cd08c003aed983b1d8df67b5eaa9beebdd8ccf67cad7905393256"  # Замени это на свой секретный ключ
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
settings = Settings()  # <--- Добавь эту строку
