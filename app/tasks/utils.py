import requests
from app.config import settings
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def send_telegram_message(chat_id: str, text: str):
    logger.info(f"Sending message to {chat_id}")
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    response = requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

    if response.status_code != 200:
        logger.error(f"Telegram error: {response.text}")
        raise Exception(f"Telegram error: {response.text}")
    
