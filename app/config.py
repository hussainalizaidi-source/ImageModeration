from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_USER: str = "your_user"
    MONGO_PASS: str = "your_pass"
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_DB: str = "your_db"
    AUTH_SOURCE: str = "admin"
    HIVE_API_KEY: str = "your_hive_api_key"

    @property
    def MONGODB_URI(self):
        # URL-encode credentials
        username = quote_plus(self.MONGO_USER)
        password = quote_plus(self.MONGO_PASS)
        return (
            f"mongodb://{username}:{password}@{self.MONGO_HOST}:"
            f"{self.MONGO_PORT}/{self.MONGO_DB}?authSource={self.AUTH_SOURCE}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
