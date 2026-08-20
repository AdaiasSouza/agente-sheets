# src/logger.py
import logging
import os
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = os.getenv("LOG_PATH", "logs/agente.log")

def configurar_logger(nome: str = "agente") -> logging.Logger:
    """
    Configura e retorna um logger com handlers para
    arquivo e console.
    """
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    logger = logging.getLogger(nome)

    # Evita duplicar handlers se o logger já foi configurado
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Formato das mensagens
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-7s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler — arquivo
    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Handler — console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger