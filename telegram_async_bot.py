#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
import config
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.exceptions import TelegramNetworkError
import MetaTrader5 as mt5

API_TOKEN = config.TELEGRAM_BOT_TOKEN
ALLOWED_CHAT_IDS = config.TELEGRAM_CHAT_IDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def on_startup():
    mt5_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    if not mt5.initialize(mt5_path):
        logging.error(f"MT5 init failed: {mt5.last_error()}")
        return False
    logging.info("MT5 ready")
    return True


async def on_shutdown():
    mt5.shutdown()
    logging.info("Shutdown complete")


@dp.message(Command("start"))
async def cmd_start(message):
    logging.info(f"/start received | chat_id={message.chat.id} | chat_type={message.chat.type}")

    if message.chat.id not in ALLOWED_CHAT_IDS:
        logging.info(f"Ignored /start from unauthorized chat: {message.chat.id}")
        return

    await message.answer("Bot is online and receiving messages.")


@dp.message()
async def debug_all_messages(message):
    logging.info("----- NEW MESSAGE -----")
    logging.info(f"CHAT ID   : {message.chat.id}")
    logging.info(f"CHAT TYPE : {message.chat.type}")
    logging.info(f"TEXT      : {message.text}")
    logging.info(f"FROM USER : {getattr(message.from_user, 'id', None)}")

    if message.chat.id not in ALLOWED_CHAT_IDS:
        logging.info(f"Ignored: chat ID {message.chat.id} is not in ALLOWED_CHAT_IDS={ALLOWED_CHAT_IDS}")
        return

    if not message.text:
        logging.info("Ignored: message has no text")
        return

    await message.answer(f"Received signal text:\n{message.text}")


async def main():
    print("Token loaded:", repr(API_TOKEN))

    if not await on_startup():
        return

    try:
        await dp.start_polling(bot, skip_updates=True)
    except TelegramNetworkError as e:
        logging.error(f"Telegram network error: {e}")
    finally:
        await on_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
