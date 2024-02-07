# import os
import re
from fuzzywuzzy import process
# import telebot
import json
# from dotenv import load_dotenv
from ner_lstm import identify_stations  # type: ignore
# from fuzzy import getSimilar  # type: ignore

class TicketInspector:
    def __init__(self, line, station, direction):
        # self.time = time
        self.line = line
        self.station = station
        self.direction = direction


with open('data/stations_and_lines.json', 'r') as f:
    lines_with_stations = json.load(f)


def find_line(text, lines):
    # remove all of the commas and dots from the text
    text = text.replace(',', ' ')
    text = text.replace('.', ' ')

    # Split the text into individual words
    words = text.split()

    # Sort lines by length in descending order to prioritize longer matches
    sorted_lines = sorted(lines.keys(), key=len, reverse=True)

    # Check if the word is 's' or 'u' and combine it with the next word
    for i, word in enumerate(words):
        if word.lower() == 's' or word.lower() == 'u':
            if i + 1 < len(words):
                words[i + 1] = word.lower() + words[i + 1]

    print(words)
    for word in words:
        for line in sorted_lines:
            if line.lower() in word.lower():
                return line
    return None


def format_text(text):
    # Replace all '-' with whitespaces and convert to lowercase
    text = text.lower().replace('-', ' ').replace('.', ' ').replace(',', ' ')
    # Remove all isolated 's' and 'u'
    text = re.sub(r'\b(s|u)\b', '', text)
    return text


with open('data/data.json', 'r') as f:
    stations_with_synonyms = json.load(f)




def get_all_stations(line=None):
    all_stations = []

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


# def find_station(text, line=None, threshold=80):
#     all_stations = get_all_stations(line)

#     # Perform the fuzzy matching with the gathered list of stations
#     best_match, score = process.extractOne(text, all_stations)  # type: ignore
#     if score >= threshold:
#         # Find the station that matches the best match
#         for station_type in stations_with_synonyms.values():
#             for station, synonyms in station_type.items():
#                 if best_match in [station.lower()] + \
#                         [synonym.lower() for synonym in synonyms]:
#                     return station
#     return None


def find_station(text, line=None, threshold=90):
    all_stations = get_all_stations(line)

    # Perform the fuzzy matching with the gathered list of stations
    best_match, score = process.extractOne(text, all_stations)
    if score >= threshold:
        # Find the station that matches the best match
        for station_type in stations_with_synonyms.values():
            for station, synonyms in station_type.items():
                if best_match in [station.lower()] + \
                        [synonym.lower() for synonym in synonyms]:
                    return station
    return None


def find_direction(text, line):
    direction_keywords = ['nach', 'richtung', 'bis', 'zu', 'to', 'towards', 'direction']

    for keyword in direction_keywords:
        if keyword in text:
            # Split the text at the keyword
            parts = text.split(keyword, 1)
            if len(parts) > 1:
                after_keyword = parts[1].strip()

                # Split the text after keyword into words
                words_after_keyword = after_keyword.split()

                # Find the first station name in the text after the keyword
                for word in words_after_keyword:
                    found_direction = find_station(word, line)
                    if found_direction:
                        # Remove the direction and the keyword from the text
                        replace_segment = keyword + ' ' + word
                        text_without_direction = text.replace(
                            replace_segment, ''
                        ).strip()
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
    if ticket_inspector.line is None:
        return False

    line = ticket_inspector.line.lower()
    text = unformatted_text.lower()

    # get the word after the line
    line_index = text.rfind(line)
    after_line = text[line_index + len(line) :].strip()
    after_line_words = after_line.split()
    if len(after_line_words) > 0:
        # check if the word after the line is a station
        found_station = find_station(after_line_words[0], ticket_inspector.line)

        all_final_stations = []
        for stations in lines_with_stations.items():
            all_final_stations.append(stations[0])
            all_final_stations.append(stations[-1])

        if ticket_inspector.line and found_station:
            # check if the station is in the line
            if (
                found_station == lines_with_stations[ticket_inspector.line][0]
                or found_station == lines_with_stations[ticket_inspector.line][-1]
            ):
                return True

    return False


def correct_direction(ticket_inspector, lines_with_final_station):
    if ticket_inspector.line in lines_with_final_station.keys():
        stations_of_line = lines_with_final_station[ticket_inspector.line]
        if ticket_inspector.direction in [stations_of_line[0], stations_of_line[-1]]:
            return ticket_inspector
        elif (
            ticket_inspector.station in lines_with_final_station[ticket_inspector.line]
            and ticket_inspector.line
            and ticket_inspector.direction
            in lines_with_final_station[ticket_inspector.line]
        ):
            # Get index of the station and direction in the list of stations
            station_index = lines_with_final_station[ticket_inspector.line].index(
                ticket_inspector.station
            )
            direction_index = lines_with_final_station[ticket_inspector.line].index(
                ticket_inspector.direction
            )

            # Check if the station is before or after the direction to correct it
            # example: 'S7 jetzt Warschauer nach Ostkreuz' should be S7 to Ahrensfelde
            if station_index < direction_index:
                ticket_inspector.direction = lines_with_final_station[
                    ticket_inspector.line
                ][-1]
            else:
                ticket_inspector.direction = lines_with_final_station[
                    ticket_inspector.line
                ][0]

            return ticket_inspector
        else:
            print('Not enough information to correct direction')
            ticket_inspector.direction = None
            return ticket_inspector

    else:
        print('Train is not in lines_with_final_station')
        return ticket_inspector


def verify_direction(ticket_inspector, text, unformatted_text):
    # Check if the direction is the final station of the line and correct it
    ticket_inspector = correct_direction(ticket_inspector, lines_with_stations)

    # Set the Ringbahn to always be directionless
    if ticket_inspector.line == 'S41' or ticket_inspector.line == 'S42':
        ticket_inspector.direction = None

    # if station is mentioned directly after the line, it is the direction
    # example 'U8 Hermannstraße' is most likely 'U8 Richtung Hermannstraße'
    if check_if_station_is_actually_direction(unformatted_text, ticket_inspector):
        ticket_inspector.direction = ticket_inspector.station
        ticket_inspector.station = None

    # direction should be None if the ticket inspector got off the train
    if handle_get_off(text):
        print('Ticket inspector got off the train')
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
    found_line = find_line(unformatted_text, lines_with_stations)
    ticket_inspector = TicketInspector(line=found_line, station=None, direction=None)

    text = format_text(unformatted_text)
    result = find_direction(text, ticket_inspector.line)
    found_direction = result[0]
    ticket_inspector.direction = found_direction
    text_without_direction = result[1]

    found_station = find_station(text_without_direction, ticket_inspector.line)
    ticket_inspector.station = found_station

    if found_line or found_station or found_direction:
        verify_direction(ticket_inspector, text, unformatted_text)
        verify_line(ticket_inspector, unformatted_text)
        
        return ticket_inspector.__dict__
    else:
        return None


# if __name__ == '__main__':
#     load_dotenv()  # take environment variables from .env.
#     BOT_TOKEN = os.getenv('BOT_TOKEN')
#     bot = telebot.TeleBot(BOT_TOKEN)

#     print('Bot is running...🏃‍♂️')

#     # Messages set to private for testing purposes
#     @bot.message_handler(func=lambda message: message.chat.type == 'private')
#     def get_info(message):
#         info = extract_ticket_inspector_info(message.text)
#         if info:
#             print(info)
#         else:
#             print('No valuable information found')
#             return None

#     bot.infinity_polling()
