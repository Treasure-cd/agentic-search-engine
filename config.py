import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Config(BaseSettings):
    DATABASE_URL: str = Field(default="sqlite:///dev.db", env="DATABASE_URL")

    @property
    def db_type(self):
        return "postgres" if "postgresql" in self.DATABASE_URL else "sqlite"

# Load the configuration
settings = Config()