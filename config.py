import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
    JWT_EXPIRATION_MINUTES = int(os.getenv('JWT_EXPIRATION_MINUTES', '60'))
    WORK_DIR = os.getenv('WORK_DIR', './work')
    ACP_EXPORT_CMD = os.getenv('ACP_EXPORT_CMD', './acp export')
    ACP_IMPORT_CMD = os.getenv('ACP_IMPORT_CMD', './acp import')
    AVERIFY_CMD = os.getenv('AVERIFY_CMD', './averify')
