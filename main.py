import os
import telebot
import datetime
from dotenv import load_dotenv
from verify_info import verify_direction, verify_line
from process_message import (
    find_line,
    find_direction,
    find_station,
    format_text,
    lines_with_stations
)
from db_utils import create_table_if_not_exists, insert_ticket_info, update_info


class TicketInspector:
    def __init__(self, line, station, direction):
        self.line = line
        self.station = station
        self.direction = direction
        

def extract_ticket_inspector_info(unformatted_text):
    # usually just a question about an old report not a new report
    if '?' in unformatted_text:
        ticket_inspector = TicketInspector(line=None, station=None, direction=None)
        return ticket_inspector.__dict__
    
    found_line = find_line(unformatted_text, lines_with_stations)
    ticket_inspector = TicketInspector(line=found_line, station=None, direction=None)

    # Get the direction
    text = format_text(unformatted_text)
    found_direction = find_direction(text, ticket_inspector)[0]
    ticket_inspector.direction = found_direction

    # Pass the text without direction to avoid finding the direction again
    text_without_direction = find_direction(text, ticket_inspector)[1]
    found_station = find_station(text_without_direction, ticket_inspector)
    ticket_inspector.station = found_station

    # With the found info we can cross check the direction and line
    if found_line or found_station or found_direction:
        verify_direction(ticket_inspector, text)
        verify_line(ticket_inspector, text)
        
        return ticket_inspector.__dict__
    else:
        return None


def merge_messages(author_id, message, conversations, current_time):
    last_message = conversations[author_id][-1]
    last_message_time = last_message['time']
    time_difference = current_time - last_message_time

    # If the last message was sent less than 60 seconds ago, merge the messages
    if time_difference.total_seconds() <= 60:
        last_known_message = last_message['text']
        merged_text = f'{last_message["text"]} {message.text}'
        last_message['text'] = merged_text
        last_message['time'] = current_time
        info = extract_ticket_inspector_info(merged_text)
        last_message['info'] = info

        if info:
            update_info(
                last_known_message,
                current_time,
                merged_text,
                author_id,
                info.get('line'),
                info.get('direction'),
                info.get('station')
            )
            print('Merged info:', info)
        else:
            print('No valuable information found')
    else:
        process_new_message(author_id, message, current_time, conversations)


def process_new_message(author_id, message, current_time, conversations):
    info = extract_ticket_inspector_info(message.text)
    if author_id not in conversations:
        conversations[author_id] = []
    conversations[author_id].append({'text': message.text, 'time': current_time, 'info': info})
    if info:
        print('Found Info:', info)
        insert_ticket_info(
            current_time,
            message.text,
            author_id,
            info.get('line'),
            info.get('direction'),
            info.get('station')
        )
    else:
        print('No valuable information found')


if __name__ == '__main__':
    load_dotenv()
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    bot = telebot.TeleBot(BOT_TOKEN)
    conversations = {}

    create_table_if_not_exists()

    print('Bot is running...')
    
    DEV_CHAT_ID = os.getenv('DEV_CHAT_ID')
    FREIFAHREN_BE_CHAT_ID = os.getenv('FREIFAHREN_BE_CHAT_ID')
    
    @bot.message_handler(func=lambda message: message.chat.id in [
        int(DEV_CHAT_ID),
        int(FREIFAHREN_BE_CHAT_ID)
    ])
    def get_info(message):
        author_id = message.from_user.id
        current_time = datetime.datetime.now()

        if author_id in conversations and conversations[author_id]:
            merge_messages(author_id, message, conversations, current_time)
        else:
            process_new_message(author_id, message, current_time, conversations)
            
    bot.infinity_polling()
