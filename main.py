import logging
import os
from config import TOKEN_BOT_QR
from qr_gener import get_green_qrcode
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


logging.basicConfig(level=logging.INFO)

my_storg = MemoryStorage()

bot = Bot(token=TOKEN_BOT_QR, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=my_storg)


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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
