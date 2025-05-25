from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_USER: str
    MONGO_PASS: str
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str
    AUTH_SOURCE: str

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
