import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

TOKEN = 'YOUR_TOKEN'


def load_data():
    try:
        with open('data/data.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return {}


async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("آخرین وضعیت ترافیکی محور های شمالی", callback_data="menu_1")],
        [InlineKeyboardButton("آخرین وضعیت ترافیکی سایر محور ها", callback_data="menu_3")],  # New menu button
        [InlineKeyboardButton("محورهای مسدود", callback_data="menu_2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text('منوی اصلی:', reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text('منوی اصلی:', reply_markup=reply_markup)


async def main_road_menu(update: Update, context: CallbackContext) -> None:
    data = load_data()

    if not isinstance(data, list) or len(data) < 2 or not isinstance(data[1], dict):
        await update.callback_query.edit_message_text("Error loading data. Please try again later.")
        return

    keyboard = [[InlineKeyboardButton(key, callback_data=f"key_{key}")] for key in data[1].keys()]
    keyboard.append([InlineKeyboardButton("بازگشت به منوی اصلی>>", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(f'{data[0]}\n اطلاعات در دسترس:', reply_markup=reply_markup)


# Function to handle new menu (Data[2])
async def other_road_menu(update: Update, context: CallbackContext) -> None:
    data = load_data()

    if not isinstance(data, list) or len(data) < 3 or not isinstance(data[2], dict):
        await update.callback_query.edit_message_text("Error loading data for the new menu.")
        return

    keyboard = [[InlineKeyboardButton(key, callback_data=f"new_key_{key}")] for key in data[2].keys()]
    keyboard.append([InlineKeyboardButton("بازگشت به منوی اصلی>>", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(f'اطلاعات جدید در دسترس:', reply_markup=reply_markup)


# Function to handle Option 2 (Data[3])
async def road_closers(update: Update, context: CallbackContext) -> None:
    data = load_data()

    if not isinstance(data, list) or len(data) < 4:
        await update.callback_query.edit_message_text("Error loading data[3].")
        return

    value = data[3] if isinstance(data[3], str) else json.dumps(data[3], indent=2)
    keyboard = [[InlineKeyboardButton("بازگشت به منوی اصلی>>", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(f'آخرین وضعیت ترافیکی سایر محور ها:\n{value}',
                                                  reply_markup=reply_markup)


async def handle_menu_key(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    data = load_data()

    # Check if data[1] is a dictionary
    if not isinstance(data, list) or len(data) < 2 or not isinstance(data[1], dict):
        await query.edit_message_text(text="Error loading data.")
        return

    # Extract the key from the callback data (removing 'key_' prefix)
    key = query.data.replace("key_", "", 1)  # This removes 'key_' only once
    value = data[1].get(key, "No value found")

    keyboard = [[InlineKeyboardButton("بازگشت به منوی اصلی>>", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=f'{key}: {value}', reply_markup=reply_markup)


async def handle_new_menu_key(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    data = load_data()

    if not isinstance(data, list) or len(data) < 3 or not isinstance(data[2], dict):
        await query.edit_message_text(text="Error loading new menu data.")
        return

    key = query.data.split("_")[2]
    value = data[2].get(key, "No value found")

    keyboard = [[InlineKeyboardButton("بازگشت به منوی اصلی>>", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=f'{key}: {value}', reply_markup=reply_markup)


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "menu_1":
        await main_road_menu(update, context)
    elif query.data == "menu_2":
        await road_closers(update, context)
    elif query.data == "menu_3":  # Handling new menu
        await other_road_menu(update, context)
    elif query.data == "main_menu":
        await start(update, context)
    elif query.data.startswith("key_"):
        await handle_menu_key(update, context)
    elif query.data.startswith("new_key_"):
        await handle_new_menu_key(update, context)


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()


if __name__ == '__main__':
    main()