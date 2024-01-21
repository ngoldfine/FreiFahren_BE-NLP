import os

import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

print('Bot is running... 🏃‍♂️')

messages = []
@bot.message_handler(func=lambda msg: True)
def get_info(message):
    messages.append(message.text)
    print(messages)
    



bot.infinity_polling()