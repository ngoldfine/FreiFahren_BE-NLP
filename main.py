import os
import re

import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

print('Bot is running... 🏃‍♂️')

class DeconstructedMessage:
    def __init__(self, time, train, station, direction):
        self.time = time
        self.train = train
        self.station = station
        self.direction = direction
        

ubahn_lines = ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9']
sbahn_lines = ['S1', 'S2', 'S3', 'S5', 'S7', 'S8' 'S9', 'S25', 'S26', 'S41', 'S42', 'S45', 'S46', 'S75', 'S47', 'S85']

def find_line(text, lines):
    # remove all whitespaces from the text
    text = text.replace(' ', '')
    for line in lines:
        if line.lower() in text.lower():
            return line
    return None

@bot.message_handler(func=lambda msg: True)
def get_info(message):
    text = message.text
    found_line = find_line(text, ubahn_lines + sbahn_lines)

    if found_line:
        print(f'Found line: {found_line}')
    else:
        print('No valuable information found')
        return


bot.infinity_polling()