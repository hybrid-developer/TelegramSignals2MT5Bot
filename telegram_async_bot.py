import asyncio
from aiogram import Bot, Dispatcher, types
from parser import SignalParser
from executor import execute, build_tp_scaling
from ai_filter import is_a_plus
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS
import MetaTrader5 as mt5

# Initialize MT5
mt5.initialize()
parser = SignalParser()

# Initialize bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

async def handle_signal(message: types.Message):
    # Only messages from allowed chat IDs
    if TELEGRAM_CHAT_IDS and message.chat.id not in TELEGRAM_CHAT_IDS:
        return

    text = message.text
    signal = parser.parse(text)
    if not signal:
        await message.reply("❌ Could not parse signal")
        return

    if not is_a_plus(signal):
        await message.reply("⚠️ Signal rejected by AI filter")
        return

    signal["tp_levels"] = build_tp_scaling(signal["tps"])
    balance = mt5.account_info().balance
    result = execute(signal, balance)
    await message.reply(f"✅ Signal executed: {result}")

dp.register_message_handler(handle_signal, content_types=types.ContentTypes.TEXT)

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())