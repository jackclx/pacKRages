import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
import asyncio
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes,CallbackQueryHandler
from telegram import Update
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Image preprocessing and text extraction functions
def preprocess_image(image_path):
    img = Image.open(image_path)
    img = img.resize([dim * 2 for dim in img.size], Image.LANCZOS)
    img = img.convert('L')
    img = img.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)
    img = img.filter(ImageFilter.SHARPEN)
    return img

def extract_text(img):
    text = pytesseract.image_to_string(img)
    return text

def extract_name(text):
    # Try to match the first pattern

    
    # Try to match the second pattern
    match = re.search(r"TO \(ADDRESSEE\)[\s\S]*?\n\n(.*?)[\n\d]", text)
    if match:
        return match.group(1).strip()
    
    match = re.search(r"^(.*?)\n", text)
    if match:
        return match.group(1).strip()

    return "Name not found"

# File event handler
class MyHandler(FileSystemEventHandler):
    def __init__(self, queue):
        self.queue = queue

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            self.queue.put_nowait(event.src_path)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Monitoring for new photos...')
    queue = asyncio.Queue()
    uploads_dir = '/Users/jack/Desktop/Python /pacKRages/uploads'  # Set your uploads directory path
    event_handler = MyHandler(queue)
    observer = Observer()
    observer.schedule(event_handler, path=uploads_dir, recursive=False)
    observer.start()
    context.bot_data['photo_queue_processor'] = asyncio.create_task(process_photo_queue(context, queue, update.effective_chat.id))


# Process photo queue
async def process_photo_queue(context, queue, chat_id):
    photo_counter = 1
    while True:
        photo_path = await queue.get()
        preprocessed_img = preprocess_image(photo_path)
        name = extract_name(extract_text(preprocessed_img))

        with open(photo_path, 'rb') as photo:
            keyboard = [[InlineKeyboardButton("Claim", callback_data=f'claim-{photo_counter}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            caption = f'Name: {name}\nYour parcel is in box: {photo_counter}'
            message = await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, reply_markup=reply_markup)
            context.bot_data[f'photo_message_{photo_counter}'] = message.message_id
            photo_counter = (photo_counter % 5) + 1
        queue.task_done()

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Extract photo counter from the callback data
    _, photo_counter = query.data.split('-')

    # Delete the message with the photo
    message_id = context.bot_data.get(f'photo_message_{photo_counter}')
    if message_id:
        try:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=message_id)
            await query.edit_message_text(text=f"Photo {photo_counter} claimed!")  # Optional, if you want to show a confirmation message
        except Exception as e:
            logger.error(f"Error deleting message: {e}")



# Main function
if __name__ == '__main__':
    token_id = '6893237714:AAG7Ndju2OWHrCVMldfzBfUshvapeEHj0Fk'
    application = ApplicationBuilder().token(token_id).build()
    start_handler = CommandHandler("start", start)
    button_handler = CallbackQueryHandler(button)
    application.add_handler(button_handler)
    application.add_handler(start_handler)
    application.run_polling()



