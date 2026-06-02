import sys
import os
from loguru import logger


def setup_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="INFO",
        colorize=True
    )
    os.makedirs("logs", exist_ok=True)
    logger.add(
        "logs/agent.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG"
    )
    return logger
