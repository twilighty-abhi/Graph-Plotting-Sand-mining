import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your bot token from BotFather
TOKEN = "Meow Meow Meoww"

# Start Command: Shows welcome message and fetch location option
async def start(update: Update, context):
    # Create a button that asks for location
    location_button = KeyboardButton(text="Share Location", request_location=True)
    reply_markup = ReplyKeyboardMarkup([[location_button]], one_time_keyboard=True)

    await update.message.reply_text(
        "Hello! I am your Location Bot.\n\nClick the button below to share your location.",
        reply_markup=reply_markup
    )

# Location Handler: Responds with the user's location
async def location(update: Update, context):
    user_location = update.message.location
    if user_location:
        await update.message.reply_text(
            f"Your location is:\nLatitude: {user_location.latitude}\nLongitude: {user_location.longitude}"
        )
    else:
        await update.message.reply_text("Sorry, I couldn't get your location.")

# Main function to run the bot
if __name__ == '__main__':
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.LOCATION, location))

    # Start the Bot
    logger.info("Bot is running...")
    application.run_polling()
