import importlib.util
from os.path import dirname
from threading import Thread
from config import TELEGRAM_API_TOKEN, TELEGRAM_PROXY_URL
from app import app
from telebot import TeleBot, apihelper


def load_handlers():
    handler_dir = dirname(__file__) + "/handlers/"
    for name in handler_names:
        spec = importlib.util.spec_from_file_location(name, f"{handler_dir}{name}.py")
        spec.loader.exec_module(importlib.util.module_from_spec(spec))


@app.on_event("startup")
def start_bot():
    if TELEGRAM_API_TOKEN:
        bot = TeleBot(TELEGRAM_API_TOKEN)

    handler_thread = Thread(target=load_handlers)
    handler_thread.start()

    from app.telegram import utils  # setup custom handlers
    utils.setup()

    thread = Thread(target=bot.infinity_polling, daemon=True)
    thread.start()


def send_status_change_report(bot, message, user_id, message_id, new_status):
    report_message = f"User {user_id} status changed to {new_status}"
    bot.send_message(message.chat.id, report_message, message_id)


def report_status_change(bot, message, user_id, message_id, new_status):
    send_status_change_report(bot, message, user_id, message_id, new_status)

    with apihelper.proxy_from_url(TELEGRAM_PROXY_URL):
        if new_status == "deleted":
            report_user_deletion(bot, message, user_id, message_id)
        else:
            report_user_subscription_revoked(bot, message, user_id, message_id)


from .handlers.report import (  # noqa
    report,
    report_new_user,
    report_user_modification,
    report_user_deletion,
    report_status_change,
    report_user_usage_reset,
    report_user_data_reset_by_next,
    report_user_subscription_revoked,
    report_login
)

__all__ = [
    "bot",
    "report",
    "report_new_user",
    "report_user_modification",
    "report_user_deletion",
    "report_status_change",
    "report_user_usage_reset",
    "report_user_data_reset_by_next",
    "report_user_subscription_revoked",
    "report_login"
]
