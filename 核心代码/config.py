"""应用配置"""
import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'pipi-studio-secret-change-me')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DB_PATH = os.getenv('DB_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.db'))


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
