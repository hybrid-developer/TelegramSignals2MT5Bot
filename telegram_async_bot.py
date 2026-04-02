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

from parser import SignalParser
from executor import execute, build_tp_scaling
from manager import manage_positions
from logger import (
    log_signal_received,
    log_filter_rejected,
    log_execution_rejected,
    log_trade_placed,
    log_trade_failed,
)
from ai_filter import is_a_plus

API_TOKEN = config.TELEGRAM_BOT_TOKEN
ALLOWED_CHAT_IDS = config.TELEGRAM_CHAT_IDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
parser = SignalParser()


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


@dp.channel_post()
async def handle_channel_post(message):
    logging.info("===== NEW CHANNEL POST =====")
    logging.info(f"CHAT ID   : {message.chat.id}")
    logging.info(f"CHAT TYPE : {message.chat.type}")
    logging.info(f"TEXT      : {message.text}")
    logging.info("SENDER    : channel_post")

    if message.chat.id not in ALLOWED_CHAT_IDS:
        logging.info(f"Ignored channel post: chat ID {message.chat.id} is not in ALLOWED_CHAT_IDS={ALLOWED_CHAT_IDS}")
        return

    if not message.text:
        logging.info("Ignored channel post: no text")
        return

    raw_text = message.text.strip()
    logging.info(f"AUTHORIZED CHANNEL SIGNAL:\n{raw_text}")

    signal = parser.parse(raw_text)
    if not signal:
        logging.warning("Parser rejected signal")
        return

    logging.info(f"Parsed signal: {signal}")
    log_signal_received(signal, source_chat=message.chat.id, raw_signal=raw_text)

    if not is_a_plus(signal):
        logging.warning("Signal rejected by AI filter")
        log_filter_rejected(signal, reason="Rejected by AI filter", source_chat=message.chat.id, raw_signal=raw_text)
        return

    account = mt5.account_info()
    if account is None:
        logging.error("Failed to fetch MT5 account info")
        log_execution_rejected(signal, reason="Failed to fetch MT5 account info", source_chat=message.chat.id, raw_signal=raw_text)
        return

    balance = account.balance
    signal["tp_levels"] = build_tp_scaling(signal.get("tps", []))

    try:
        result = execute(signal, balance)
        logging.info(f"Execution result: {result}")

        if isinstance(result, str):
            log_execution_rejected(signal, reason=result, source_chat=message.chat.id, raw_signal=raw_text)
            return

        if isinstance(result, dict):
            for item in result.get("results", []):
                if item.get("success"):
                    log_trade_placed(
                        signal=signal,
                        tp=item.get("tp"),
                        tp_index=item.get("tp_index"),
                        lot=item.get("lot"),
                        order_id=item.get("order_id"),
                        deal_id=item.get("deal_id"),
                        source_chat=message.chat.id,
                        raw_signal=raw_text,
                    )
                else:
                    log_trade_failed(
                        signal=signal,
                        tp=item.get("tp"),
                        tp_index=item.get("tp_index"),
                        lot=item.get("lot", config.MULTI_TP_LOT_SIZE),
                        reason=item.get("error"),
                        source_chat=message.chat.id,
                        raw_signal=raw_text,
                    )

        manage_positions()

    except Exception as e:
        logging.exception(f"Execution failed: {e}")
        log_execution_rejected(signal, reason=str(e), source_chat=message.chat.id, raw_signal=raw_text)


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
