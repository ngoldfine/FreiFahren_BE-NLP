import os
import re
from fuzzywuzzy import process
import telebot
import json
from dotenv import load_dotenv
from NER.TransportInformationRecognizer import TextProcessor


class TicketInspector:
    def __init__(self, line, station, direction):
        # self.time = time
        self.line = line
        self.station = station
        self.direction = direction
        

with open('stations_and_lines.json', 'r') as f:
    lines_with_stations = json.load(f)
   

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
    # Remove all isolated 's' and 'u'
    text = re.sub(r'\b(s|u)\b', '', text)
    return text


with open('data.json', 'r') as f:
    stations_with_synonyms = json.load(f)


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
    NER_results = TextProcessor.process_text(text)
    print(f'Text returned from the NER: {NER_results}')

    for NER_result in NER_results:
        # Get the fuzzy match of the NER result with the stations
        best_match = get_best_match(NER_result, all_stations, threshold)
        if best_match:
            # Find the correct station name for the best match
            found_station_name = find_match_in_stations(best_match, stations_with_synonyms)
            if found_station_name:
                # Catch secret direction, as the next station
                # This is triggered when the direction could not be found via direction keywords
                if ticket_inspector.direction is None and len(NER_results) > 1:
                    best_match = get_best_match(NER_results[1], all_stations, threshold)
                    if best_match:
                        direction = find_match_in_stations(best_match, stations_with_synonyms)
                        if direction:
                            ticket_inspector.direction = direction
                            print(f'set direction to be: {direction}')
                return found_station_name
    return None


direction_keywords = ['nach', 'richtung', 'bis', 'zu', 'to', 'towards', 'direction', 'ri']


def find_direction(text, ticket_inspector):
    words = text.split()
    for word in words:
        if word in direction_keywords:
            found_direction_keyword = word
            # Split the text at the keyword
            parts = text.split(word, 1)
            if len(parts) > 1:
                after_keyword = parts[1].strip()

                # Split the text after keyword into words
                words_after_keyword = after_keyword.split()

                # Find the first station name in the text after the keyword
                for word in words_after_keyword:
                    found_direction = find_station(word, ticket_inspector)
                    if found_direction:
                        # Remove the direction and the keyword from the text
                        replace_segment = word
                        text_without_direction = text.replace(
                            replace_segment, ''
                        ).strip()
                        return found_direction, text_without_direction

                # If no station is found after the keyword, check word directly before the keyword
                index = words.index(found_direction_keyword)
                print('found word:', found_direction_keyword)
                if index > 0:
                    previous_word = words[index - 1]
                    print(f'previous_word: {previous_word}')
                    found_direction = find_station(previous_word, ticket_inspector)
                    if found_direction:
                        # Remove the direction and the keyword from the text
                        replace_segment = previous_word + ' ' + found_direction_keyword
                        text_without_direction = text.replace(
                            replace_segment, ''
                        ).strip()
                        return text_without_direction

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
            print('direction is not a final station')
            ticket_inspector.direction = None
            return ticket_inspector

    else:
        return ticket_inspector


def check_word_before_direction_keyword(unformatted_text, ticket_inspector):
    for keyword in direction_keywords:
        if keyword in unformatted_text:
            # Get the word directly before the keyword
            parts = unformatted_text.split(keyword, 1)
            if len(parts) > 1:
                before_keyword = parts[0].strip()
                words_before_keyword = before_keyword.split()
                if len(words_before_keyword) > 0:
                    # Check if the word before the keyword is a station
                    found_station = find_station(words_before_keyword[-1], ticket_inspector)
                    if found_station and found_station != ticket_inspector.station:
                        ticket_inspector.direction = found_station

                        return ticket_inspector
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
    if ticket_inspector.direction is None and ticket_inspector.station is not None:
        print('station is actually direction')
        check_if_station_is_actually_direction(text, ticket_inspector)

    if ticket_inspector.direction is None:
        check_word_before_direction_keyword(text, ticket_inspector)

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

    text = format_text(unformatted_text)
    result = find_direction(text, ticket_inspector)
    found_direction = result[0]
    print(f'found_direction: {found_direction}')
    ticket_inspector.direction = found_direction
    text_without_direction = result[1]

    print(f'text_without_direction: {text_without_direction}')
    found_station = find_station(text_without_direction, ticket_inspector)
    print(f'found_station: {found_station}')
    ticket_inspector.station = found_station

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

    print('Bot is running...🏃‍♂️')

    while True:
        message = input("\nEnter your message: ")
        info = extract_ticket_inspector_info(message)
        if info:
            print(info)
        else:
            print('No valuable information found')
