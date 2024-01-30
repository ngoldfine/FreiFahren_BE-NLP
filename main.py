import os
import re
from fuzzywuzzy import process
import telebot
import json
from dotenv import load_dotenv
import requests

class TicketInspector:
    def __init__(self, time, train, station, direction):
        #self.time = time
        self.train = train
        self.station = station
        self.direction = direction
        

ubahn_lines = {
'U1': ['Warschauer Straße', 'Uhland Straße'], 
'U2': ['Pankow', 'Ruhleben'], 
'U3': ['Krumme Lanke', 'Warschauer Straße'],
'U4': ['Innsbrucker Platz', 'Nollendorfplatz'],
'U5': ['Hauptbahnhof', 'Hönow'],
'U6': ['Alt-Tegel', 'Alt-Mariendorf'],
'U7': ['Rathaus Spandau', 'Rudow'], 
'U8': ['Wittenau', 'Hermannstraße'],
'U9': ['Osloer Straße', 'Rathaus Steglitz'],
}
sbahn_lines = {
'S1': ['Oranienburg', 'Wannsee'],
'S2': ['Bernau', 'Blankenfelde'], 
'S3': ['Erkner', 'Spandau'],
'S5': ['Strausberg Nord', 'Westkreuz'],
'S7': ['Potsdam Hauptbahnhof', 'Ahrensfelde'],
'S8': ['Wildau', 'Birkenwerder'], 
'S9': ['Flughafen BER', 'Spandau'],
'S25': ['Teltow Stadt', 'Hennigsdorf'],
'S26': ['Waidmannslust', 'Teltow Stadt'],
'S41': [None, None],
'S42': [None, None],
'S45': ['Flughafen BER', 'Südkreuz'],
'S46': ['Königs Wusterhausen', 'Westend'],
'S75': ['Wartenberg', 'Warschauer Straße'], 
'S47': ['Spindlersfeld', 'Hermannstraße'], 
'S85': ['Grünau', 'Pankow'],
}
merged_lines = {**ubahn_lines, **sbahn_lines}

def find_line(text, lines):
    # remove all whitespaces from the text
    text = text.replace(' ', '')
    for key in lines.keys():
        if key.lower() in text.lower():
            return key
    return None

# get station_data from json file
with open('data.json', 'r') as f:
    stations_data = json.load(f)

def format_text(text):
    # Replace all '-' with whitespaces and convert to lowercase
    text = text.lower().replace('-', ' ').replace('.', ' ').replace(',', ' ')
    # Remove all isolated 's' and 'u' 
    text = re.sub(r'\b(s|u)\b', '', text)
    return text

def find_station(text, threshold=80):
    all_stations = []

    # Add all stations and synonyms to the list
    for station_type in stations_data.values():
        for station, synonyms in station_type.items():
            all_stations.append(station.lower())
            all_stations.extend([syn.lower() for syn in synonyms])

    best_match, score = process.extractOne(text, all_stations)
    if score >= threshold:
        # Find the station that matches the best match
        for station_type in stations_data.values():
            for station, synonyms in station_type.items():
                if best_match in [station.lower()] + [syn.lower() for syn in synonyms]:
                    return station
    return None

def find_direction(text):
    text = format_text(text)

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
                    found_direction = find_station(word)
                    if found_direction:
                        # Replace the word that was identified as a station, not the found direction
                        replace_segment = keyword + ' ' + word
                        text_without_direction = text.replace(replace_segment, keyword, 1).strip()
                        return found_direction, text_without_direction

    return None, text

def handle_get_off(text):
    getting_off_keywords = ['ausgestiegen', 'raus', 'aussteigen', 'got off', 'get off', 'getting off', 'steigen aus']
    
    # if any of the keywords are in the text return True
    for keyword in getting_off_keywords:
        if keyword in text:
            return True

def check_if_station_is_actually_direction(text, ticket_inspector):
    line = ticket_inspector.train.lower()
    text = text.lower()
    
    # get the word after the line
    line_index = text.rfind(line)
    after_line = text[line_index + len(line):].strip()
    after_line_words = after_line.split()
    print(f'After line: {after_line_words}') 
    if len(after_line_words) > 0:
        # check if the word after the line is a station
        found_station = find_station(after_line_words[0])
        print(f'Word after the line: {after_line_words[0]}')
        print(f'Station after the train: {found_station}')
        if found_station:
            return True
    return False

def fetch_station_id(station):
    url = f'https://v6.vbb.transport.rest/stations?query={station}'
    print(url)
    response = requests.get(url)
    data = response.json()

    if data:
        first_key = list(data.keys())[0]  # Get the first key in the dictionary
        station_id = data[first_key]['id']  # Use the first key to access the ID
        return station_id
    else:
        print("No data found for station:", station)
        return None


def correct_direction(ticket_inspector, lines_with_final_station):
    print('Correcting direction')
    if ticket_inspector.train in lines_with_final_station.keys():
        print('Train is in lines_with_final_station')
        if ticket_inspector.direction in lines_with_final_station[ticket_inspector.train]:
            print('Direction is in final stations')
            return ticket_inspector 
        elif ticket_inspector.direction and ticket_inspector.station and ticket_inspector.train:
            # Get final stations of the line
            final_stations = lines_with_final_station[ticket_inspector.train]
            final_stations = [station.replace(' ', '') for station in final_stations]
            
            # Get the ids of the final stations
            station_ids = [fetch_station_id(station) for station in final_stations]
            print('IDs of the final stations: ',station_ids)
            return ticket_inspector

        else:
            print('Not enough information to correct direction')
            ticket_inspector.direction = None
            return ticket_inspector
        
                
def verify_direction(ticket_inspector, text, unformatted_text):
    # Set the Ringbahn to always be directionless
    if ticket_inspector.train == 'S41' or ticket_inspector.train == 'S42':
        ticket_inspector.direction = None
        
    # direction should be None if the ticket inspector got off the train
    if handle_get_off(text):
        ticket_inspector.direction = None

    # if station is mentioned directly after the line, it is the direction, for example "U8 Hermannstraße" is most likely "U8 Richtung Hermannstraße"
    if check_if_station_is_actually_direction(unformatted_text, ticket_inspector):
        print('Station is actually direction')
        ticket_inspector.direction = ticket_inspector.station
        ticket_inspector.station = None
        
    # Check if the directiion is the final station of the line and correct it if it is not
    ticket_inspector = correct_direction(ticket_inspector, merged_lines)
    return ticket_inspector
    
if __name__ == "__main__":
    load_dotenv()  # take environment variables from .env.
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    bot = telebot.TeleBot(BOT_TOKEN)

    print('Bot is running... 🏃‍♂️')

    @bot.message_handler(func=lambda msg: True)
    def get_info(message):
        text = message.text
        found_line = find_line(text, merged_lines)

        # remove ',', '.', '-' and isolated u + s from the text
        text = format_text(text)
        result = find_direction(text)
        found_direction = result[0]
        text_without_direction = result[1]
        print('Passed text without direction: ' + text_without_direction)
        # Passing text without direction to not confuse the direction with a station
        found_station = find_station(text_without_direction)
        if found_line or found_station or found_direction:
            print(f'Found station: {found_station}')
            print(f'Found line: {found_line}')
            ticket_inspector = TicketInspector(time=None, train=found_line, station=found_station, direction=found_direction)

            # verify direction by checking if:
            # 1. The train is a Ringbahn
            # 2. The ticket inspector got off the train
            verified_ticket_inspector = verify_direction(ticket_inspector, text, message.text)
            print(verified_ticket_inspector.__dict__)
        else:
            print('No valuable information found')
            return

    bot.infinity_polling()