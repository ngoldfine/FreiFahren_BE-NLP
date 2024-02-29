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


class TicketInspector:
    def __init__(self, line, station, direction):
        self.line = line
        self.station = station
        self.direction = direction
        

def extract_ticket_inspector_info(unformatted_text):
    # If the text contains a question mark, indicate that no processing should occur
    if '?' in unformatted_text:
        ticket_inspector = TicketInspector(line=None, station=None, direction=None)
        return ticket_inspector.__dict__
    
    found_line = find_line(unformatted_text, lines_with_stations)
    ticket_inspector = TicketInspector(line=found_line, station=None, direction=None)

    # Get the direction
    text = format_text(unformatted_text)
    found_direction = find_direction(text, ticket_inspector)[0]
    ticket_inspector.direction = found_direction

    # Get the station
    text_without_direction = find_direction(text, ticket_inspector)[1]
    found_station = find_station(text_without_direction, ticket_inspector)
    ticket_inspector.station = found_station

    # Verify the direction and line with the given information
    if found_line or found_station or found_direction:
        verify_direction(ticket_inspector, text)
        verify_line(ticket_inspector, text)
        
        return ticket_inspector.__dict__
    else:
        return None


if __name__ == '__main__':
    load_dotenv()  # take environment variables from .env.
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    bot = telebot.TeleBot(BOT_TOKEN)
    conversations = {}  # Dictionary to store conversations with more detailed structure

    print('Bot is running...🏃‍♂️')

    @bot.message_handler(func=lambda message: message.chat.type == 'private')  # private for testing
    def get_info(message):
        author_id = message.chat.id
        current_time = datetime.datetime.now()
        
        # Check if this author_id already has messages
        if author_id in conversations and conversations[author_id]:
            last_message = conversations[author_id][-1]  # Get the last message from this author_id
            last_message_time = last_message['time']
            time_difference = current_time - last_message_time
            
            if time_difference.total_seconds() <= 60:
                # If the new message is within one minute of the last message, merge them
                merged_text = f"{last_message['text']} {message.text}"
                
                # Update the last message in the conversation
                last_message['text'] = merged_text
                last_message['time'] = current_time  # Update the timestamp to the latest message
                info = extract_ticket_inspector_info(merged_text)
                last_message['info'] = info

                # Print the information after merging the messages
                if info:
                    print('Found Info:', info)
                else:
                    print('No valuable information found')
            else:
                # Handle as a new message
                process_new_message(author_id, message, current_time)
        else:
            # This is the first message from this author_id or no previous conversation exists
            process_new_message(author_id, message, current_time)

    def process_new_message(author_id, message, current_time):
        info = extract_ticket_inspector_info(message.text)
        if author_id not in conversations:
            conversations[author_id] = []
        conversations[author_id].append({'text': message.text, 'time': current_time, 'info': info})
        if info:
            print('Found Info:', info)
        else:
            print('No valuable information found')
            
    bot.infinity_polling()
