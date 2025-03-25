from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # POSTGRES_USER: str
    # POSTGRES_PASSWORD: str
    # POSTGRES_HOST: str
    POSTGRES_DB: str
    PGADMIN_DEFAULT_EMAIL: str
    PGADMIN_DEFAULT_PASSWORD: str
    APPLICATION_PORT: str
    PAYSTACK_SECRET_KEY: str
    PAYSTACK_BASE_URL: str
    POSTGRES_URL: str
    EMAIL_SENDER: str
    EMAIL_RECEIVER: str
    EMAIL_PASSWORD: str
    SMTP_SERVER: str
    SMTP_PORT: int
    AUTH_SECRET_KEY: str
    CALLBACK_URL: str
    NOREPLY_EMAIL: str
    NOREPLY_PASSWORD: str
    ICT_SMTP_SERVER: str

    class Config:
        env_file = './.env'
        extra = 'ignore'


settings = Settings()
