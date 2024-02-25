# Freifahren

## What is Freifahren?
Freifahren is a project that aims to track all ticket inspectors in the berlin public transport system. The goal is to provide a live map of all ticket inspectors in the city, so that people can avoid them for whatever reason.

The data for the live map is provided by the community of the [Freifahren](https://t.me/freifahren_BE) Telegram group. Members of the group are reporting when they see ticket inspectors and the data is then processed and displayed on the map. This repository is responsible for the natural language processing and the data processing of the messages in the Telegram group.

**Current Accuracy:** 82.7% of messages are processed perfectly, 17.3% of messages are processed with some errors.

## Quickstart Guide

### Prerequisites
- Python 3.6 or higher

### Setup
1. Clone the repository
````bash
git clone https://github.com/johan-t/freiFahren
````
2. Install the required packages with `pip install -r requirements.txt`
3. Set the environment variable `BOT_TOKEN` to your Bot API Token. You can get one by creating a new bot with the [BotFather](https://t.me/botfather).

### Run the bot
````bash
python main.py
````
Once the bot is running it will start processing the messages it receives from the Telegram group.

## How does it work?
When the bot notices a new message in the group it will trigger the `extract_data` function. This function will extract the relevant information of station where the ticket inspectors were seen, the name of line they were on, the direction the train was going as well as the time of the sighting. 

### how extract_data works 

The `extract_data` function is separated into two parts. In the first part we are initially getting the station, line and direction from the messages. In the second part we are correcting the data, by validating it using the already collected data about the stations, lines and directions.

### find_station

The find_station function is responsible for finding the stations mentioned in the messages. It is called multiple times in the pipeline of the extract_data function. 
It uses an NER model to find what characters in the message are stations. The NER model is trained on the labeled messages from the group.
We then pass the info of the NER model into a fuzzy matching algorithm to find the most similar station out of the list of stations and their synonyms.


### find_line

The find_line function is responsible for finding the lines mentioned in the messages. It uses a simple word search to identify the lines in the messages. The word search is done using a list of all the lines in the Berlin public transport system.

### find_direction

The find_direction function is responsible for finding the direction mentioned in the messages. It splits the message into two parts seperated by a direction keyword, for example "torwards". It then looks for a station in the part after the keyword by using `find_station`.

### validate_data
Once we have the basic data gathered we can cross validate it with the data we already have with the following rules:
- The ringbahn is always directionless.
- If it is mentioned that the inspectors got off the train, the ticket inspectors should be directionless and without a line.
- If the direction was set to a not valid station for example by using the info of the station and the line.


