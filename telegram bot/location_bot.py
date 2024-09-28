

import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your bot token from BotFather
TOKEN = "7572982062:AAE9S_rrNyntTOtq0piXPez7JoFodjsis8Q"

# Define states for conversation
ENTER_LONGITUDE, ENTER_LATITUDE = range(2)

# Start Command: Initiates conversation and shows buttons
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("User Input", callback_data='user_input')],
        [InlineKeyboardButton("Share Location", callback_data='share_location')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Please choose an option:", reply_markup=reply_markup)

# Callback for button presses
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    if query.data == 'user_input':
        # Ask for longitude
        await query.edit_message_text("Please enter your Longitude:")
        return ENTER_LONGITUDE
    
    elif query.data == 'share_location':
        # Provide a button to share the user's location
        location_button = [[KeyboardButton("Share My Location", request_location=True)]]
        reply_markup = ReplyKeyboardMarkup(location_button, one_time_keyboard=True)
        await query.edit_message_text("Please share your location using the button below:")
        await update.effective_chat.send_message("Click the button to share your location:", reply_markup=reply_markup)
        return ConversationHandler.END  # End the conversation

# Receive Longitude: Store it and ask for Latitude
async def receive_longitude(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['longitude'] = update.message.text  # Store longitude
    await update.message.reply_text("Thank you! Now, please enter your Latitude:")
    return ENTER_LATITUDE

# Receive Latitude: Send the message about the location
async def receive_latitude(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['latitude'] = update.message.text  # Store latitude
    
    # Accessing the stored coordinates
    longitude = context.user_data['longitude']
    latitude = context.user_data['latitude']
    
    # Get the user's username
    user_username = update.message.from_user.username or "Unknown User"

    # Print the coordinates and username to the terminal
    print(f"User: {user_username}, Longitude: {longitude}, Latitude: {latitude}")

    # Send request to the API endpoint
    api_url = f"https://adminhierarchy.indiaobservatory.org.in/API/getRegionDetailsByLatLon?lat={latitude}&lon={longitude}"
    response = requests.get(api_url)

    # Print the API response to the terminal
    print("API Response:", response.json())

    # Check if the request was successful
    if response.status_code == 200:
        try:
            data = response.json()  # Parse the JSON response

            # Check if the structure is as expected
            if "text" in data and isinstance(data["text"], list):
                # Extracting the village, district, and state from the response
                village = next((item["name"] for item in data["text"] if item["type"] == "Village"), "Unknown Village")
                district = next((item["name"] for item in data["text"] if item["type"] == "District"), "Unknown District")
                state = next((item["name"] for item in data["text"] if item["type"] == "State"), "Unknown State")
                
                response_message = f"The village is {village},\nThe district is {district},\nThe state is {state}."
            else:
                response_message = "Unexpected data format received from the API."

        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            response_message = "Failed to fetch location details due to an error."

    else:
        response_message = "Failed to fetch location details. Please try again later."

    await update.message.reply_text("Thank you for providing the coordinates!")
    await update.message.reply_text(response_message)

    return ConversationHandler.END

# Handle the location sharing
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the user's location
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude

    # Get the user's username
    user_username = update.message.from_user.username or "Unknown User"

    # Print the coordinates and username to the terminal
    print(f"User: {user_username}, Longitude: {longitude}, Latitude: {latitude}")

    # Send request to the API endpoint
    api_url = f"https://adminhierarchy.indiaobservatory.org.in/API/getRegionDetailsByLatLon?lat={latitude}&lon={longitude}"
    response = requests.get(api_url)

    # Print the API response to the terminal
    print("API Response:", response.json())

    # Check if the request was successful
    if response.status_code == 200:
        try:
            data = response.json()  # Parse the JSON response

            # Check if the structure is as expected
            if "text" in data and isinstance(data["text"], list):
                # Extracting the village, district, and state from the response
                village = next((item["name"] for item in data["text"] if item["type"] == "Village"), "Unknown Village")
                district = next((item["name"] for item in data["text"] if item["type"] == "District"), "Unknown District")
                state = next((item["name"] for item in data["text"] if item["type"] == "State"), "Unknown State")
                
                response_message = f"The village is {village},\nThe district is {district},\nThe state is {state}."
            else:
                response_message = "Unexpected data format received from the API."

        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            response_message = "Failed to fetch location details due to an error."

    else:
        response_message = "Failed to fetch location details. Please try again later."

    await update.message.reply_text(response_message)

# End the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# Main function to run the bot
if __name__ == '__main__':
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TOKEN).build()

    # Conversation Handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ENTER_LONGITUDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_longitude)],
            ENTER_LATITUDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_latitude)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Run the bot
    application.run_polling()


import logging
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define states for the conversation handler
ENTER_LONGITUDE, ENTER_LATITUDE = range(2)

# Start command: shows the menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("User Input", callback_data='user_input')],
        [InlineKeyboardButton("Share Location", callback_data='share_location')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text('Please choose an option:', reply_markup=reply_markup)

# Button callback handler for the menu
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    if query.data == 'user_input':
        await query.edit_message_text("Please enter your Longitude:")
        return ENTER_LONGITUDE  # Move to asking for longitude

    elif query.data == 'share_location':
        location_button = [[KeyboardButton("Share My Location", request_location=True)]]
        reply_markup = ReplyKeyboardMarkup(location_button, one_time_keyboard=True)
        await query.edit_message_text("Please share your location using the button below:")
        await update.effective_chat.send_message("Click the button to share your location:", reply_markup=reply_markup)
        return ConversationHandler.END  # No further state needed for location sharing

# Receive longitude input
async def receive_longitude(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['longitude'] = update.message.text  # Store longitude
    await update.message.reply_text("Thank you! Now, please enter your Latitude:")
    return ENTER_LATITUDE  # Move to asking for latitude

# Receive latitude input
async def receive_latitude(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['latitude'] = update.message.text  # Store latitude

    longitude = context.user_data['longitude']
    latitude = context.user_data['latitude']
    
    # Fetch location details via API
    api_url = f"https://adminhierarchy.indiaobservatory.org.in/API/getRegionDetailsByLatLon?lat={latitude}&lon={longitude}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        village = next((item["name"] for item in data["text"] if item["type"] == "Village"), "Unknown Village")
        district = next((item["name"] for item in data["text"] if item["type"] == "District"), "Unknown District")
        state = next((item["name"] for item in data["text"] if item["type"] == "State"), "Unknown State")
        
        response_message = f"The village is {village},\nThe district is {district},\nThe state is {state}."
    else:
        response_message = "Failed to fetch location details. Please try again later."

    await update.message.reply_text(response_message)
    return ConversationHandler.END  # End conversation after receiving coordinates

# Location handler: handle shared location from the user
async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude

    # Fetch location details via API
    api_url = f"https://adminhierarchy.indiaobservatory.org.in/API/getRegionDetailsByLatLon?lat={latitude}&lon={longitude}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        village = next((item["name"] for item in data["text"] if item["type"] == "Village"), "Unknown Village")
        district = next((item["name"] for item in data["text"] if item["type"] == "District"), "Unknown District")
        state = next((item["name"] for item in data["text"] if item["type"] == "State"), "Unknown State")
        
        response_message = f"The village is {village},\nThe district is {district},\nThe state is {state}."
    else:
        response_message = "Failed to fetch location details. Please try again later."

    await update.message.reply_text(response_message)

# Cancel command handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# Error handler
def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f"Update {update} caused error {context.error}")

# Main function to set up the bot
def main():
    # Create the application instance
    application = Application.builder().token("YOUR_BOT_TOKEN_HERE").build()  # Replace with your actual bot token

    # Define the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ENTER_LONGITUDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_longitude)],
            ENTER_LATITUDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_latitude)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.LOCATION, location_handler))  # Handle location sharing

    # Log errors
    application.add_error_handler(error)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
