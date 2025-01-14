import logging
from telegram import Update
from telegram.ext import (Application, CommandHandler, MessageHandler, ContextTypes)
from telegram.ext.filters import PHOTO
import asyncpraw
import requests
import os


# Configure logging
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

# Reddit API setup
reddit = asyncpraw.Reddit(
    client_id="HzIs8P0iWxVGvtkpuP9gfw",
    client_secret="NuOhRtQaL4taAQ9bY6QXbt19OPAaHw",
    user_agent = "myRedditBot/1.0 (by u/EffectiveSouth3544)",
    username="EffectiveSouth3544",
    password="AdinRoss@21701"
)


# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! Send me a message to post . You can also send media (images/videos) with captions."
    )


SAVE_PATH = '/home/hbg2024/image/'

async def post_tweet_with_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    caption = update.message.caption or ""  # Get the caption
    media_file = None  # Initialize media_file to handle different types
    media_type = None  # This variable will store whether it's 'photo' or 'video'


    try:
        # Check if the message contains a photo or video
        if update.message.photo:
                media_file = update.message.photo[-1]  # Get the highest resolution photo
                file_name = f"photo_{media_file.file_id}.jpg"  # Generate file name dynamically
                media_type = "photo"
        elif update.message.video:
                media_file = update.message.video  # Handle video
                file_name = f"video_{media_file.file_id}.mp4"  # Generate file name dynamically
                media_type = "video"
        else:
                # No valid media found
                await update.message.reply_text("No media file found in the message.")
                return

        logging.info("Received media file. Starting download...")

            # Get the file using its file_id
        file = await context.bot.get_file(media_file.file_id)
        file_path = os.path.join(SAVE_PATH, file_name)

            # Download the file
        await file.download_to_drive(file_path)

            # Acknowledge successful download

        logging.info(f"Media saved at: {file_path}")

            # Add your code here to upload the file to Twitter or process it further

        # Upload to Reddit
        logging.info("Uploading media to Reddit...")
        subreddit = await reddit.subreddit("desipornleaks")

        if media_type == "photo":
              await  subreddit.submit_image(title=caption, image_path=file_path)
        elif media_type == "video":
              await  subreddit.submit_video(title=caption, video_path=file_path)
        else:
               await update.message.reply_text("Unsupported media type.")
               return

                # Step 3: Delete the media file from server after upload
        os.remove(file_path)
        logging.info(f"Temporary media file {file_path} deleted from server.")

                # Step 4: Send a success message
        await update.message.reply_text(f"reddit with media and text '{caption}' posted successfully!")


    except Exception as e:
        await update.message.reply_text(f"Failed to post image: {e}")


# Main function
def main():
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = "7757070657:AAEwkKIxfESoAnEesuCAzdUC5w6TA54dEpg"

    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(PHOTO, post_tweet_with_media))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
