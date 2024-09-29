import logging
from typing import Union, TypedDict
import requests
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler
)

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define data structures for API responses
class LocationResponse(TypedDict):
    village: str
    district: str
    state: str

class ApiError(TypedDict):
    error: Union[str, requests.exceptions.RequestException]

# Initialize the bot
bot = Bot(token="7572982062:AAE9S_rrNyntTOtq0piXPez7JoFodjsis8Q")

# Command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    user_name = update.message.chat.first_name
    welcome_message = (
        f"Hi {user_name}, Welcome to the Location Bot! "
        "You can use this bot to get location details based on coordinates or by sharing your location."
    )
    await bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)
    await show_location_options(update, context)

# Command: Show location options (manual or share location)
async def show_location_options(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Enter Coordinates", callback_data='manual_input')],
        [InlineKeyboardButton("Share My Location", callback_data='share_location')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await bot.send_message(chat_id=update.effective_chat.id, text="How would you like to provide your location?", reply_markup=reply_markup)

# Callback: Handle manual or share location input
async def location_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    if query.data == 'manual_input':
        await query.edit_message_text("Please enter your latitude (as a number):")
        context.user_data['state'] = 'waiting_for_latitude'
    elif query.data == 'share_location':
        await query.edit_message_text("Please share your location using the Telegram location-sharing feature.")

# Function to receive coordinates and fetch location details
async def receive_coordinates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.user_data.get('state')
    
    try:
        if state == 'waiting_for_latitude':
            # Process Latitude Input
            context.user_data['latitude'] = float(update.message.text)
            logger.info(f"Received Latitude: {context.user_data['latitude']}")  # Log latitude
            await update.message.reply_text("Thank you! Now, please enter your longitude (as a number):")
            context.user_data['state'] = 'waiting_for_longitude'  # Transition to waiting for longitude
            
        elif state == 'waiting_for_longitude':
            # Process Longitude Input
            context.user_data['longitude'] = float(update.message.text)
            logger.info(f"Received Longitude: {context.user_data['longitude']}")  # Log longitude
            
            # Fetch location details after getting both coordinates
            await fetch_location_details(update, context.user_data['longitude'], context.user_data['latitude'])

            # Resetting state after fetching location details
            context.user_data['state'] = None  # Clear state after use
            del context.user_data['latitude']
            del context.user_data['longitude']
            
        else:
            await update.message.reply_text("Please enter the latitude first.")
            
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a valid number.")

# Fetch location details from API using longitude and latitude
async def fetch_location_details(update: Update, longitude: float, latitude: float) -> None:
    try:
        api_url = f"https://adminhierarchy.indiaobservatory.org.in/API/getRegionDetailsByLatLon?lat={latitude}&lon={longitude}"
        response = requests.get(api_url)
        logger.info(f"API Response Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Ensure that data is in the correct format
            if isinstance(data, dict) and "text" in data:
                village = next((item["name"] for item in data["text"] if isinstance(item, dict) and item.get("type") == "Village"), "Unknown Village")
                district = next((item["name"] for item in data["text"] if isinstance(item, dict) and item.get("type") == "District"), "Unknown District")
                state = next((item["name"] for item in data["text"] if isinstance(item, dict) and item.get("type") == "State"), "Unknown State")

                response_message = f"Village: {village}\nDistrict: {district}\nState: {state}"

                # Send the location details back to the user
                await update.message.reply_text(response_message)
            else:
                await update.message.reply_text("Unexpected data format received.")
        else:
            await update.message.reply_text("Failed to fetch location details. Please try again.")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"An error occurred: {e}")
        logger.error(f"API request error: {e}")

# Handle shared location from the user
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude

    logger.info(f"Received location: Longitude: {longitude}, Latitude: {latitude}")
    await fetch_location_details(update, longitude, latitude)

# Main function to set up the bot
def main() -> None:
    application = ApplicationBuilder().bot(bot).build()

    # Add handlers for commands and location handling
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(location_callback, pattern='manual_input|share_location'))

    # MessageHandler for receiving coordinates
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_coordinates))  # For both coordinates

    # MessageHandler for receiving location sharing
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
