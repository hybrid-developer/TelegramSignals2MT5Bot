from pyrogram import Client, filters
import forwarder_config as cfg

app = Client(
    cfg.SESSION_NAME,
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    phone_number=cfg.PHONE_NUMBER
)

@app.on_message(filters.chat(cfg.SOURCE_CHATS))
def forward_signal(client, message):
    try:
        if cfg.FORWARD_MODE.lower() == "forward":
            message.forward(chat_id=cfg.TARGET_CHAT)
        else:
            message.copy(chat_id=cfg.TARGET_CHAT)

        print(f"Copied: {message.text or '[non-text]'}")
    except Exception as e:
        print("Copy failed:", e)

app.run()
