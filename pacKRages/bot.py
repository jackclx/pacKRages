import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
import asyncio
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
import re

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
    uploads_dir = '/Users/jack/Desktop/Python /ParcelTracker2/uploads'  # Set your uploads directory path
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
            caption = f'Name: {name}\nYour parcel is in box: {photo_counter}'
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)
            photo_counter = (photo_counter % 5) + 1
        queue.task_done()

# Main function
if __name__ == '__main__':
    token_id = '6893237714:AAG7Ndju2OWHrCVMldfzBfUshvapeEHj0Fk'
    application = ApplicationBuilder().token(token_id).build()
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    application.run_polling()

