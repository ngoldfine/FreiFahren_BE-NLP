import os
import re
from fuzzywuzzy import process
import telebot
import datetime
import json
from dotenv import load_dotenv
from NER.TransportInformationRecognizer import TextProcessor


class TicketInspector:
    def __init__(self, line, station, direction):
        self.line = line
        self.station = station
        self.direction = direction


def load_data(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


lines_with_stations = load_data('stations_and_lines.json')
stations_with_synonyms = load_data('data.json')
   

def format_text_for_line_search(text):
    # Replace commas, dots, dashes, and slashes with spaces
    text = text.replace(',', ' ').replace('.', ' ').replace('-', ' ').replace('/', ' ')
    words = text.split()

    # When 's' or 'u' are followed by a number, combine them
    formatted_words = []
    for i, word in enumerate(words):
        lower_word = word.lower()
        if (lower_word == 's' or lower_word == 'u') and i + 1 < len(words):
            combined_word = lower_word + words[i + 1]
            formatted_words.append(combined_word)
        else:
            formatted_words.append(word)

    return ' '.join(formatted_words)


def process_matches(matches_per_word):
    # Decide what to return based on the collected matches
    if len(matches_per_word) == 1:
        return sorted(matches_per_word[list(matches_per_word.keys())[0]], key=len, reverse=True)[0]
    elif any(len(matches) > 1 for matches in matches_per_word.values()):
        for _word, matches in matches_per_word.items():
            if len(matches) > 1:
                return sorted(matches, key=len, reverse=True)[0]
    return None


def find_line(text, lines):
    formatted_text = format_text_for_line_search(text)
    if formatted_text is None:
        return None

    words = formatted_text.split()
    sorted_lines = sorted(lines.keys(), key=len, reverse=True)
    matches_per_word = {}

    for word in set(words):
        for line in sorted_lines:
            if line.lower() in word.lower():
                matches_per_word.setdefault(word, []).append(line)

    return process_matches(matches_per_word)


def format_text(text):
    # Replace all '-' with whitespaces and convert to lowercase
    text = text.lower().replace('.', ' ').replace(',', ' ')
    # Remove all isolated 's' and 'u' to reduce noise
    text = re.sub(r'\b(s|u)\b', '', text)
    return text


def get_all_stations(line=None):
    all_stations = []
    line = line.upper() if line is not None else None

    if line is not None:
        # If a specific line is provided, add stations and synonyms from that line
        stations_of_line = lines_with_stations.get(line, [])
        all_stations.extend([station.lower() for station in stations_of_line])
        
        # Add synonyms for the stations on the specified line
        for station in stations_of_line:
            for station_type in stations_with_synonyms.values():
                if station in station_type:
                    synonyms = station_type[station]
                    all_stations.extend([synonym.lower() for synonym in synonyms])
                    break
    else:
        # If no line is specified, add all stations and synonyms
        for station_type in stations_with_synonyms.values():
            for station, synonyms in station_type.items():
                all_stations.append(station.lower())
                all_stations.extend([synonym.lower() for synonym in synonyms])

    return all_stations


def get_best_match(text, items, threshold=75):
    match = process.extractOne(text, items)
    best_match, score = match
    if score >= threshold:
        return best_match
    return None


def find_match_in_stations(best_match, stations_with_synonyms):
    for station_type in stations_with_synonyms.values():
        for station, synonyms in station_type.items():
            if best_match in [station.lower()] + [synonym.lower() for synonym in synonyms]:
                return station
    return None


def find_station(text, ticket_inspector, threshold=75):
    all_stations = get_all_stations(ticket_inspector.line)
    
    # Use the NER Model to get the unrecognized stations from the text
    ner_results = TextProcessor.process_text(text)

    for ner_result in ner_results:
        # Get the fuzzy match of the NER result with the stations
        best_match = get_best_match(ner_result, all_stations, threshold)
        if best_match:
            # Find the correct station name for the best match
            found_station_name = find_match_in_stations(best_match, stations_with_synonyms)
            if found_station_name:
                # Catch secret direction, as the next station
                # This is triggered when the direction could not be found via direction keywords
                if ticket_inspector.direction is None and len(ner_results) > 1:
                    best_match = get_best_match(ner_results[1], all_stations, threshold)
                    if best_match:
                        direction = find_match_in_stations(best_match, stations_with_synonyms)
                        if direction:
                            ticket_inspector.direction = direction
                return found_station_name
    return None


def remove_direction_and_keyword(text, direction_keyword, direction):
    if direction_keyword and direction:
        replace_segment = f'{direction_keyword} {direction}'
        text_without_direction = text.replace(replace_segment, '').strip()
        return text_without_direction
    return text


direction_keywords = ['nach', 'richtung', 'bis', 'zu', 'to', 'towards', 'direction', 'ri']


def find_direction(text, ticket_inspector):
    words = text.split()
    word_after_keyword = None  # Because we want to use it outside the loop

    for word in words:
        if word in direction_keywords:
            found_direction_keyword = word
            parts = text.split(word, 1)
            if len(parts) > 1:
                after_keyword = parts[1].strip()
                words_after_keyword = after_keyword.split()

                for word_after_keyword in words_after_keyword:
                    found_direction = find_station(word_after_keyword, ticket_inspector)
                    if found_direction:
                        text_without_direction = remove_direction_and_keyword(
                            text, found_direction_keyword, word_after_keyword
                        )
                        return found_direction, text_without_direction

                # If no station found after keyword, check the word directly before the keyword
                index = words.index(found_direction_keyword)
                if index > 0:
                    previous_word = words[index - 1]
                    found_direction = find_station(previous_word, ticket_inspector)
                    if found_direction:
                        text_without_direction = remove_direction_and_keyword(
                            text, found_direction_keyword, word_after_keyword
                        )
                        return found_direction, text_without_direction

    return None, text


def handle_get_off(text):
    getting_off_keywords = [
        'ausgestiegen',
        'raus',
        'aussteigen',
        'got off',
        'get off',
        'getting off',
        'steigen aus',
    ]
    
    # if any of the keywords are in the text return True
    for keyword in getting_off_keywords:
        if keyword in text:
            return True


def check_if_station_is_actually_direction(unformatted_text, ticket_inspector):
    line = ticket_inspector.line.lower()
    text = unformatted_text.lower()

    # Get the final stations of the line
    final_stations = []
    if ticket_inspector.line in lines_with_stations:
        final_stations.append(lines_with_stations[ticket_inspector.line][0])
        final_stations.append(lines_with_stations[ticket_inspector.line][-1])

    # Get the word after the line
    line_index = text.rfind(line)
    after_line = text[line_index + len(line):].strip()
    after_line_words = after_line.split()
    if len(after_line_words) > 0:
        # Check if the word after the line is a station
        found_station = find_station(after_line_words[0], ticket_inspector)

        if found_station:
            # Check if the station matches one of the final stations of the line
            if found_station in final_stations and found_station != ticket_inspector.station:
                ticket_inspector.direction = found_station
                # remove the word after the line from the text
                text_without_direction = text.replace(after_line_words[0], '').strip()
                ticket_inspector.station = find_station(text_without_direction, ticket_inspector)

                return ticket_inspector

    return False


def correct_direction(ticket_inspector, lines_with_final_station):
    line = ticket_inspector.line
    direction = ticket_inspector.direction
    station = ticket_inspector.station

    # No need to correct the direction if it is already a final station
    if line is None:
        return ticket_inspector

    stations_of_line = lines_with_final_station[line]

    # If direction is a final station, return ticket_inspector
    if direction in [stations_of_line[0], stations_of_line[-1]]:
        return ticket_inspector

    # If station and direction are in the line, correct the direction
    if station in stations_of_line and direction in stations_of_line:
        station_index = stations_of_line.index(station)
        direction_index = stations_of_line.index(direction)

        # Correct the direction based on the station's position
        # For example: 'S7 jetzt Alexanderplatz richtung Ostkreuz' should be to Ahrensfelde
        if station_index < direction_index:
            ticket_inspector.direction = stations_of_line[-1]
        else:
            ticket_inspector.direction = stations_of_line[0]

        return ticket_inspector

    # If direction is not a final station, set direction to None
    ticket_inspector.direction = None
    return ticket_inspector

    
def verify_direction(ticket_inspector, text):
    # direction should be None if the ticket inspector got off the train
    if handle_get_off(text):
        ticket_inspector.direction = None
        ticket_inspector.line = None
        return ticket_inspector
    
    # Check if the direction is the final station of the line and correct it
    ticket_inspector = correct_direction(ticket_inspector, lines_with_stations)
    
    # Set the Ringbahn to always be directionless
    if ticket_inspector.line == 'S41' or ticket_inspector.line == 'S42':
        ticket_inspector.direction = None

    # if station is mentioned directly after the line, it is the direction
    # example 'U8 Hermannstraße' is most likely 'U8 Richtung Hermannstraße'
    if ticket_inspector.direction is None and ticket_inspector.station and ticket_inspector.line:
        check_if_station_is_actually_direction(text, ticket_inspector)

    # direction should be None if the ticket inspector got off the train
    if handle_get_off(text):
        ticket_inspector.direction = None
        ticket_inspector.line = None

    return ticket_inspector


def handle_ringbahn(text):
    ring_keywords = ['ring', 'ringbahn']
    # remove commas and dots from the text
    text = text.replace(',', '').replace('.', '')
    # split the text into individual words
    words = text.lower().split()
    # check if any word in the text matches the ring keywords
    for word in words:
        if word in ring_keywords:
            return True
    return False

    
def verify_line(ticket_inspector, text):
    # If it the ring set to S41
    if handle_ringbahn(text.lower()) and ticket_inspector.line is None:
        ticket_inspector.line = 'S41'
        
    return ticket_inspector
        

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

    @bot.message_handler(func=lambda message: message.chat.type == 'private')
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
    
