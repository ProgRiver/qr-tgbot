import logging
import os
from qr_gener import get_green_qrcode
from aiogram.utils.executor import start_webhook
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


TOKEN = os.getenv("TOKEN_BOT_QR")

HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME")

# webhook settings
WEBHOOK_HOST = f"https://{HEROKU_APP_NAME}.herokuapp.com"
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = os.getenv("PORT", default=8000)

logging.basicConfig(level=logging.INFO)

my_storg = MemoryStorage()

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=my_storg)
dp.middleware.setup(LoggingMiddleware())


class QRgen(StatesGroup):
    url_user = State()


@dp.message_handler(commands=['start'], state=None)
async def msg_start_bot(msg: types.Message):
    await msg.answer(f"👋 <i>{msg.from_user.full_name}</i>, введите ссылку")
    await msg.answer("Начало ссылки обязательно с <b>'https://'</b>")
    await QRgen.url_user.set()


@dp.message_handler(content_types=types.ContentType.TEXT, state=QRgen.url_user)
async def input_user_url(msg: types.Message, state: FSMContext):
    if not msg.text.startswith("https://"):
        await msg.answer("ℹ️ Проверьте ссылку и начните заново")
        await state.finish()
    else:
        new_user_id = msg.from_user.id
        url = msg.text
        file_name = get_green_qrcode(url, new_user_id)
        res = types.InputFile(file_name)
        await msg.answer_photo(res, caption="✅ QR код вашей ссылки готов. Проверьте.")
        await state.finish()
        os.remove(file_name)


async def on_startup(dp):
    logging.warning("Starting connection. Старт.")
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dp):
    logging.warning("Shutting down. Завершение.")
    await bot.delete_webhook()


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
