from elon.chat.notify import send_telegram
from elon.workers.celery_app import celery_app


@celery_app.task(name="elon.workers.tasks.notify.telegram_message")
def telegram_message(chat_id: str, text: str) -> None:
    send_telegram(chat_id, text)
