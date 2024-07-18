from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

BASEDIR = Path(__file__).parent.parent


class JWTSettings(BaseSettings):
    private_key: Path = BASEDIR / 'certs' / 'jwt-private.pem'
    public_key: Path = BASEDIR / 'certs' / 'jwt-public.pem'
    algorithm: str = 'RS256'
    access_token_expire_minutes: int = 3
    refresh_token_expire_days: int = 90


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.auth-env', extra='ignore')
    jwt_settings: JWTSettings = JWTSettings()

    echo_sql: bool = True
    DATABASE_URL: str

    domain: str = 'localhost'


settings = Settings()
