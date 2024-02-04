import json
import csv
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)


def get_input_messages():
    with open('messages_and_times.json', 'r') as f:
        messages = json.load(f)
    input_messages = [message['message'] for message in messages]
    return input_messages


def label_data(messages):
    labeled_data = []
    for message in messages[:5]:  # Only label the first 5 messages for testing
        try:
            response = client.chat.completions.create(
                model='gpt-4-0125-preview',
                messages=[
                    {'role': 'system',
                     'content': '''
                        Du bist ein Experte des Berliner Öffentlichen
                        Nahverkehrs und musst dem Nutzer helfen Daten zu
                        labeln.

                        Der Nutzer wird dir eine Nachricht, aus einem Telegram
                        Chat geben, indem der der Standort von Kontrolleuren
                        gemeldet wird.

                        Deine Aufgabe wird es sein drei Relevante Infos aus
                        der Nachricht zu ziehen: Die Station wo der
                        Kontrolleur gemeldet wurde, die Sbahn oder Ubahn
                        Linie in der sich der Kontrolleur befindet und die
                        Endhaltestelle der Linie.

                        Deine Antwort sollte das folgende Format haben:

                        """
                        Direction: "Richtung",
                        Station: "Station",
                        Line:  "Linie"
                        """

                        Zum Beispiel sollte deine Antwort, so aussehen für
                        diese Nachricht.
                        Beispiel Nachricht: "
                        2x Hellblau U8 Hermannplatz Richtung Wittenau am
                        Bahnsteig"

                        Beispiel Antwort:
                        """
                        Direction: "Wittenau",
                        Station: "Hermannplatz",
                        Line: "U8"
                        """

                        Wenn die Nachricht in einem Punkt keine Relevanten
                        Infos enthält, setze ein leere Zeichenkette ein. Falls
                        sie gar keine Relevanten Infos enthält, setzte bei
                        Direction, Station und Line eine leere Zeichenkette
                        ein.

                        Beispiel Nachricht:
                        "U 8 Heinrich Heine str"

                        Beispiel Antwort:
                        """
                        Direction: "",
                        Station: "Heinrich-Heine-Straße",
                        Line: "U8"
                        """

                        Es hat oberste Priorität, dass deine Antwort in diesem
                        Format ist, da sie geparsed wird von einem Programm
                        welches dieses Format erwartet.

                        Es gibt ein paar extra Regeln,
                        die du beachten solltest:
                        1. Die Bahnen S41 und S42 sollten nie eine Richtung
                        haben, also sollte immer eine leere Zeichenkette für
                        Direction eingesetzt werden.
                        2. Wenn erwähnt wurde, dass die Kontrolleure die Bahn
                        verlassen haben sollte die Line und Direction auf eine
                        leere Zeichenkette gesetzt werden.
                        3. Straßenbahnen können ignoriert werden.
                        4. Manchmal geben Nutzer eine Richtung an die nicht
                        die Endhaltestelle der Bahn ist. Dafür solltest die
                        Endhaltestellen der Bahn im Kopf behalten.

                        Dies sind die Endhaltestellen der Linien:

                        U1: [Warschauerstraße, Uhlandstraße],
                        U2: [Pankow, Ruhleben]
                        U3: [Warschauerstraße, Krumme Lanke]
                        U4: [Nollendorfplatz, Innsbruckerplatz],
                        U5: [Hönow, Hauptbahnhof],
                        U6: [Alt-Tegel, Alt-Mariendorf],
                        U7: [Rathaus Spandau, Rudow],
                        U9: [Osloerstraße, Rathaus Steglitz],
                        S1: [Wannsee, Oranienburg],
                        S2: [Blankenfelde, Bernau],
                        S3: [Erkner, Spandau],
                        S5: [Strausberg Nord, Grunewald],
                        S7: [Ahrensfelde, Potsdam Hauptbahnhof],
                        S8: [Wildau, Birkenwerder],
                        S9: [Flughafen BER, Spandau],
                        S25: [Teltow Stadt, Henningsdorf],
                        S26: [Teltow Stadt, Blankenburg],
                        S45: [Flughafen BER, Charlottenburg]
                        S46: [Königs Wusterhausen, Westend],
                        S75: [Wartenberg, Ostbahnhof],
                        S47: [Spindlersfeld, Hermannstraße],
                        S85: [Grünau, Frohnau]

                        Bitte achte darauf, dass du die Stationen ohne S und U
                        vor der Station zurück gibst und dass du Straßen und
                        Plätze immer zusammen schreibst.

                        Beispielsweise statt "S + U Hauptbahnhof",
                        nur "Hauptbahnhof" oder statt "S Insbrucker Platz"
                        nur "Insbruckerplatz".
                    '''},
                 
                    {'role': 'user',
                     'content': f"""
                        Atme tief durch und label diese Nachricht
                        nach deinen Anweisungen.

                        Nachricht:
                        {message}
                    """}
                ],
                temperature=0.25
            )
            # Parse the response to extract station, line, and direction
            content = response.choices[0].message.content
            print('API reponse: ', content)
            parsed_data = parse_response(content)
            print('Parsed data: ', parsed_data)
            labeled_data.append(parsed_data)
        except Exception as e:
            print(f'An error occurred: {e}')
            labeled_data.append({
                'Station': 'Error',
                'Line': 'Error',
                'Direction': 'Error'
            })
    return labeled_data


def parse_response(content):
    # Initialize default values in case some information is missing
    parsed_data = {'Station': '', 'Line': '', 'Direction': ''}
    lines = content.split('\n')
    for line in lines:
        if 'Direction:' in line:
            parsed_data['Direction'] = line.split('"')[1]
        elif 'Line:' in line:
            parsed_data['Line'] = line.split('"')[1]
        elif 'Station:' in line:
            parsed_data['Station'] = line.split('"')[1]
    return parsed_data


def save_to_csv(labeled_data, input_messages):
    with open('labeled_messages.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'Input Message',
            'Station',
            'Line',
            'Direction'
        ])
        writer.writeheader()
        for i, data in enumerate(labeled_data):
            row = {'Input Message': input_messages[i], **data}
            writer.writerow(row)


if __name__ == '__main__':
    input_messages = get_input_messages()
    labeled_data = label_data(input_messages)
    save_to_csv(labeled_data, input_messages)
